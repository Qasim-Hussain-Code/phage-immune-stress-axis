"""Check or push this project's existing private GitHub repository.

The default only checks. --push sends exactly the verified commit to main;
this command never creates a repository or changes its visibility.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LOGIN = 'Qasim-Hussain-Code'
REPOSITORY = LOGIN + '/phage-immune-stress-axis'
URL = 'https://github.com/' + REPOSITORY + '.git'
AUTHOR_NAME = 'Qasim Hussain'
GITHUB_COMMITTER = ('GitHub', 'noreply@github.com')
MAX_BLOB_BYTES = 5_000_000
MAX_SCAN_BYTES = 40_000_000
SECRET_PATTERNS = [re.compile(pattern) for pattern in (
    rb'gh[pousr]_[A-Za-z0-9]{30,}', rb'github_pat_[A-Za-z0-9_]{30,}',
    rb'AKIA[0-9A-Z]{16}', rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    rb'\bxox[baprs]-[A-Za-z0-9-]{20,}', rb'\bsk-proj-[A-Za-z0-9_-]{30,}')]


class PolicyError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise PolicyError(message)


class Commands:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.environment = dict(os.environ, GIT_TERMINAL_PROMPT='0', GH_PROMPT_DISABLED='1', GH_HOST='github.com',
                                GIT_NO_REPLACE_OBJECTS='1', GIT_GRAFT_FILE=os.devnull)
        # Unlike GIT_CONFIG_GLOBAL, GIT_CONFIG changes only `git config`'s
        # lookup and could conceal settings still used by the push transport.
        self.environment.pop('GIT_CONFIG', None)

    def run(self, args, *, binary=False, data=None, timeout=45, allowed_codes=(0,)):
        try:
            result = subprocess.run(args, cwd=self.root, env=self.environment,
                                    input=data, capture_output=True, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise PolicyError('Command unavailable or timed out; no credential output retained.') from error
        require(result.returncode in allowed_codes,
                'Command failed; inspect the private working copy. No credential output retained.')
        return result.stdout if binary else result.stdout.decode('utf-8').strip()

    def git(self, *args, **kwargs):
        return self.run(['git', '--no-replace-objects', '-c', 'safe.directory=' + self.root.as_posix(), *args], **kwargs)

    def github(self, endpoint, *, paginate=False):
        flags = ['--paginate', '--slurp'] if paginate else []
        try:
            return json.loads(self.run(['gh', 'api', '--hostname', 'github.com', *flags, endpoint]))
        except (ValueError, UnicodeError) as error:
            raise PolicyError('GitHub returned an invalid metadata response.') from error


def validate_repository(metadata):
    require(isinstance(metadata, dict) and metadata.get('full_name') == REPOSITORY,
            'Unexpected GitHub repository.')
    require(metadata.get('private') is True, 'Repository must remain private; no push attempted.')
    require(metadata.get('default_branch') == 'main', 'Unexpected default branch.')
    require(metadata.get('archived') is not True, 'Repository is archived.')


def validate_contributors(pages):
    require(isinstance(pages, list) and pages and all(isinstance(page, list) for page in pages),
            'Missing or malformed GitHub contributor response.')
    people = [person for page in pages for person in page]
    require(len(people) == 1 and isinstance(people[0], dict) and people[0].get('login') == LOGIN,
            'GitHub must list exactly the researcher account as contributor.')


def check_destinations(commands):
    require(commands.git('remote', 'get-url', '--all', 'origin').splitlines() == [URL],
            'Unexpected or multiple effective fetch URLs.')
    require(commands.git('remote', 'get-url', '--push', '--all', 'origin').splitlines() == [URL],
            'Unexpected or multiple effective push URLs.')
    # An explicit origin pushurl can mask pushInsteadOf during get-url, while
    # pushing an explicit URL would still apply that rewrite. Reject applicable
    # redirects in either namespace; unrelated rewrite rules are harmless.
    rewrites = commands.git('config', '--null', '--get-regexp',
                           r'^url\..*\.(insteadof|pushinsteadof)$', allowed_codes=(0, 1))
    for record in rewrites.split('\0'):
        if not record:
            continue
        key, separator, prefix = record.partition('\n')
        require(bool(separator), 'Malformed Git URL rewrite setting.')
        suffix = '.pushinsteadof' if key.endswith('.pushinsteadof') else '.insteadof'
        base = key[len('url.'):-len(suffix)]
        require(not URL.startswith(prefix) or base + URL[len(prefix):] == URL,
                'A Git URL rewrite redirects the approved destination.')


def _valid_author_email(value):
    if not isinstance(value,str) or not 3 <= len(value) <= 254 or value.count('@')!=1:
        return False
    local,domain=value.split('@')
    return (len(local)<=64 and not local.startswith('.') and not local.endswith('.') and '..' not in local
            and re.fullmatch(r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~.-]+",local) is not None
            and re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?'
                             r'(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+',domain) is not None)


def load_approved_author(commands):
    """Read one explicit repository-local approval, never current user.email."""
    payload=commands.git('config','--local','--no-includes','--null','--get-all','pisa.authorEmail',
                         binary=True,allowed_codes=(0,1))
    message='Configure exactly one well-formed approved email in local pisa.authorEmail before release.'
    require(isinstance(payload,bytes),message)
    values=payload.split(b'\0')
    require(len(values)==2 and values[-1]==b'',message)
    try:
        email=values[0].decode('utf-8')
    except UnicodeError as error:
        raise PolicyError(message) from error
    require(_valid_author_email(email),message)
    return AUTHOR_NAME,email


def validate_history(history,approved_author):
    require(isinstance(approved_author,tuple) and len(approved_author)==2
            and approved_author[0]==AUTHOR_NAME and _valid_author_email(approved_author[1]),
            'An explicit approved researcher identity is required.')
    encoded = history.encode('utf-8')
    require(len(encoded) <= MAX_BLOB_BYTES, 'Commit metadata exceeds its 5 MB scan bound.')
    require(not any(pattern.search(encoded) for pattern in SECRET_PATTERNS),
            'Credential pattern found in commit metadata; no credential value is printed.')
    commits = 0
    for record in history.split('\x1e'):
        if not record.strip():
            continue
        fields = record.strip('\r\n').split('\0')
        require(len(fields) == 7, 'Malformed commit metadata.')
        sha, author, email, committer, committer_email, subject, body = fields
        require(re.fullmatch(r'[0-9a-f]{40}', sha) is not None, 'Invalid commit identity.')
        require((author, email) == approved_author, 'Only the researcher may author project commits.')
        require((committer, committer_email) in {approved_author,GITHUB_COMMITTER}, 'Unexpected commit committer.')
        require(re.fullmatch(r'[a-z]+(?:_[a-z]+){1,2}', subject) is not None,
                'Commit subjects require two or three lowercase underscore-separated words.')
        require(re.search(r'(?im)^\s*co-authored-by\s*:', body) is None,
                'Coauthor trailers are not permitted.')
        commits += 1
    require(commits > 0, 'No commits found for release.')
    return commits


def scan_new_history(commands, remote_sha):
    """Check all new blobs, including a credential deleted by a later commit."""
    listing = commands.git('rev-list', '--objects', remote_sha + '..HEAD')
    objects = []
    for row in listing.splitlines():
        sha, _, path = row.partition(' ')
        require(re.fullmatch(r'[0-9a-f]{40}', sha) is not None, 'Malformed object inventory.')
        parts = Path(path).parts
        forbidden = {'.cache', '.codex', '.agents', '.aws', '.ssh', '.venv', 'tmp'}
        require(not forbidden.intersection(parts) and not Path(path).name.lower().startswith('.env')
                and Path(path).suffix.lower() not in {'.pem', '.key', '.p12', '.pfx'}
                and Path(path).name not in {'AGENTS.md', 'Pasted text.txt'},
                'New history includes a private working file.')
        objects.append(sha)
    if not objects:
        return 0
    inventory = commands.git('cat-file', '--batch-check',
                             data=('\n'.join(objects)+'\n').encode())
    blobs = []
    sizes = {}
    total = 0
    for row in inventory.splitlines():
        sha, kind, size_text = row.split()
        require(sha in objects and size_text.isdecimal(), 'Malformed object metadata.')
        if kind != 'blob':
            continue
        size = int(size_text)
        require(size <= MAX_BLOB_BYTES, 'New history includes a blob above 5 MB.')
        total += size
        require(total <= MAX_SCAN_BYTES, 'New-history scan exceeds its 40 MB bound.')
        blobs.append(sha)
        sizes[sha] = size
    if not blobs:
        return 0
    payload = commands.git('cat-file', '--batch', data=('\n'.join(blobs)+'\n').encode(), binary=True)
    offset = 0
    for expected in blobs:
        end = payload.find(b'\n', offset)
        require(end >= 0, 'Truncated object response.')
        header = payload[offset:end].decode('ascii').split()
        require(header == [expected, 'blob', str(sizes[expected])], 'Unexpected object response.')
        offset = end + 1
        body = payload[offset:offset+sizes[expected]]
        require(len(body) == sizes[expected] and payload[offset+len(body):offset+len(body)+1] == b'\n',
                'Truncated object payload.')
        require(not any(pattern.search(body) for pattern in SECRET_PATTERNS),
                'Credential pattern found in new history; no credential value is printed.')
        offset += len(body) + 1
    require(offset == len(payload), 'Unexpected trailing object payload.')
    return len(blobs)


def preflight(commands):
    identity = commands.github('user')
    require(isinstance(identity, dict) and identity.get('login') == LOGIN, 'Unexpected authenticated account.')
    validate_repository(commands.github('repos/' + REPOSITORY))
    validate_contributors(commands.github('repos/' + REPOSITORY + '/contributors?anon=true&per_page=100', paginate=True))
    approved_author=load_approved_author(commands)
    check_destinations(commands)
    require(not commands.git('status', '--porcelain=v1'), 'Commit or remove working changes before release.')
    require(commands.git('branch', '--show-current') == 'main', 'Release requires the main branch.')
    require(commands.git('rev-parse', '--is-shallow-repository') == 'false',
            'A complete local history is required for release checks.')
    head = commands.git('rev-parse', 'HEAD')
    require(re.fullmatch(r'[0-9a-f]{40}', head) is not None, 'Invalid local commit.')
    count = validate_history(commands.git('log', 'HEAD', '--format=%x1e%H%x00%an%x00%ae%x00%cn%x00%ce%x00%s%x00%b'),
                             approved_author)
    remote = commands.github('repos/' + REPOSITORY + '/commits/main')
    remote_sha = remote.get('sha') if isinstance(remote, dict) else None
    require(isinstance(remote_sha, str) and re.fullmatch(r'[0-9a-f]{40}', remote_sha) is not None,
            'Invalid remote commit.')
    commands.git('merge-base', '--is-ancestor', remote_sha, head)
    scanned = scan_new_history(commands, remote_sha)
    commands.run([sys.executable, str(commands.root/'scripts/check_release.py'), '--git-scope', 'head'], timeout=300)
    require(commands.git('rev-parse', 'HEAD') == head and not commands.git('status', '--porcelain=v1'),
            'Working source changed during release checks.')
    return head, remote_sha, count, scanned


def execute(commands, push=False):
    head, previous, count, scanned = preflight(commands)
    result = {'schema_version': 1, 'status': 'private_push_preflight_passed',
              'repository': REPOSITORY, 'visibility': 'private', 'local_commit': head,
              'remote_main_commit_before': previous, 'commits_checked': count,
              'new_blobs_scanned': scanned, 'sole_github_contributor': LOGIN,
              'sole_project_author': AUTHOR_NAME, 'force_push': False, 'visibility_changed': False,
              'tool_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if push:
        check_destinations(commands)
        validate_repository(commands.github('repos/' + REPOSITORY))
        require(commands.git('rev-parse', 'HEAD') == head, 'Local commit changed before push.')
        # Pin both the destination and the source commit; no default refspecs or tag pushes.
        credentials = ['-c', 'credential.helper=', '-c', 'credential.helper=!gh auth git-credential']
        commands.git(*credentials, '-c', 'push.followTags=false', 'push', '--recurse-submodules=no',
                     URL, head + ':refs/heads/main', timeout=120)
        ref = commands.git(*credentials, 'ls-remote', URL, 'refs/heads/main').split()
        require(len(ref) == 2 and ref == [head, 'refs/heads/main'], 'Remote Git reference did not match.')
        commit = commands.github('repos/' + REPOSITORY + '/commits/main')
        require(isinstance(commit, dict) and commit.get('sha') == head, 'GitHub commit did not match.')
        validate_repository(commands.github('repos/' + REPOSITORY))
        validate_contributors(commands.github('repos/' + REPOSITORY + '/contributors?anon=true&per_page=100', paginate=True))
        result.update(status='private_push_verified', remote_main_commit=head)
    result['checked_utc'] = datetime.now(timezone.utc).isoformat()
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--push', action='store_true', help='Push the checked commit after all checks pass.')
    args = parser.parse_args(argv)
    try:
        result = execute(Commands(ROOT), push=args.push)
    except (PolicyError, ValueError, UnicodeError) as error:
        print('Private release refused: ' + str(error), file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

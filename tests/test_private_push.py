"""Offline release-policy cases; no test contacts GitHub or performs a push."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1]/'scripts/push_private.py'
spec = importlib.util.spec_from_file_location('private_push', SCRIPT)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
APPROVED_AUTHOR = (policy.AUTHOR_NAME, 'researcher@example.invalid')


def history(author=APPROVED_AUTHOR, committer=APPROVED_AUTHOR, subject='update_research_results', body=''):
    return '\x1e' + '\0'.join(['a'*40, *author, *committer, subject, body]) + '\n'


class ReleaseIdentity(unittest.TestCase):
    def test_api_host_is_pinned_despite_an_inherited_enterprise_host(self):
        response = subprocess.CompletedProcess([], 0, stdout=b'{"login":"Qasim-Hussain-Code"}', stderr=b'')
        with patch.dict(os.environ, {'GH_HOST': 'elsewhere.example.invalid'}), \
             patch.object(policy.subprocess, 'run', return_value=response) as transport:
            commands = policy.Commands(SCRIPT.parents[1])
            self.assertEqual(commands.github('user')['login'], policy.LOGIN)
        arguments = transport.call_args.args[0]
        self.assertEqual(arguments[:4], ['gh', 'api', '--hostname', 'github.com'])
        self.assertEqual(transport.call_args.kwargs['env']['GH_HOST'], 'github.com')

    def test_private_target_and_single_researcher_are_required(self):
        valid = {'full_name': policy.REPOSITORY, 'private': True, 'default_branch': 'main'}
        policy.validate_repository(valid)
        policy.validate_contributors([[{'login': policy.LOGIN}]])
        for changed in ({'private': False}, {'private': 1}, {'private': None},
                        {'full_name': 'elsewhere/repository'}, {'default_branch': 'other'}, {'archived': True}):
            with self.subTest(changed=changed), self.assertRaises(policy.PolicyError):
                policy.validate_repository(dict(valid, **changed))
        for people in ([], [[]], [[{'name': 'anonymous'}]], [[{'login': 'someone_else'}]],
                       [[{'login': policy.LOGIN}, {'login': 'another_person'}]], {'login': policy.LOGIN}):
            with self.subTest(people=people), self.assertRaises(policy.PolicyError):
                policy.validate_contributors(people)

    def test_user_authored_github_web_commits_remain_valid(self):
        self.assertEqual(policy.validate_history(history(committer=('GitHub', 'noreply@github.com')), APPROVED_AUTHOR), 1)

    def test_other_authors_committers_and_coauthor_trailers_are_rejected(self):
        for record in (history(author=('Someone else', 'other@example.invalid')),
                       history(committer=('A bot', 'bot@example.invalid')),
                       history(body='Co-authored-by: Someone else <other@example.invalid>'),
                       history(body='  co-AUTHORED-by: Someone else <other@example.invalid>')):
            with self.subTest(record=record), self.assertRaises(policy.PolicyError):
                policy.validate_history(record, APPROVED_AUTHOR)

    def test_commit_message_format_is_enforced(self):
        for subject in ('Update README', 'single', 'four_words_are_invalid', 'update-readme', 'Update_readme', 'update_readme!'):
            with self.subTest(subject=subject), self.assertRaises(policy.PolicyError):
                policy.validate_history(history(subject=subject), APPROVED_AUTHOR)
        self.assertEqual(policy.validate_history(history(subject='update_readme'), APPROVED_AUTHOR), 1)

    def test_credentials_in_commit_bodies_are_rejected_without_echoing_values(self):
        marker = 'gh' + 'p_' + 'Z'*36
        with self.assertRaises(policy.PolicyError) as error:
            policy.validate_history(history(body='An accidentally pasted value: '+marker), APPROVED_AUTHOR)
        self.assertNotIn(marker, str(error.exception))

    def test_public_target_stops_before_any_git_or_push_operation(self):
        class PublicTarget:
            def github(self, endpoint, **kwargs):
                if endpoint == 'user':
                    return {'login': policy.LOGIN}
                return {'full_name': policy.REPOSITORY, 'private': False, 'default_branch': 'main'}

            def git(self, *args, **kwargs):
                raise AssertionError('Public repository must stop before Git operations')
        with self.assertRaisesRegex(policy.PolicyError, 'private'):
            policy.execute(PublicTarget(), push=True)

    def test_optimized_python_cannot_disable_the_private_check(self):
        program = ('import importlib.util; '
                   f's=importlib.util.spec_from_file_location("guard",{str(SCRIPT)!r}); '
                   'm=importlib.util.module_from_spec(s); s.loader.exec_module(m); '
                   'm.validate_repository({"full_name":m.REPOSITORY,"private":False,"default_branch":"main"})')
        result = subprocess.run([sys.executable, '-B', '-O', '-c', program], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('PolicyError', result.stderr)

    def test_default_check_never_invokes_a_push(self):
        class NoMutation:
            def git(self, *args, **kwargs):
                raise AssertionError('Check-only execution must not invoke Git after its preflight')
        with patch.object(policy, 'preflight', return_value=('a'*40, 'b'*40, 15, 3)):
            result = policy.execute(NoMutation())
        self.assertEqual(result['status'], 'private_push_preflight_passed')

    def test_verified_push_pins_commit_and_url_and_blocks_visibility_change(self):
        head = 'a'*40
        class Transport:
            def __init__(self, private=True):
                self.private = private
                self.pushes = []

            def git(self, *args, **kwargs):
                if 'push' in args:
                    self.pushes.append(args)
                if args[:2] == ('rev-parse', 'HEAD'):
                    return head
                if 'ls-remote' in args:
                    return head + '\trefs/heads/main'
                return ''

            def github(self, endpoint, **kwargs):
                if '/contributors?' in endpoint:
                    return [[{'login': policy.LOGIN}]]
                if endpoint.endswith('/commits/main'):
                    return {'sha': head}
                return {'full_name': policy.REPOSITORY, 'private': self.private, 'default_branch': 'main'}
        with patch.object(policy, 'preflight', return_value=(head, 'b'*40, 15, 3)), \
             patch.object(policy, 'check_destinations'):
            public = Transport(private=False)
            with self.assertRaises(policy.PolicyError):
                policy.execute(public, push=True)
            self.assertEqual(public.pushes, [])
            private = Transport()
            result = policy.execute(private, push=True)
        self.assertEqual(result['status'], 'private_push_verified')
        self.assertEqual(len(private.pushes), 1)
        self.assertEqual(private.pushes[0][-2:], (policy.URL, head + ':refs/heads/main'))
        self.assertNotIn('--force', private.pushes[0])
        self.assertNotIn('origin', private.pushes[0])


class GitPolicy(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.commands = policy.Commands(self.root)
        self.commands.environment.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
        for key in list(self.commands.environment):
            if key == 'GIT_CONFIG_COUNT' or key.startswith(('GIT_CONFIG_KEY_', 'GIT_CONFIG_VALUE_')):
                del self.commands.environment[key]
        self.commands.git('init', '--quiet')
        self.commands.git('config', 'core.autocrlf', 'false')
        self.commands.git('config', 'user.name', APPROVED_AUTHOR[0])
        self.commands.git('config', 'user.email', APPROVED_AUTHOR[1])
        self.commands.git('config', '--local', 'pisa.authorEmail', APPROVED_AUTHOR[1])
        self.commands.git('remote', 'add', 'origin', policy.URL)

    def tearDown(self):
        self.temporary.cleanup()

    def commit(self, message='update_fixture'):
        self.commands.git('add', '--all')
        self.commands.git('commit', '--quiet', '--allow-empty', '-m', message)
        return self.commands.git('rev-parse', 'HEAD')

    def test_default_approved_destination_is_valid(self):
        policy.check_destinations(self.commands)

    def test_local_author_approval_is_explicit_and_history_remains_exact(self):
        approved=policy.load_approved_author(self.commands)
        self.assertEqual(approved,APPROVED_AUTHOR)
        self.assertEqual(policy.validate_history(history(),approved),1)
        self.commands.git('config','user.email','different@example.invalid')
        self.assertEqual(policy.load_approved_author(self.commands),APPROVED_AUTHOR)
        self.commit()
        actual=self.commands.git('log','HEAD','--format=%x1e%H%x00%an%x00%ae%x00%cn%x00%ce%x00%s%x00%b')
        with self.assertRaisesRegex(policy.PolicyError,'Only the researcher'):
            policy.validate_history(actual,approved)

    def test_current_git_identity_without_approval_is_insufficient(self):
        self.commands.git('config','--local','--unset-all','pisa.authorEmail')
        self.assertEqual(self.commands.git('config','user.email'),APPROVED_AUTHOR[1])
        with self.assertRaisesRegex(policy.PolicyError,'local pisa.authorEmail'):
            policy.load_approved_author(self.commands)

    def test_duplicate_local_author_approval_is_rejected(self):
        for second in (APPROVED_AUTHOR[1],'different@example.invalid'):
            self.commands.git('config','--local','--replace-all','pisa.authorEmail',APPROVED_AUTHOR[1])
            self.commands.git('config','--local','--add','pisa.authorEmail',second)
            with self.subTest(second=second),self.assertRaisesRegex(policy.PolicyError,'exactly one'):
                policy.load_approved_author(self.commands)

    def test_invalid_local_author_approval_is_rejected_without_echoing_it(self):
        invalid=('', ' ', 'not-an-email', 'Name <researcher@example.invalid>',
                 'a..b@example.invalid', '.a@example.invalid', 'a.@example.invalid',
                 'a@-example.invalid', 'a@example', 'a@example.invalid\nextra',
                 ' researcher@example.invalid', 'researcher@example.invalid ')
        for email in invalid:
            self.commands.git('config','--local','--replace-all','pisa.authorEmail',email)
            with self.subTest(email=email),self.assertRaisesRegex(policy.PolicyError,'well-formed') as failure:
                policy.load_approved_author(self.commands)
            if email.strip():
                self.assertNotIn(email,str(failure.exception))

    def test_global_inherited_and_included_values_cannot_supply_local_approval(self):
        self.commands.git('config','--local','--unset-all','pisa.authorEmail')
        global_config=self.root/'global-config'
        self.commands.git('config','--file',str(global_config),'pisa.authorEmail',APPROVED_AUTHOR[1])
        self.commands.environment['GIT_CONFIG_GLOBAL']=str(global_config)
        with self.assertRaisesRegex(policy.PolicyError,'local pisa.authorEmail'):
            policy.load_approved_author(self.commands)
        self.commands.environment.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='pisa.authorEmail',
                                         GIT_CONFIG_VALUE_0=APPROVED_AUTHOR[1])
        with self.assertRaisesRegex(policy.PolicyError,'local pisa.authorEmail'):
            policy.load_approved_author(self.commands)
        self.commands.git('config','--local','include.path',str(global_config))
        with self.assertRaisesRegex(policy.PolicyError,'local pisa.authorEmail'):
            policy.load_approved_author(self.commands)

    def test_separate_public_push_url_is_rejected(self):
        self.commands.git('remote', 'set-url', '--push', 'origin', 'https://example.invalid/public.git')
        self.assertEqual(self.commands.git('remote', 'get-url', 'origin'), policy.URL)
        with self.assertRaisesRegex(policy.PolicyError, 'push URLs'):
            policy.check_destinations(self.commands)

    def test_multiple_push_destinations_are_rejected(self):
        self.commands.git('remote', 'set-url', '--push', 'origin', policy.URL)
        self.commands.git('remote', 'set-url', '--add', '--push', 'origin', 'https://example.invalid/second.git')
        with self.assertRaisesRegex(policy.PolicyError, 'push URLs'):
            policy.check_destinations(self.commands)

    def test_push_only_url_rewrite_is_rejected(self):
        self.commands.git('config', 'url.https://example.invalid/public.git.pushInsteadOf', policy.URL)
        self.assertEqual(self.commands.git('remote', 'get-url', 'origin'), policy.URL)
        with self.assertRaises(policy.PolicyError):
            policy.check_destinations(self.commands)

    def test_generic_url_rewrite_is_rejected(self):
        self.commands.git('config', 'url.https://example.invalid/public.git.insteadOf', policy.URL)
        with self.assertRaises(policy.PolicyError):
            policy.check_destinations(self.commands)

    def test_explicit_url_rewrite_is_checked_even_with_an_approved_pushurl(self):
        self.commands.git('remote', 'set-url', '--push', 'origin', policy.URL)
        self.commands.git('config', 'url.https://example.invalid/public.git.pushInsteadOf', policy.URL)
        # An explicit pushurl prevents the origin check from expanding pushInsteadOf.
        self.assertEqual(self.commands.git('remote', 'get-url', '--push', 'origin'), policy.URL)
        with self.assertRaisesRegex(policy.PolicyError, 'rewrite'):
            policy.check_destinations(self.commands)

    def test_inherited_config_selector_cannot_hide_transport_rewrites(self):
        self.commands.git('remote', 'set-url', '--push', 'origin', policy.URL)
        self.commands.git('config', 'url.https://example.invalid/public.git.pushInsteadOf', policy.URL)
        mask = self.root/'empty-config'
        mask.write_text('', encoding='utf-8')
        with patch.dict(os.environ, dict(self.commands.environment, GIT_CONFIG=str(mask))):
            commands = policy.Commands(self.root)
            with self.assertRaisesRegex(policy.PolicyError, 'rewrite'):
                policy.check_destinations(commands)
            self.assertEqual(os.environ['GIT_CONFIG'], str(mask))
        self.assertNotIn('GIT_CONFIG', commands.environment)

    def test_credentials_removed_by_later_commit_still_block_release(self):
        baseline = self.commit()
        path = self.root/'fixture.txt'
        path.write_text('gh' + 'p_' + 'Z'*36, encoding='utf-8')
        self.commit('add_fixture')
        path.unlink()
        self.commit('remove_fixture')
        with self.assertRaisesRegex(policy.PolicyError, 'Credential pattern'):
            policy.scan_new_history(self.commands, baseline)

    def test_git_replacement_cannot_conceal_original_credential_blob(self):
        baseline = self.commit()
        (self.root/'fixture.txt').write_text('gh' + 'p_' + 'Z'*36, encoding='utf-8')
        unsafe = self.commit('add_fixture')
        tree = self.commands.git('rev-parse', baseline+'^{tree}')
        safe = self.commands.git('commit-tree', tree, '-p', baseline, '-m', 'safe_fixture')
        self.commands.git('replace', unsafe, safe)
        with self.assertRaisesRegex(policy.PolicyError, 'Credential pattern'):
            policy.scan_new_history(self.commands, baseline)

    def test_private_working_file_in_new_history_is_rejected(self):
        baseline = self.commit()
        (self.root/'.env').write_text('DUMMY=example\n', encoding='utf-8')
        self.commit('add_fixture')
        with self.assertRaisesRegex(policy.PolicyError, 'private working file'):
            policy.scan_new_history(self.commands, baseline)

    def test_clean_new_blob_and_empty_commit_are_supported(self):
        baseline = self.commit()
        self.assertEqual(policy.scan_new_history(self.commands, baseline), 0)
        self.commit('empty_fixture')
        self.assertEqual(policy.scan_new_history(self.commands, baseline), 0)
        (self.root/'fixture.txt').write_text('synthetic non-biological fixture\n', encoding='utf-8')
        self.commit('add_fixture')
        self.assertEqual(policy.scan_new_history(self.commands, baseline), 1)


if __name__ == '__main__':
    unittest.main()

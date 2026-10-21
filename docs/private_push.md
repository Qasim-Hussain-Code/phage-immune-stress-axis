# Checked private pushes

The repository remains private at `Qasim-Hussain-Code/phage-immune-stress-axis`.
Qasim Hussain is the sole project author and `Qasim-Hussain-Code` is the sole
GitHub contributor. Upstream experimental data and software retain their
citations and licenses.

After committing the completed, validated work, run:

```bash
python scripts/push_private.py
```

The default performs checks without pushing. To send the checked commit:

```bash
python scripts/push_private.py --push
```

The command requires the existing GitHub CLI login, a clean `main` branch and
exactly the approved HTTPS repository URL. It checks both effective fetch and
push URLs, rejects multiple destinations, and rejects URL rewrite rules that
could redirect the approved URL. A separate `remote.origin.pushurl` therefore
cannot bypass the private-repository check.

GitHub must report private visibility, the expected account and default branch,
and exactly one contributor. Every released commit must be authored by Qasim
Hussain. Existing user-authored GitHub web commits may retain GitHub's service
committer signature. Subjects must contain two or three lowercase words joined
by underscores, and coauthor trailers are rejected.
API calls are pinned to `github.com`; an inherited GitHub Enterprise host
setting cannot provide metadata for a different server.

The current GitHub commit must be an ancestor of the local candidate. If a web
edit has advanced the remote branch, fetch and preserve that edit before
retrying. The tool does not merge, rewrite history or force-push.

Release validation checks the committed scientific payload against the verified
working files, including source-cell lineage, frozen input sizes and hashes,
current validation records and figure-review hashes. New history is also
checked for common credential patterns and known private working-file paths.
This includes blobs added and subsequently deleted before the push. Each blob
is limited to 5 MB and the new-blob scan to 40 MB. These checks do not determine
whether arbitrary prose is confidential; keep working notes outside tracked
files and review the proposed diff.
Commit messages are scanned as well. Git replacement objects and grafts are
disabled for child commands, shallow histories are rejected, and a process-only
configuration selector cannot hide transport URL rewrites from the checks.

The push names the approved HTTPS destination, exact candidate commit and
`refs/heads/main` explicitly. It disables automatic tag following and submodule
pushes. Visibility is checked again before and after pushing; the resulting Git
reference and GitHub API commit must match the checked candidate, and the
contributor list is rechecked. The command contains no repository-creation or
visibility-change operation. Configuration and source files should remain
unchanged while the checks and push run.

Credentials are provided by the existing GitHub CLI helper for that command.
Credential values and raw failed-command output are not included in the result.
The final JSON identifies the checked commit, private visibility, contributor,
new-blob count and tool hash. The default check does not write a publication
record or change scientific outputs.

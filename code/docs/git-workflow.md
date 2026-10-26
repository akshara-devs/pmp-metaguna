# Git workflow for frontend and backend work

Use the shared `frontend` branch for frontend work and the shared `backend` branch for backend work. Both branches are shared by everyone on that part of the project. Push your commits to the branch your team assigned you, then open a pull request (PR) into `main`.

A PR includes every change on its source branch that is not already in `main`. Coordinate with teammates before pushing overlapping work or opening another PR from the same shared branch.

## Get the project

Clone the repository once, then enter its folder:

```sh
git clone https://github.com/akshara-devs/pmp-metaguna.git
cd pmp-metaguna
```

## Start work on your team's branch

Before you start work, update `main` and your team's branch. Use `frontend` for frontend work or `backend` for backend work.

```sh
git checkout main
git pull
git checkout frontend
git pull
git merge main
```

For backend work, replace `frontend` with `backend` in the checkout command. Git uses the branch's configured remote, so `git pull` gets the latest commits for the branch you are on. The merge command brings your updated local `main` into your team's branch.

If this is your first time checking out the team branch, Git creates a local branch that tracks the matching remote branch. If Git asks which branch to track, ask a teammate to help set up the branch.

If Git reports conflicts during a pull or merge, open each named file and resolve the conflict markers (`<<<<<<<`, `=======`, and `>>>>>>>`). Then stage the resolved files and complete the merge:

```sh
git add path/to/resolved-file
git commit
```

Ask a teammate for help if you are unsure which version to keep. Do not delete another person's changes to make the conflict go away.

## Commit and push your changes

Check which files changed before you commit:

```sh
git status
git diff
```

Stage only the files for your task. Replace the example path with each file you want to include:

```sh
git add path/to/file
git commit -m "feat: describe your change"
```

Push your commit to the team branch:

```sh
git push
```

Git pushes to the remote branch that your local branch tracks. Never use `git push --force` on a shared branch.

Before you push, repeat the update steps from the previous section if a teammate may have pushed while you worked. Resolve any conflicts, commit the merge if Git asks, then run `git push`.

## Open a pull request

1. Push your branch to GitHub.
2. Open the project repository on GitHub and select **Compare & pull request**. If GitHub does not show that button, open **Pull requests**, then select **New pull request**.
3. Set the base branch to `main` and the compare branch to `frontend` or `backend`, depending on your work.
4. Check the changed files. Make sure the PR contains only work that belongs in this change. Because the branches are shared, the PR may include commits from teammates.
5. Add a short title and description. Explain what changed and list the checks you ran, or say that you did not run any checks.
6. Create the PR and ask a teammate to review it.
7. If the reviewer requests changes, make them on the same team branch, commit, and push. GitHub adds the new commits to the open PR.
8. Wait for approval, then follow your team's decision on who merges the PR.

If the PR shows another person's unfinished work or unrelated changes, do not create or merge it yet. Coordinate with the teammate using that branch so the team can decide how to split or sequence the work.

## After the PR merges

Update your local branch before starting the next task. Repeat the update steps from the first section, then continue on the shared team branch. Do not delete the branch after a PR merges.

## Quick command reference

| Task | Frontend | Backend |
| --- | --- | --- |
| Switch branch | `git checkout frontend` | `git checkout backend` |
| Get latest changes from the branch | `git pull` | `git pull` |
| Update the team branch from `main` | `git checkout main`, `git pull`, `git checkout frontend`, `git pull`, then `git merge main` | `git checkout main`, `git pull`, `git checkout backend`, `git pull`, then `git merge main` |
| Push commits | `git push` | `git push` |
| PR destination | `main` | `main` |

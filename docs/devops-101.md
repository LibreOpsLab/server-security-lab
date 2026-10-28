# DevOps 101: set up your development environment

This guide is for students who are new to Git, GitHub and Visual Studio Code. It walks through setting up a
Windows workstation, cloning your course repository into a `dev` folder in your user profile, and saving
and sharing your work.

For the lab's weekly branch, pull-request and upstream-sync workflow, continue with
[Git workflow for the lab](git-workflow.md). When you are set up, read the
[welcome guide](build/00-welcome.md) and start the build with
[guide 01](build/01-prepare-the-workstation.md).

> **What you should have at the end of this guide, and what to save as evidence:** Git, VS Code and Python
> installed; your private repo cloned into `$HOME\dev`; and one test commit pushed on a branch. Save the
> output of `git --version`, `python --version`, `git remote -v` and `git log --oneline -3` in
> `portfolio/evidence/00-devops-101/`, with a short `evidence.md` (copy
> [`portfolio/templates/evidence-log.md`](../portfolio/templates/evidence-log.md)).

## 1. Install the tools with winget

Open **Windows Terminal** or **PowerShell**. Check that `winget` is available:

```powershell
winget --version
```

Install Git, Visual Studio Code and Python:

```powershell
winget install --id Git.Git --exact
winget install --id Microsoft.VisualStudioCode --exact
winget install --id Python.Python.3.13 --exact
```

These are the tools used for editing the repository, keeping its history and running its Python checks.
Python 3.13 meets this project's Python 3.11+ requirement. If `winget` is not recognized, ask your
instructor or IT support to install/update **App Installer** or provide the approved installers.

Close and reopen the terminal after installation so it picks up the new commands. Check the installations:

```powershell
git --version
code --version
python --version
```

If `python` is not found, try `py --version`. If neither command works, reopen the terminal once more, then
ask your instructor or IT support.

### Optional: GitHub CLI

The GitHub CLI (`gh`) is useful for creating a private copy from the terminal, but it is not needed to clone
an existing course repository or to use Git's basic commands:

```powershell
winget install --id GitHub.cli --exact
gh --version
gh auth login
```

Follow the browser sign-in prompts. Never put your GitHub password or access token in a Git command or
repository file. Git for Windows includes Git Credential Manager, which can securely handle sign-in when
you clone or push over HTTPS.

## 2. Configure Git once

Git records the author name and email on your commits. Set these to the name and email you use for your
GitHub account:

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

Replace the example name and email with your own. If you have enabled GitHub's private email address
setting, use the GitHub-provided `noreply` address instead. Check what Git saved:

```powershell
git config --global --list
```

These settings apply to all repositories for your Windows user. They identify commits; they do not sign you
in to GitHub.

## 3. Create a `dev` folder and clone your course repository

Your instructor should provide the URL for **your private course repository**. Use that URL here. Do not
push lab work, passwords, generated secrets or private configuration to the public upstream repository.
If you do not have a private repository URL, ask your instructor before continuing.

In PowerShell, create a `dev` folder under your Windows user profile and move into it:

```powershell
New-Item -ItemType Directory -Force "$HOME\dev"
Set-Location "$HOME\dev"
```

Clone your repository. Replace the example URL with the private URL from your instructor:

```powershell
git clone https://github.com/YOUR-ACCOUNT/server-security-lab.git
Set-Location .\server-security-lab
```

`clone` downloads the repository and its history into a new folder. `origin` is the nickname Git gives the
repository you cloned from. Check that it points to your private course repository:

```powershell
git remote -v
git status
```

The working folder is now `$HOME\dev\server-security-lab`. If GitHub asks you to sign in, follow the
browser/Git Credential Manager prompts. If access is denied, check that you used the correct URL and that
your GitHub account has been granted access.

## 4. Open the repository in VS Code

From the repository folder in PowerShell, open VS Code:

```powershell
code .
```

The `.` means “this folder.” If VS Code asks whether you trust the folder, trust it only if you cloned the
repository URL provided by your instructor. The **Explorer** on the left shows files; select a file to edit
it. The built-in terminal is available from **Terminal > New Terminal**.

Before editing, confirm the terminal is at the repository root:

```powershell
git status
```

Keep student work in the designated learner-owned folders such as `build/` and `portfolio/`, and follow the
week guide. Do not add `.env` files, passwords, private keys or generated secrets to Git.

### Trust folders and code

When VS Code opens a folder for the first time, it may ask whether you trust the authors. This is a security
decision, not just a setup question.

- If you do not know where the folder came from, choose **No, I don't trust the authors** or leave it in
  **Restricted Mode**. You can still browse files, but VS Code limits features that can run code, including
  terminals, tasks, debugging, some extensions and AI agents.
- Trust the course folder only after checking that you cloned the repository URL provided by your instructor
  and that the folder is the expected `server-security-lab` repository. Trusting it lets VS Code and its
  extensions run project code and tasks. It does not prove that every script or command is safe.
- Before running a task or script, read the relevant week instructions and inspect commands you do not
  recognize. Ask your instructor if you are unsure.

Do not trust random folders or downloaded projects just to make a warning go away. You can review or change
folder trust later from the **Manage** link in the Restricted Mode banner, or by selecting the Restricted
Mode indicator in the VS Code status bar. See the [VS Code Workspace Trust guide](https://code.visualstudio.com/docs/editing/workspaces/workspace-trust)
for details.

### Navigate code and read documentation

- **Explorer** (file icon, or `Ctrl+Shift+E`) shows the repository folders. Expand a folder and select a
  file to open it. Use the Explorer search box or `Ctrl+P` to find a file by name.
- Open a `.md` file such as a week guide to read its source. To see the formatted document, press
  `Ctrl+Shift+V` for a Markdown preview, or `Ctrl+K` then `V` to open the preview beside the source. Links
  in the preview are clickable.
- The integrated terminal (**Terminal > New Terminal**) starts in the repository folder. Use it for the
  Git commands in this guide and the commands in the week instructions.
- The repository browser view on GitHub also renders Markdown files. Open `docs/` or `weeks/`, then select
  a `.md` file to read it. Local edits appear in the browser only after you commit and push them.

### Connect VS Code to GitHub

Git commands use Git for Windows and its Git Credential Manager to authenticate when needed. VS Code's
GitHub sign-in is a separate connection that enables GitHub features inside VS Code, such as creating or
reviewing pull requests.

1. In VS Code, open the **Accounts** menu (person/profile icon) and choose **Sign in with GitHub**. Follow
   the browser sign-in and authorization prompts. If you only need to edit, commit, pull and push, this
   VS Code sign-in is optional; sign in when prompted to use GitHub features.
2. Open **Source Control** (branch icon, or `Ctrl+Shift+G`). This view lists changed files and provides
   buttons for staging, committing, pulling and pushing.
3. Check the branch name in the lower-left status bar. Use it to switch branches or create a new branch.
   Work on the week's branch, not directly on `main`, as described in
   [Git workflow for the lab](git-workflow.md).

If Git or VS Code reports that you do not have permission, confirm that you cloned your private course
repository and that the signed-in GitHub account has been granted access. Do not sign in with someone
else's account or put a password/token into a source file.

### Set up GitHub Copilot in VS Code

Copilot can offer inline code suggestions and answer questions about code in the editor. Access may be
provided by your school, or by an eligible GitHub Copilot plan. Use your own GitHub account and check your
school's rules before enabling it; signing in does not guarantee that your account has access.

1. Make sure the expected course folder is open and trusted. AI features may be unavailable in Restricted
   Mode.
2. Select the Copilot icon in the VS Code status bar and choose **Use AI Features**, then sign in with the
   GitHub account that has Copilot access. Follow the browser prompts. If Copilot is not available in your
   VS Code installation, open **Extensions** (`Ctrl+Shift+X`), find **GitHub Copilot** published by GitHub,
   install it, and follow its sign-in prompt. Do not install similarly named extensions from unknown
   publishers.
3. Open a code file and start typing to see possible inline suggestions. Review a suggestion before
   accepting it. To ask a question, open Copilot Chat from the Copilot icon or Command Palette, or select a
   small section of code and ask what it does.
4. Review every proposed edit in the editor or Source Control diff. Copilot can produce incorrect,
   insecure, or irrelevant code. Run the tests or checks required by the week guide and ask your instructor
   when you cannot explain a suggestion.

Do not send passwords, tokens, private keys, `.env` contents, personal information or real student/customer
data to Copilot. Follow your institution's AI-use and data-handling rules. Treat text in files, terminal
output and AI responses as untrusted: verify commands before running them, especially commands that change
systems or contact network targets. See the [VS Code Copilot setup guide](https://code.visualstudio.com/docs/setup/copilot)
for current account and setup details.

## 5. Save and sync a change

Git keeps a history of changes. These are the basic steps:

1. **Check** what has changed:

   ```powershell
   git status
   git diff
   ```

2. **Stage** the file or files you intend to save. Staging is a review area for the next commit; it does not
   upload anything:

   ```powershell
   git add build/ portfolio/
   git diff --staged
   ```

   Stage only your intended changes. Review the staged diff and make sure it contains no secrets.

3. **Commit** a named snapshot to your local history:

   ```powershell
   git commit -m "Record week 04 lab build"
   ```

   A commit is saved on your computer. It is not uploaded to GitHub yet.

4. **Push** your branch to your private GitHub repository:

   ```powershell
   git push
   ```

   The first time you push a new branch, Git may ask you to set its upstream. Use:

   ```powershell
   git push --set-upstream origin week-04
   ```

   Replace `week-04` with your branch name. After that, `git push` is enough for that branch.

5. **Pull** changes others have already pushed to the current branch:

   ```powershell
   git pull --ff-only
   ```

   Pull downloads and integrates remote commits into your current branch. Start by pulling before you begin
   work, so you are not working from an old copy. If Git says the histories cannot be fast-forwarded or a
   conflict needs resolving, stop and ask for help rather than forcing the update.

### Do the same using the VS Code Source Control view

1. Select the **Source Control** icon or press `Ctrl+Shift+G`. Review the listed changed files; select a file
   to inspect its diff.
2. Hover over a file and select **+** to stage it, or use the **+** beside **Changes** to stage all listed
   files. Stage only work you intend to commit, and inspect the staged diff for secrets.
3. Enter a short description in the **Message** box and select **Commit** (checkmark). This saves a local
   commit; it does not upload it.
4. Select **Sync Changes** or **… > Pull**, then **… > Push** to exchange commits with GitHub. For a new
   branch, choose **Publish Branch** or use the first-push command above. Read any prompt before accepting;
   if VS Code reports a conflict or asks to force a push, stop and ask your instructor.

Pull before starting work; commit before syncing your own changes. **Sync Changes** may pull and push as a
combined action, so review the status and prompts. Pushing uploads commits to your private GitHub repository;
it does not create or merge a pull request. Open a pull request on GitHub when the lab workflow asks you to.

## 6. Work on a branch

A branch is a separate line of work. It lets you make a week's changes without putting unfinished work
directly on `main`. For example, start week 04 like this:

```powershell
git switch main
git pull --ff-only origin main
git switch -c week-04
```

Make and commit your changes on `week-04`, then push it:

```powershell
git push --set-upstream origin week-04
```

When your course workflow asks you to, open a pull request on GitHub from `week-04` into your private
repository's `main`. A pull request is a place to review and discuss a branch before merging it; it does not
automatically merge your work. The lab-specific guide explains the full process and how to get upstream
updates without overwriting your work.

## Quick command reference

| Command | Meaning |
| --- | --- |
| `git status` | Show the current branch and changed files |
| `git diff` | Review unstaged edits |
| `git add <path>` | Stage changes for the next commit |
| `git diff --staged` | Review staged changes |
| `git commit -m "message"` | Save a snapshot in local history |
| `git pull --ff-only` | Bring remote changes into the current branch |
| `git push` | Upload committed changes on the current branch |
| `git switch <branch>` | Change to an existing branch |
| `git switch -c <branch>` | Create and switch to a new branch |
| `git log --oneline --decorate -10` | View recent commits |

If you are unsure what a command will do, run `git status` first. Do not use `git reset --hard`, `git clean`
or force-push commands to try to fix a problem; these can discard work. Ask your instructor for help.

# Git & GitHub Learning Notes

Author: Shravana Malawade

---

# What is Git?

Git is a distributed Version Control System (VCS).

It helps developers:

- Track changes in code.
- Maintain version history.
- Collaborate with multiple developers.
- Restore previous versions if required.

Git works locally on the developer's machine.

---

# What is GitHub?

GitHub is a cloud-based platform that hosts Git repositories.

It provides:

- Remote repository storage
- Collaboration
- Pull Requests
- Code Reviews
- Issue Tracking
- CI/CD Integration

GitHub uses Git internally.

---

# What is GitHub CLI (gh)?

GitHub CLI is a command-line tool developed by GitHub.

It allows developers to perform GitHub operations without opening the browser.

Example:

- Create repositories
- Clone repositories
- Create Pull Requests
- Create Issues
- Manage Releases

---

# Difference between Git and GitHub

Git

- Version Control System
- Runs locally
- Tracks project history

GitHub

- Cloud platform
- Stores Git repositories
- Enables collaboration

---

# Repository

A repository (Repo) is the storage location of a project.

It contains:

- Source Code
- Documentation
- Configuration Files
- Commit History

Example:

network-validation-framework

---

# Local Repository

Stored on the developer's computer.

Example:

~/projects/network-validation-framework

---

# Remote Repository

Stored on GitHub.

Example:

git@github.com:Shravana-Malawade/network-validation-framework.git

---

# SSH

SSH (Secure Shell) provides secure communication between the local machine and GitHub.

Instead of username and password authentication, SSH uses public/private key pairs.

Private Key

Stored locally.

Example:

~/.ssh/id_ed25519

Never share it.

Public Key

Example:

~/.ssh/id_ed25519.pub

Uploaded to GitHub.

Safe to share.

---

# Git Workflow

Write Code

↓

git add .

↓

git commit -m "message"

↓

git push

↓

GitHub Repository

---

# Commands Learned

## Check Git version

git --version

Purpose:

Verify Git installation.

---

## Check GitHub CLI version

gh --version

Purpose:

Verify GitHub CLI installation.

---

## Login to GitHub CLI

gh auth login

Purpose:

Authenticate GitHub CLI with GitHub.

---

## Check login status

gh auth status

Purpose:

Verify authentication.

---

## List repositories

gh repo list Shravana-Malawade

Purpose:

Displays all repositories.

---

## Show repository details

gh repo view

Purpose:

Displays repository information.

---

## Show Git remote

git remote -v

Purpose:

Displays connected remote repositories.

---

## Add files

git add .

Purpose:

Stages all modified files.

---

## Commit

git commit -m "message"

Purpose:

Creates a snapshot of the project.

---

## First Push

git push -u origin main

Purpose:

Uploads code and sets the upstream branch.

---

## Future Push

git push

Purpose:

Pushes new commits.

---

## Pull Latest Changes

git pull

Purpose:

Downloads the latest changes from GitHub.

---

# Today's Learning Summary

- Learned Git basics.
- Learned GitHub.
- Learned GitHub CLI.
- Understood SSH authentication.
- Connected local repository to GitHub.
- Successfully pushed the Network Validation Framework.

# Git Process

This document will provide a quick overview of how, what, and when you should use some of the general git commands for development. It also serves as a way for me to make sure that I'm saying the same thing every time I tell us to do something different.

## Branches Reference

To see what branches you have in your repository:

`git branch`

To delete a branch in your repository:

`git branch -d <branch_name>`

To work on a branch, you check it out:

`git checkout <branch_name>`

* Note that this only works if the branch is already existing.

To create and then checkout a branch:

`git checkout -b <new_branch> <optional: old_branch_name>`

* This is the same as:
    * `git branch <new_branch>`
    * `git checkout <new_branch>`

* Note that it matters what branch you START on when you're doing this. Start on development when creating a new branch.
* Note that if, at any point, you get stuck on a *DETACHED HEAD* state, that you should leave that immediately if you plan to do development. You need to checkout a new branch, or at least revert what you've just done.

## Feature Branches

### Requirements:

- Feature branches should have a descriptive name
- Feature branches should only contain work related to that descriptive name
    - If work needs to be done that is not related to that descriptive name, create a new branch and do the work there. Then you can (merge/rebase) those branches back together later.
- Feature branches should be pushed to `origin` or the central repository (Github).
- Special Branches:
    - `development`: A branch that is committed to only when feature branches appear to be functional or at a stage where they don't break things. It can be incremental updates to feature branches, but the branches should be working and actively passing tests.
    - `master`: Can only be committed to from development. Will only be pushed at major releases (e.g. a working web client, but no GUI).
    - `release-*`: The release branch at a certain time. Maybe 1.0.0, etc.

### Flow

```bash
# Create a new branch new_branch
git checkout -b new_branch

# Make commits and stuff here
git add awesome_file_that_fixes_everything.py

# Make a nice commit message here
git commit

# Push changes to Github so everyone can see them
#   These changes do not have to be a completed branch
#   Or even have everything working. This is still on YOUR
#   person branch.
git push -u origin new_branch

# After the '-u origin new_branch' stuff, you can now just do
git push
# when you are on this branch.
```

This can continue going on until you finish the branch. You can pretend you are just in your own little world working on your branch, and you don't have to worry too much about what is happening outside.

However, if commits are made to `development`, you should attempt to incorporate those into your branch to make sure that it doesn't break anything, and that you are taking advantage of the newest things that we've built on the branch.

To do this:

```bash
# Make sure you have the most up-to-date development branch
git fetch origin development

# Be on the right brnach
git checkout new_branch

# Now perform a rebase
git rebase development
```

This will rebase the development commits BEFORE the commits on your current branch. Make sure that you do it this way. It is very important.

After doing this, make sure to run any tests that you've made, so that as you continue your work, you don't break anything unexpected because of a new change.

You can also rebase on your own branch.

```bash
# Checkout the branch you want to modify
git checkout new_branch

# Rebase the last three commits
git rebase -i HEAD^3
```

This lets you modify the commits you made for the last three commits. In other words, you can rewrite a little bit of history to make sure that your commits are succint and make sense. In case you have a commit like `went to lunch` you can just squash that in with `Add new database table`.

Important Quote:

```
So, before you run git rebase, always ask yourself, "Is anyone else looking at this branch?" If the answer is yes, take your hands off the keyboard and start thinking about a non-destructive way to make your changes (e.g., the git revert command). Otherwise, you’re safe to re-write history as much as you like.
```

This is to remind you to make sure you are rebasing the correct way.

Once you are sure that your feature branch is up-to-date with development, you can do this to update development with your feature branch.

```bash
# IT IS VERY IMPORANT THAT YOUR FEATURE BRANCH IS UP TO DATE
#   PLEASE DO NOT PROCESS UNLESS THAT IS TRUE

# Next switch back to your feature branch
git checkout new_branch

# Now rebase your commits onto development
git rebase development
```

And that's all. 

If done correctly, your commits should go from looking like this:

![Before Rebase](https://www.atlassian.com/git/images/tutorials/advanced/merging-vs-rebasing/01.svg)

Your commits should now look like:

![Rebased History](https://www.atlassian.com/git/images/tutorials/advanced/merging-vs-rebasing/03.svg)

#### Thanks

Thank you to atlassian.com for the help with Git. I got a lot of the tips and tricks from there.

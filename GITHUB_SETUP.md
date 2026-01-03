# GitHub Setup Instructions

## Repository Created Locally ✅

Your local git repository has been initialized and committed.

## Next Steps to Push to GitHub

### Option 1: Create Repository on GitHub.com (Recommended)

1. **Go to GitHub.com** and sign in
2. **Click the "+" icon** in the top right → "New repository"
3. **Repository settings:**
   - Name: `VocalNode` (or your preferred name)
   - Description: "Cross-platform speech-to-text dictation tool"
   - Visibility: Public or Private (your choice)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. **Click "Create repository"**
5. **Copy the repository URL** (e.g., `https://github.com/yourusername/VocalNode.git`)

### Option 2: Use GitHub CLI (if installed)

```bash
gh repo create VocalNode --public --source=. --remote=origin --push
```

### After Creating the Repository

Run these commands to push:

```bash
cd /home/jb/dev/VocalNode

# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/VocalNode.git

# Or if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/VocalNode.git

# Push to GitHub
git push -u origin main
```

### If You Already Have a GitHub Repository

If you've already created the repository on GitHub, just run:

```bash
cd /home/jb/dev/VocalNode
git remote add origin https://github.com/YOUR_USERNAME/VocalNode.git
git push -u origin main
```

## Troubleshooting

### Authentication Issues

If you get authentication errors:

1. **Use Personal Access Token:**
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token with `repo` scope
   - Use token as password when pushing

2. **Or use SSH:**
   - Set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
   - Use SSH URL: `git@github.com:USERNAME/VocalNode.git`

### Push Rejected

If push is rejected:
- Make sure the remote repository is empty (no README/license)
- Or use: `git push -u origin main --force` (only if you're sure!)

## Current Status

- ✅ Git repository initialized
- ✅ All files committed
- ✅ Branch set to `main`
- ⏳ Waiting for GitHub repository creation and remote setup


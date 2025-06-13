#!/bin/bash

# Install GitHub CLI on Debian Linux
# This script installs gh CLI using the official GitHub repository

set -e  # Exit on any error

echo "Installing GitHub CLI (gh) on Debian Linux..."

# Update package list
echo "Updating package list..."
sudo apt update

# Install required dependencies
echo "Installing dependencies..."
sudo apt install -y curl gnupg lsb-release

# Add GitHub's official GPG key
echo "Adding GitHub's GPG key..."
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg

# Add GitHub CLI repository to sources
echo "Adding GitHub CLI repository..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null

# Update package list with new repository
echo "Updating package list with GitHub CLI repository..."
sudo apt update

# Install GitHub CLI
echo "Installing GitHub CLI..."
sudo apt install -y gh

# Verify installation
echo "Verifying installation..."
gh --version

echo "GitHub CLI installation completed successfully!"
echo "You can now use 'gh' commands. Run 'gh auth login' to authenticate with GitHub."
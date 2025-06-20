#!/bin/bash

# Install GitHub CLI on Ubuntu Linux
# This script installs gh CLI using the official GitHub repository

set -e  # Exit on any error

# Create a local bin directory
mkdir -p ~/.local/bin

# Download the latest release (adjust version/architecture as needed)
wget https://github.com/cli/cli/releases/download/v2.40.1/gh_2.40.1_linux_amd64.tar.gz

# Extract it
tar -xzf gh_2.40.1_linux_amd64.tar.gz

# Copy the binary to your local bin
cp gh_2.40.1_linux_amd64/bin/gh ~/.local/bin/

# Make sure ~/.local/bin is in your PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

echo "GitHub CLI installation completed successfully!"
echo "You can now use 'gh' commands. Run 'gh auth login' to authenticate with GitHub."
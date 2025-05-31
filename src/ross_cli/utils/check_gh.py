import platform
import subprocess
import os
import sys
import tempfile
import shutil

def check_gh() -> bool:
    """Verify that the gh CLI is installed.
    Return True if already installed, or was just installed.
    Return False if not installed, and user indicated not to install it."""
    try:
        is_installed = True
        subprocess.run(["gh", "--version"], capture_output=True)        
    except:
        is_installed = False
        pass

    if is_installed:
        return True
    
    system = platform.system()

    response = input("gh cli not installed! Would you like to install it now?(y/N)")
    if response == "":
        response = "N"

    if response.lower() not in ["y", "yes"]:
        return False

    if system == "Windows":
        install_gh_cli_windows()
    elif system == "Darwin":  # macOS
        install_gh_cli_mac()
    else:
        print(f"Unsupported operating system: {system}")
        print("This script only supports Windows and macOS.")
        sys.exit(1)

    print("After installing the gh cli, you will need to completely close and reopen the Terminal/VSCode (if using integrated terminal).")
    print("You may even need to restart the computer for the gh installation to take effect.")
    print("After successfully running gh --version, then run gh auth login to connect to your GitHub account.")

    return False

def install_gh_cli_windows():
    """Install GitHub CLI on Windows using winget or by downloading the installer."""
    try:
        # First try using winget which is the easiest method
        print("Attempting to install GitHub CLI using winget...")        
        subprocess.run(["winget", "install", "--id", "GitHub.cli"], check=True)
        print("GitHub CLI installed successfully using winget!")
        return None
    except (subprocess.SubprocessError, FileNotFoundError):
        print("winget not available, falling back to manual installation...")

    # If winget fails, download the installer manually
    import urllib.request
    import zipfile

    # Create a temporary directory for the download
    temp_dir = tempfile.mkdtemp()
    try:
        # Download the latest release
        download_url = "https://github.com/cli/cli/releases/latest/download/gh_windows_amd64.zip"
        zip_path = os.path.join(temp_dir, "gh.zip")
        
        print(f"Downloading GitHub CLI from {download_url}...")
        urllib.request.urlretrieve(download_url, zip_path)
        
        # Extract the ZIP file
        extract_dir = os.path.join(temp_dir, "extracted")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find the extracted directory (it usually contains a version number)
        gh_dir = None
        for item in os.listdir(extract_dir):
            if item.startswith("gh_"):
                gh_dir = os.path.join(extract_dir, item)
                break
        
        if not gh_dir:
            print("Could not find GitHub CLI directory in the extracted files.")
            return None
        
        # Install to Program Files
        install_dir = os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "GitHub CLI")
        os.makedirs(install_dir, exist_ok=True)
        
        # Copy files
        for item in os.listdir(gh_dir):
            src = os.path.join(gh_dir, item)
            dst = os.path.join(install_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        
        # Add to PATH
        bin_dir = os.path.join(install_dir, "bin")
        path_env = os.environ.get("PATH", "")
        if bin_dir not in path_env:
            print(f"\nTo use GitHub CLI, add the following directory to your PATH:")
            print(f"{bin_dir}")
            print("\nYou can run the following command in PowerShell to add it to your PATH for the current session:")
            print(f'$env:PATH = "{bin_dir};" + $env:PATH')
        
        print("\nGitHub CLI installed successfully!")
        
    except Exception as e:
        print(f"Error installing GitHub CLI: {e}")
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

def install_gh_cli_mac():
    """Install GitHub CLI on macOS using Homebrew or by downloading the installer."""
    try:
        # First try using Homebrew which is the recommended method
        print("Attempting to install GitHub CLI using Homebrew...")
        subprocess.run(["brew", "install", "gh"], check=True)
        print("GitHub CLI installed successfully using Homebrew!")
        return None
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Homebrew not available, falling back to manual installation...")

    # If Homebrew fails, download the installer manually
    import urllib.request
    import tarfile

    # Create a temporary directory for the download
    temp_dir = tempfile.mkdtemp()
    try:
        # Download the latest release
        download_url = "https://github.com/cli/cli/releases/latest/download/gh_mac_amd64.tar.gz"
        tar_path = os.path.join(temp_dir, "gh.tar.gz")
        
        print(f"Downloading GitHub CLI from {download_url}...")
        urllib.request.urlretrieve(download_url, tar_path)
        
        # Extract the tar file
        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        with tarfile.open(tar_path, 'r:gz') as tar_ref:
            tar_ref.extractall(extract_dir)
        
        # Find the extracted directory (it usually contains a version number)
        gh_dir = None
        for item in os.listdir(extract_dir):
            if item.startswith("gh_"):
                gh_dir = os.path.join(extract_dir, item)
                break
        
        if not gh_dir:
            print("Could not find GitHub CLI directory in the extracted files.")
            return None
        
        # Install to /usr/local
        install_dir = "/usr/local/share/gh"
        bin_dir = "/usr/local/bin"
        
        try:
            os.makedirs(install_dir, exist_ok=True)
            os.makedirs(bin_dir, exist_ok=True)
        except PermissionError:
            print("Permission denied. Try running this script with sudo.")
            return None
        
        # Copy files
        for item in os.listdir(gh_dir):
            src = os.path.join(gh_dir, item)
            dst = os.path.join(install_dir, item)
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        
        # Create symlink to bin directory
        gh_bin = os.path.join(install_dir, "bin", "gh")
        gh_link = os.path.join(bin_dir, "gh")
        
        if os.path.exists(gh_link):
            os.remove(gh_link)
        
        os.symlink(gh_bin, gh_link)
        
        print("\nGitHub CLI installed successfully!")
        
    except Exception as e:
        print(f"Error installing GitHub CLI: {e}")
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
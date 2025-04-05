import subprocess

def release_package(pyproject_toml: dict, args: list):
    """Need to already be in the package directory"""
    version = pyproject_toml["project"]["version"]
    try:
         # Create the release using the GitHub CLI
        subprocess.run(["gh","release", "create", version] + args)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error creating release: {e}")
        return 1
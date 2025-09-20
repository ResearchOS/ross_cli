from pathlib import Path

def get_installed_package_repo_url(package_path: Path) -> str:
    """Get the GitHub repository URL from the installed package's .dist-info folder."""
    package_path = Path(package_path)
    dist_info_folders = list(package_path.parent.glob(f"{package_path.name.replace('-', '_')}*-info"))
    if not dist_info_folders:
        raise FileNotFoundError(f"No .dist-info folder found for package {package_path.name}")
    
    for dist_info_folder in dist_info_folders:
        metadata_file = dist_info_folder / "METADATA"
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                for line in f:
                    if line.startswith("Home-page:"):
                        url = line.split(":", 1)[1].strip()
                        if "github.com" in url:
                            return url
    raise ValueError(f"No GitHub URL found in METADATA for package {package_path.name}")
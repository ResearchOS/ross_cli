

def build_pyproject_from_rtoproject(rto_project_toml: dict) -> dict:
    """Build the pyproject.toml file from the rtoproject.toml file."""

    pyproject_toml = {}
    pyproject_toml["project"]  = {}
    pyproject_toml["project"]["name"] = rto_project_toml["name"] if "name" in rto_project_toml else ValueError("name not found in rtoproject.toml")
    pyproject_toml["project"]["version"] = rto_project_toml["version"] if "version" in rto_project_toml else ValueError("version not found in rtoproject.toml")
    pyproject_toml["project"]["description"] = rto_project_toml["description"] if "description" in rto_project_toml else ValueError("description not found in rtoproject.toml")
    pyproject_toml["project"]["dependencies"] = rto_project_toml["dependencies"] if "dependencies" in rto_project_toml else ValueError("dependencies not found in rtoproject.toml")
    pyproject_toml["project"]["authors"] = rto_project_toml["authors"] if "authors" in rto_project_toml else ValueError("authors not found in rtoproject.toml")
    pyproject_toml["project"]["readme"] = rto_project_toml["readme"] if "readme" in rto_project_toml else ValueError("readme not found in rtoproject.toml")

    pyproject_toml["build-system"] = {}
    pyproject_toml["build-system"]["requires"] = ["hatchling"]
    pyproject_toml["build-system"]["build-backend"] = "hatchling.build"

    return pyproject_toml
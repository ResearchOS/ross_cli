

def build_pyproject_from_rossproject(ross_project_toml: dict) -> dict:
    """Build the pyproject.toml file from the rossproject.toml file."""

    pyproject_toml = {}
    pyproject_toml["project"]  = {}
    pyproject_toml["project"]["name"] = ross_project_toml["name"] if "name" in ross_project_toml else ValueError("name not found in rossproject.toml")
    pyproject_toml["project"]["version"] = ross_project_toml["version"] if "version" in ross_project_toml else ValueError("version not found in rossproject.toml")
    pyproject_toml["project"]["description"] = ross_project_toml["description"] if "description" in ross_project_toml else ValueError("description not found in rossproject.toml")
    pyproject_toml["project"]["dependencies"] = ross_project_toml["dependencies"] if "dependencies" in ross_project_toml else ValueError("dependencies not found in rossproject.toml")
    pyproject_toml["project"]["authors"] = ross_project_toml["authors"] if "authors" in ross_project_toml else ValueError("authors not found in rossproject.toml")
    pyproject_toml["project"]["readme"] = ross_project_toml["readme"] if "readme" in ross_project_toml else ValueError("readme not found in rossproject.toml")

    pyproject_toml["build-system"] = {}
    pyproject_toml["build-system"]["requires"] = ["hatchling"]
    pyproject_toml["build-system"]["build-backend"] = "hatchling.build"

    return pyproject_toml
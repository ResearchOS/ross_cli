# How to Use
## Installation
1. `pip install ross-project` or download from GitHub.

## Usage
### Create a new project
1. Create a new project folder `~/<project_name>`.
2. Create a git repository in the project folder.
3. Connect the git repository to GitHub.
4. Create a new virtual environment in the project folder with `python -m .venv venv`.
5. Activate the virtual environment with `source venv/bin/activate` or `venv\Scripts\activate`.
6. Add the project folder to the custom index with `ross add <project_name>`.

### Install dependencies
1. From PyPi: `pip install <package_name>`
2. From the custom index: `ross install <package_name>`
NOTE: All `pip install` options are supported.
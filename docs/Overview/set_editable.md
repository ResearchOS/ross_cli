# Clone the GitHub repository to make edits to the code

```bash
ross set-editable <package-name>
```

Performs the following steps under the hood:

1. Check if the package is installed by finding its installation location. If it doesn't exist, exits with code 19.

2. If it is installed, get the URL of the package's GitHub repository (TODO: from where?)

3. Clones the GitHub repository for the specified package name into ~/ross_packages/<package-name> (with --depth 1 to avoid cloning the full git history).

4. Copy the installed package's source files into the cloned repository, overwriting any existing files, thereby preserving any preexisting changes.

5. `ross uninstall <package-name>` to uninstall the package.

6. `pip install -e /path/to/cloned/package/repo` to install the package in editable mode.
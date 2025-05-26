# Add a Package to an Index
To be able to `ross install` a package, the package must be added to a `ross` index.

Several criteria must be met for a package to be added to an index:

1. The index GitHub repository must exist.

2. The package must contain a git repository, and a corresponding GitHub remote repository must exist.

3. The package folder must contain a `rossproject.toml` file with the minimum required metadata.
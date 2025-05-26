# GitHub Package Indexes

An index is simply a GitHub repository that contains an `index.toml` file. This file contains a list of package names and their corresponding GitHub repository URLs. The `ross` CLI uses this index to find and install packages.

For example, if a research lab creates a private package index (a GitHub repository that contains an `index.toml` file), then any member of the lab with access to the repository can `ross tap <URL>` the index repository. After that, they can directly install packages from it using `ross install <package>`, similar to `pip install <package>` for installing packages from PyPI. 

!!!note 
    If the index repository is made public, then anyone can tap the index and install packages from it.

## How to Create an Index
To create an index, you can follow these steps:

1. Go to [GitHub](https://github.com) and create a new repository.

2. Name the repository something meaningful, like `my_data_analyses_index`.

3. You can choose to make the repository public or private, depending on your needs.

4. You can leave the repository empty; `ross` will create the `index.toml` file for you when you tap the index.

!!!note
    The index repository must be a GitHub repository. No local copy of the repository is necessary.

## Example `index.toml`
```toml
[[package]]
name = "github_repo"
url = "https://github.com/github_user/github_repo"
```

## How to Tap an Index
To tell the `ross` tool about this index of packages, it must be tapped. This is similar to how [Homebrew](https://docs.brew.sh/Taps) manages non-standard package indexes.

To tap an index, you can use the `ross tap` command followed by the URL of the GitHub repository. For example:
```bash
ross tap https://github.com/github_user/github_repo
```
This command adds the index URL to your local `ross` configuration file. Now, running `ross install` will search through the tapped indexes for corresponding packages to install.
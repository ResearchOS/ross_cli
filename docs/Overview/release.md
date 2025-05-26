# Release a Package

To share your package with the world, it must be released. With `ross release`, you can easily create a GitHub release of your package.

Releases can be created for a variety of reasons, such as:

1. Sharing a stable version of your package with others

2. Fixing bugs or adding features to your data analysis

3. Creating new pipelines or workflows

4. Creating snapshots of an entire data analysis project, for example when submitting to a journal

The metadata for the release is defined in the project's `rossproject.toml` file:
```toml
name = "my-package"
version = "0.1.0"
description = "A brief description of my package"
authors = ["Your Name"]
dependencies = ["dependency1", "dependency2"]
```

## Version
When running `ross release`, you can specify either `patch`, `minor`, or `major` to indicate the type of version bump you want to apply. This will automatically update the version in your `rossproject.toml` file. If you do not specify a version type, `ross` will attempt to release the package with the current version.

## Message
You can also provide a message for the release. If you do not specify a message, `ross` will use the default message format: "Release {version}".
```bash
ross release patch -m "My release message"
```
# ROSS Philosophy

## Data analysis code is not reused
Data analysis is a crucial part of many fields, from business intelligence to scientific research, and Python is the de facto standard language for data analysis, with a mature ecosystem of packages for nearly any purpose. [PyPI](https://pypi.org) (Python Package Index) is the standard repository for publishing Python packages, and `pip` is the standard tool for installing them. 

However, PyPI is generally not used for data analyses, and there are many good reasons for not publishing data analyses on PyPI (privacy, burdensome metadata, etc.). Therefore, data analysts are left without a standard way to share their work and utilize the work of others.

## Share data analysis code using `ross`
`ross` is a command-line interface (CLI) tool created to fill the gap of reusing data analyses. It provides a simple and private way to publish and install data analyses, making it easy to share and reuse code with minimal overhead. 

This tool is built with data analysts in mind - people who are generally proficient with coding for data analysis, but may not have experience with software development and creating packages. `ross` leverages familiar tools (`pip` and the GitHub CLI), allowing users to leverage the power of code reuse with minimal time spent on the complexities of package management.

## How does `ross` work?

`ross` is intended to facilitate reusing data analyses by providing mechanisms for publishing and installation. These analyses could be any meaningful unit of work - a one line script, a series of analyses that form a pipeline, of a complete start to finish data analysis project. `ross` uses GitHub repositories as (1) a private package index, and (2) a platform for publishing and installing data analyses.

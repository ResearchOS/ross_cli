---
title: 'ROSS CLI: A Tool to Facilitate Research Software Reuse'
tags:
  - Python
  - MATLAB
  - R
  - software reuse
authors:
  - name: 'Mitchell Tillman'
    orcid: 0000-0002-3115-1587
    equal-contrib: true
    affiliation: '1'
affiliations:
  - name: 'Shirley Ryan AbilityLab, United States'
    index: 1

date: 31 May 2025
bibliography: paper.bib
---

// Other software addressing related needs?

# Summary

Historically, the factor limiting the pace of scientific progress has been data availability [ref]. However, recently the rate of data acquisition and reuse has exploded, such that the limiting factor is now often the pace of data analysis [ref]. And while foundational data analysis tools have greatly improved in all three of the major languages used in academia today - such as MATLAB's toolboxes [ref], Python's NumPy [ref] and SciKit Learn [ref], and R's Tidyverse [ref] - codes for the data analyses published in journal articles are much less frequently shared, slowing the pace of scientific progress [ref].

# Statement of need

The Research Open Source Software (ROSS) command line interface aims to simplify sharing scientific data analyses across MATLAB, Python, and R, utilizing the same best practices when building data analysis software as the software engineering community has converged on over decades. The ROSS CLI builds on top of the `pip` tool developed by the Python community for package management [ref] and the `gh` CLI published by GitHub [ref], and the core concept borrows heavily from the `brew tap` private indexing functionality found in Homebrew [ref]. ROSS mitigates barriers to sharing data analyses by (1) requiring minimal metadata, (2) working with public or private GitHub repositories, which many researchers already use.

ROSS can be used for sharing data analysis code of any size - a single line equation, a pipeline consisting of several computational steps, and even the code for an entire research project. With greater code availability, future researchers can speed up their own data analyses, as well as validate or improve upon algorithms.

# Acknowledgements
The author would like to acknowledge the support of Dr. Jun Ming Liu and Dr. Antonia Zaferiou for their support during my efforts working on the precursors to this tool, as well as my colleagues at Shirley Ryan AbilityLab, who have tested and provided feedback on this tool.

# References
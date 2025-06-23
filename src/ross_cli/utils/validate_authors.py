import re

import typer

from ..constants import EMAIL_REGEX

AUTHOR_FIELDS = ["name", "email"]

def validate_authors(authors: list):
    if not isinstance(authors, list):
        raise typer.Exit(code=15)
    
    for count, author in enumerate(authors):
        validate_author(author, count + 1)

def validate_author(author: dict, count: int):
    if not isinstance(author, dict):
        raise typer.Exit(code=15)
    
    # Check fields
    missing_fields = [f for f in AUTHOR_FIELDS if f not in author.keys()]
    extra_fields = [f for f in author.keys() if f not in AUTHOR_FIELDS]
    for field in missing_fields:
        typer.echo(f"Missing field {field} in author number {count} in `authors` field of rossproject.toml")

    for field in extra_fields:
        typer.echo(f"Extra field {field} in author number {count} in `authors` field of rossproject.toml")

    if missing_fields or extra_fields:
        typer.echo('Proper `author` field format is `{name = "Author Name", email = "author.email@example.com}')
        raise typer.Exit(code=15)
    
    # Check author format
    if not isinstance(author["name"], str):
        typer.echo(f"Author number {count} name must be a string.")
        raise typer.Exit(code=15)
    
    if not isinstance(author["email"], str) or not bool(re.match(EMAIL_REGEX, author["email"])):
        typer.echo(f"Author number {count} email must be a string containing an email address (matching this regex: {EMAIL_REGEX})")
        raise typer.Exit(code=15)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gather generated PNGs and link to heatmap in a GitHub-flavored Markdown string."""
from dataclasses import dataclass
import os
from pathlib import Path
import sys
from typing import Generator

from github import Github


@dataclass
class EnvVars:
    """Dataclass for environment variables."""

    github_token: str
    owner: str
    repo: str
    sha: str
    testing_owner: str

    def __init__(self) -> None:
        """Initialize the dataclass from the environment."""
        attrs = ["github_token", "owner", "repo", "sha", "testing_owner"]
        for attr in attrs:
            setattr(self, attr, os.environ.get(attr.upper(), ""))


_ENV = EnvVars()


def gather_images(path: Path) -> Generator[Path, None, None]:
    """Gather the images.

    Parameters
    ----------
    path : Path
        The path to the correlations directory..

    Yields
    ------
    image : Path
       The path to an image.
    """
    return path.glob("*.png")


def gather_text(path: Path) -> str:
    """Gathers and concatenates all text files in the given directory.

    Parameters
    ----------
    path : Path
        The path to the correlations directory.

    Returns
    -------
    str
        The concatenated text.
    """
    text = ""
    for file in path.glob("*.txt"):
        with open(file, "r", encoding="utf=8") as _f:
            text += _f.read()
        text += "\n"
    return text.strip()


def generate_comment(path: Path) -> str:
    """Generate the comment.

    Parameters
    ----------
    path : Path
        The path to the correlations directory.

    Returns
    -------
    str : The comment.
    """
    comment = ""
    for image in gather_images(path):
        raw_image_path = _raw_image_path(_ENV.testing_owner, _ENV.repo, _ENV.sha, image)
        comment += f"![{image.stem}]({raw_image_path})\n"
    return comment + gather_text(path)


def main() -> None:
    """Generate and post a comment on a GitHub commit.

    Also post the comment to any open PR in which the commit is the most recent.
    """
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print("Usage: cpac_regsuite_generate_comment [path]")
            print("If no path is given, the current working directory is used.")
            print("Required environment variables:")
            print(
                "GITHUB_TOKEN: A personal access token with scope to write to "
                "comments and pull requests."
            )
            print("OWNER: The owner of the repository.")
            print("REPO: The name of the repository.")
            print("SHA: The SHA of the commit.")
            print("TESTING_OWNER: The owner of the testing repository.")
            sys.exit(0)
        path = Path(sys.argv[1])
    else:
        path = Path(os.getcwd())
    personal_access_token = os.environ.get("GITHUB_TOKEN")
    g = Github(personal_access_token)
    repo = g.get_repo(f"{_ENV.owner}/{_ENV.repo}")
    commit = repo.get_commit(_ENV.sha)
    comment = generate_comment(path)
    commit.create_comment(comment)
    for pr in repo.get_pulls(state="open", sort="created"):
        if pr.head.sha == _ENV.sha:
            pr.create_issue_comment(comment)


def _raw_image_path(owner: str, repo: str, sha: str, image: Path) -> str:
    """Generate the raw image path.

    Parameters
    ----------
    owner : str
        The owner of the repository.

    repo : str
        The name of the repository.

    sha : str
        The SHA of the commit.

    image : Path
        The path to the image.

    Returns
    -------
    str : The raw image path.
    """
    return f"https://raw.githubusercontent.com/{owner}/regtest-runlogs/{repo}_{sha}/{image.name}"


if __name__ == "__main__":
    main()

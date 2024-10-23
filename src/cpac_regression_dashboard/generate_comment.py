#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gather generated PNGs and link to heatmap in a GitHub-flavored Markdown string."""
import asyncio
from dataclasses import dataclass
from importlib.metadata import metadata
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Generator, Optional

from cairosvg import svg2png
from git import Repo
from git.exc import GitCommandError
from github import Github
from github.Repository import Repository
from playwright.async_api import async_playwright
import requests

from ._version import __version__


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


@dataclass
class Heatmap:
    """Heatmap dataclass."""

    filename: str
    content: str


def add_heatmap_to_branch(file: Heatmap) -> None:
    """Add a heatmap to a branch.

    Parameters
    ----------
    file : Heatmap
        The heatmap file to add.

    Returns
    -------
    None
    """
    g = Github(_ENV.github_token)
    repo = g.get_repo(f"{_ENV.testing_owner}/regtest-runlogs")
    branch_name = f"{_ENV.repo}_{_ENV.sha}"
    with tempfile.TemporaryDirectory() as _temp_dir:
        temp_dir = Path(_temp_dir)
        local_repo = Repo.clone_from(
            repo.clone_url.replace(
                "https://", f"https://${_ENV.github_token}:x-oauth-basic@"
            ),
            temp_dir,
            branch=branch_name,
            depth=1,
        )
        # make sure branch is up to date
        local_repo.remotes.origin.fetch("+refs/heads/*:refs/remotes/origin/*")
        local_repo.remotes.origin.pull(branch_name)
        svg_path = temp_dir / f"{file.filename}.svg"
        png_path = temp_dir / f"{file.filename}.png"
        with open(svg_path, "w") as _f:
            _f.write(file.content)
        svg2png(background_color="white", url=str(svg_path), write_to=str(png_path))
        local_repo.index.add([png_path])
        local_repo.index.commit(":loud_sound: Add heatmap image")
        try:
            local_repo.remotes.origin.push(branch_name)
        except GitCommandError:
            local_repo.remotes.origin.push(branch_name, force=True)


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
    text = "|feature|coefficient|\n|---|---|\n"
    for file in path.glob("*.txt"):
        with open(file, "r", encoding="utf=8") as _f:
            for line in _f.readlines():
                text += f"|{'|'.join(_.strip() for _ in line.split(':', 1))}|\n"
    return text.strip()


async def generate_comment(path: Path) -> str:
    """Generate the comment.

    Parameters
    ----------
    path : Path
        The path to the correlations directory.

    Returns
    -------
    str : The comment.
    """
    project_urls = metadata(__package__).get_all("Project-URL", [])
    source_url = None
    for _url in project_urls:
        if _url.startswith("Source Code, "):
            source_url = _url.split(",")[1].strip()
            break
    if source_url is None:
        comment = f"Generated by {__name__} {__version__}\n\n"
    else:
        _packageless_name = __name__.replace(__package__, "").lstrip(".")
        comment = (
            f"Generated by [{__package__}]({source_url})."
            f"{_packageless_name} {__version__}\n\n"
        )
    comment += await get_heatmap()
    for image in gather_images(path):
        raw_image_path = _raw_image_path(_ENV.testing_owner, _ENV.repo, _ENV.sha, image)
        comment += f"![{image.stem}]({raw_image_path})\n"
    return comment + gather_text(path)


async def get_heatmap() -> str:
    """Get a heatmap image."""
    subprocess.run(
        "playwright install chromium".split(" "), check=False
    )  # update chromium
    url = f"https://{_ENV.testing_owner}.github.io/dashboard/?data_sha={_ENV.sha}"
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            svg_string = await page.evaluate(
                """() => {
    let svg = document.querySelector('svg');
    return svg ? svg.outerHTML : null;
}"""
            )
        except Exception as exception:
            from warnings import warn

            warn(
                f"{exception}\n\nAre playwright and chromium installed?", RuntimeWarning
            )
        if svg_string is not None:
            _heatmap = Heatmap("heatmap", svg_string)
            add_heatmap_to_branch(_heatmap)
            heatmap = _raw_image_path(
                _ENV.testing_owner,
                _ENV.repo,
                _ENV.sha,
                Path(f"{_heatmap.filename}.png"),
            )
            heatmap = f"[![heatmap]({heatmap})]({url})"
        else:
            heatmap = ""

        await browser.close()
    return heatmap


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
            print("PLAYWRIGHT_BROWSERS_PATH: The path for Playwright browsers.")
            print("REPO: The name of the repository.")
            print("SHA: The SHA of the commit.")
            print("TESTING_OWNER: The owner of the testing repository.")
            sys.exit(0)
        elif sys.argv[1] in ["-v", "--version"]:
            print(f"{__name__} version {__version__}")
            sys.exit(0)
        path = Path(sys.argv[1])
    else:
        path = Path(os.getcwd())
    asyncio.run(post_comment(path))


def repost_comment_on_pull_request(
    repo: Repository, comment: str, pr: dict[str, str]
) -> None:
    """Repost a commit comment on a PR containing that commit."""
    pr_number = pr["number"]
    issue = repo.get_issue(number=pr_number)
    issue.create_comment(comment)


def repost_comment_on_pull_requests(repo: Repository, comment: str) -> None:
    """Repost a commit comment on all PR containing that commit."""
    pr_url: str = f"https://api.github.com/repos/{_ENV.owner}/{_ENV.repo}/commits/{_ENV.sha}/pulls"
    headers: dict[str, str] = {
        "Authorization": f"Bearer {_ENV.github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    response: requests.Response = requests.get(pr_url, headers=headers)
    success_response = 200
    if response.status_code == success_response:
        pull_requests: Optional[list[dict]] = response.json()
        if pull_requests:
            for pr in pull_requests:
                repost_comment_on_pull_request(repo, comment, pr)


async def post_comment(path: Path) -> None:
    """Post a comment on a GitHub commit and relevant PR."""
    personal_access_token = _ENV.github_token
    g = Github(personal_access_token)
    repo = g.get_repo(f"{_ENV.owner}/{_ENV.repo}")
    commit = repo.get_commit(_ENV.sha)
    comment = await generate_comment(path)
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

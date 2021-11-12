"""Create a branch in all addons project.

TODO
- load copier answers from a previous branch
"""
import subprocess

import click

from .oca_projects import get_repositories, temporary_clone


@click.command("Create an orphan branch from a 'copier' template")
@click.argument("new_branch")
@click.option(
    "--copier-template",
    default="gh:oca/oca-addons-repo-template",
    show_default=True,
)
@click.option(
    "--copier-template-vcs-ref",
)
@click.option(
    "--repo",
    "repos",
    multiple=True,
)
@click.option(
    "--org_name",
    "org_name",
    default='OCA',
    show_default=True,
)
def main(new_branch, copier_template, copier_template_vcs_ref, repos, org_name):
    for repo in repos or get_repositories(org_name):
        print("=" * 10, repo, "=" * 10)
        with temporary_clone(repo, org_name=org_name):
            # check if branch already exists
            if subprocess.check_output(
                ["git", "ls-remote", "--head", "origin", new_branch]
            ):
                print(f"branch {new_branch} already exist in {repo}")
                continue
            # set git user/email
            subprocess.check_call(
                ["git", "config", "user.name", "Giovanni"],
            )
            subprocess.check_call(
                ["git", "config", "user.email", "giovanni@gslab.it"],
            )
            # create empty git branch
            subprocess.check_call(["git", "checkout", "--orphan", new_branch])
            subprocess.check_call(["git", "reset", "--hard"])
            # copier
            copier_cmd = [
                "copier",
                "--data",
                f"odoo_version={new_branch}",
                "--data",
                f"repo_slug={repo}",
                "--data",
                f"repo_name={repo}",
                "--data",
                "repo_description=TODO: add repo description.",
                "--data",
                "dependency_installation_mode=PIP",
                "--data",
                "ci=GitHub",
                "--force",
            ]
            if copier_template_vcs_ref:
                copier_cmd += ["--vcs-ref", copier_template_vcs_ref]
            copier_cmd += [copier_template, "."]
            subprocess.check_call(copier_cmd)
            # pre-commit run -a
            subprocess.check_call(["git", "add", "."])
            subprocess.call(["pre-commit", "run", "-a"])
            # commit and push
            subprocess.check_call(["git", "add", "."])
            subprocess.check_call(
                ["git", "commit", "-m", f"Initialize {new_branch} branch"]
            )
            subprocess.check_call(["pre-commit", "run", "-a"])  # to be sure
            subprocess.check_call(["git", "push", "origin", new_branch])

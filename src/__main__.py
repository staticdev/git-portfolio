import getpass
import logging
import sys
from typing import Any
from typing import Dict

import github
import inquirer


# starting log
FORMAT = "%(asctime)s %(message)s"
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"
logging.basicConfig(level=logging.ERROR, format=FORMAT, datefmt=DATE_FORMAT)
LOGGER = logging.getLogger(__name__)


def _not_empty_validation(answers: Dict[str, Any], current: str) -> bool:
    """Validade if current answer is not just spaces.

    Args:
        answers (Dict[str, Any]): answers to previous questions (ignored).
        current (str): answer to current question.

    Returns:
        bool: if is valid output.
    """
    current_without_spaces = current.strip()
    return True if current_without_spaces else False


def _ignore_if_not_confirmed(answers: Dict[str, Any]) -> bool:
    return not answers["confirmation"]


class Manager():
    def __init__(self):
        self.github_repos = []
        self.selected_github_repos = []
        self.github_username = getpass.getuser()
        self.github_connection = None

    def issue_create(self) -> None:
        questions = [
            inquirer.Text('title', message='Write an issue title', validate=_not_empty_validation),
            inquirer.Text('body', message='Write an issue body [optional]'),
            inquirer.Text('labels', message='Write issue labels separated by comma [optional]'),
            inquirer.Confirm('correct',  message='Confirm creation of issue for the project(s) {}. Continue?'.format(self.selected_github_repos), default=False),
        ]
        answers = inquirer.prompt(questions)
        labels = [label.strip() for label in answers['labels'].split(",")]
        if answers['correct']:
            for github_repo in self.selected_github_repos:
                repo = self.github_connection.get_repo(github_repo)
                try:
                    repo.create_issue(title=answers['title'], body=answers['body'], labels=labels)
                    print("{}: issue created successfully.".format(github_repo))
                except github.GithubException as github_exception:
                    if github_exception.data["message"] == "Issues are disabled for this repo":
                        print("{}: {}. It may be a fork.".format(github_repo, github_exception.data["message"]))
                    else:
                        print("{}: {}.".format(github_repo, github_exception.data["message"]))

    def pull_request_create(self) -> None:
        # TODO create issue for github to add labels to their API
        questions = [
            inquirer.Text('base', message='Write base branch name (destination)', default="master", validate=_not_empty_validation),
            inquirer.Text('head', message='Write the head branch name (source)', validate=_not_empty_validation),
            inquirer.Text('title', message='Write an pull request title', validate=_not_empty_validation),
            inquirer.Text('body', message='Write an pull request body [optional]'),
            inquirer.Confirm('draft',  message='Do you want to create a draft pull request?', default=False),
            inquirer.Confirm('confirmation',  message='Do you want to link pull request to issues by title?', default=False),
            inquirer.Text('link', message='Write issue title (or part of it)', validate=_not_empty_validation, ignore=_ignore_if_not_confirmed),
            inquirer.Confirm('correct',  message='Confirm creation of pull request(s) for the project(s) {}. Continue?'.format(self.selected_github_repos), default=False)
        ]
        answers = inquirer.prompt(questions)
        if answers['correct']:
            body = answers['body']
            for github_repo in self.selected_github_repos:
                repo = self.github_connection.get_repo(github_repo)
                # link issues
                if answers['confirmation']:
                    issues = repo.get_issues(state='open')
                    closes = ""
                    for issue in issues:
                        if answers['link'] in issue.title:
                            closes += "#{} ".format(issue.number)
                    closes = closes.strip()
                    if closes:
                        body += "\n\nCloses {}".format(closes)
                try:
                    repo.create_pull(title=answers['title'], body=body, head=answers['head'], base=answers['base'], draft=answers['draft'])
                    print("{}: PR created successfully.".format(github_repo))
                except github.GithubException as github_exception:
                    extra = ""
                    for error in github_exception.data["errors"]:
                        if "message" in error:
                            extra += "{} ".format(error["message"])
                        else:
                            extra += "Invalid field {}. ".format(error["field"])
                    print("{}: {}. {}".format(github_repo, github_exception.data["message"], extra))

    def pull_request_merge(self) -> None:
        """Merge pull request."""
        state = "open"
        questions = [
            inquirer.Text('base', message='Write base branch name (destination)', default="master", validate=_not_empty_validation),
            inquirer.Text('head', message='Write the head branch name (source)', validate=_not_empty_validation),
            inquirer.Text('prefix', message='Write base user or organization name from PR head', default=self.github_username, validate=_not_empty_validation),
            inquirer.Confirm('correct',  message='Confirm merging of pull request(s) for the project(s) {}. Continue?'.format(self.selected_github_repos), default=False)
        ]
        answers = inquirer.prompt(questions)
        # Important note: base and head arguments have different import formats.
        # https://developer.github.com/v3/pulls/#list-pull-requests
        # head needs format "user/org:branch"
        head = "{}:{}".format(answers["prefix"], answers["head"])

        if answers['correct']:
            for github_repo in self.selected_github_repos:
                repo = self.github_connection.get_repo(github_repo)
                pulls = repo.get_pulls(state=state, base=answers['base'], head=head)
                if pulls.totalCount == 1:
                    pull = pulls[0]
                    if pull.mergeable:
                        try:
                            pull.merge()
                            print("{}: PR merged successfully.".format(github_repo))
                        except github.GithubException as github_exception:
                            print("{}: {}.".format(github_repo, github_exception.data["message"]))
                    else:
                        print("{}: PR not mergeable, GitHub checks may be running.".format(github_repo))
                else:
                    print("{}: no open PR found for {}:{}.".format(github_repo, answers['base'], answers['head']))

    def branch_delete(self):
        questions = [
            inquirer.Text('branch', message='Write the branch name', validate=_not_empty_validation),
            inquirer.Confirm('correct',  message='Confirm deleting of branch(es) for the project(s) {}. Continue?'.format(self.selected_github_repos), default=False)
        ]
        answers = inquirer.prompt(questions)
        if answers['correct']:
            for github_repo in self.selected_github_repos:
                repo = self.github_connection.get_repo(github_repo)
                try:
                    branch = repo.get_branch(branch=answers['branch'])

                    print("{}: branch deleted successfully.".format(github_repo))
                except github.GithubException as github_exception:
                    print("{}: {}.".format(github_repo, github_exception.data["message"]))

    def github_connect(self):
        print("We are going to connect to GitHub")
        questions = [
            inquirer.Text('github_username', message='GitHub username', default=self.github_username, validate=_not_empty_validation),
            inquirer.Password('github_access_token', message='GitHub access token', validate=_not_empty_validation),
            inquirer.Text('github_hostname', message='GitHub hostname (change ONLY if you use GitHub Enterprise)'),
        ]
        answers = inquirer.prompt(questions)
        self.github_username = answers["github_username"]
        access_token = answers["github_access_token"].strip()
        # GitHub Enterprise
        if answers["github_hostname"]:
            base_url = "https://{}/api/v3".format(answers["github_hostname"])
            self.github_connection = github.Github(base_url=base_url, login_or_token=access_token)
        # GitHub.com
        else:
            self.github_connection = github.Github(access_token)
        user = self.github_connection.get_user()
        self.github_repos = user.get_repos()
        self.github_repos_select()

    def github_repos_select(self):
        try:
            repo_names = [repo.full_name for repo in self.github_repos]
        except github.BadCredentialsException:
            print("Wrong GitHub credentials. Please try again.")
            return self.github_connect()
        except github.GithubException as github_exception:
            LOGGER.exception(github_exception)
            print("Wrong GitHub token/permissions. Please try again.")
            return self.github_connect()

        while True:
            selected = inquirer.prompt([inquirer.Checkbox("github_repos",
                    message="Which repos are you working on? (Select pressing space)",
                    choices=repo_names,
                )])["github_repos"]
            if len(selected) == 0:
                print("Please select with `space` at least one repo.\n")
            else:
                break

        self.selected_github_repos = selected
        self.issue_create()


def main():
    manager = Manager()
    manager.github_connect()


if __name__ == "__main__":
    main()

import os
import shutil
import time

import requests
from git import GitCommandError, Repo

from ncatbot.plugin import PluginLoader

MAIN_REPO_OWNER = "ncatbot"
MAIN_BRANCH_NAME = "main"
MAIN_REPO_NAME = "NcatBot-Plugins"

github_token = None
token_owner = None


def get_github_token(token):
    token = os.getenv("GITHUB_TOKEN", None)
    if token is None:
        print("WARNING: GITHUB_TOKEN environment variable not set.")
        print("input your token:")
        token = input()
    return token


def test_github_token(token):
    if token is None:
        return False
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    api_url = "https://api.github.com/user"
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        print(f"This token is owned by: {get_token_owner(token)}")
        return True
    else:
        raise ValueError(f"Please Check your GitHub Token: {token}")


def get_token_owner(token):
    global token_owner
    if token_owner is not None:
        return token_owner
    """通过 GitHub API 获取 Token 所属用户的用户名"""
    api_url = "https://api.github.com/user"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        token_owner = response.json()["login"]
        return token_owner
    else:
        print(f"Failed to get token owner: {response.text}")
        return None


def create_pull_request(local_branch_name, plugin_name, version):
    print("creating pull request")
    global github_token
    # 获取主仓库的 owner 和 repo 名称
    owner = MAIN_REPO_OWNER
    repo = MAIN_REPO_NAME

    # GitHub API URL
    api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "title": f"Publish plugin {plugin_name} version {version}",
        "head": f"{get_token_owner(github_token)}:{local_branch_name}",
        "base": MAIN_BRANCH_NAME,
        "body": f"Publish plugin {plugin_name} version {version}",
    }

    response = requests.post(api_url, json=data, headers=headers)
    if response.status_code == 201:
        print("Pull Request created successfully!")
    else:
        print(f"Failed to create Pull Request: {response.text}")


def get_plugin_info(path):
    if os.path.exists(path):
        return PluginLoader().get_plugin_info(path)
    else:
        raise FileNotFoundError(f"dir not found: {path}")


# 检查是否已经存在 Fork
def has_existing_fork(user_name, repo_name):
    global github_token
    fork_url = f"https://api.github.com/repos/{user_name}/{repo_name}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(fork_url, headers=headers)
    return response.status_code == 200


def create_pull_request_to_fork(
    fork_owner, fork_repo_name, source_owner, source_repo_name, base_branch, head_branch
):
    """创建拉取请求到 fork 仓库"""
    url = f"https://api.github.com/repos/{fork_owner}/{fork_repo_name}/pulls"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "title": "Sync with upstream",
        "body": "Automatically sync with the upstream repository",
        "head": f"{source_owner}:{head_branch}",
        "base": base_branch,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return response.json()["number"]
    else:
        raise Exception(
            f"Failed to create pull request: {response.status_code} - {response.text}"
        )


def merge_pull_request(fork_owner, fork_repo_name, pull_number):
    """合并拉取请求"""
    url = f"https://api.github.com/repos/{fork_owner}/{fork_repo_name}/pulls/{pull_number}/merge"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.put(url, headers=headers)
    if response.status_code in [200, 201]:
        print(f"Pull request #{pull_number} merged successfully!")
    else:
        raise Exception(
            f"Failed to merge pull request: {response.status_code} - {response.text}"
        )


def check_branch_diff(
    source_owner, source_repo, source_branch, fork_owner, fork_repo, fork_branch
):
    """检查分支差异"""
    url = f"https://api.github.com/repos/{fork_owner}/{fork_repo}/compare/{source_owner}:{source_branch}...{fork_owner}:{fork_branch}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        compare_data = response.json()
        behind_by = compare_data.get("behind_by", 0)
        return behind_by > 0
    except requests.exceptions.HTTPError as e:
        print(f"Error checking branch diff: {e}")
        return False


def sync_fork_with_source():
    try:
        # 获取 source 仓库的默认分支
        source_default_branch = MAIN_BRANCH_NAME
        # print(f"Source repository default branch: {source_default_branch}")

        # 获取 fork 仓库的默认分支
        fork_default_branch = MAIN_BRANCH_NAME
        # print(f"Fork repository default branch: {fork_default_branch}")

        # 解构 fork 和 source 的路径
        fork_owner, fork_repo_name = get_token_owner(github_token), MAIN_REPO_NAME
        source_owner, source_repo_name = MAIN_REPO_OWNER, MAIN_REPO_NAME

        # 检查是否已经最新
        has_diff = check_branch_diff(
            source_owner,
            source_repo_name,
            source_default_branch,
            fork_owner,
            fork_repo_name,
            fork_default_branch,
        )
        if not has_diff:
            print("No difference between source and fork branches. Exiting...")
            return

        # 创建拉取请求
        pr_number = create_pull_request_to_fork(
            fork_owner,
            fork_repo_name,
            source_owner,
            source_repo_name,
            fork_default_branch,
            source_default_branch,
        )
        print(f"Pull request #{pr_number} created.")

        # 合并拉取请求
        merge_pull_request(fork_owner, fork_repo_name, pr_number)
        print(f"Synced fork {fork_owner}/{fork_repo_name} successfully!")

    except Exception as e:
        print(f"Error occurred during synchronization: {e}")


def fork(owner, repo):
    global github_token
    token_owner = get_token_owner(github_token)
    if has_existing_fork(token_owner, MAIN_REPO_NAME):
        print("Existing fork detected, trying to sync...")
        return sync_fork_with_source()
    else:
        # Fork 主仓库
        fork_url = f"https://api.github.com/repos/{owner}/{repo}/forks"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        response = requests.post(fork_url, headers=headers)
        if response.status_code != 202:
            print(f"Failed to fork repository: {response.text}")
            return None
        return response.json()["html_url"]


def main():
    global github_token

    print("Where is your Plugin?")
    path = input()

    plugin_name, version = get_plugin_info(path)
    source_folder = path

    github_token = get_github_token(github_token)
    test_github_token(github_token)

    # Fork 主仓库
    fork(MAIN_REPO_OWNER, MAIN_REPO_NAME)
    fork_repo = (
        f"https://github.com/{get_token_owner(github_token)}/{MAIN_REPO_NAME}.git"
    )
    print(f"Fork finished: {fork_repo}")

    # 克隆 Fork 的仓库
    try:
        print("Cloning repository...")
        repo = Repo.clone_from(fork_repo, f"temp_repo{time.time()}")
    except GitCommandError as e:
        print(f"Failed to clone repository: {e}")
        return

    print("Cloning finished. Making a new branch to publish plugin...")
    # 创建新分支
    branch_name = f"publish-{plugin_name}-{version}"
    repo.git.checkout("-b", branch_name)

    # 复制插件文件到目标路径
    target_folder = os.path.join("plugins", plugin_name, version)
    shutil.copytree(source_folder, os.path.join(repo.working_dir, target_folder))

    # 添加并提交更改
    repo.git.add(all=True)
    commit_message = f"Publish plugin {plugin_name} version {version}"
    repo.git.commit("-m", commit_message)

    # 推送更改到 GitHub
    try:
        print("Pushing changes...")
        repo.git.push("--force", "origin", branch_name)
    except GitCommandError as e:
        print(f"Failed to push changes: {e}")
        return

    # 创建 Pull Request
    create_pull_request(branch_name, plugin_name, version)


main()

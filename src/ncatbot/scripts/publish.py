# 插件发布脚本

import os
import shutil
import stat
import time
from pathlib import Path

import requests
from git import GitCommandError, Repo

from ncatbot.scripts.utils import get_plugin_info

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
    print("正在创建插件推送请求...")
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
        print("成功发起请求!")
    else:
        print(f"发起请求失败: {response.text}")


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
            print("已 Fork 的仓库和官方无差异")
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
        print(f"成功同步 fork {fork_owner}/{fork_repo_name}!")

    except Exception as e:
        print(f"Error occurred during synchronization: {e}")


def fork(owner, repo):
    """fork 主仓库, 如果已经存在则尝试同步"""
    global github_token
    token_owner = get_token_owner(github_token)
    if has_existing_fork(token_owner, MAIN_REPO_NAME):
        print("已经存在 Fork, 尝试同步")
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


def get_plugin_path():
    path = input("输入插件文件夹路径 (plugins/your_plugin_name)\n")
    return path


def make_archive_with_gitignore(plugin_name, version, path):
    """
    打包文件, 同时忽略 .gitignore 中的文件
    """

    def read_gitignore(path):
        """
        解析 .gitignore 文件，返回被忽略的文件模式列表
        """
        ignore_patterns = [".git"]
        gitignore_path = Path(path) / ".gitignore"

        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    ignore_patterns.append(line)
        return ignore_patterns

    def should_ignore(file_path, ignore_patterns):
        """
        判断文件是否应该被忽略
        """
        for pattern in ignore_patterns:
            if file_path.match(pattern):
                return True
        return False

    def remove_read_only_files(temp_dir):
        """
        遍历并修改临时目录中文件和目录的权限，确保能够删除
        """
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    os.chmod(file_path, 0o777)  # 修改文件权限为可写
                    os.remove(file_path)
                except PermissionError:
                    print(f"无法删除文件: {file_path}")

            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    os.chmod(dir_path, 0o777)  # 修改目录权限为可写
                    os.rmdir(dir_path)
                except PermissionError:
                    print(f"无法删除目录: {dir_path}")

    # 解析 .gitignore 文件
    ignore_patterns = read_gitignore(path)

    # 创建一个临时目录用于存放需要打包的文件
    temp_dir = Path(path) / "temp_pack"
    temp_dir.mkdir(exist_ok=True)

    # 遍历根目录下的所有文件和文件夹
    for root, dirs, files in os.walk(path):
        for name in files:
            file_path = Path(root) / name
            relative_path = file_path.relative_to(path)

            # 如果文件在 .gitignore 中，则跳过
            if should_ignore(relative_path, ignore_patterns):
                continue

            # 将文件复制到临时目录
            target_path = temp_dir / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, target_path)

    # 使用 shutil.make_archive 打包临时目录
    archive_name = f"{plugin_name}-{version}"
    shutil.make_archive(archive_name, "zip", temp_dir)

    # 删除临时目录，并确保有权限删除
    remove_read_only_files(temp_dir)
    shutil.rmtree(temp_dir)

    print(f"打包完成：{archive_name}.zip")
    return archive_name + ".zip"


def do_version_change(target_base_folder, version):
    version_list = os.path.join(target_base_folder, "version.txt")
    os.makedirs(target_base_folder, exist_ok=True)
    if not os.path.exists(version_list):
        with open(version_list, "w") as f:
            f.write(version + "\n")
    else:
        with open(version_list, "r") as f:
            versions = f.readlines()
        if version in versions:
            print(f"版本 {version} 已存在, 请更改版本号后再使用自动发布功能")
            exit(1)
        with open(version_list, "a") as f:
            f.write(version + "\n")


def main():
    def prepare():
        """准备工作
        1. 获取插件路径和插件基本信息
        2. 获取并测试 github token
        """
        global plugin_name, version, path, github_token
        path = get_plugin_path()
        plugin_name, version = get_plugin_info(path)
        if plugin_name is None:
            print("获取插件信息失败, 请检查错误信息")
            exit(0)
        print(f"Plugin name: {plugin_name}, version: {version}")
        github_token = get_github_token(github_token)
        test_github_token(github_token)
        return f"publish-{plugin_name}-{version}"

    def to_local():
        """转移最新的远端仓库到本地"""
        # Fork 主仓库
        fork(MAIN_REPO_OWNER, MAIN_REPO_NAME)
        fork_repo = (
            f"https://github.com/{get_token_owner(github_token)}/{MAIN_REPO_NAME}.git"
        )
        print(f"Fork 完成: {fork_repo}")

        # 克隆 Fork 的仓库
        try:
            print("正在克隆远端仓库...")
            repo = Repo.clone_from(fork_repo, f"temp_repo{time.time()}")
        except GitCommandError as e:
            print(f"Failed to clone repository: {e}")
            return

        print("克隆完成, 为插件发布创建新的分支...")
        # 创建新分支
        repo.git.checkout("-b", branch_name)
        return repo, os.path.join(repo.working_dir, "plugins", plugin_name)

    def do_change(repo, target_base_folder):
        """打包插件并创建更新"""
        # 写版本
        do_version_change(target_base_folder, version)

        # 打包插件并移动到对应文件夹(打包文件而非文件夹, 要解压到 plugins/plugin_name/)
        archived_file = make_archive_with_gitignore(plugin_name, version, path)

        # 移动到 git 文件夹
        shutil.move(archived_file, target_base_folder)

        # 添加并提交更改
        repo.git.add(all=True)
        commit_message = f"Publish plugin {plugin_name} version {version}"
        repo.git.commit("-m", commit_message)

    def do_pull_request(repo, branch_name):
        """推送更改并创建 PR"""
        try:
            print("推送更改...")
            repo.git.push("--force", "origin", branch_name)
        except GitCommandError as e:
            print(f"Failed to push changes: {e}")
            return

        # 创建 Pull Request
        create_pull_request(branch_name, plugin_name, version)

    def do_close(repo):
        """完成发布工作后清理本地临时文件"""
        # 删除临时文件夹
        temp_repo_path = repo.working_dir
        print(f"删除临时路径: {temp_repo_path}")

        # 首先关闭仓库对象以释放文件句柄
        repo.close()
        # 抽象repo关太慢了，不小睡一下会继续占用
        time.sleep(2)

        def on_rm_error(func, path, _):
            # 去掉只读
            os.chmod(path, stat.S_IWRITE)
            func(path)

        try:
            shutil.rmtree(temp_repo_path, onexc=on_rm_error)
            print("成功删除临时路径.")
        except Exception as e:
            print(f"删除临时路径时出错: {e}")

    branch_name = prepare()
    repo, target_base_folder = to_local()
    do_change(repo, target_base_folder)
    do_pull_request(repo, branch_name)
    do_close(repo)


main()

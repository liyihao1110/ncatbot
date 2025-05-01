# 插件发布脚本

import json
import os
import shutil
import stat
import time
from pathlib import Path
from typing import List, Tuple

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


def verify_branch_exists(owner: str, repo: str, branch: str) -> bool:
    """验证分支是否存在"""
    global github_token
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers)
    return response.status_code == 200


def create_pull_request(local_branch_name, plugin_name, version):
    print("正在创建插件推送请求...")
    global github_token
    token_owner = get_token_owner(github_token)

    # GitHub API URL for the official repository
    api_url = f"https://api.github.com/repos/{MAIN_REPO_OWNER}/{MAIN_REPO_NAME}/pulls"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "title": f"Update plugin {plugin_name} to version {version}",
        "head": f"{token_owner}:{local_branch_name}",
        "base": MAIN_BRANCH_NAME,
        "body": f"Update plugin {plugin_name} to version {version}\n\nChanges:\n- Added/Updated submodule for {plugin_name}\n- Updated plugin index",
    }

    response = requests.post(api_url, json=data, headers=headers)
    if response.status_code == 201:
        print("成功发起请求!")
    else:
        print(f"发起请求失败: {response.text}")
        if response.status_code == 422:
            print("请检查:")
            print(
                "1. 如果仍然使用老版本的插件仓库，请删除自己 fork 的 ncatbot/Ncatbot-Plugins"
            )
        exit(1)


def has_existing_repo(owner: str, repo: str) -> bool:
    """检查仓库是否存在"""
    global github_token
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers)
    return response.status_code == 200


def create_repo(name: str, description: str) -> str:
    """创建新的 GitHub 仓库"""
    global github_token
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "name": name,
        "description": description,
        "private": False,
        "auto_init": True,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return response.json()["clone_url"]
    else:
        raise Exception(f"Failed to create repository: {response.text}")


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
            with open(gitignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        ignore_patterns.append(line)
        return ignore_patterns

    def should_ignore(file_path, ignore_patterns):
        """
        检查文件是否应该被忽略
        """
        for pattern in ignore_patterns:
            if pattern in str(file_path):
                return True
        return False

    def remove_read_only_files(temp_dir):
        """
        移除临时目录中的只读文件
        """
        for root, dirs, files in os.walk(temp_dir):
            for name in files:
                file_path = Path(root) / name
                if file_path.exists():
                    os.chmod(file_path, stat.S_IWRITE)

    # 创建临时目录
    temp_dir = Path("temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    # 读取 .gitignore 文件
    ignore_patterns = read_gitignore(path)

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

    # 创建压缩包
    archive_name = f"{plugin_name}-{version}.zip"
    shutil.make_archive(archive_name[:-4], "zip", temp_dir)

    # 清理临时目录
    remove_read_only_files(temp_dir)
    shutil.rmtree(temp_dir)

    return archive_name


def do_version_change(target_base_folder, version):
    version_list = os.path.join(target_base_folder, "version.txt")
    os.makedirs(target_base_folder, exist_ok=True)

    # Normalize version string to ensure consistent format
    version = version.strip()

    if not os.path.exists(version_list):
        # Create new version.txt with proper newline
        with open(version_list, "w", newline="\n") as f:
            f.write(version + "\n")
    else:
        # Read existing versions and clean up the file
        with open(version_list, "r", newline="\n") as f:
            versions = [v.strip() for v in f.readlines()]
            # Remove empty lines and duplicates while preserving order
            versions = [v for v in versions if v]

        if version in versions:
            print(f"版本 {version} 已存在, 请更改版本号后再使用自动发布功能")
            exit(1)

        # Write back cleaned up versions plus new version
        with open(version_list, "w", newline="\n") as f:
            f.write("\n".join(versions) + "\n" + version + "\n")


def get_plugin_versions(version_file: str) -> List[str]:
    """获取插件的所有版本"""
    if not os.path.exists(version_file):
        return []
    with open(version_file, "r", newline="\n") as f:
        return [v.strip() for v in f.readlines() if v.strip()]


def update_plugin_index(
    repo: Repo, plugin_name: str, version: str, plugin_meta: dict
) -> None:
    """更新插件索引

    Args:
        repo: Git repository object
        plugin_name: Name of the plugin being published
        version: Version of the plugin being published
        plugin_meta: Plugin metadata
    """
    index_file = os.path.join(repo.working_dir, "index.json")

    # 读取现有索引或创建新索引
    if os.path.exists(index_file):
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                index_data = json.load(f)
        except:
            index_data = {
                "plugins": {},
                "last_update": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }
    else:
        index_data = {
            "plugins": {},
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        }

    # 获取现有版本列表
    existing_versions = []
    if plugin_name in index_data["plugins"]:
        existing_versions = index_data["plugins"][plugin_name].get("versions", [])

    # 更新当前插件的索引信息
    plugin_data = {
        "name": plugin_name,
        "versions": sorted(
            list(set(existing_versions + [version])), reverse=True
        ),  # 保留所有版本并按降序排序
        "latest_version": version,
        "description": plugin_meta.get("description", ""),
        "author": plugin_meta.get("author", ""),
        "plugin_dependencies": plugin_meta.get("plugin_dependencies", {}),
        "tags": plugin_meta.get("tags", []),
        "homepage": plugin_meta.get("homepage", ""),
        "funcs": plugin_meta.get("funcs", []),
        "configs": plugin_meta.get("configs", []),
        "repository": f"https://github.com/{get_token_owner(github_token)}/{plugin_name}",
    }
    index_data["plugins"][plugin_name] = plugin_data

    # 更新时间戳
    index_data["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 写入索引文件
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    # 提交更改
    repo.index.add([index_file])
    commit_message = f"Update plugin index for {plugin_name} version {version}"
    repo.index.commit(commit_message)


def sync_with_official_repo(repo: Repo, force_sync: bool = True) -> None:
    """同步用户的主仓库与官方仓库。

    参数:
        repo: 本地仓库的 GitPython Repo 对象。
        force_sync: 如果为 True，允许合并无关的历史记录。

    步骤:
        1. 添加官方仓库为远程源。
        2. 获取最新更改。
        3. 合并更改到主分支，冲突时优先使用上游更改。
        4. 强制推送更改到用户仓库。
    """
    try:
        print("正在同步官方仓库...")

        # 添加或更新上游远程源
        try:
            repo.create_remote(
                "upstream", f"https://github.com/{MAIN_REPO_OWNER}/{MAIN_REPO_NAME}.git"
            )
        except GitCommandError:
            # 如果远程源已存在，则更新 URL
            repo.git.remote(
                "set-url",
                "upstream",
                f"https://github.com/{MAIN_REPO_OWNER}/{MAIN_REPO_NAME}.git",
            )

        # 获取上游的最新更改
        repo.git.fetch("upstream")

        # 确保在主分支上
        repo.git.checkout(MAIN_BRANCH_NAME)

        # 合并上游更改，冲突时优先使用上游版本
        merge_args = [f"upstream/{MAIN_BRANCH_NAME}", "-X", "theirs"]
        if force_sync:
            merge_args.append("--allow-unrelated-histories")

        repo.git.merge(*merge_args)

        # 强制推送更改到用户仓库
        repo.git.push("origin", MAIN_BRANCH_NAME, "--force")

        print("成功同步官方仓库！")

    except GitCommandError as e:
        print(f"同步官方仓库失败: {e}")
        if "unrelated histories" in str(e) and not force_sync:
            print("仓库历史记录无关。若要强制同步，请设置 force_sync=True。")
        else:
            print("请检查错误信息并手动同步仓库后重试。")
        exit(1)


def main():
    def prepare():
        """准备工作
        1. 获取插件路径和插件基本信息
        2. 获取并测试 github token
        """
        global plugin_name, version, path, github_token, plugin_meta
        path = get_plugin_path()
        plugin_name, version, plugin_meta = get_plugin_info(path)
        if plugin_name is None:
            print("获取插件信息失败, 请检查错误信息")
            exit(0)
        print(f"Plugin name: {plugin_name}, version: {version}")
        if plugin_meta.get("description"):
            print(f"Description: {plugin_meta['description']}")
        if plugin_meta.get("author"):
            print(f"Author: {plugin_meta['author']}")
        if plugin_meta.get("plugin_dependencies"):
            print(f"Dependencies: {plugin_meta['plugin_dependencies']}")
        github_token = get_github_token(github_token)
        test_github_token(github_token)
        return f"update-{plugin_name}-{version}"

    def setup_plugin_repo() -> Tuple[Repo, str]:
        """设置插件仓库
        1. 检查插件仓库是否存在
        2. 如果不存在则创建
        3. 克隆仓库并创建新版本分支
        """
        global github_token
        token_owner = get_token_owner(github_token)

        # 检查插件仓库是否存在
        if not has_existing_repo(token_owner, plugin_name):
            print(f"插件仓库 {plugin_name} 不存在，正在创建...")
            repo_url = create_repo(plugin_name, plugin_meta.get("description", ""))
        else:
            repo_url = f"https://github.com/{token_owner}/{plugin_name}.git"

        # 克隆仓库
        try:
            print("正在克隆插件仓库...")
            repo = Repo.clone_from(repo_url, f"temp_repo{time.time()}")
        except GitCommandError as e:
            print(f"Failed to clone repository: {e}")
            exit(1)

        # 创建新版本分支
        branch_name = f"v{version}"
        try:
            # 确保我们在主分支上
            repo.git.checkout(MAIN_BRANCH_NAME)
            # 创建并切换到新分支
            repo.git.checkout("-b", branch_name)
            print(f"Created and switched to branch: {branch_name}")
        except GitCommandError as e:
            print(f"Failed to create branch: {e}")
            exit(1)

        return repo, os.path.join(repo.working_dir)

    def setup_main_repo() -> Repo:
        """设置主仓库
        1. 检查主仓库是否存在
        2. 如果不存在则从官方仓库 fork
        3. 克隆仓库并创建新分支
        """
        global github_token
        token_owner = get_token_owner(github_token)

        # 检查主仓库是否存在
        if not has_existing_repo(token_owner, MAIN_REPO_NAME):
            print(f"主仓库 {MAIN_REPO_NAME} 不存在，正在从官方仓库 fork...")
            # Fork 官方仓库
            api_url = (
                f"https://api.github.com/repos/{MAIN_REPO_OWNER}/{MAIN_REPO_NAME}/forks"
            )
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
            }
            response = requests.post(api_url, headers=headers)
            if response.status_code != 202:
                print(f"Fork 官方仓库失败: {response.text}")
                exit(1)
            print("Fork 成功，等待 GitHub 处理...")
            time.sleep(2)  # 等待 GitHub 处理 fork 请求

        # 克隆仓库
        try:
            print("正在克隆主仓库...")
            repo_url = f"https://github.com/{token_owner}/{MAIN_REPO_NAME}.git"
            repo = Repo.clone_from(repo_url, f"temp_main_repo{time.time()}")
        except GitCommandError as e:
            print(f"Failed to clone repository: {e}")
            exit(1)

        # 同步官方仓库
        sync_with_official_repo(repo)

        # 创建新分支
        branch_name = f"update-{plugin_name}-{version}"
        try:
            # 确保我们在主分支上
            repo.git.checkout(MAIN_BRANCH_NAME)
            # 创建并切换到新分支
            repo.git.checkout("-b", branch_name)
            print(f"Created and switched to branch: {branch_name}")
        except GitCommandError as e:
            print(f"Failed to create branch: {e}")
            exit(1)

        return repo

    def do_plugin_changes(repo: Repo, target_dir: str):
        """处理插件仓库的更改
        1. 创建版本文件
        2. 复制源代码
        3. 打包插件文件到 release/ 目录
        4. 提交更改
        """
        # 创建版本文件
        version_file = os.path.join(target_dir, "version.txt")
        do_version_change(target_dir, version)

        # 创建 release 目录
        release_dir = os.path.join(target_dir, "release")
        os.makedirs(release_dir, exist_ok=True)

        # 打包插件文件到 release 目录
        archived_file = make_archive_with_gitignore(plugin_name, version, path)
        shutil.move(archived_file, release_dir)

        # 复制源代码
        def copy_source_files(source_path, target_path):
            """递归复制源代码文件，忽略 .git 目录"""
            for item in os.listdir(source_path):
                source_item = os.path.join(source_path, item)
                target_item = os.path.join(target_path, item)

                if item == ".git":
                    continue

                if os.path.isdir(source_item):
                    shutil.copytree(source_item, target_item, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_item, target_item)

        # 复制源代码到插件仓库
        copy_source_files(path, target_dir)

        # 提交更改
        repo.git.add(all=True)
        commit_message = f"Release version {version}"
        repo.git.commit("-m", commit_message)

        try:
            print("推送插件仓库更改...")
            repo.git.push("--force", "origin", f"v{version}")
        except GitCommandError as e:
            print(f"Failed to push plugin changes: {e}")
            exit(1)

    def do_main_changes(repo: Repo):
        """处理主仓库的更改
        1. 添加 submodule
        2. 更新插件索引
        3. 提交更改
        """
        # 添加或更新 submodule
        plugin_repo_url = (
            f"https://github.com/{get_token_owner(github_token)}/{plugin_name}.git"
        )
        plugin_dir = os.path.join("plugins", plugin_name)
        version_branch = f"v{version}"

        try:
            # 检查 submodule 是否已经在 git 索引中
            try:
                repo.git.submodule("status", plugin_dir)
                print(f"更新插件 {plugin_name} 的 submodule...")
                # 先删除旧的 submodule
                repo.git.submodule("deinit", "-f", plugin_dir)
                repo.git.rm("-f", plugin_dir)
                # 重新添加 submodule 并指定分支
                repo.git.submodule(
                    "add", "-b", version_branch, plugin_repo_url, plugin_dir
                )
            except GitCommandError:
                # 如果 submodule 不在索引中，则添加新的 submodule
                print(f"添加插件 {plugin_name} 作为 submodule...")
                repo.git.submodule(
                    "add", "-b", version_branch, plugin_repo_url, plugin_dir
                )

            # 初始化并更新 submodule
            repo.git.submodule("update", "--init", "--recursive")

        except GitCommandError as e:
            print(f"Failed to add/update submodule: {e}")
            exit(1)

        # 更新主索引
        update_plugin_index(repo, plugin_name, version, plugin_meta)

    def do_pull_requests(plugin_repo: Repo, main_repo: Repo, branch_name: str):
        """推送更改并创建 PR
        1. 推送插件仓库更改
        2. 推送主仓库更改并创建 PR
        """
        try:
            print("推送主仓库更改...")
            # 确保我们在正确的分支上
            main_repo.git.checkout(branch_name)
            # 推送更改
            main_repo.git.push("--force", "origin", branch_name)
            # 等待 GitHub 处理推送
            time.sleep(5)  # 增加等待时间
        except GitCommandError as e:
            print(f"Failed to push main repository changes: {e}")
            exit(1)

        # 创建 Pull Request
        create_pull_request(branch_name, plugin_name, version)

    def cleanup(repos: List[Repo]):
        """清理临时文件
        1. 关闭所有仓库对象
        2. 删除所有临时目录
        """
        # 首先关闭所有仓库对象
        for repo in repos:
            try:
                repo.close()
            except Exception as e:
                print(f"Error closing repository: {e}")

        # 等待文件句柄释放
        time.sleep(2)

        def on_rm_error(func, path, _):
            """处理删除错误，移除只读属性后重试"""
            os.chmod(path, stat.S_IWRITE)
            func(path)

        # 删除所有临时目录
        for repo in repos:
            temp_repo_path = repo.working_dir
            print(f"删除临时路径: {temp_repo_path}")
            try:
                shutil.rmtree(temp_repo_path, onexc=on_rm_error)
                print("成功删除临时路径.")
            except Exception as e:
                print(f"删除临时路径时出错: {e}")

        # 删除临时打包目录
        temp_dir = Path("temp")
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir, onexc=on_rm_error)
                print("成功删除临时打包目录.")
            except Exception as e:
                print(f"删除临时打包目录时出错: {e}")

    # 执行发布流程
    branch_name = prepare()
    plugin_repo, plugin_dir = setup_plugin_repo()
    main_repo = setup_main_repo()

    do_plugin_changes(plugin_repo, plugin_dir)
    do_main_changes(main_repo)
    do_pull_requests(plugin_repo, main_repo, branch_name)
    cleanup([plugin_repo, main_repo])


# if __name__ == "__main__":
#     github_token = get_github_token(github_token)
#     create_pull_request("update-TestPlugin-0.0.5", "TestPlugin", "0.0.5")
main()

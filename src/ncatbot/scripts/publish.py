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
        print(f"获取 token 拥有者失败: {response.text}")
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
        raise Exception(f"创建仓库失败: {response.text}")


def get_plugin_path():
    path = input("输入插件文件夹路径 (plugins/your_plugin_name)\n")
    return path


def make_archive_with_gitignore(plugin_name, version, path):
    """
    打包文件，同时忽略 .gitignore 中的文件
    """

    def read_gitignore(path):
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
        for pattern in ignore_patterns:
            if pattern in str(file_path):
                return True
        return False

    def remove_read_only_files(temp_dir):
        for root, dirs, files in os.walk(temp_dir):
            for name in files:
                file_path = Path(root) / name
                if file_path.exists():
                    os.chmod(file_path, stat.S_IWRITE)

    temp_dir = Path("temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    ignore_patterns = read_gitignore(path)

    for root, dirs, files in os.walk(path):
        for name in files:
            file_path = Path(root) / name
            relative_path = file_path.relative_to(path)
            if should_ignore(relative_path, ignore_patterns):
                continue
            target_path = temp_dir / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, target_path)

    archive_name = f"{plugin_name}-{version}.zip"
    shutil.make_archive(archive_name[:-4], "zip", temp_dir)

    remove_read_only_files(temp_dir)
    shutil.rmtree(temp_dir)

    return archive_name


def do_version_change(target_base_folder, version):
    version_list = os.path.join(target_base_folder, "version.txt")
    os.makedirs(target_base_folder, exist_ok=True)

    version = version.strip()

    if not os.path.exists(version_list):
        with open(version_list, "w", newline="\n") as f:
            f.write(version + "\n")
    else:
        with open(version_list, "r", newline="\n") as f:
            versions = [v.strip() for v in f.readlines()]
            versions = [v for v in versions if v]

        if version in versions:
            print(f"版本 {version} 已存在，请更改版本号后再使用自动发布功能")
            exit(1)

        with open(version_list, "w", newline="\n") as f:
            f.write("\n".join(versions) + "\n" + version + "\n")


def get_plugin_versions(version_file: str) -> List[str]:
    if not os.path.exists(version_file):
        return []
    with open(version_file, "r", newline="\n") as f:
        return [v.strip() for v in f.readlines() if v.strip()]


def update_plugin_index(
    repo: Repo, plugin_name: str, version: str, plugin_meta: dict
) -> None:
    index_file = os.path.join(repo.working_dir, "index.json")

    if os.path.exists(index_file):
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                index_data = json.load(f)
        except Exception:
            index_data = {
                "plugins": {},
                "last_update": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }
    else:
        index_data = {
            "plugins": {},
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        }

    existing_versions = []
    if plugin_name in index_data["plugins"]:
        existing_versions = index_data["plugins"][plugin_name].get("versions", [])

    plugin_data = {
        "name": plugin_name,
        "versions": sorted(list(set(existing_versions + [version])), reverse=True),
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

    index_data["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    repo.index.add([index_file])
    commit_message = f"Update plugin index for {plugin_name} version {version}"
    repo.index.commit(commit_message)


def sync_with_official_repo(repo: Repo, force_sync: bool = True) -> None:
    try:
        print("正在同步官方仓库...")

        try:
            repo.create_remote(
                "upstream", f"https://github.com/{MAIN_REPO_OWNER}/{MAIN_REPO_NAME}.git"
            )
        except GitCommandError:
            repo.git.remote(
                "set-url",
                "upstream",
                f"https://github.com/{MAIN_REPO_OWNER}/{MAIN_REPO_NAME}.git",
            )

        repo.git.fetch("upstream")
        repo.git.checkout(MAIN_BRANCH_NAME)

        merge_args = [f"upstream/{MAIN_BRANCH_NAME}", "-X", "theirs"]
        if force_sync:
            merge_args.append("--allow-unrelated-histories")

        repo.git.merge(*merge_args)
        repo.git.push("origin", MAIN_BRANCH_NAME, "--force")

        print("成功同步官方仓库！")

    except GitCommandError as e:
        print(f"同步官方仓库失败: {e}")
        if "unrelated histories" in str(e) and not force_sync:
            print("仓库历史记录无关。若要强制同步，请设置 force_sync=True。")
        else:
            print("请检查错误信息并手动同步仓库后重试。")
        exit(1)


def create_github_release(
    plugin_name: str, version: str, repo_url: str, plugin_meta: dict, zip_file: str
) -> None:
    global github_token
    token_owner = get_token_owner(github_token)
    api_url = f"https://api.github.com/repos/{token_owner}/{plugin_name}/releases"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "tag_name": f"v{version}",
        "target_commitish": f"b{version}",
        "name": f"{plugin_name} v{version}",
        "body": plugin_meta.get("description", ""),
        "draft": False,
        "prerelease": False,
    }

    response = requests.post(api_url, json=data, headers=headers)
    if response.status_code == 201:
        print(f"成功创建 GitHub Release: {plugin_name} v{version}")
        release_id = response.json()["id"]

        # 上传 ZIP 文件作为 Release 资产
        upload_url = f"https://uploads.github.com/repos/{token_owner}/{plugin_name}/releases/{release_id}/assets?name={plugin_name}-{version}.zip"
        with open(zip_file, "rb") as f:
            headers["Content-Type"] = "application/zip"
            upload_response = requests.post(upload_url, headers=headers, data=f)
        if upload_response.status_code == 201:
            print(f"成功上传 ZIP 文件: {plugin_name}-{version}.zip")
        else:
            print(f"上传 ZIP 文件失败: {upload_response.text}")
            exit(1)
    else:
        print(f"创建 GitHub Release 失败: {response.text}")
        exit(1)


def do_plugin_changes(repo: Repo, target_dir: str):
    global version, path, plugin_name
    # version_file = os.path.join(target_dir, "version.txt")
    do_version_change(target_dir, version)

    def copy_source_files(source_path, target_path):
        for item in os.listdir(source_path):
            source_item = os.path.join(source_path, item)
            target_item = os.path.join(target_path, item)
            if item == ".git":
                continue
            if os.path.isdir(source_item):
                shutil.copytree(source_item, target_item, dirs_exist_ok=True)
            else:
                shutil.copy2(source_item, target_item)

    copy_source_files(path, target_dir)

    # 打包插件文件
    zip_file = make_archive_with_gitignore(plugin_name, version, path)

    repo.git.add(all=True)
    commit_message = f"Release version {version}"
    repo.git.commit("-m", commit_message)

    try:
        existing_branches = repo.git.branch("-r").split()
        if f"origin/b{version}" in existing_branches:
            print(f"分支 b{version} 已存在于远程仓库，请删除或使用其他版本号")
            exit(1)

        existing_tags = repo.git.tag().split()
        if f"v{version}" in existing_tags:
            print(f"标签 v{version} 已存在于本地仓库，请删除或使用其他版本号")
            exit(1)
    except GitCommandError as e:
        print(f"检查分支或标签时出错: {e}")
        exit(1)

    try:
        repo.git.tag(f"v{version}")
        print(f"创建版本标签: v{version}")
    except GitCommandError as e:
        print(f"创建版本标签失败: {e}")
        exit(1)

    try:
        print("推送插件仓库分支...")
        repo.git.push("--force", "origin", f"b{version}")
    except GitCommandError as e:
        print(f"推送分支失败: {e}")
        exit(1)

    try:
        print("推送插件仓库标签...")
        repo.git.push("--force", "origin", f"refs/tags/v{version}")
    except GitCommandError as e:
        print(f"推送标签失败: {e}")
        exit(1)

    return zip_file


def cleanup(repos: List[Repo], zip_file: str = None):
    for repo in repos:
        try:
            repo.close()
        except Exception as e:
            print(f"关闭仓库时出错: {e}")

    time.sleep(2)

    def on_rm_error(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    for repo in repos:
        temp_repo_path = repo.working_dir
        print(f"删除临时路径: {temp_repo_path}")
        try:
            shutil.rmtree(temp_repo_path, onexc=on_rm_error)
            print("成功删除临时路径.")
        except Exception as e:
            print(f"删除临时路径时出错: {e}")

    temp_dir = Path("temp")
    if temp_dir.exists():
        try:
            shutil.rmtree(temp_dir, onexc=on_rm_error)
            print("成功删除临时打包目录.")
        except Exception as e:
            print(f"删除临时打包目录时出错: {e}")

    if zip_file and os.path.exists(zip_file):
        try:
            os.remove(zip_file)
            print(f"成功删除 ZIP 文件: {zip_file}")
        except Exception as e:
            print(f"删除 ZIP 文件时出错: {e}")


def main():
    def prepare():
        global plugin_name, version, path, github_token, plugin_meta
        path = get_plugin_path()
        plugin_name, version, plugin_meta = get_plugin_info(path)
        if plugin_name is None:
            print("获取插件信息失败，请检查错误信息")
            exit(0)
        print(f"插件名称: {plugin_name}, 版本: {version}")
        if plugin_meta.get("description"):
            print(f"描述: {plugin_meta['description']}")
        if plugin_meta.get("author"):
            print(f"作者: {plugin_meta['author']}")
        if plugin_meta.get("plugin_dependencies"):
            print(f"依赖: {plugin_meta['plugin_dependencies']}")
        github_token = get_github_token(github_token)
        test_github_token(github_token)
        return f"update-{plugin_name}-{version}"

    def setup_plugin_repo() -> Tuple[Repo, str]:
        global github_token
        token_owner = get_token_owner(github_token)

        if not has_existing_repo(token_owner, plugin_name):
            print(f"插件仓库 {plugin_name} 不存在，正在创建...")
            repo_url = create_repo(plugin_name, plugin_meta.get("description", ""))
        else:
            repo_url = f"https://github.com/{token_owner}/{plugin_name}.git"

        try:
            print("正在克隆插件仓库...")
            repo = Repo.clone_from(repo_url, f"temp_repo{time.time()}")
        except GitCommandError as e:
            print(f"克隆仓库失败: {e}")
            exit(1)

        branch_name = f"b{version}"
        try:
            repo.git.checkout(MAIN_BRANCH_NAME)
            repo.git.checkout("-b", branch_name)
            print(f"创建并切换到分支: {branch_name}")
        except GitCommandError as e:
            print(f"创建分支失败: {e}")
            exit(1)

        return repo, os.path.join(repo.working_dir)

    def setup_main_repo() -> Repo:
        global github_token
        token_owner = get_token_owner(github_token)

        if not has_existing_repo(token_owner, MAIN_REPO_NAME):
            print(f"主仓库 {MAIN_REPO_NAME} 不存在，正在从官方仓库 fork...")
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
            time.sleep(2)

        try:
            print("正在克隆主仓库...")
            repo_url = f"https://github.com/{token_owner}/{MAIN_REPO_NAME}.git"
            repo = Repo.clone_from(repo_url, f"temp_main_repo{time.time()}")
        except GitCommandError as e:
            print(f"克隆仓库失败: {e}")
            exit(1)

        sync_with_official_repo(repo)

        branch_name = f"update-{plugin_name}-{version}"
        try:
            repo.git.checkout(MAIN_BRANCH_NAME)
            repo.git.checkout("-b", branch_name)
            print(f"创建并切换到分支: {branch_name}")
        except GitCommandError as e:
            print(f"创建分支失败: {e}")
            exit(1)

        return repo

    def do_main_changes(repo: Repo):
        plugin_repo_url = (
            f"https://github.com/{get_token_owner(github_token)}/{plugin_name}.git"
        )
        plugin_dir = os.path.join("plugins", plugin_name)
        version_branch = f"b{version}"

        try:
            try:
                repo.git.submodule("status", plugin_dir)
                print(f"更新插件 {plugin_name} 的 submodule...")
                repo.git.submodule("deinit", "-f", plugin_dir)
                repo.git.rm("-f", plugin_dir)
                repo.git.submodule(
                    "add", "-b", version_branch, plugin_repo_url, plugin_dir
                )
            except GitCommandError:
                print(f"添加插件 {plugin_name} 作为 submodule...")
                repo.git.submodule(
                    "add", "-b", version_branch, plugin_repo_url, plugin_dir
                )

            repo.git.submodule("update", "--init", "--recursive")

        except GitCommandError as e:
            print(f"添加/更新 submodule 失败: {e}")
            exit(1)

        update_plugin_index(repo, plugin_name, version, plugin_meta)

    def do_pull_requests(
        plugin_repo: Repo, main_repo: Repo, branch_name: str, zip_file: str
    ):
        plugin_repo_url = (
            f"https://github.com/{get_token_owner(github_token)}/{plugin_name}.git"
        )
        create_github_release(
            plugin_name, version, plugin_repo_url, plugin_meta, zip_file
        )

        try:
            print("推送主仓库更改...")
            main_repo.git.checkout(branch_name)
            main_repo.git.push("--force", "origin", branch_name)
            time.sleep(5)
        except GitCommandError as e:
            print(f"推送主仓库更改失败: {e}")
            exit(1)

        create_pull_request(branch_name, plugin_name, version)

    branch_name = prepare()
    plugin_repo, plugin_dir = setup_plugin_repo()
    main_repo = setup_main_repo()

    zip_file = do_plugin_changes(plugin_repo, plugin_dir)
    do_main_changes(main_repo)
    do_pull_requests(plugin_repo, main_repo, branch_name, zip_file)
    cleanup([plugin_repo, main_repo], zip_file)


if __name__ == "__main__":
    main()

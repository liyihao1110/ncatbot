import argparse
import os
import subprocess
import sys
import time
import traceback
from typing import List


ALL_MODULES = [
    # quick_start
    "examples.unified_registry.quick_start.test_basic",
    "examples.unified_registry.quick_start.test_permissions_and_filters",
    "examples.unified_registry.quick_start.test_full_example",
    "examples.unified_registry.quick_start.test_external_funcs",
    # readme
    "examples.unified_registry.test_readme",
    # filters
    "examples.unified_registry.filters.test_builtin_filters",
    "examples.unified_registry.filters.test_combo_filters",
    "examples.unified_registry.filters.test_custom_filters",
    "examples.unified_registry.filters.test_level_and_cooldown",
    # params
    "examples.unified_registry.params.test_basic_syntax",
    "examples.unified_registry.params.test_options_and_named",
    "examples.unified_registry.params.test_types_and_errors",
    "examples.unified_registry.params.test_media_and_advanced",
    # commands
    "examples.unified_registry.commands.test_basic_and_alias",
    "examples.unified_registry.commands.test_external_command",
    "examples.unified_registry.commands.test_groups",
    "examples.unified_registry.commands.test_complex",
    # cases
    "examples.unified_registry.cases.test_qa_bot",
    "examples.unified_registry.cases.test_group_management",
    "examples.unified_registry.cases.test_info_query",
    "examples.unified_registry.cases.test_data_processing",
    "examples.unified_registry.cases.test_web_api",
]


def ensure_project_root():
    """Warn if current working directory doesn't look like project root (pyproject.toml missing)."""
    cwd = os.getcwd()
    marker = os.path.join(cwd, "pyproject.toml")
    if not os.path.exists(marker):
        print(
            "[WARN] 未在当前工作目录发现 pyproject.toml，建议在项目根目录运行：python -m examples.run_test",
            file=sys.stderr,
        )


def run_one(module: str, verbose: bool = False):
    """在新进程中执行 `python -m <module>` 并捕获输出。"""
    start = time.perf_counter()
    try:
        completed = subprocess.run(
            [sys.executable, "-m", module],
            text=True,
            check=False,  # 我们自己判断返回值
        )
        error = None
        if completed.returncode not in (0, None):
            error = RuntimeError(f"模块以非零退出码退出: {completed.returncode}")
    except Exception as e:  # noqa: BLE001
        error = e
        completed = None  # 异常时无结果

    elapsed = time.perf_counter() - start
    out = completed.stdout if completed else ""
    err = completed.stderr if completed else ""
    if verbose:
        print(out, end="")
        print(err, end="", file=sys.stderr)

    return {
        "name": module,
        "ok": error is None,
        "elapsed": elapsed,
        "stdout": out,
        "stderr": err,
        "error": error,
        "trace": traceback.format_exc() if error else "",
    }


def main(argv: List[str] = None) -> int:
    ensure_project_root()
    parser = argparse.ArgumentParser(
        description="一键运行 UnifiedRegistry 文档验证示例"
    )
    parser.add_argument(
        "--only",
        nargs="*",
        help="仅运行指定模块（完整模块路径或包含关键字的子串，支持多值）",
    )
    parser.add_argument(
        "--skip",
        nargs="*",
        help="跳过指定模块（完整模块路径或包含关键字的子串，支持多值）",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="首个失败即停止",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="打印各模块完整输出",
    )
    args = parser.parse_args(argv)

    selected = list(ALL_MODULES)
    if args.only:
        keys = [k.lower() for k in args.only]
        selected = [m for m in selected if any(k in m.lower() or m == k for k in keys)]
    if args.skip:
        keys = [k.lower() for k in args.skip]
        selected = [
            m for m in selected if not any(k in m.lower() or m == k for k in keys)
        ]

    total = len(selected)
    print(f"将运行 {total} 个模块…\n")

    results = []
    failures = 0
    start_all = time.perf_counter()
    for idx, mod in enumerate(selected, 1):
        print(f"[{idx:02d}/{total:02d}] 运行 {mod} …", flush=True)
        res = run_one(mod, verbose=args.verbose)
        results.append(res)
        status = "PASS" if res["ok"] else "FAIL"
        print(f"→ {status} ({res['elapsed']:.2f}s)\n")
        if not res["ok"]:
            failures += 1
            if not args.verbose:
                # Show brief error now
                print(f"[错误] {mod}: {res['error']}")
            if args.fail_fast:
                break

    elapsed_all = time.perf_counter() - start_all

    # Summary
    print("=" * 72)
    print("汇总结果")
    print(
        f"总计: {len(results)}, 通过: {len(results) - failures}, 失败: {failures}, 用时: {elapsed_all:.2f}s"
    )
    if failures:
        print("\n失败详情：")
        for res in results:
            if res["ok"]:
                continue
            print("-" * 72)
            print(f"模块: {res['name']}")
            print(f"错误: {res['error']}")
            print(f"重新运行: {str(sys.executable)} -m {res['name']}")
            if res["stderr"].strip():
                print("[stderr]")
                print(res["stderr"].rstrip())
            # 限制 stdout 的体量，避免刷屏
            if res["stdout"].strip():
                preview = res["stdout"].splitlines()
                head = "\n".join(preview[:50])
                tail = "\n".join(preview[-10:]) if len(preview) > 50 else ""
                print("[stdout|前50行]")
                print(head)
                if tail:
                    print("… …")
                    print("[stdout|末10行]")
                    print(tail)

    # Non-zero exit code if any failure
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

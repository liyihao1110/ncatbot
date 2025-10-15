from pathlib import Path
import sys

project_root = Path(__file__).parent.parent  # 因为当前在 examples/ 下
sys.path.insert(0, str(project_root))

from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system import (
    StringTokenizer as t,
)

print(t("a = -1 --").tokenize())
print(t("-= -1 -- ").tokenize())
print(t("--==").tokenize())
print(t("--a=1").tokenize())
print(t('"asdasd').tokenize())

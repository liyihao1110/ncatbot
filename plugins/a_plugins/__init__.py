import sys
from pathlib import Path
# 动态添加项目根目录到 sys.path
sys.path.append(str( Path(__file__).resolve().parents[2]))

from .main import Test

sys.path.pop(-1)
__all__ = [
    'Test'
    ]
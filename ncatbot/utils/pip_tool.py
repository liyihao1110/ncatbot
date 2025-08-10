import subprocess
import json
from typing import List, Dict

class PipTool:
    """简单的pip包管理工具"""
    
    def list_installed(self) -> List[Dict[str, str]]:
        """获取已安装的包列表
        
        Returns:
            List[Dict[str, str]]: 包含包信息的字典列表，每个字典包含name和version
        """
        try:
            output = subprocess.check_output(['pip', 'list', '--format=json']).decode()
            return json.loads(output)
        except:
            return []
            
    def install(self, package: str) -> bool:
        """安装指定的包
        
        Args:
            package (str): 包名称，可以包含版本约束
            
        Returns:
            bool: 安装是否成功
        """
        try:
            subprocess.check_call(['pip', 'install', package])
            return True
        except:
            return False

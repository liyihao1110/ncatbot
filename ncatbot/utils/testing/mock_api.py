# 创建 ncatbot/utils/testing/mock_api.py
from typing import Dict, List, Tuple, Any, Callable, Union
from ncatbot.utils import get_log

LOG = get_log("MockAPIAdapter")


class MockAPIAdapter:
    """模拟 API 适配器"""

    def __init__(self):
        self.call_history: List[Tuple[str, Dict]] = []
        self.response_rules: Dict[str, Any] = {}
        self.message_id_counter = 1000000
        self.default_responses = {
            "/send_group_msg": lambda ep, data: {
                "retcode": 0,
                "data": {"message_id": self._generate_message_id()},
            },
            "/send_private_msg": lambda ep, data: {
                "retcode": 0,
                "data": {"message_id": self._generate_message_id()},
            },
            "/delete_msg": {"retcode": 0, "data": {}},
            "/get_login_info": {
                "retcode": 0,
                "data": {"user_id": "123456789", "nickname": "TestBot"},
            },
            "/get_group_info": {
                "retcode": 0,
                "data": {
                    "group_id": "123456789",
                    "group_name": "测试群",
                    "member_count": 10,
                },
            },
            "/get_group_member_info": {
                "retcode": 0,
                "data": {
                    "user_id": "987654321",
                    "nickname": "TestUser",
                    "role": "member",
                },
            },
        }

    def _generate_message_id(self) -> str:
        """生成消息 ID"""
        self.message_id_counter += 1
        return str(self.message_id_counter)

    async def mock_callback(self, endpoint: str, data: Dict) -> Dict:
        """模拟 API 回调"""
        # 记录调用
        self.call_history.append((endpoint, data.copy()))

        # 使用 LOG 输出调用参数
        LOG.info(f"API 调用: {endpoint}")
        LOG.info(f"调用参数: {data}")

        # 返回预设响应或默认响应
        if endpoint in self.response_rules:
            response = self.response_rules[endpoint]
            if callable(response):
                return response(endpoint, data)
            return response.copy() if isinstance(response, dict) else response

        default_response = self.default_responses.get(
            endpoint, {"retcode": 0, "data": {}}
        )
        if callable(default_response):
            return default_response(endpoint, data)
        return (
            default_response.copy()
            if isinstance(default_response, dict)
            else default_response
        )

    def set_response(self, endpoint: str, response: Union[Dict, Callable]):
        """设置特定端点的响应

        Args:
            endpoint: API 端点
            response: 响应数据或生成响应的函数
        """
        self.response_rules[endpoint] = response

    def get_call_history(self) -> List[Tuple[str, Dict]]:
        """获取调用历史"""
        return self.call_history.copy()

    def get_calls_for_endpoint(self, endpoint: str) -> List[Dict]:
        """获取特定端点的调用记录"""
        return [data for ep, data in self.call_history if ep == endpoint]

    def clear_call_history(self):
        """清空调用历史"""
        self.call_history.clear()

    def assert_called_with(self, endpoint: str, expected_data: Dict):
        """断言特定调用"""
        calls = self.get_calls_for_endpoint(endpoint)
        assert calls, f"端点 {endpoint} 未被调用"

        for call_data in calls:
            if self._match_call_data(call_data, expected_data):
                return True

        raise AssertionError(f"端点 {endpoint} 未使用预期数据调用: {expected_data}")

    def _match_call_data(self, actual: Dict, expected: Dict) -> bool:
        """匹配调用数据"""
        for key, value in expected.items():
            if key not in actual or actual[key] != value:
                return False
        return True

    def get_call_count(self, endpoint: str) -> int:
        """获取特定端点的调用次数"""
        return len(self.get_calls_for_endpoint(endpoint))

# 贡献指南
欢迎参与ncatbot项目！我们致力于打造一个友好的开源社区，以下是参与贡献的规范流程。
## 📌 开始之前
1. 确认项目采用 
2. 阅读 [项目文档](README.md)
3. 加入开发者交流群：`201487478`
## 🌱 开发流程
### 分支管理
```bash
git clone https://github.com/liyihao1110/ncatbot
git checkout -b feat/Function-development  # 功能开发分支
# 或
git checkout -b fix/issue-fix         # 问题修复分支
```
### 提交规范
采用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：
```bash
git commit -m "feat: 添加消息撤回功能"
git commit -m "fix(api): 修复消息队列溢出问题 #123"
git commit -m "docs: 更新安装指南"
```
### Pull Request
1. 推送分支到远程仓库
2. 在Github创建Pull Request
3. 关联相关Issue（如 `#123`）
4. 通过CI测试后等待审核
## 🧪 测试要求(待更新...)[tests文件夹未更新]
所有代码修改必须通过测试：
```bash
# 运行单元测试
pytest tests/
# 检查代码风格
flake8 ncatbot_sync/
# 验证类型提示
mypy ncatbot_sync/
```
## 🖋 代码规范
1. 遵循 PEP8 规范
2. 类型提示强制要求：
```python
def send_message(content: str, group_id: int) -> MessageResult:
    ...
```
3. 文档字符串标准：
```python
def handle_event(event: Event):
    """处理机器人事件
    Args:
        event: 继承自BaseEvent的事件对象
    Returns:
        无返回值，可能产生副作用
    """
```
## 📚 文档贡献
1. 模块文档需包含使用示例
2. 中文文档在 `/docs/zh` 目录
3. 英文文档在 `/docs/en` 目录（如果你愿意的话）
4. 使用Markdown格式编写
## 🐛 Issue规范
提交问题请包含：
```markdown
## 环境信息
- 系统版本：Windows 11 22H2
- Python版本：3.10.6
- 框架版本：v0.2.1
- 项目版本：v0.0.1
## 重现步骤
1. 调用API发送图片
2. 连续发送10次请求
3. 观察控制台输出
## 预期行为
正常返回消息ID
## 实际行为
抛出ConnectionError异常
```
## 💡 新功能提案
提交提案需包含：
1. 功能使用场景
2. 建议的API设计
3. 与其他模块的兼容性分析
## 🚫 行为准则
1. 禁止提交恶意代码
2. 讨论时保持专业态度
3. 尊重不同技术选择
4. 及时响应代码审查意见
## 🙌 鸣谢
所有贡献者将加入贡献者名单，重大贡献者授予Committer角色。
## 📜 版本发布
在开发者交流群内通知所有成员后全员同意后进行版本发布,违者将被踢出开发者
## 📜 额外信息
1. 在不确定是否可用的情况下,请对源文件进行备份,备份目录定位于`/resources`文件夹
2. 请不要提交任何非必要的文件,如`.idea`,`__pycache__`等
3. 该文件可能会持续更新,请定期查看
class Sentence(str):
    """继承自 str 的句子类型，用于参数解析时捕获完整句子（包含空格）

    与普通 str 的区别：
    - str: 在参数解析时按空格分割，每次只取一个单词
    - Sentence: 在参数解析时取整个 Text 消息段的完整内容

    由于继承自 str，支持所有字符串操作
    """

    def __new__(cls, text: str):
        return super().__new__(cls, text)

    def __repr__(self):
        return f"Sentence('{str(self)}')"

from ncatbot.core.event.message_segment import MessageArray, Node, Image, Text, Forward, Node, File, Video

class ForwardConstructor:
    def __init__(self, user_id: str="123456", nickname: str="QQ用户", content: list[Node]=None):
        self.user_id = user_id
        self.nickname = nickname
        self.content = content if content else []

    def attach(self, content: MessageArray, user_id: str=None, nickname: str=None):
        if user_id is not None:
            self.user_id = user_id
        if nickname is not None:
            self.nickname = nickname
        self.content.append(Node(user_id=self.user_id, nickname=self.nickname, content=content))

    def attach_text(self, text: str, user_id: str=None, nickname: str=None):
        self.attach(MessageArray(Text(text)), user_id, nickname)
        
    def attach_image(self, image: str, user_id: str=None, nickname: str=None):
        self.attach(MessageArray(Image(image)), user_id, nickname)
        
    def attach_file(self, file: str, user_id: str=None, nickname: str=None):
        self.attach(MessageArray(File(file)), user_id, nickname)
    
    def attach_viedo(self, video: str, user_id: str=None, nickname: str=None):
        self.attach(MessageArray(Video(video)), user_id, nickname)
    
    def attach_forward(self, forward: Forward, user_id: str=None, nickname: str=None):
        self.attach(MessageArray(forward), user_id, nickname)
    
    def to_forward(self) -> Forward:
        return Forward(content=self.content)
    
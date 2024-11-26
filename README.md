
![ncatbot](https://github.com/user-attachments/assets/b22bc036-3945-40ba-a093-3ea62855e397)

[![Language](https://img.shields.io/badge/language-python-green.svg?style=plastic)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg?style=plastic)](https://github.com/liyihao1110/NcatBot/blob/master/LICENSE)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![PyPI](https://img.shields.io/pypi/v/NcatBot)

---
### NcatBot

基于Napcat，参考qqbotpy项目格式的PythonSDK👻

待更新...
欢迎大家来pr👋

如果你觉得本项目不错，请帮忙点个star✨

### 介绍
✨ 基于 NapcatQQ API 实现的机器人框架 ✨

✨ 参考 qqbotpy 项目架构实现，希望更多开发者们贡献这个项目 ✨

### 实现进度
- [x] 群聊私聊监听
- [x] 各类消息注册
- [x] 各类消息发送
- [x] 各类接口的定义与测试
- [x] windows发送markdown
- [x] 添加了各类设置登录号的接口
- [ ] 不知道自己还做了什么...

### 帮助文档
1. [下载NapCat](https://github.com/NapNeko/NapCatQQ/releases) 找到 **NapCat.Shell.zip** 并解压
2. 启动NapCat：
   1. 第一次启动机器人：直接双击 **launcher.bat** 文件
   2. 启动已经扫码登录过的机器人，当前目录地址栏输入 **cmd** 或右击打开命令行，在当前目录打开 **cmd** 命令行，输入 **start launcher.bat \[你的QQ号\]**
3. 部分使用参考代码可查看main.py
4. **example** 文件夹里是每个经过测试的 **api** 类别例子，没有标注其他情况的是完全执行成功过的，可以使用异步正常插入代码中
5. 每个 **api** 提供了有限帮助支持（在编辑器里按住 <kbd>Ctrl</kbd> 并单击 **api** 方法即可跳转）
6. 部分教程可查看[NapCatQQ开发机器人PythonSDK](https://blog.csdn.net/qq_71745595/article/details/143988362)
7. 如果可以，希望你可以帮助完善😀

### 接口速查
#### 用户类
需求|API
-:|:-
设置账号信息|set_qq_profile
获取推荐好友/群聊卡片|ark_share_peer
获取推荐群聊卡片|ark_share_group
设置在线状态|set_online_status
获取好友分组列表|get_friends_with_category
设置头像|set_qq_avatar
点赞|send_like
创建收藏|create_collection
处理好友请求|set_friend_add_request
设置个性签名|set_self_longnick
获取账号信息|get_stranger_info
获取好友列表|get_friend_list
获取点赞列表|get_profile_like
获取收藏表情|fetch_custom_face
上传私聊文件|upload_private_file
删除好友|delete_friend
~~获取用户状态~~|~~nc_get_user_status~~
~~获取小程序卡片~~|~~get_mini_app_ark~~

#### 消息类
需求|API
-:|:-
设置消息已读|mark_msg_as_read
设置群聊已读|mark_group_msg_as_read
设置私聊已读|mark_private_msg_as_read
_设置所有消息已读|mark_all_as_read
撤回消息|delete_msg
获取消息详情|get_msg
获取图片消息详情|get_image
获取语音消息详情|get_record
获取文件信息|get_file
获取群历史消息|get_group_msg_history
贴表情|set_msg_emoji_like
获取好友历史消息|get_friend_msg_history
最近消息列表|get_recent_contact
获取贴表情详情|fetch_emoji_like
获取合并转发消息|get_forward_msg
~~发送合并转发消息~~|~~send_forward_msg~~

#### 群聊类
需求|API
-:|:-
群踢人|set_group_kick
群禁言|set_group_ban
获取群系统消息|get_group_system_msg
获取群精华消息|get_essence_msg_list
全体禁言|set_group_whole_ban
设置群头像|set_group_portrait
设置群管理|set_group_admin
~~设置群精华消息~~|~~set_essence_msg~~
设置群成员名片|set_group_card
删除群精华消息|delete_essence_msg
设置群名|set_group_name
退群|set_group_leave
_发送群公告|send_group_notice
_获取群公告|get_group_notice
~~设置群头衔~~|~~set_group_special_title~~
上传群文件|upload_group_file
处理加群请求|set_group_add_request
获取群信息|get_group_info
获取群信息ex|get_group_info_ex
创建群文件文件夹|create_group_file_folder
删除群文件|delete_group_file
删除群文件夹|delete_group_folder
获取群文件系统信息|get_group_file_system_info
获取群根目录文件列表|get_group_root_files
获取群子目录文件列表|get_group_files_by_folder
~~获取群文件资源链接~~|~~get_group_file_url~~
获取群列表|get_group_list
获取群成员信息|get_group_member_info
获取群成员列表|get_group_member_list
获取群荣誉|get_group_honor_info
获取群 @全体成员 剩余次数|get_group_at_all_remain
获取群过滤系统消息|get_group_ignored_notifies
~~设置群打卡~~|~~set_group_sign~~
~~发送群打卡~~|~~send_group_sign~~
~~获取AI语音人物~~|~~get_ai_characters~~
~~发送群AI语音~~|~~send_group_ai_record~~
~~获取AI语音~~|~~get_ai_record~~

#### 系统类
需求|API
-:|:-
获取当前账号在线客户端列表|get_online_clients
获取机器人账号范围|get_robot_uin_range
OCR 图片识别|ocr_image
英译中|translate_en2zh
获取登录号信息|get_login_info
设置输入状态|set_input_status
下载文件到缓存目录|download_file
获取cookies|get_cookies
获取 CSRF Token|get_csrf_token
_删除群公告|del_group_notice
获取 QQ 相关接口凭证|get_credentials
_获取在线机型|get_model_show
_设置在线机型|set_model_show
检查是否可以发送图片|can_send_image
获取packet状态|nc_get_packet_status
检查是否可以发送语音|can_send_record
获取状态|get_status
获取rkey|nc_get_rkey
获取版本信息|get_version_info
~~获取群禁言列表~~|~~get_group_shut_list~~

#### 消息链
需求|API
-:|:-
添加消息id|add_id
发送群消息|send_group_msg
发送私聊消息|send_private_msg
添加文本|add_text
添加小表情|add_face
添加媒体|add_media
添加图片|add_image
添加语音|add_record
添加视频|add_video
添加@某人|add_at
超级表情——猜拳|rps
超级表情——骰子|dice
音乐分享|music
添加引用|add_reply
添加json|add_json
添加文件|add_file
添加markdown|add_markdown
清除消息链|clear

### 欢迎交流开发，贡献者们

👋欢迎加入 [学习QQ群](https://qm.qq.com/q/dRTyqlFCRG) ！

🔗[微信公众号](https://mp.weixin.qq.com/s/8i-AoSQFf0nXJRRJLrPxLQ)

### 致谢

感谢 [NapCatQQ](https://github.com/NapNeko/NapCatQQ)

### 想要更多的Star⭐


[![Star History Chart](https://api.star-history.com/svg?repos=NcatBot/NcatBot&type=Date)](https://star-history.com/#NcatBot/NcatBot&Date)


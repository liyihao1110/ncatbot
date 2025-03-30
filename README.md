# NcatBot

---

![img.png](https://socialify.git.ci/liyihao1110/NcatBot/image?description=1&forks=1&issues=1&language=1&logo=https%3A%2F%2Fdocs.ncatbot.xyz%2Fimages%2Flogo.png&name=1&owner=1&pulls=1&stargazers=1&theme=Auto)

<h2 align="center">基于 NapCat 的 QQ 机器人 Python 快速开发框架 (SDK)</h2>
<p align="center">
 <a href="https://pypi.org/project/ncatbot/"><img src="https://img.shields.io/pypi/v/ncatbot"></a>
  <a><img src="https://img.shields.io/badge/License-NcatBot License-green.svg"></a>
    <a href="https://qm.qq.com/q/CHbzJ2LH4k"><img src="https://img.shields.io/badge/官方群聊-201487478-brightgreen.svg"></a>
    <a href="https://qm.qq.com/q/CHbzJ2LH4k"><img src="https://img.shields.io/badge/官方频道-pd63222487-brightgreen.svg"></a>
    <a href="https://qm.qq.com/q/S2zIli2qsu"><img src="https://img.shields.io/badge/基于ncatbot开发的小机器人-3786498591-brightgreen.svg"></a>
    <a href="https://ippclub.org"><img src="https://img.shields.io/badge/I%2B%2B%E4%BF%B1%E4%B9%90%E9%83%A8-%E8%AE%A4%E8%AF%81-11A7E2?logo=data%3Aimage%2Fsvg%2Bxml%3Bcharset%3Dutf-8%3Bbase64%2CPHN2ZyB2aWV3Qm94PSIwIDAgMjg4IDI3NCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWw6c3BhY2U9InByZXNlcnZlIiBzdHlsZT0iZmlsbC1ydWxlOmV2ZW5vZGQ7Y2xpcC1ydWxlOmV2ZW5vZGQ7c3Ryb2tlLWxpbmVqb2luOnJvdW5kO3N0cm9rZS1taXRlcmxpbWl0OjIiPjxwYXRoIGQ9Im0xNDYgMzEgNzIgNTVWMzFoLTcyWiIgc3R5bGU9ImZpbGw6I2Y2YTgwNjtmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Im0xNjkgODYtMjMtNTUgNzIgNTVoLTQ5WiIgc3R5bGU9ImZpbGw6I2VmN2EwMDtmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Ik0yNiAzMXY1NWg4MEw4MSAzMUgyNloiIHN0eWxlPSJmaWxsOiMwN2ExN2M7ZmlsbC1ydWxlOm5vbnplcm8iLz48cGF0aCBkPSJNMTA4IDkydjExMmwzMS00OC0zMS02NFoiIHN0eWxlPSJmaWxsOiNkZTAwNWQ7ZmlsbC1ydWxlOm5vbnplcm8iLz48cGF0aCBkPSJNMCAyNzR2LTUyaDk3bC0zMyA1MkgwWiIgc3R5bGU9ImZpbGw6I2Y2YTgwNjtmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Im03NyAyNzQgNjctMTA3djEwN0g3N1oiIHN0eWxlPSJmaWxsOiNkZjI0MzM7ZmlsbC1ydWxlOm5vbnplcm8iLz48cGF0aCBkPSJNMTUyIDI3NGgyOWwtMjktNTN2NTNaIiBzdHlsZT0iZmlsbDojMzM0ODVkO2ZpbGwtcnVsZTpub256ZXJvIi8%2BPHBhdGggZD0iTTE5MSAyNzRoNzl2LTUySDE2N2wyNCA1MloiIHN0eWxlPSJmaWxsOiM0ZTI3NWE7ZmlsbC1ydWxlOm5vbnplcm8iLz48cGF0aCBkPSJNMjg4IDEwMGgtMTdWODVoLTEzdjE1aC0xN3YxM2gxN3YxNmgxM3YtMTZoMTd2LTEzWiIgc3R5bGU9ImZpbGw6I2M1MTgxZjtmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Im0yNiA4NiA1Ni01NUgyNnY1NVoiIHN0eWxlPSJmaWxsOiMzMzQ4NWQ7ZmlsbC1ydWxlOm5vbnplcm8iLz48cGF0aCBkPSJNOTMgMzFoNDJsLTMwIDI5LTEyLTI5WiIgc3R5bGU9ImZpbGw6IzExYTdlMjtmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Ik0xNTggMTc2Vjg2bC0zNCAxNCAzNCA3NloiIHN0eWxlPSJmaWxsOiMwMDU5OGU7ZmlsbC1ydWxlOm5vbnplcm8iLz48cGF0aCBkPSJtMTA2IDU5IDQxLTEtMTItMjgtMjkgMjlaIiBzdHlsZT0iZmlsbDojMDU3Y2I3O2ZpbGwtcnVsZTpub256ZXJvIi8%2BPHBhdGggZD0ibTEyNCAxMDAgMjItNDEgMTIgMjctMzQgMTRaIiBzdHlsZT0iZmlsbDojNGUyNzVhO2ZpbGwtcnVsZTpub256ZXJvIi8%2BPHBhdGggZD0ibTEwNiA2MCA0MS0xLTIzIDQxLTE4LTQwWiIgc3R5bGU9ImZpbGw6IzdiMTI4NTtmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Im0xMDggMjA0IDMxLTQ4aC0zMXY0OFoiIHN0eWxlPSJmaWxsOiNiYTAwNzc7ZmlsbC1ydWxlOm5vbnplcm8iLz48cGF0aCBkPSJtNjUgMjc0IDMzLTUySDBsNjUgNTJaIiBzdHlsZT0iZmlsbDojZWY3YTAwO2ZpbGwtcnVsZTpub256ZXJvIi8%2BPHBhdGggZD0iTTc3IDI3NGg2N2wtNDAtNDUtMjcgNDVaIiBzdHlsZT0iZmlsbDojYTgxZTI0O2ZpbGwtcnVsZTpub256ZXJvIi8%2BPHBhdGggZD0iTTE2NyAyMjJoNThsLTM0IDUyLTI0LTUyWiIgc3R5bGU9ImZpbGw6IzExYTdlMjtmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Im0yNzAgMjc0LTQ0LTUyLTM1IDUyaDc5WiIgc3R5bGU9ImZpbGw6IzA1N2NiNztmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Ik0yNzUgNTVoLTU3VjBoMjV2MzFoMzJ2MjRaIiBzdHlsZT0iZmlsbDojZGUwMDVkO2ZpbGwtcnVsZTpub256ZXJvIi8%2BPHBhdGggZD0iTTE4NSAzMWg1N3Y1NWgtMjVWNTVoLTMyVjMxWiIgc3R5bGU9ImZpbGw6I2M1MTgxZjtmaWxsLXJ1bGU6bm9uemVybyIvPjwvc3ZnPg%3D%3D&labelColor=fff"></a>
</p>

NcatBot 是 **[NapCat](https://github.com/NapNeko/NapCatQQ)** 的 Python SDK, 它提供了一套方便易用的 Python 接口用于开发基于 NapCat 的项目——也就是 QQ 机器人.

## 如何使用

### 使用限制

- **严禁将本项目以任何形式用于传播 反动、暴力、淫秽 信息，违者将追究法律责任**.
- 将本项目以**任何形式**用于**盈利性用途**时，必须取得项目开发组(本仓库 Collaborators 和 Owner)的**书面授权**.

### 用户使用

针对没有计算机基础的用户群体, 可以直接下载我们的**一键安装包**安装 NcatBot 运行时环境, 并使用他人发布的插件.

[阅读有关文档了解更多](https://docs.ncatbot.xyz/guide/onestepi/).

### 开发者使用

请**认真阅读**[文档](https://docs.ncatbot.xyz/). 文档中包含详细的**开发指南**和**示例项目及其解析**.

[插件仓库地址](https://github.com/ncatbot/NcatBot-Plugins).

## 更新进度

---

[![木子/ncatbot](https://gitee.com/li-yihao0328/nc_bot/widgets/widget_card.svg?colors=ffffff,1e252b,323d47,455059,d7deea,99a0ae)](https://gitee.com/li-yihao0328/nc_bot)

## 欢迎来玩

[是 QQ 群哦喵~](https://qm.qq.com/q/L6XGXYqL86)

## 获取帮助

- 遇到任何困难时, 请先按照以下顺序尝试自己解决:

  1. **仔细阅读**[文档](https://docs.ncatbot.xyz/).
  2. 询问 [DeepSeek](https://chat.deepseek.com), [Kimi](https://kimi.ai) 等人工智能.
  3. 搜索本项目的 [Issue 列表](https://github.com/liyihao1110/ncatbot/issues).
- 如果以上方法都无法解决你的问题, 那么:

  也可以[进群](https://qm.qq.com/q/L6XGXYqL86)提问.

## 联系我们

作者: [最可爱的木子喵~](https://gitee.com/li-yihao0328)

邮箱: <lyh_02@foxmail.com>

## 贡献者们

---

<a href="https://github.com/liyihao1110/ncatbot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=liyihao1110/ncatbot" />
</a>

如果你有好的 Idea, 欢迎提 Issue 和 PR!

## 致谢

---

感谢 [NapCat](https://github.com/NapNeko/NapCatQQ) 提供底层接口.

感谢 [IppClub](https://github.com/IppClub) 的宣传支持.

感谢 [Fcatbot](https://github.com/Fish-LP/Fcatbot) 提供代码和灵感.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=liyihao1110/ncatbot&type=Date)](https://www.star-history.com/#liyihao1110/ncatbot&Date)


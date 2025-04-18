<div align="center">

# 🚀 ncatbot

---

![logo.png](https://socialify.git.ci/liyihao1110/NcatBot/image?custom_description=ncatbot+%EF%BC%8C%E5%9F%BA%E4%BA%8E+%E5%8D%8F%E8%AE%AE+%E7%9A%84+QQ+%E6%9C%BA%E5%99%A8%E4%BA%BA+Python+SDK%EF%BC%8C%E5%BF%AB%E9%80%9F%E5%BC%80%E5%8F%91%EF%BC%8C%E8%BD%BB%E6%9D%BE%E9%83%A8%E7%BD%B2%E3%80%82&description=1&font=Jost&forks=1&issues=1&logo=https%3A%2F%2Fimg.remit.ee%2Fapi%2Ffile%2FAgACAgUAAyEGAASHRsPbAAO9Z_FYKczZ5dly9IKmC93J_sF7qRUAAmXEMRtA2ohX1eSKajqfARABAAMCAAN5AAM2BA.jpg&pattern=Signal&pulls=1&stargazers=1&theme=Auto)

 <a href="https://pypi.org/project/ncatbot/"><img src="https://img.shields.io/pypi/v/ncatbot"></a>
 [![OneBot v11](https://img.shields.io/badge/OneBot-v11-black.svg)](https://github.com/botuniverse/onebot)
 [![访问量统计](https://visitor-badge.laobi.icu/badge?page_id=li-yihao0328.ncatbot_sync)](https://github.com/liyihao1110/ncatbot)
  <a><img src="https://img.shields.io/badge/License-NcatBot License-green.svg"></a>
    <a href="https://qm.qq.com/q/CHbzJ2LH4k"><img src="https://img.shields.io/badge/官方群聊-201487478-brightgreen.svg"></a>
    <a href="https://qm.qq.com/q/CHbzJ2LH4k"><img src="https://img.shields.io/badge/官方频道-pd63222487-brightgreen.svg"></a>
    <a href="https://ippclub.org"><img src="https://img.shields.io/badge/I%2B%2B%E4%BF%B1%E4%B9%90%E9%83%A8-%E8%AE%A4%E8%AF%81-11A7E2?logo=data%3Aimage%2Fsvg%2Bxml%3Bcharset%3Dutf-8%3Bbase64%2CPHN2ZyB2aWV3Qm94PSIwIDAgMjg4IDI3NCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWw6c3BhY2U9InByZXNlcnZlIiBzdHlsZT0iZmlsbC1ydWxlOmV2ZW5vZGQ7Y2xpcC1ydWxlOmV2ZW5vZGQ7c3Ryb2tlLWxpbmVqb2luOnJvdW5kO3N0cm9rZS1taXRlcmxpbWl0OjIiPjxwYXRoIGQ9Im0xNDYgMzEgNzIgNTVWMzFoLTcyWiIgc3R5bGU9ImZpbGw6I2Y2YTgwNjtmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Im0xNjkgODYtMjMtNTUgNzIgNTVoLTQ5WiIgc3R5bGU9ImZpbGw6I2VmN2EwMDtmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Ik0yNiAzMXY1NWg4MEw4MSAzMUgyNloiIHN0eWxlPSJmaWxsOiMwN2ExN2M7ZmlsbC1ydWxlOm5vbnplcm8iLz48cGF0aCBkPSJNMTA4IDkydjExMmwzMS00OC0zMS02NFoiIHN0eWxlPSJmaWxsOiNkZTAwNWQ7ZmlsbC1ydWxlOm5vbnplcm8iLz48cGF0aCBkPSJNMCAyNzR2LTUyaDk3bC0zMyA1MkgwWiIgc3R5bGU9ImZpbGw6I2Y2YTgwNjtmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Im03NyAyNzQgNjctMTA3djEwN0g3N1oiIHN0eWxlPSJmaWxsOiNkZjI0MzM7ZmlsbC1ydWxlOm5vbnplcm8iLz48cGF0aCBkPSJNMTUyIDI3NGgyOWwtMjktNTN2NTNaIiBzdHlsZT0iZmlsbDojMzM0ODVkO2ZpbGwtcnVsZTpub256ZXJvIi8%2BPHBhdGggZD0iTTE5MSAyNzRoNzl2LTUySDE2N2wyNCA1MloiIHN0eWxlPSJmaWxsOiM0ZTI3NWE7ZmlsbC1ydWxlOm5vbnplcm8iLz48cGF0aCBkPSJNMjg4IDEwMGgtMTdWODVoLTEzdjE1aC0xN3YxM2gxN3YxNmgxM3YtMTZoMTd2LTEzWiIgc3R5bGU9ImZpbGw6I2M1MTgxZjtmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Im0yNiA4NiA1Ni01NUgyNnY1NVoiIHN0eWxlPSJmaWxsOiMzMzQ4NWQ7ZmlsbC1ydWxlOm5vbnplcm8iLz48cGF0aCBkPSJNOTMgMzFoNDJsLTMwIDI5LTEyLTI5WiIgc3R5bGU9ImZpbGw6IzExYTdlMjtmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Ik0xNTggMTc2Vjg2bC0zNCAxNCAzNCA3NloiIHN0eWxlPSJmaWxsOiMwMDU5OGU7ZmlsbC1ydWxlOm5vbnplcm8iLz48cGF0aCBkPSJtMTA2IDU5IDQxLTEtMTItMjgtMjkgMjlaIiBzdHlsZT0iZmlsbDojMDU3Y2I3O2ZpbGwtcnVsZTpub256ZXJvIi8%2BPHBhdGggZD0ibTEyNCAxMDAgMjItNDEgMTIgMjctMzQgMTRaIiBzdHlsZT0iZmlsbDojNGUyNzVhO2ZpbGwtcnVsZTpub256ZXJvIi8%2BPHBhdGggZD0ibTEwNiA2MCA0MS0xLTIzIDQxLTE4LTQwWiIgc3R5bGU9ImZpbGw6IzdiMTI4NTtmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Im0xMDggMjA0IDMxLTQ4aC0zMXY0OFoiIHN0eWxlPSJmaWxsOiNiYTAwNzc7ZmlsbC1ydWxlOm5vbnplcm8iLz48cGF0aCBkPSJtNjUgMjc0IDMzLTUySDBsNjUgNTJaIiBzdHlsZT0iZmlsbDojZWY3YTAwO2ZpbGwtcnVsZTpub256ZXJvIi8%2BPHBhdGggZD0iTTc3IDI3NGg2N2wtNDAtNDUtMjcgNDVaIiBzdHlsZT0iZmlsbDojYTgxZTI0O2ZpbGwtcnVsZTpub256ZXJvIi8%2BPHBhdGggZD0iTTE2NyAyMjJoNThsLTM0IDUyLTI0LTUyWiIgc3R5bGU9ImZpbGw6IzExYTdlMjtmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Im0yNzAgMjc0LTQ0LTUyLTM1IDUyaDc5WiIgc3R5bGU9ImZpbGw6IzA1N2NiNztmaWxsLXJ1bGU6bm9uemVybyIvPjxwYXRoIGQ9Ik0yNzUgNTVoLTU3VjBoMjV2MzFoMzJ2MjRaIiBzdHlsZT0iZmlsbDojZGUwMDVkO2ZpbGwtcnVsZTpub256ZXJvIi8%2BPHBhdGggZD0iTTE4NSAzMWg1N3Y1NWgtMjVWNTVoLTMyVjMxWiIgc3R5bGU9ImZpbGw6I2M1MTgxZjtmaWxsLXJ1bGU6bm9uemVybyIvPjwvc3ZnPg%3D%3D&labelColor=fff"></a>
</p>

[文档](docs/) | [许可证](LICENSE) | [QQ群](https://qm.qq.com/q/AmdNUkSxFY)

NcatBot 是基于 onebot11协议 的 Python SDK, 它提供了一套方便易用的 Python 接口用于开发 QQ 机器人.

</div>


## 如何使用

### 用户使用

针对没有计算机基础的用户群体, 可以直接下载我们的**一键安装包**安装 NcatBot 运行时环境, 并使用他人发布的插件.

[阅读文档了解更多](https://docs.ncatbot.xyz/guide/onestepi/)

### 开发者使用

请**认真阅读**[文档](https://docs.ncatbot.xyz/). 文档中包含详细的**开发指南**和**示例项目及其解析**.

[插件仓库地址](https://github.com/ncatbot/NcatBot-Plugins).


## 欢迎来玩

[是 QQ 群哦喵~](https://qm.qq.com/q/L6XGXYqL86)

## 获取帮助

- 遇到任何困难时, 请先按照以下顺序尝试自己解决:

  1. **仔细阅读**[文档](https://docs.ncatbot.xyz/).
  2. 询问 [DeepSeek](https://chat.deepseek.com), [Kimi](https://kimi.ai) 等人工智能.
  3. 搜索本项目的 [Issue 列表](https://github.com/liyihao1110/ncatbot/issues).
- 如果以上方法都无法解决你的问题, 那么:

  可以[进群](https://qm.qq.com/q/L6XGXYqL86)提问.

## 联系我们

作者: [最可爱的木子喵~](https://gitee.com/li-yihao0328)

邮箱: <lyh_02@foxmail.com>


## 使用限制

1. **严禁将本项目以任何形式用于传播 反动、暴力、淫秽 信息，违者将追究法律责任**.
2. 将本项目以**任何形式**用于**盈利性用途**时，必须取得项目开发组(本仓库 Collaborators 和 Owner)的**书面授权**.


## 致谢

感谢 [NapCat](https://github.com/NapNeko/NapCatQQ) 提供底层接口 | [IppClub](https://github.com/IppClub) 的宣传支持 | [Fcatbot](https://github.com/Fish-LP/Fcatbot) 提供代码和灵感.

感谢 [扶摇互联](https://v10.fyyun.net/) | [林枫云](https://www.dkdun.cn/) 提供服务器支持.

## 参与贡献
欢迎通过 Issue 或 Pull Request 参与项目开发！请先阅读 [贡献指南](CONTRIBUTING.md)。

如果你在使用过程中遇到任何问题，欢迎在 [GitHub Issues](https://github.com/liyihao1110/ncatbot/issues) 中反馈。感谢你的支持！


<div align="center">

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=liyihao1110/ncatbot&type=Date)](https://www.star-history.com/#liyihao1110/ncatbot&Date)

## 贡献者们

<a href="https://github.com/liyihao1110/ncatbot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=liyihao1110/ncatbot" />
</a>

</div>

---

# 🎉 新用户专享 | 免费抽15台高性能挂机宝！🔥

**⏰ 活动时间**  
即日起至抽完为止  

---

## 🚀 活动内容  
✅ **免费抽取15台挂机宝**
✅ **配置拉满，小白也能变大神**：  
   - **CPU**: 铂金(Platinum)8272CL-K1  
   - **规格**: 2G内存｜1核｜2M带宽  
   - **存储**: 三星SSD系统盘35G（读写速度起飞💨）  
   - **网络**: 江苏宿迁电信单线｜150Gbps DDoS防御（安全稳如泰山🛡️）  
   - **扩展性**: 2个端口转发｜原生NAT云机IP（已购用户可升级更多端口！）  
   - **流量**: 不限量！任性跑🔄  

---

## 🎁 参与资格  
- **全新用户专属**：未注册/未购买过本平台服务  
- **时效福利**：中奖机器享**1个月免费使用权**  

---

## 📝 如何领取？  
1️⃣ **立即注册** 👉 [点击跳转抽奖群聊](https://qm.qq.com/q/sYOBJL9WiO)  
2️⃣ **参与抽奖**：进群后询问管理如何进行抽奖 
3️⃣ **静候佳音**：中奖者请添加管理员获取

---

## ⚠️ 注意事项  
- 每个账号仅限参与1次  
- 中奖后需在3天内激活使用  
- 配置不可选，默认发放活动机型  

---

> 📢 **活动说明**：  
> 本活动最终解释权归平台所有，15台机器抽完即止！  
> **防御扛打｜配置能打｜新人白嫖党狂喜**  
> 速来上车，手慢无！🚨  


# FilterRegistry 实战案例

## 🎯 真实应用场景

本文档提供了多个完整的实战案例，展示如何使用 FilterRegistry 构建实际的机器人功能。

## 案例1: 签到系统

### 功能需求
- 每日签到功能
- 连续签到奖励
- 签到排行榜
- 补签功能（VIP专用）

### 完整实现

```python
from ncatbot.plugin import BasePlugin
from ncatbot.plugin_system.builtin_plugin.filter_registry import filter
from ncatbot.core.event.message import BaseMessageEvent
from ncatbot.utils import get_log
import datetime
import json
import os

class CheckInPlugin(BasePlugin):
    """签到系统插件"""
    
    name = "CheckInPlugin"
    version = "1.0.0"
    
    def __init__(self):
        super().__init__()
        self.log = get_log(self.name)
        self.data_file = "data/checkin/user_data.json"
        self.user_data = self._load_data()
    
    def _load_data(self):
        """加载用户数据"""
        if not os.path.exists(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            return {}
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_data(self):
        """保存用户数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_data, f, ensure_ascii=False, indent=2)
    
    def _get_today_str(self):
        """获取今天的日期字符串"""
        return datetime.date.today().strftime("%Y-%m-%d")
    
    def _get_user_data(self, user_id: str):
        """获取用户数据"""
        return self.user_data.setdefault(user_id, {
            "total_days": 0,
            "continuous_days": 0,
            "last_checkin": None,
            "total_points": 0,
            "checkin_dates": []
        })
    
    @filter.command("签到")
    async def daily_checkin(self, event: BaseMessageEvent):
        """每日签到"""
        user_id = str(event.user_id)
        today = self._get_today_str()
        user_data = self._get_user_data(user_id)
        
        # 检查是否已签到
        if today in user_data["checkin_dates"]:
            await event.reply("❌ 你今天已经签到过了！")
            return
        
        # 计算连续天数
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        if user_data["last_checkin"] == yesterday:
            user_data["continuous_days"] += 1
        elif user_data["last_checkin"] != today:
            user_data["continuous_days"] = 1
        
        # 计算奖励
        base_points = 10
        continuous_bonus = min(user_data["continuous_days"] * 2, 50)  # 最高50点连续奖励
        total_reward = base_points + continuous_bonus
        
        # 更新数据
        user_data["total_days"] += 1
        user_data["last_checkin"] = today
        user_data["total_points"] += total_reward
        user_data["checkin_dates"].append(today)
        
        # 保存数据
        self._save_data()
        
        # 回复消息
        reply = f"""✅ 签到成功！
📅 签到天数: {user_data['total_days']} 天
🔥 连续签到: {user_data['continuous_days']} 天
🎁 获得积分: {total_reward} 分（基础{base_points} + 连续奖励{continuous_bonus}）
💰 总积分: {user_data['total_points']} 分"""
        
        # 连续签到里程碑奖励
        if user_data["continuous_days"] in [7, 30, 100]:
            milestone_reward = user_data["continuous_days"] * 10
            user_data["total_points"] += milestone_reward
            reply += f"\n\n🎉 连续签到 {user_data['continuous_days']} 天里程碑奖励: {milestone_reward} 分！"
            self._save_data()
        
        await event.reply(reply)
    
    @filter.command("签到状态")
    async def checkin_status(self, event: BaseMessageEvent):
        """查看签到状态"""
        user_id = str(event.user_id)
        user_data = self._get_user_data(user_id)
        today = self._get_today_str()
        
        is_today_checkin = today in user_data["checkin_dates"]
        status_emoji = "✅" if is_today_checkin else "❌"
        
        reply = f"""📊 签到状态报告
{status_emoji} 今日签到: {'已完成' if is_today_checkin else '未完成'}
📅 累计签到: {user_data['total_days']} 天
🔥 连续签到: {user_data['continuous_days']} 天
💰 总积分: {user_data['total_points']} 分
📆 最后签到: {user_data['last_checkin'] or '从未签到'}"""
        
        await event.reply(reply)
    
    @filter.command("签到排行")
    async def checkin_ranking(self, event: BaseMessageEvent, rank_type: str = "total"):
        """签到排行榜"""
        if rank_type not in ["total", "continuous", "points"]:
            await event.reply("❌ 排行类型错误！支持: total(总天数), continuous(连续天数), points(积分)")
            return
        
        # 根据排行类型排序
        sort_key = {
            "total": "total_days",
            "continuous": "continuous_days", 
            "points": "total_points"
        }[rank_type]
        
        # 排序用户数据
        sorted_users = sorted(
            [(uid, data) for uid, data in self.user_data.items()],
            key=lambda x: x[1].get(sort_key, 0),
            reverse=True
        )[:10]  # 取前10名
        
        if not sorted_users:
            await event.reply("❌ 暂无排行数据")
            return
        
        # 生成排行榜
        rank_names = {
            "total": "累计签到天数",
            "continuous": "连续签到天数",
            "points": "积分"
        }
        
        reply = f"🏆 {rank_names[rank_type]}排行榜\n\n"
        for i, (uid, data) in enumerate(sorted_users, 1):
            emoji = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
            value = data.get(sort_key, 0)
            reply += f"{emoji} 用户{uid[-4:]}: {value}\n"  # 只显示用户ID后4位
        
        await event.reply(reply)
    
    # VIP补签功能
    def is_vip_user(self, manager, event: BaseMessageEvent) -> bool:
        """检查是否为VIP用户"""
        # 这里应该根据实际的VIP系统来判断
        # 示例：检查用户是否有VIP角色
        return manager.rbac_manager.user_has_role(event.user_id, "vip")
    
    @filter.custom(is_vip_user)
    @filter.command("补签")
    async def makeup_checkin(self, event: BaseMessageEvent, date_str: str):
        """VIP补签功能"""
        user_id = str(event.user_id)
        
        # 验证日期格式
        try:
            target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            await event.reply("❌ 日期格式错误！请使用 YYYY-MM-DD 格式，如：2023-12-25")
            return
        
        # 检查日期限制
        today = datetime.date.today()
        if target_date >= today:
            await event.reply("❌ 不能补签今天或未来的日期！")
            return
        
        if target_date < today - datetime.timedelta(days=7):
            await event.reply("❌ 只能补签最近7天的日期！")
            return
        
        user_data = self._get_user_data(user_id)
        date_str = target_date.strftime("%Y-%m-%d")
        
        # 检查是否已签到
        if date_str in user_data["checkin_dates"]:
            await event.reply("❌ 该日期已经签到过了！")
            return
        
        # 执行补签
        user_data["checkin_dates"].append(date_str)
        user_data["checkin_dates"].sort()  # 保持日期排序
        user_data["total_days"] += 1
        
        # 补签费用
        cost = 50  # VIP补签费用50积分
        if user_data["total_points"] < cost:
            await event.reply(f"❌ 积分不足！补签需要 {cost} 积分，当前积分: {user_data['total_points']}")
            return
        
        user_data["total_points"] -= cost
        self._save_data()
        
        await event.reply(f"""✅ 补签成功！
📅 补签日期: {date_str}
💰 消耗积分: {cost}
💰 剩余积分: {user_data['total_points']}
📊 累计签到: {user_data['total_days']} 天""")
```

## 案例2: 天气查询系统

### 功能需求
- 实时天气查询
- 天气预报
- 城市管理
- 天气提醒订阅

### 完整实现

```python
import aiohttp
import asyncio
from datetime import datetime, timedelta

class WeatherPlugin(BasePlugin):
    """天气查询插件"""
    
    name = "WeatherPlugin"
    version = "1.0.0"
    
    def __init__(self):
        super().__init__()
        self.log = get_log(self.name)
        # 这里应该使用真实的天气API key
        self.api_key = "your_weather_api_key"
        self.api_base = "https://api.openweathermap.org/data/2.5"
        
        # 用户城市配置
        self.user_cities = {}
        self._load_user_cities()
    
    def _load_user_cities(self):
        """加载用户城市配置"""
        try:
            with open("data/weather/user_cities.json", 'r', encoding='utf-8') as f:
                self.user_cities = json.load(f)
        except FileNotFoundError:
            self.user_cities = {}
    
    def _save_user_cities(self):
        """保存用户城市配置"""
        os.makedirs("data/weather", exist_ok=True)
        with open("data/weather/user_cities.json", 'w', encoding='utf-8') as f:
            json.dump(self.user_cities, f, ensure_ascii=False, indent=2)
    
    async def _get_weather_data(self, city: str):
        """获取天气数据"""
        url = f"{self.api_base}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "zh_cn"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    raise Exception(f"API请求失败: {resp.status}")
    
    def _format_weather(self, data):
        """格式化天气信息"""
        city = data["name"]
        country = data["sys"]["country"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        weather = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"]
        
        # 时间转换
        dt = datetime.fromtimestamp(data["dt"])
        sunrise = datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset = datetime.fromtimestamp(data["sys"]["sunset"])
        
        return f"""🌤 {city}, {country} 天气
📅 更新时间: {dt.strftime('%Y-%m-%d %H:%M')}
🌡 温度: {temp}°C (体感 {feels_like}°C)
☁️ 天气: {weather}
💨 风速: {wind_speed} m/s
💧 湿度: {humidity}%
📊 气压: {pressure} hPa
🌅 日出: {sunrise.strftime('%H:%M')}
🌇 日落: {sunset.strftime('%H:%M')}"""
    
    @filter.command("天气")
    async def weather_query(self, event: BaseMessageEvent, city: str = None):
        """查询天气"""
        user_id = str(event.user_id)
        
        # 如果没有指定城市，使用用户默认城市
        if not city:
            city = self.user_cities.get(user_id)
            if not city:
                await event.reply("❌ 请指定城市名称，或先使用 '设置城市 城市名' 设置默认城市")
                return
        
        try:
            # 获取天气数据
            weather_data = await self._get_weather_data(city)
            
            # 格式化并回复
            formatted_weather = self._format_weather(weather_data)
            await event.reply(formatted_weather)
            
        except Exception as e:
            self.log.error(f"天气查询失败: {e}")
            await event.reply(f"❌ 天气查询失败: {str(e)}")
    
    @filter.command("设置城市")
    async def set_default_city(self, event: BaseMessageEvent, city: str):
        """设置默认城市"""
        user_id = str(event.user_id)
        
        try:
            # 验证城市是否有效
            weather_data = await self._get_weather_data(city)
            city_name = weather_data["name"]
            
            # 保存用户默认城市
            self.user_cities[user_id] = city_name
            self._save_user_cities()
            
            await event.reply(f"✅ 默认城市已设置为: {city_name}")
            
        except Exception as e:
            await event.reply(f"❌ 城市设置失败: {str(e)}")
    
    @filter.command("我的城市")
    async def my_city(self, event: BaseMessageEvent):
        """查看我的默认城市"""
        user_id = str(event.user_id)
        city = self.user_cities.get(user_id)
        
        if city:
            await event.reply(f"📍 你的默认城市: {city}")
        else:
            await event.reply("❌ 你还没有设置默认城市")
    
    # 天气预报功能
    async def _get_forecast_data(self, city: str):
        """获取天气预报数据"""
        url = f"{self.api_base}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "zh_cn"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    raise Exception(f"API请求失败: {resp.status}")
    
    def _format_forecast(self, data):
        """格式化天气预报"""
        city = data["city"]["name"]
        forecasts = data["list"][:5]  # 取前5个时段
        
        result = f"📅 {city} 天气预报\n\n"
        
        for forecast in forecasts:
            dt = datetime.fromtimestamp(forecast["dt"])
            temp = forecast["main"]["temp"]
            weather = forecast["weather"][0]["description"]
            
            result += f"🕐 {dt.strftime('%m-%d %H:%M')}\n"
            result += f"🌡 {temp}°C - {weather}\n\n"
        
        return result.rstrip()
    
    @filter.command("天气预报")
    async def weather_forecast(self, event: BaseMessageEvent, city: str = None):
        """查询天气预报"""
        user_id = str(event.user_id)
        
        if not city:
            city = self.user_cities.get(user_id)
            if not city:
                await event.reply("❌ 请指定城市名称，或先设置默认城市")
                return
        
        try:
            forecast_data = await self._get_forecast_data(city)
            formatted_forecast = self._format_forecast(forecast_data)
            await event.reply(formatted_forecast)
            
        except Exception as e:
            self.log.error(f"天气预报查询失败: {e}")
            await event.reply(f"❌ 天气预报查询失败: {str(e)}")
```

## 案例3: 群管理系统

### 功能需求
- 群成员管理
- 违规检测
- 自动化处理
- 管理日志

### 完整实现

```python
import re
from datetime import datetime, timedelta

class GroupManagementPlugin(BasePlugin):
    """群管理插件"""
    
    name = "GroupManagementPlugin"
    version = "1.0.0"
    
    def __init__(self):
        super().__init__()
        self.log = get_log(self.name)
        
        # 违规词库
        self.banned_words = [
            "违规词1", "违规词2", "违规词3"
        ]
        
        # 用户警告记录 {user_id: [警告时间列表]}
        self.user_warnings = {}
        
        # 群配置 {group_id: config}
        self.group_configs = {}
        
        self._load_configs()
    
    def _load_configs(self):
        """加载配置"""
        try:
            with open("data/group_mgmt/configs.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.banned_words = data.get("banned_words", self.banned_words)
                self.user_warnings = data.get("user_warnings", {})
                self.group_configs = data.get("group_configs", {})
        except FileNotFoundError:
            pass
    
    def _save_configs(self):
        """保存配置"""
        os.makedirs("data/group_mgmt", exist_ok=True)
        data = {
            "banned_words": self.banned_words,
            "user_warnings": self.user_warnings,
            "group_configs": self.group_configs
        }
        with open("data/group_mgmt/configs.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _get_group_config(self, group_id: str):
        """获取群配置"""
        return self.group_configs.setdefault(group_id, {
            "auto_ban": True,           # 自动封禁
            "warn_before_ban": True,    # 封禁前警告
            "max_warnings": 3,          # 最大警告次数
            "warning_expire_hours": 24, # 警告过期时间
            "welcome_new_members": True, # 欢迎新成员
            "anti_spam": True,          # 反垃圾信息
            "admin_users": []           # 群管理员
        })
    
    # 违规检测过滤器
    def contains_banned_words(self, event: BaseMessageEvent) -> bool:
        """检测是否包含违规词"""
        message = event.raw_message.lower()
        return any(word in message for word in self.banned_words)
    
    def is_spam_message(self, event: BaseMessageEvent) -> bool:
        """检测是否为垃圾消息"""
        message = event.raw_message
        
        # 检测重复字符
        if re.search(r'(.)\1{10,}', message):  # 同一字符重复10次以上
            return True
        
        # 检测过多链接
        url_count = len(re.findall(r'http[s]?://\S+', message))
        if url_count > 3:
            return True
        
        # 检测过多@
        at_count = message.count('@')
        if at_count > 5:
            return True
        
        return False
    
    @filter.group_message()
    @filter.custom(contains_banned_words)
    async def handle_banned_words(self, event: BaseMessageEvent):
        """处理违规词汇"""
        group_id = str(event.group_id)
        user_id = str(event.user_id)
        config = self._get_group_config(group_id)
        
        if not config["auto_ban"]:
            return
        
        # 删除违规消息
        try:
            await event.delete_message()
        except:
            pass
        
        # 警告处理
        if config["warn_before_ban"]:
            warnings = self._add_warning(user_id)
            
            if warnings >= config["max_warnings"]:
                # 达到警告上限，执行封禁
                try:
                    await event.ban_group_member(user_id, duration=3600)  # 封禁1小时
                    await event.reply(f"⚠️ 用户 {user_id} 因多次违规被封禁1小时")
                    self._clear_warnings(user_id)
                except Exception as e:
                    self.log.error(f"封禁用户失败: {e}")
            else:
                remaining = config["max_warnings"] - warnings
                await event.reply(
                    f"⚠️ 检测到违规内容已删除\n"
                    f"用户警告: {warnings}/{config['max_warnings']}\n"
                    f"剩余警告次数: {remaining}"
                )
        else:
            # 直接封禁
            try:
                await event.ban_group_member(user_id, duration=3600)
                await event.reply(f"⚠️ 用户 {user_id} 因违规被封禁1小时")
            except Exception as e:
                self.log.error(f"封禁用户失败: {e}")
    
    @filter.group_message()
    @filter.custom(is_spam_message)
    async def handle_spam(self, event: BaseMessageEvent):
        """处理垃圾消息"""
        group_id = str(event.group_id)
        config = self._get_group_config(group_id)
        
        if not config["anti_spam"]:
            return
        
        try:
            await event.delete_message()
            await event.reply("⚠️ 检测到垃圾信息已删除")
        except:
            pass
    
    def _add_warning(self, user_id: str) -> int:
        """添加警告记录"""
        current_time = datetime.now()
        
        if user_id not in self.user_warnings:
            self.user_warnings[user_id] = []
        
        # 清理过期警告
        expire_time = current_time - timedelta(hours=24)
        self.user_warnings[user_id] = [
            warn_time for warn_time in self.user_warnings[user_id]
            if datetime.fromisoformat(warn_time) > expire_time
        ]
        
        # 添加新警告
        self.user_warnings[user_id].append(current_time.isoformat())
        self._save_configs()
        
        return len(self.user_warnings[user_id])
    
    def _clear_warnings(self, user_id: str):
        """清除警告记录"""
        if user_id in self.user_warnings:
            del self.user_warnings[user_id]
            self._save_configs()
    
    # 管理员命令
    def is_group_admin(self, manager, event: BaseMessageEvent) -> bool:
        """检查是否为群管理员"""
        if not event.is_group_msg():
            return False
        
        # 检查系统管理员权限
        if manager.rbac_manager.user_has_role(event.user_id, "admin"):
            return True
        
        # 检查群管理员配置
        group_id = str(event.group_id)
        user_id = str(event.user_id)
        config = self._get_group_config(group_id)
        
        return user_id in config["admin_users"]
    
    @filter.custom(is_group_admin)
    @filter.command("封禁")
    async def ban_user(self, event: BaseMessageEvent, user_id: str, duration: int = 3600):
        """封禁用户"""
        try:
            await event.ban_group_member(user_id, duration)
            hours = duration // 3600
            await event.reply(f"✅ 用户 {user_id} 已被封禁 {hours} 小时")
        except Exception as e:
            await event.reply(f"❌ 封禁失败: {str(e)}")
    
    @filter.custom(is_group_admin)
    @filter.command("解封")
    async def unban_user(self, event: BaseMessageEvent, user_id: str):
        """解封用户"""
        try:
            await event.unban_group_member(user_id)
            await event.reply(f"✅ 用户 {user_id} 已解封")
        except Exception as e:
            await event.reply(f"❌ 解封失败: {str(e)}")
    
    @filter.custom(is_group_admin)
    @filter.command("添加违规词")
    async def add_banned_word(self, event: BaseMessageEvent, word: str):
        """添加违规词"""
        if word not in self.banned_words:
            self.banned_words.append(word)
            self._save_configs()
            await event.reply(f"✅ 已添加违规词: {word}")
        else:
            await event.reply(f"❌ 违规词已存在: {word}")
    
    @filter.custom(is_group_admin)
    @filter.command("群配置")
    async def group_config(self, event: BaseMessageEvent, 
                          setting: str, value: str = None):
        """群配置管理"""
        group_id = str(event.group_id)
        config = self._get_group_config(group_id)
        
        if value is None:
            # 显示当前配置
            if setting in config:
                await event.reply(f"{setting} = {config[setting]}")
            else:
                await event.reply(f"❌ 配置项 {setting} 不存在")
        else:
            # 设置配置
            if setting in config:
                # 类型转换
                if isinstance(config[setting], bool):
                    value = value.lower() in ['true', '1', 'on', 'yes']
                elif isinstance(config[setting], int):
                    try:
                        value = int(value)
                    except ValueError:
                        await event.reply(f"❌ 配置值必须为整数")
                        return
                
                config[setting] = value
                self._save_configs()
                await event.reply(f"✅ 配置已更新: {setting} = {value}")
            else:
                await event.reply(f"❌ 配置项 {setting} 不存在")
    
    # 通知事件处理
    @filter.notice_event()
    async def handle_group_notice(self, event):
        """处理群通知事件"""
        if event.notice_type == "group_increase":
            # 新成员加群
            group_id = str(event.group_id)
            user_id = str(event.user_id)
            config = self._get_group_config(group_id)
            
            if config["welcome_new_members"]:
                welcome_msg = f"🎉 欢迎新成员 {user_id} 加入群聊！\n" \
                             f"请遵守群规，和谐交流～"
                await event.reply(welcome_msg)
```

## 案例4: 积分商城系统

### 功能需求
- 积分获取
- 商品管理
- 购买记录
- 库存管理

### 关键代码片段

```python
class PointsShopPlugin(BasePlugin):
    """积分商城插件"""
    
    @filter.command("商城")
    async def show_shop(self, event: BaseMessageEvent, category: str = "all"):
        """显示商城商品"""
        # 实现商城展示逻辑
        pass
    
    @filter.command("购买")
    async def buy_item(self, event: BaseMessageEvent, item_id: str, quantity: int = 1):
        """购买商品"""
        # 实现购买逻辑
        pass
    
    @filter.admin_only()
    @filter.command("上架商品")
    async def add_item(self, event: BaseMessageEvent, 
                      name: str, price: int, stock: int, description: str):
        """管理员上架商品"""
        # 实现商品上架逻辑
        pass
```

这些实战案例展示了如何使用 FilterRegistry 构建完整的功能模块。每个案例都包含了完整的错误处理、数据持久化、权限控制等最佳实践。

# 插件加载器

插件加载器负责管理插件的生命周期。

## 创建插件

1. 创建一个继承自 `BasePlugin` 的类
2. 定义必需的元数据
3. 实现生命周期方法

```python
class MyPlugin(BasePlugin):
    # 必需的元数据
    name = "my_plugin"  
    version = "1.0.0"
  
    # 可选元数据
    author = "作者"
    description = "插件描述"
    dependencies = {
        "other_plugin": ">=1.0.0"
    }
  
    # 生命周期方法
    async def on_load(self):
        """插件加载时调用"""
        pass
      
    async def on_reload(self):
        """插件重载时调用""" 
        pass
      
    async def on_close(self):
        """插件卸载时调用"""
        pass
```

## 插件目录结构

```tree
plugins/
  my_plugin/
    __init__.py      # 插件主文件
    requirements.txt # 依赖声明(可选)
```

## 配置管理

插件配置存储在 `self.config` 字典中,会自动保存/加载:

```python
class MyPlugin(BasePlugin):
    async def on_load(self):
        # 读取配置
        debug = self.config.get("cat", False)
  
        # 修改配置 
        self.config["cat"] = True
```

## 工作目录

每个插件都有独立的工作目录用于存储数据:

- `self.workspace`: 插件工作目录
- `self.data_file`: 配置文件路径
- `self.source_dir`: 插件源码目录

## 调试

设置 `debug=True` 开启调试模式:

```python
loader = PluginLoader(event_bus, debug=True)
```

调试模式下:

- 插件 `debug` 属性标记为 `True`

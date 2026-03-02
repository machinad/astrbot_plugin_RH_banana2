# AGENTS.md - 项目上下文文档

本文档为 AI 助手（如 iFlow CLI）提供项目上下文，以便更好地理解和协助开发。

## 项目概览

**项目名称:** astrbot_plugin_RH_banana2

**项目类型:** AstrBot 插件

**项目描述:** 这是一个用于 AstrBot 的插件，通过 RunningHub 代理提供 banana2 图生图、文生图功能。定价经济实惠，4K 图片约 0.08 元/张。

**作者:** machinad

**许可证:** GNU Affero General Public License v3.0 (AGPL-3.0)

**仓库地址:** https://github.com/machinad/astrbot_plugin_RH_banana2

## 技术栈

- **语言:** Python 3.14+
- **框架:** AstrBot 插件系统
- **异步支持:** 使用 `async/await` 异步编程模式

## 项目结构

```
astrbot_plugin_RH_banana2/
├── main.py           # 插件主入口文件
├── metadata.yaml     # 插件元数据配置
├── README.md         # 项目说明文档
├── LICENSE           # AGPL-3.0 许可证
├── AGENTS.md         # 本文件 - AI 上下文文档
├── .gitignore        # Git 忽略规则
└── plugin_docs/      # 插件文档目录（被 git 忽略）
```

## 核心文件说明

### metadata.yaml

插件元数据配置文件，包含以下字段：

| 字段 | 说明 |
|------|------|
| `name` | 插件唯一标识名，必须以 `astrbot_plugin_` 为前缀 |
| `display_name` | 人类可读的展示名称 |
| `desc` | 插件简短描述 |
| `version` | 插件版本号（格式：v1.1.1 或 v1.1） |
| `author` | 作者名称 |
| `repo` | 插件仓库地址 |

### main.py

插件主入口文件，定义插件的核心逻辑：

- 继承自 `Star` 基类
- 使用 `@register` 装饰器注册插件
- 使用 `@filter.command` 装饰器注册指令
- 支持异步初始化 (`initialize`) 和销毁 (`terminate`) 方法

## AstrBot 插件开发规范

### 基本结构

```python
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("插件名", "作者", "描述", "版本")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选：异步初始化方法"""
        pass

    @filter.command("指令名")
    async def command_handler(self, event: AstrMessageEvent):
        """指令处理方法"""
        yield event.plain_result("回复内容")

    async def terminate(self):
        """可选：异步销毁方法"""
        pass
```

### 常用 API

- `event.get_sender_name()` - 获取发送者名称
- `event.message_str` - 获取纯文本消息字符串
- `event.get_messages()` - 获取消息链
- `event.plain_result(text)` - 生成纯文本回复
- `logger.info()` / `logger.error()` - 日志输出

### 指令注册

使用 `@filter.command("指令名")` 装饰器注册指令。用户发送 `/指令名` 即可触发。

## 开发指南

### 环境要求

- Python 3.14+
- AstrBot 运行环境

### 开发流程

1. 修改 `main.py` 实现插件逻辑
2. 更新 `metadata.yaml` 中的版本号（如有更改）
3. 在本地 AstrBot 环境中测试插件
4. 提交代码至 Git 仓库

### 测试

将插件放置在 AstrBot 的 `data/plugins/` 目录下，启动 AstrBot 进行测试。

### 代码风格

- 使用异步函数处理消息事件
- 为 handler 方法添加文档字符串描述功能
- 使用 `yield` 返回消息结果

## 相关资源

- [AstrBot 仓库](https://github.com/AstrBotDevs/AstrBot)
- [AstrBot 插件开发文档（中文）](https://docs.astrbot.app/dev/star/plugin-new.html)
- [AstrBot 插件开发文档（英文）](https://docs.astrbot.app/en/dev/star/plugin-new.html)

## 注意事项

1. 插件名称必须以 `astrbot_plugin_` 为前缀
2. 使用 AGPL-3.0 许可证，修改后需开源
3. 插件文档目录 `plugin_docs/` 被 git 忽略，不会提交到仓库

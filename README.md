# astrbot_plugin_RH_banana2

超便宜的 RunningHub Banana2 图生图、文生图插件。4K 图仅需 0.08 元/张。

## 更新日志

### v0.1.1
- 新增多 API Key 轮询机制，失败自动切换
- 支持多张参考图输入（最多 10 张）
- 优化任务查询与消息处理流程

## 效果展示

| 文生图 | 图生图 | 多图融合 |
|:---:|:---:|:---:|
| ![文生图效果](https://example.com/text-to-image.png) | ![图生图效果](https://example.com/image-to-image.png) | ![多图融合效果](https://example.com/multi-image.png) |

## 使用说明

### 配置
1. 在 RunningHub 官网注册账号并获取 API Key
2. 在 AstrBot 插件配置中填入 API Key（支持多个 Key）
3. 选择默认分辨率和宽高比

### 指令
| 指令 | 说明 | 示例 |
|------|------|------|
| `/rh <提示词>` | 文生图 | `/rh 一只可爱的猫咪` |
| `/rh <提示词> [图片]` | 图生图 | `/rh 转换为水彩风格 [图片]` |

### 特性
- 支持 1K/2K/4K 分辨率
- 支持多种宽高比
- 多 API Key 轮询，提高可用性
- 支持最多 10 张参考图

---

> [AstrBot](https://github.com/AstrBotDevs/AstrBot) is an agentic assistant for both personal and group conversations. It can be deployed across dozens of mainstream instant messaging platforms, including QQ, Telegram, Feishu, DingTalk, Slack, LINE, Discord, Matrix, etc. In addition, it provides a reliable and extensible conversational AI infrastructure for individuals, developers, and teams. Whether you need a personal AI companion, an intelligent customer support agent, an automation assistant, or an enterprise knowledge base, AstrBot enables you to quickly build AI applications directly within your existing messaging workflows.

## Supports

- [AstrBot Repo](https://github.com/AstrBotDevs/AstrBot)
- [AstrBot Plugin Development Docs (Chinese)](https://docs.astrbot.app/dev/star/plugin-new.html)
- [AstrBot Plugin Development Docs (English)](https://docs.astrbot.app/en/dev/star/plugin-new.html)
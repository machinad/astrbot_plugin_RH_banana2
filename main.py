"""
RH Banana2 图像生成插件
通过 RunningHub API 提供文生图、图生图功能
"""

import asyncio
import json
import aiohttp
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import Image


@register("rh_banana2", "machinad", "RunningHub Banana2 文生图/图生图插件", "0.1.1")
class RHBanana2Plugin(Star):
    """RunningHub Banana2 图像生成插件主类"""

    # ============ 全局变量 - API 配置 ============
    API_BASE_URL: str = "https://www.runninghub.cn/openapi/v2"
    api_key: str = ""
    resolution: str = "1k"
    aspect_ratio: str = "1:1"

    # ============ 初始化方法 ============
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config

    async def initialize(self):
        """插件初始化，从配置读取参数"""
        self.api_key = self.config.get("api_key", "")
        self.resolution = self.config.get("resolution", "1k")
        self.aspect_ratio = self.config.get("aspect_ratio", "1:1")
        logger.info(f"RH Banana2 插件初始化完成，分辨率: {self.resolution}, 宽高比: {self.aspect_ratio}")

    # ============ 主指令处理器 ============
    @filter.command("rh")
    async def rh(self, event: AstrMessageEvent):
        """
        RH 图像生成指令
        用法: /rh <提示词> [图片]
        - 无图片时执行文生图
        - 有图片时执行图生图
        """
        # 检查 API Key
        if not self.api_key:
            yield event.plain_result("请先在插件配置中设置 API Key")
            return

        # 获取用户消息
        message_str = event.message_str.strip()
        prompt = message_str

        # 解析消息中的图片 URL
        image_urls = await self.parse_image_urls(event)

        if image_urls:
            # 有图片，执行图生图
            logger.info(f"检测到 {len(image_urls)} 张图片，执行图生图，提示词: {prompt}")
            result = await self.image_to_image(image_urls, prompt)
        else:
            # 无图片，执行文生图
            logger.info(f"执行文生图，提示词: {prompt}")
            result = await self.text_to_image(prompt)

        # 统一处理结果并发送消息
        if result["success"] and result["type"] == "image":
            yield event.image_result(result["data"])
        else:
            yield event.plain_result(result.get("error", "未知错误"))

    # ============ 文生图函数 ============
    async def text_to_image(self, prompt: str) -> dict:
        """
        文生图函数
        :param prompt: 文本提示词
        :return: {"success": bool, "type": "image"|"text", "data": str, "error": str}
        """
        url = f"{self.API_BASE_URL}/rhart-image-n-g31-flash/text-to-image"
        headers = self._get_headers()
        payload = {
            "prompt": prompt,
            "resolution": self.resolution,
        }
        if self.aspect_ratio:
            payload["aspectRatio"] = self.aspect_ratio

        try:
            async with aiohttp.ClientSession() as session:
                # 提交任务
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {"success": False, "error": f"提交任务失败: {error_text}"}
                    result = await response.json()

                task_id = result.get("taskId")
                if not task_id:
                    return {"success": False, "error": f"获取任务ID失败: {result}"}

                # 轮询查询结果
                return await self.query_task(session, task_id)

        except Exception as e:
            logger.error(f"文生图异常: {e}")
            return {"success": False, "error": f"发生错误: {str(e)}"}

    # ============ 图生图函数 ============
    async def image_to_image(self, image_urls: list, prompt: str) -> dict:
        """
        图生图函数（支持多张参考图）
        :param image_urls: 原始图片 URL 列表（最多10张）
        :param prompt: 文本提示词
        :return: {"success": bool, "type": "image"|"text", "data": str, "error": str}
        """
        try:
            # 限制最多10张图片
            image_urls = image_urls[:10]
            
            # 上传所有图片到 RH
            rh_image_urls = []
            for i, image_url in enumerate(image_urls):
                rh_url = await self.upload_image(image_url)
                if rh_url:
                    rh_image_urls.append(rh_url)
                    logger.info(f"图片 {i+1}/{len(image_urls)} 上传成功")
                else:
                    logger.warning(f"图片 {i+1}/{len(image_urls)} 上传失败，跳过")

            if not rh_image_urls:
                return {"success": False, "error": "所有图片上传失败"}

            logger.info(f"成功上传 {len(rh_image_urls)} 张图片")

            url = f"{self.API_BASE_URL}/rhart-image-n-g31-flash/image-to-image"
            headers = self._get_headers()
            payload = {
                "imageUrls": rh_image_urls,
                "prompt": prompt,
                "resolution": self.resolution,
            }
            if self.aspect_ratio:
                payload["aspectRatio"] = self.aspect_ratio

            async with aiohttp.ClientSession() as session:
                # 提交任务
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {"success": False, "error": f"提交任务失败: {error_text}"}
                    result = await response.json()

                task_id = result.get("taskId")
                if not task_id:
                    return {"success": False, "error": f"获取任务ID失败: {result}"}

                # 轮询查询结果
                return await self.query_task(session, task_id)

        except Exception as e:
            logger.error(f"图生图异常: {e}")
            return {"success": False, "error": f"发生错误: {str(e)}"}

    # ============ 上传图片函数 ============
    async def upload_image(self, image_url: str) -> str:
        """
        上传图片到 RunningHub
        :param image_url: 原始图片 URL
        :return: RH 返回的新图片 URL，失败返回空字符串
        """
        upload_url = f"{self.API_BASE_URL}/media/upload/binary"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                # 下载原始图片
                async with session.get(image_url) as download_response:
                    if download_response.status != 200:
                        logger.error(f"下载图片失败: {download_response.status}")
                        return ""
                    image_data = await download_response.read()

                # 上传到 RH
                form_data = aiohttp.FormData()
                form_data.add_field('file', image_data, filename='image.png', content_type='image/png')

                async with session.post(upload_url, headers=headers, data=form_data) as upload_response:
                    if upload_response.status != 200:
                        error_text = await upload_response.text()
                        logger.error(f"上传图片失败: {error_text}")
                        return ""
                    result = await upload_response.json()

                if result.get("code") == 0:
                    return result.get("data", {}).get("download_url", "")
                else:
                    logger.error(f"上传失败: {result.get('message')}")
                    return ""

        except Exception as e:
            logger.error(f"上传图片异常: {e}")
            return ""

    # ============ 查询任务函数 ============
    async def query_task(self, session: aiohttp.ClientSession, task_id: str) -> dict:
        """
        查询任务状态并返回结果数据
        :param session: aiohttp 会话
        :param task_id: 任务 ID
        :return: {"success": bool, "type": "image"|"text", "data": str, "error": str}
        """
        url = f"{self.API_BASE_URL}/query"
        headers = self._get_headers()
        payload = {"taskId": task_id}

        max_retries = 60
        retry_count = 0

        while retry_count < max_retries:
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {"success": False, "error": f"查询任务失败: {error_text}"}
                    result = await response.json()

                status = result.get("status", "")

                if status == "SUCCESS":
                    results = result.get("results", [])
                    if results and len(results) > 0:
                        output_url = results[0].get("url", "")
                        if output_url:
                            return {"success": True, "type": "image", "data": output_url}
                        else:
                            return {"success": False, "error": "生成成功但未获取到图片URL"}
                    else:
                        return {"success": False, "error": "生成成功但结果为空"}

                elif status == "FAILED":
                    error_msg = result.get("errorMessage", "未知错误")
                    return {"success": False, "error": f"任务失败: {error_msg}"}

                elif status in ["RUNNING", "QUEUED"]:
                    await asyncio.sleep(3)
                    retry_count += 1
                else:
                    return {"success": False, "error": f"未知状态: {status}"}

            except Exception as e:
                logger.error(f"查询任务异常: {e}")
                return {"success": False, "error": f"查询异常: {str(e)}"}

        return {"success": False, "error": "任务超时，请稍后重试"}

    # ============ 解析图片 URL 函数 ============
    async def parse_image_urls(self, event: AstrMessageEvent) -> list:
        """
        解析消息中的图片 URL
        :param event: 消息事件
        :return: 图片 URL 列表
        """
        image_urls = []
        message_chain = event.get_messages()

        for component in message_chain:
            if isinstance(component, Image):
                # 优先使用 URL，其次使用 file
                url = component.url or component.file
                if url:
                    image_urls.append(url)

        return image_urls

    # ============ 辅助方法 ============
    def _get_headers(self) -> dict:
        """获取 API 请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def terminate(self):
        """插件销毁方法"""
        logger.info("RH Banana2 插件已卸载")

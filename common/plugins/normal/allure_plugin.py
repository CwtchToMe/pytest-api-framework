"""
Allure 附件插件 - 自动将 HTTP 请求/响应附加到 Allure 报告

功能：
- after_request 钩子：生成 Request JSON + Response JSON 附件
- on_request_error 钩子：附加错误信息文本

启用状态：默认启用，可通过 disable("allure_attachment") 禁用
"""

import logging

import allure

from ..base import Plugin

logger = logging.getLogger(__name__)


class AllurePlugin(Plugin):
    """
    Allure 附件插件

    自动将每次 HTTP 请求的请求体和响应体以 JSON 格式附加到 Allure 报告。
    无需在测试代码中手动调用 allure.attach()。
    """

    @property
    def name(self) -> str:
        return "allure_attachment"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "自动将 HTTP 请求/响应以附件形式附加到 Allure 报告"

    @property
    def author(self) -> str:
        return "framework"

    def after_request(self, response, method: str, url: str, **kwargs):
        """请求成功后，附加请求详情和响应详情到 Allure 报告"""
        try:
            # 提取端点名称作为附件名
            endpoint = url.rstrip("/").rsplit("/", 1)[-1] if "/" in url else url

            # 构造请求附件
            request_info = {"method": method, "url": url}
            if "json" in kwargs and kwargs["json"]:
                request_info["body"] = kwargs["json"]
            elif "data" in kwargs and kwargs["data"]:
                request_info["body"] = kwargs["data"]

            allure.attach(
                str(request_info),
                name=f"Request  {method} /{endpoint}",
                attachment_type=allure.attachment_type.JSON,
            )

            # 构造响应附件
            response_info = {"status_code": response.status_code}
            try:
                response_info["body"] = response.json()
            except Exception:
                response_info["body"] = response.text[:500]

            allure.attach(
                str(response_info),
                name=f"Response  {method} /{endpoint}",
                attachment_type=allure.attachment_type.JSON,
            )

        except Exception as e:
            logger.debug(f"AllurePlugin.after_request 执行异常: {e}")

    def on_request_error(self, error, method: str, url: str, **kwargs):
        """请求异常时，附加错误信息到 Allure 报告"""
        try:
            endpoint = url.rstrip("/").rsplit("/", 1)[-1] if "/" in url else url

            allure.attach(
                str({"method": method, "url": url, "error": str(error)}),
                name=f"Error  {method} /{endpoint}",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception as e:
            logger.debug(f"AllurePlugin.on_request_error 执行异常: {e}")

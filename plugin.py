"""Zayu 灯光 MCP 服务插件壳。

实际灯光控制能力由同目录的 mcp_server.py 通过 MCP stdio 暴露给 MaiSaka。
这个插件类只用于让插件目录符合 MaiBot 第三方插件结构。
"""

from importlib.util import find_spec
from typing import Dict

from maibot_sdk import Field, MaiBotPlugin, PluginConfigBase


class PluginSectionConfig(PluginConfigBase):
    """插件基础配置。"""

    __ui_label__ = "插件"
    __ui_icon__ = "lightbulb"
    __ui_order__ = 0

    enabled: bool = Field(default=True, description="是否启用插件壳")
    config_version: str = Field(default="1.0.0", description="配置版本")


class ZayuLightMCPConfig(PluginConfigBase):
    """Zayu 灯光 MCP 服务插件配置。"""

    plugin: PluginSectionConfig = Field(default_factory=PluginSectionConfig)


class ZayuLightMCPPlugin(MaiBotPlugin):
    """Zayu 灯光 MCP 服务插件壳。"""

    config_model = ZayuLightMCPConfig

    async def on_load(self) -> None:
        """处理插件加载。"""
        self.ctx.logger.info("Zayu 灯光 MCP 服务插件壳已加载")
        if find_spec("serial") is None:
            self.ctx.logger.warning("Zayu 灯光 MCP 控制缺少 pyserial 依赖，开关灯工具会执行失败")

    async def on_unload(self) -> None:
        """处理插件卸载。"""
        self.ctx.logger.info("Zayu 灯光 MCP 服务插件壳已卸载")

    async def on_config_update(self, scope: str, config_data: Dict[str, object], version: str) -> None:
        """处理配置热重载事件。"""
        if scope != "self":
            return

        self.set_plugin_config(config_data)
        self.ctx.logger.info(f"Zayu 灯光 MCP 服务插件配置已更新，版本: {version}")


def create_plugin() -> ZayuLightMCPPlugin:
    """创建插件实例。"""
    return ZayuLightMCPPlugin()

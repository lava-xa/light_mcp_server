# Zayu 灯光 MCP 控制

这个目录包含一个合规的 MaiBot 第三方插件壳，以及一个本地 MCP Server。

MCP Server 暴露两个工具：

- `zayu_light_on`：调用插件内串口控制代码，向 ESP32 发送 `0`
- `zayu_light_off`：调用插件内串口控制代码，向 ESP32 发送 `1`

MaiBot 需要在 `config/bot_config.toml` 的 `mcp.servers` 中配置该服务，并在重启后生效。

插件在 `_manifest.json` 中声明了 `pyserial>=3.5`，MaiBot 插件依赖流水线会把它加入自动安装计划。

可选环境变量：

- `ESP32_PORT`：指定串口，例如 `/dev/ttyUSB0`
- `ESP32_BAUD`：指定波特率，默认 `115200`

"""Zayu 灯光 MCP Server。

通过两个白名单 MCP 工具调用插件内的串口控制模块。
stdout 只输出 JSON-RPC 消息，避免污染 MCP stdio 协议。
"""

from typing import Any, Dict, List, Optional

import json
import sys

from serial_light import turn_off, turn_on


SERVER_NAME = "zayu-light-controller"
SERVER_VERSION = "1.0.0"


def _tool_specs() -> List[Dict[str, Any]]:
    """返回 MCP tools/list 所需的工具声明。"""

    empty_input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": [],
    }
    return [
        {
            "name": "zayu_light_on",
            "description": "打开 Zayu 灯光。用户要求开灯、打开灯、把灯打开时使用。",
            "inputSchema": empty_input_schema,
        },
        {
            "name": "zayu_light_off",
            "description": "关闭 Zayu 灯光。用户要求关灯、关闭灯、把灯关掉时使用。",
            "inputSchema": empty_input_schema,
        },
    ]


def _call_tool(name: str) -> Dict[str, Any]:
    """执行指定 MCP 工具。"""

    try:
        if name == "zayu_light_on":
            text = turn_on()
        elif name == "zayu_light_off":
            text = turn_off()
        else:
            raise ValueError(f"未知灯光工具: {name}")
    except Exception as exc:
        return {
            "content": [{"type": "text", "text": str(exc)}],
            "isError": True,
        }

    return {
        "content": [{"type": "text", "text": text}],
        "isError": False,
    }


def _response(request_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
    """构造 JSON-RPC 成功响应。"""

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result,
    }


def _error_response(request_id: Any, code: int, message: str) -> Dict[str, Any]:
    """构造 JSON-RPC 错误响应。"""

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message,
        },
    }


def _handle_request(message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """处理单条 JSON-RPC 消息。"""

    request_id = message.get("id")
    method = str(message.get("method") or "")
    params = message.get("params")
    if not isinstance(params, dict):
        params = {}

    if request_id is None:
        return None

    if method == "initialize":
        protocol_version = str(params.get("protocolVersion") or "2024-11-05")
        return _response(
            request_id,
            {
                "protocolVersion": protocol_version,
                "capabilities": {
                    "tools": {
                        "listChanged": False,
                    },
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION,
                },
            },
        )

    if method == "ping":
        return _response(request_id, {})

    if method == "tools/list":
        return _response(request_id, {"tools": _tool_specs()})

    if method == "tools/call":
        tool_name = str(params.get("name") or "")
        return _response(request_id, _call_tool(tool_name))

    return _error_response(request_id, -32601, f"方法不存在: {method}")


def _write_message(message: Dict[str, Any]) -> None:
    """向 stdout 写入单条 JSON-RPC 消息。"""

    sys.stdout.write(json.dumps(message, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def main() -> None:
    """运行 MCP stdio 消息循环。"""

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
            if not isinstance(message, dict):
                raise ValueError("JSON-RPC 消息必须是对象")
            response = _handle_request(message)
        except Exception as exc:
            response = _error_response(None, -32603, str(exc))

        if response is not None:
            _write_message(response)


if __name__ == "__main__":
    main()

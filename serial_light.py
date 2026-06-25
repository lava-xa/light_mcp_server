"""Zayu 灯光串口控制。"""

from typing import List, Optional

import glob
import os
import time


DEFAULT_BAUD_RATE = 115200
PORT_PATTERNS: tuple[str, ...] = (
    "/dev/ttyUSB*",
    "/dev/ttyACM*",
    "/dev/cu.usbserial*",
    "/dev/cu.SLAB_USBtoUART*",
    "/dev/cu.wchusbserial*",
    "COM*",
)


def find_port(configured_port: Optional[str] = None) -> str:
    """查找 ESP32 串口。"""

    if configured_port:
        return configured_port

    env_port = os.environ.get("ESP32_PORT")
    if env_port:
        return env_port

    ports: List[str] = []
    for pattern in PORT_PATTERNS:
        ports.extend(glob.glob(pattern))

    if not ports:
        raise RuntimeError("未找到 ESP32 串口，请设置 ESP32_PORT，例如 ESP32_PORT=/dev/ttyUSB0")

    return sorted(ports)[0]


def send_value(value: str, configured_port: Optional[str] = None) -> str:
    """向 ESP32 串口发送指定值。"""

    try:
        import serial
    except ImportError as exc:
        raise RuntimeError("缺少 pyserial 依赖，请先安装 pyserial 后再控制灯光") from exc

    baud_rate = int(os.environ.get("ESP32_BAUD", str(DEFAULT_BAUD_RATE)))
    port = find_port(configured_port)
    with serial.Serial(port, baud_rate, timeout=1) as esp32:
        time.sleep(2)
        esp32.write(value.encode("ascii"))
        esp32.flush()

    return f"已向 {port} 发送 {value}"


def turn_on() -> str:
    """打开灯光。"""

    return send_value("0")


def turn_off() -> str:
    """关闭灯光。"""

    return send_value("1")

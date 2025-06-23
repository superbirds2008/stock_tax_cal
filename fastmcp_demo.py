#!/usr/bin/env python3
import logging
from fastmcp import FastMCP
import time

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 MCP 服务器
mcp = FastMCP(
    name="Demo",
    # description="A simple FastMCP demo server",
)

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    logger.info("Executing add(%d, %d)", a, b)
    mcp.send_event("status", {"message": f"Processing add({a}, {b})"})
    # 模拟处理时间
    time.sleep(1)
    mcp.send_event("status", {"message": "Add operation completed"})
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    mcp.send_event("status", {"message": f"Processing multiple({a}, {b})"})
    # 模拟处理时间
    time.sleep(1)
    mcp.send_event("status", {"message": "Multiply operation completed"})
    logger.info("Executing multiply(%d, %d)", a, b)
    return a * b

def main():
    logger.info("Starting MCP server 'Demo'...")
    try:
        # mcp.run(transport="stdio"
        # 如需 HTTP 通信，取消下行注
        # mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)
        mcp.run(transport="sse", host="0.0.0.0", port=8080)
    except Exception as e:
        logger.exception("Unexpected error:")

if __name__ == "__main__":
    main()

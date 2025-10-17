import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".xiaozhi_mcp_config.json"

def load_config():
    # 优先从环境变量读取，避免硬编码泄露
    env_mcp = os.environ.get("MCP_ENDPOINT", "")
    env_zhipu = os.environ.get("ZHIPU_API_KEY", "")
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            file_cfg = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        file_cfg = {}
    return {
        "MCP_ENDPOINT": env_mcp or file_cfg.get("MCP_ENDPOINT", ""),
        "ZHIPU_API_KEY": env_zhipu or file_cfg.get("ZHIPU_API_KEY", ""),
    }

def save_config(config):
    # 仅保存非敏感配置，密钥不写入磁盘
    safe_config = {
        "MCP_ENDPOINT": str(config.get("MCP_ENDPOINT", "")),
    }
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(safe_config, f, indent=2)
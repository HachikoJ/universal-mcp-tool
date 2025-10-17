# Universal MCP Tool

一个将任意 HTTP API 动态注册为 MCP（Model Context Protocol）工具的实用组件，支持图形界面（GUI）管理与测试、持久化配置、自动注册为 MCP 工具并通过 WebSocket 端点与上层系统交互。

适合将已有业务 API 快速“接入”到支持 MCP 的 AI 助手或应用中。

---

## 功能概览

- 动态注册 API 为 MCP 工具（支持 GET/POST）
- GUI 图形界面：
  - 录入/修改/删除 API 配置
  - 可视化测试 API（请求参数填写、响应展示与基本校验）
  - 启动后台服务并查看日志
- 自动持久化 API 配置到 `api_configs.json`
- 从 `.env` 与用户主目录 `~/.xiaozhi_mcp_config.json` 读取 MCP 端点与密钥（密钥优先用环境变量，不落盘）
- 通过 `mcp_pipe.py` 将本地 MCP 脚本进程的 stdin/stdout/stderr 转发到 WebSocket 端点，支持断线重连与指数退避
- 规范日志输出：`universal_mcp.log`、`mcp_pipe.log`

---

## 目录结构与关键文件

- `universal_mcp_tool.py`  
  核心服务：使用 FastMCP 启动并将配置的 API 注册为 MCP 工具；提供管理工具（注册/列出/删除）。

- `universal_mcp_gui.py`  
  GUI 应用：管理 MCP 端点与 API 列表，支持新增/编辑/测试 API、启动服务与查看日志。

- `mcp_pipe.py`  
  连接器：将 MCP 脚本（如 `universal_mcp_tool.py`）的输入输出与 WebSocket 端点双向转发，支持断线重连。

- `config_manager.py`  
  配置读写：从环境变量与 `~/.xiaozhi_mcp_config.json` 读取 MCP 端点与密钥；仅保存非敏感配置。

- `启动_universal_mcp.py`  
  入口脚本：启动 GUI。

- `.env.example`  
  环境变量示例（复制为 `.env` 后填写真实值）。

- `requirements.txt`  
  Python 依赖列表。

- `README.md`  
  项目说明文档。

---

## 架构与数据流

- 启动方式一（推荐）：GUI
  1. 运行 `启动_universal_mcp.py` 打开 GUI，配置 MCP 端点并管理 API。
  2. GUI 写入 `api_configs.json`，并通过按钮启动服务：创建临时批处理，调用 `mcp_pipe.py universal_mcp_tool.py`。
  3. `mcp_pipe.py` 读取 MCP_ENDPOINT，建立 WebSocket 连接，将来自端点的数据流转发给 `universal_mcp_tool.py`，并反向发送工具输出到端点。
  4. `universal_mcp_tool.py` 使用 FastMCP，将 `api_configs.json` 中的每个 API 注册为 MCP 工具。

- 启动方式二：手动 CLI
  - 直接运行 `python mcp_pipe.py universal_mcp_tool.py --endpoint wss://...` 或设置环境变量后 `python mcp_pipe.py universal_mcp_tool.py`。

---

## 环境要求

- Python 3.8+
- 操作系统：Windows / macOS / Linux
- 依赖（见 `requirements.txt`）：
  - zhipuai>=1.0.0
  - requests>=2.31.0
  - beautifulsoup4>=4.12.3
  - websockets>=12.0
  - python-dotenv>=1.0.0
  - fastmcp>=0.1.0

---

## 安装与初始化

1) 安装依赖
```bash
pip install -r requirements.txt
```

2) 配置环境变量（复制示例）
- 复制 `.env.example` 为 `.env` 并填写真实值：
```env
MCP_ENDPOINT=wss://your-endpoint.example/mcp/?token=YOUR_TOKEN
ZHIPU_API_KEY=your-zhipu-api-key
```
- 或者在系统环境变量中设置（优先级高于配置文件）。

3) 首次运行 GUI（Windows PowerShell）
```powershell
python .\启动_universal_mcp.py
```

---

## 使用指南（GUI）

1) 基本配置
- 在“基本配置”页填写 MCP 端点（例如：`wss://example.com/mcp/?token=...`）
- 点击“保存配置”后，端点会写入 `~/.xiaozhi_mcp_config.json`（不含敏感信息）

2) 添加/修改 API
- 在“API管理”页右侧表单填写：
  - API名称（唯一）
  - API URL（完整路径）
  - 请求方法（GET/POST）
  - API描述（可选）
  - API密钥（可选，显示为“*”掩码）
  - 密钥位置：header/query/body
  - 密钥参数名：默认 Authorization；若为 Authorization 则以 Bearer 形式自动拼接
  - 请求参数格式（JSON）：键为参数名，值为类型（string/number/boolean/object/array）
  - 返回参数格式（JSON）：期望响应的顶层字段及类型（用于基本校验）
- 点击“保存API”，配置将写入 `api_configs.json`；若同名则覆盖。

3) 查看/删除/刷新
- 左侧列表显示已注册 API
- 支持刷新列表、删除选中、查看详情并回填到右侧表单

4) 测试 API
- 选中列表项，点击“测试API”
- 在弹窗中填写参数，发送请求后显示响应（自动尝试 JSON 解析与字段存在性校验）

5) 启动服务
- 在“日志”页点击“启动服务”，GUI 会创建批处理并后台执行：
  - `mcp_pipe.py universal_mcp_tool.py`
- 日志显示连接状态与错误信息；弹窗提示服务已在后台运行

---

## 使用指南（CLI）

- 直接运行工具（需要 MCP_ENDPOINT 环境变量或传参）
```bash
# 方式一：环境变量
export MCP_ENDPOINT="wss://your-endpoint.example/mcp/?token=YOUR_TOKEN"
python mcp_pipe.py universal_mcp_tool.py

# 方式二：命令行参数
python mcp_pipe.py universal_mcp_tool.py --endpoint "wss://your-endpoint.example/mcp/?token=YOUR_TOKEN"
```

- 仅运行 MCP 脚本（用于调试 FastMCP；通常结合 mcp_pipe 使用）
```bash
python universal_mcp_tool.py
```
注意：`universal_mcp_tool.py` 会读取 `MCP_ENDPOINT` 并尝试通过 stdio 运行 MCP 服务；生产场景建议用 `mcp_pipe.py` 连接到 WebSocket 端点。

---

## API 配置格式示例（api_configs.json）

```json
[
  {
    "api_name": "getWeather",
    "api_url": "https://api.example.com/weather",
    "method": "GET",
    "request_format": {
      "city": "string",
      "days": "number"
    },
    "response_format": {
      "status": "string",
      "data": "object"
    },
    "description": "查询天气",
    "api_key": "YOUR_API_KEY",
    "key_location": "header",
    "key_name": "Authorization"
  }
]
```

- 密钥放置规则：
  - header：若 `key_name` 为 `Authorization`，自动拼接为 `Bearer ${api_key}`；否则按原值放置
  - query：将 `key_name=api_key` 加入 URL 查询参数
  - body：将 `key_name: api_key` 加入请求体

---

## MCP 工具的注册与调用

- `universal_mcp_tool.py` 启动后，会将 `api_configs.json` 中的每个 API 注册为一个 MCP 工具，工具名即 `api_name`。
- 还提供管理工具：
  - `register_api(api_name, api_url, method, request_format, response_format, description, api_key?, key_location?, key_name?)`
  - `list_registered_apis()`
  - `remove_registered_api(api_name)`
- 当上层 MCP 客户端调用某工具时，本服务会按配置转换为 HTTP 请求并返回 JSON 响应。

---

## 日志与排错

- 日志文件
  - `universal_mcp.log`：服务端（MCP 工具）日志
  - `mcp_pipe.log`：连接器日志（含断线重连信息）
- 常见问题
  - 未设置 MCP_ENDPOINT
    - 解决：在 `.env` 或系统环境变量中设置 MCP_ENDPOINT，或在 GUI 配置后保存，或 CLI 传入 `--endpoint`
  - WebSocket 连接失败/频繁重连
    - 解决：检查端点地址、网络连通性与鉴权 token；`mcp_pipe.py` 已内置指数退避
  - API 响应非 JSON
    - 测试弹窗会显示原始文本并截断超长内容；如需兼容非 JSON，调整 `response_format` 校验逻辑或上层调用约定
  - API 密钥泄露风险
    - 密钥仅从环境变量读取并传递到请求，不写入磁盘；请勿将 `.env` 提交到仓库

---

## 安全实践

- 切勿将真实密钥写入仓库或 `~/.xiaozhi_mcp_config.json`
- `.env` 文件加入 `.gitignore`（已在仓库配置）
- 生产环境使用更细化的权限与网络访问控制
- 日志中不输出敏感字段；如需审计请做脱敏处理

---

## 开发与扩展建议

- 自定义认证方式：在 `universal_mcp_tool.py` 的 `_register_single_api` 中扩展 `key_location` 处理分支
- 响应校验增强：在 GUI 的 `_validate_response` 增加类型检测与嵌套结构校验
- 工具分组与分类：在 `api_configs.json` 增加分组字段，并在 GUI 列表中显示
- 错误重试与超时：在请求调用处增加重试与统一超时配置

---

## 运行示例（Windows）

```powershell
# 安装依赖
pip install -r .\requirements.txt

# 配置 .env
copy .env.example .env
# 编辑 .env 填写真实 MCP_ENDPOINT 与 ZHIPU_API_KEY

# 启动 GUI 并管理/测试 API
python .\启动_universal_mcp.py
```

---

## 许可

本项目未显式声明许可证。若需开源发布或二次分发，请先补充 LICENSE 并遵循依赖库的许可协议。

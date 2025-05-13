# Web Clipper

![版本](https://img.shields.io/badge/version-1.1-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![灵感来源](https://img.shields.io/badge/inspired%20by-goxofy/web_clipper-orange)

## 📝 项目概述

Web Clipper 是一个功能强大的网页剪藏后端服务。本项目借鉴了 [goxofy/web_clipper](https://github.com/goxofy/web_clipper) 的核心理念，旨在提供一个更稳定、更易于部署且功能更全面的网页内容存档和管理解决方案。

本服务能够将目标网页完整保存至 GitHub Pages 以供永久访问，自动提取关键信息并同步至 Notion 数据库，同时利用 AI 服务生成内容摘要与标签，并通过 Telegram 机器人实时推送剪藏通知。

## ✨ 主要特性

- 💾 **永久存档**：将网页完整快照保存至 GitHub Pages。
- 📚 **Notion 同步**：自动将网页元数据、摘要、标签及快照链接同步至指定的 Notion 数据库。
- 🤖 **智能处理**：
  - 集成 AI 服务自动生成内容摘要和关键词标签。
  - **高度灵活的 LLM 服务支持**：通过 `OPENAI_BASE_URL` 和 `OPENAI_API_KEY` 配置，可无缝对接任何兼容 OpenAI API 格式的大语言模型服务，例如官方 OpenAI、Deepseek、硅基流动 (SiliconFlow)、Kimi (Moonshot AI)、Google Gemini 的 OpenAI 兼容端点等。
- 📱 **即时通知**：通过 Telegram 机器人发送新增剪藏的实时通知。
- 🔒 **安全认证**：使用 API 密钥对所有请求进行认证，保障服务安全。
- 🔄 **健壮性设计**：内置自动重试机制，提高外部服务交互的成功率。
- 🐳 **容器化部署**：提供 Dockerfile，方便用户自行构建和部署。
- 🧩 **易于集成**：与 SingleFile 等浏览器插件良好兼容。

## 🏗️ 系统架构

应用采用现代化的 Python FastAPI 框架构建，模块化设计确保了代码的可维护性和扩展性。

```TXT
web_clipper/
├── .env                  # 环境变量配置文件 (用户需从 .env.example 复制创建)
├── .env.example          # 环境变量配置示例
├── Dockerfile            # Docker 构建文件
├── app/                  # 应用核心代码目录
│   ├── __init__.py       # FastAPI 应用实例化与初始化
│   ├── config.py         # 配置加载与管理模块
│   ├── routes.py         # API 路由定义
│   ├── services/         # 核心服务逻辑模块
│   │   ├── github.py     # GitHub Pages 交互服务
│   │   ├── notion.py     # Notion API 交互服务
│   │   ├── telegram.py   # Telegram Bot 通知服务
│   │   ├── ai.py         # AI (LLM) 服务交互模块
│   │   └── clipper.py    # 主剪藏处理流程协调器
│   └── utils.py          # 通用工具函数
├── main.py               # 应用主入口 (用于启动服务)
└── requirements.txt      # Python 依赖包列表
```

## 🚀 部署方式

**重要提示**：本项目目前**未发布**预构建的 Docker 镜像到 Docker Hub 或其他公共镜像仓库。用户需要通过以下方式进行部署：

1. **自行构建 Docker 镜像** (推荐)
2. **本地直接运行** (适用于开发或测试)

### 🐳 使用 Docker 部署 (推荐)

#### 前置条件

- Docker 已正确安装并运行。
- Git 已安装 (用于克隆项目仓库)。

#### 部署步骤

1. **克隆项目代码**：

    ```bash
    git clone https://github.com/melosbot/WebClipper.git web_clipper
    cd web_clipper
    ```

2. **配置环境变量**：
    - 复制环境变量示例文件：

        ```bash
        cp .env.example .env
        ```

    - 使用文本编辑器 (如 `nano`, `vim`) 打开并编辑 `.env` 文件，填入所有必要的配置信息 (详见下一章节)。

        ```bash
        nano .env
        ```

3. **构建 Docker 镜像**：
    在项目根目录下执行：

    ```bash
    docker build -t web-clipper:latest .
    ```

4. **运行 Docker 容器**：

    ```bash
    docker run -d \
      --name web-clipper \
      -p 65331:65331 \
      --restart unless-stopped \
      --env-file .env \
      web-clipper:latest
    ```

    - `-d`: 后台运行容器。
    - `--name`: 为容器指定一个名称。
    - `-p 65331:65331`: 将主机的 65331 端口映射到容器的 65331 端口。
    - `--restart unless-stopped`: 容器退出时自动重启，除非手动停止。
    - `--env-file .env`: 从 `.env` 文件加载环境变量。

5. **查看服务日志** (用于调试或监控)：

    ```bash
    docker logs -f web-clipper
    ```

#### Docker 管理命令

- **停止容器**：`docker stop web-clipper`
- **启动容器**：`docker start web-clipper`
- **删除容器**：`docker rm -f web-clipper`
- **查看容器状态**：`docker ps -a | grep web-clipper`

### 💻 本地直接运行 (适用于开发与测试)

1. **克隆项目并进入目录** (同上)。
2. **配置环境变量** (同上，创建并编辑 `.env` 文件)。
3. **创建并激活 Python 虚拟环境** (推荐)：

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate    # Windows
    ```

4. **安装依赖**：

    ```bash
    pip install -r requirements.txt
    ```

5. **启动服务**：

    ```bash
    python main.py
    ```

    服务将在 `.env` 文件中配置的 HOST 和 PORT (默认为 `0.0.0.0:65331`) 上运行。

## 🔧 环境变量配置 (`.env` 文件)

请根据 `.env.example` 文件创建并编辑您自己的 `.env` 文件。

### 服务器配置 (Server Configuration)

```env
HOST=0.0.0.0      # 应用监听的 IP 地址
PORT=65331        # 应用监听的端口
```

### GitHub 配置

```env
GITHUB_REPO=your_github_username/your_repo_name    # 您的 GitHub 用户名和用于存储快照的仓库名
GITHUB_TOKEN=your_github_personal_access_token    # GitHub Personal Access Token (PAT)
GITHUB_PAGES_DOMAIN=your_username.github.io       # GitHub Pages 域名 (若使用自定义域名，请填写)
GITHUB_PAGES_MAX_RETRIES=60                       # GitHub Pages 部署成功检查的最大重试次数 (每次间隔 5 秒)
```

**获取 GitHub Token**:

- 访问 [GitHub Tokens](https://github.com/settings/tokens)。
- 点击 "Generate new token" -> "Generate new token (classic)"。
- 勾选 `repo` scope (完全控制私有仓库)。
- 生成并妥善保管 Token。
**获取 GitHub Pages Domain**:
- 在 `GITHUB_REPO` 指定的仓库中，进入 Settings > Pages。
- 配置 Source 为从 `main` 分支 (或您选择的分支) 的 `/root` 目录部署。
- 部署成功后，GitHub Pages 会提供一个域名，通常是 `your_username.github.io/your_repo_name`。**本项目期望的是顶级域名或子域名，例如 `your_username.github.io`。生成的快照会在此域名下的 `/<your_repo_name>/clips/` 路径。** 如果您在 `.env` 中填的是 `your_username.github.io/your_repo_name`，请确保代码中处理 URL 拼接的逻辑与此一致。通常，直接填写 `your_username.github.io` 即可。

### Notion 配置

```env
NOTION_DATABASE_ID=your_notion_database_id  # Notion 数据库 ID
NOTION_TOKEN=your_notion_integration_token  # Notion Integration Token
```

**获取 Notion 配置**:

1. **Database ID**:
    - 在 Notion 中创建一个新的数据库 (Table view)。
    - **必须包含以下列 (大小写敏感，类型需匹配)**:
        - `Title` (Title 类型)
        - `OriginalURL` (URL 类型)
        - `SnapshotURL` (URL 类型)
        - `Summary` (Text/Rich Text 类型)
        - `Tags` (Multi-select 类型)
        - `Created` (Date 类型, 'Last edited time' 或 'Created time' 均可，但推荐 'Created time')
    - 从数据库 URL 中提取 ID。例如，如果 URL 是 `https://www.notion.so/your-workspace/abcdef1234567890abcdef1234567890?v=...`，则 `abcdef1234567890abcdef1234567890` 就是 Database ID。
2. **Integration Token**:
    - 访问 [Notion My Integrations](https://www.notion.so/my-integrations)。
    - 点击 "New integration"，填写名称，选择关联的工作区。
    - 提交后，复制 "Internal Integration Token"。
    - 返回到您创建的 Notion 数据库页面，点击右上角的三个点 (...) -> "Add connections" -> 搜索并选择您创建的集成，授予其编辑权限。

### Telegram 配置

```env
TELEGRAM_TOKEN=your_telegram_bot_token        # Telegram Bot Token
TELEGRAM_CHAT_ID=your_telegram_chat_id      # 接收通知的 Telegram Chat ID
```

**获取 Telegram 配置**:

1. **Bot Token**:
    - 在 Telegram 中搜索并与 [@BotFather_Official_Original_Production](https://t.me/BotFather) (或公认的 BotFather) 对话。
    - 发送 `/newbot` 命令，按照提示创建机器人，获取 Token。
2. **Chat ID**:
    - 有多种方法，一种简单的是：
        - 将您创建的 Bot 添加到目标聊天 (可以是私聊或群组)。
        - 向 Bot (或在 Bot 所在的群组中) 发送任意消息。
        - 在浏览器中访问 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` (将 `<YOUR_BOT_TOKEN>` 替换为您的真实 Token)。
        - 在返回的 JSON 数据中，找到 `result[].message.chat.id` 或 `result[].my_chat_member.chat.id`，这就是您的 Chat ID。

### OpenAI (及兼容服务) 配置

```env
OPENAI_API_KEY=your_llm_service_api_key          # 您选择的 LLM 服务的 API Key
OPENAI_BASE_URL=https://api.openai.com/v1      # LLM 服务的 API 端点
OPENAI_MODEL=gpt-4o-mini                         # 使用的 LLM 模型名称
OPENAI_MAX_RETRIES=3                             # API 调用失败时的最大重试次数
```

**重点**: 此配置**不仅仅局限于 OpenAI 官方服务**。

- `OPENAI_API_KEY`: 填入您所选服务的 API 密钥。
- `OPENAI_BASE_URL`:
  - OpenAI 官方: `https://api.openai.com/v1`
  - Deepseek: `https://api.deepseek.com/v1`
  - 硅基流动 (SiliconFlow): 通常是 `https://api.siliconflow.cn/v1` 或其提供的端点。
  - Kimi (Moonshot AI): `https://api.moonshot.cn/v1`
  - Google Gemini (OpenAI 兼容端点): 请查阅 Gemini 的最新文档获取其 OpenAI 格式的 API 端点。
  - 其他兼容服务商：请查阅其文档获取对应的 Base URL。
- `OPENAI_MODEL`: 填入对应服务商提供的模型名称，例如 `deepseek-chat`, `gpt-3.5-turbo`, `moonshot-v1-8k` 等。

### API 安全配置

```env
API_KEY=generate_a_strong_random_api_key     # 用于认证客户端请求的 API 密钥
```

**生成 API Key**:

- 强烈建议生成一个长而随机的字符串。可以使用密码管理器或以下命令生成：

    ```bash
    openssl rand -base64 32
    ```

### 文件限制配置

```env
MAX_FILE_SIZE=31457280          # (字节) 允许上传的最大文件大小，默认为 30MB
ALLOWED_EXTENSIONS=.html,.htm   # 允许上传的文件扩展名列表，逗号分隔
```

## 🧩 浏览器插件集成 (SingleFile)

推荐使用 [SingleFile](https://github.com/gildas-lormeau/SingleFile) 浏览器插件将网页发送到本服务。

### 安装 SingleFile

- Chrome: [Chrome Web Store](https://chromewebstore.google.com/detail/singlefile/mpiodijhokgodhhofbcjdecpffjipkle)
- Firefox: [Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/single-file/)
- Edge: [Microsoft Edge Add-ons](https://microsoftedge.microsoft.com/addons/detail/singlefile/efnbkdcfmcmnhlkaijjjmgpoacobhahdd)

### SingleFile 插件详细配置

在 SingleFile 插件的设置中，按如下方式配置 (配置一次即可，支持通过浏览器账户云端同步配置)：

1. **File naming (文件名)**:
    - Filename template (文件名模版): `{url-host}{url-pathname-flat}.{filename-extension}`
    - Maximum length (文件名最大长度): `384` characters (字符)
    - Replacement character (文件名替换字符): `$`

2. **Destination (保存位置)**:
    - Save to > **REST form API**
        - URL (网址): `http://your-server-ip:your-port/upload`
            - 将 `your-server-ip` 替换为运行 Web Clipper Enhanced 服务的主机 IP 地址或域名。
            - 将 `your-port` 替换为 `.env` 文件中配置的 `PORT` (默认为 `65331`)。
            - **重要**: 确保您的服务可以从运行浏览器的设备访问到该地址和端口 (例如，在同一局域网，或已配置公网访问和防火墙规则)。
        - Authorization token (授权令牌): `your_api_key`
            - 这必须与您在 `.env` 文件中设置的 `API_KEY` 完全一致。
        - File field name (文件字段名称): `singlehtmlfile`
        - URL field name (网址字段名称): `url`

配置完成后，当您在浏览器中点击 SingleFile 图标并选择保存时，它会将当前页面的 HTML 内容和原始 URL 发送到您的 Web Clipper Enhanced 服务。

## 📚 API 使用文档

### 认证机制

所有 API 请求都需要在 HTTP Header 中包含 Bearer Token 认证：
`Authorization: Bearer YOUR_API_KEY`
其中 `YOUR_API_KEY` 是您在 `.env` 文件中配置的 `API_KEY`。

### API 端点

#### 1. 上传网页进行剪藏

- **Endpoint**: `/upload` (同时也支持 `/upload/`)
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Authentication**: Bearer Token (required)
- **Form Data Parameters**:
  - `singlehtmlfile`: (file, required) 导出的 HTML 文件内容。
  - `url`: (string, optional) 原始网页的 URL。如果插件未提供，服务会尝试从文件名解析（但准确性较低）。
- **Success Response (200 OK)**:

    ```json
    {
        "status": "success",
        "github_url": "https://your_username.github.io/your_repo_name/clips/your_clip_filename.html",
        "notion_url": "https://www.notion.so/your_page_id"
    }
    ```

- **Error Responses**:
  - `400 Bad Request`: 请求参数错误 (如缺少文件，文件过大，类型不支持)。
  - `401 Unauthorized`: API 密钥无效或未提供。
  - `403 Forbidden`: (通常是401的另一种表现，或特定限流策略)
  - `500 Internal Server Error`: 服务器内部处理错误。

#### 2. 测试认证接口

- **Endpoint**: `/test-auth`
- **Method**: `GET`
- **Authentication**: Bearer Token (required)
- **Success Response (200 OK)**:

    ```json
    {
        "message": "认证成功",
        "api_key_prefix": "your_" // API Key 的前缀，用于调试
    }
    ```

### 使用 `curl` 测试 API

#### 测试认证

```bash
curl -X GET "http://<YOUR_SERVER_IP_OR_DOMAIN>:<PORT>/test-auth" \
     -H "Authorization: Bearer <YOUR_API_KEY>"
```

#### 上传文件进行剪藏

```bash
curl -X POST "http://<YOUR_SERVER_IP_OR_DOMAIN>:<PORT>/upload" \
     -H "Authorization: Bearer <YOUR_API_KEY>" \
     -F "singlehtmlfile=@/path/to/your/local/webpage.html" \
     -F "url=https://original-webpage-url.com"
```

替换尖括号中的占位符为您实际的配置。

## 🔍 故障排除

- **401/403 认证错误**:
  - 确保 `.env` 文件中的 `API_KEY` 与客户端 (SingleFile 或 curl) 提供的 Bearer Token 完全一致，无多余空格。
  - 检查服务启动日志中 `API 密钥前缀` 是否与预期一致。
- **服务无法启动**:
  - 检查 `.env` 文件是否存在且所有必需项均已配置。
  - 查看 `docker logs web-clipper` 或控制台输出来获取详细错误信息。
  - 确保配置的端口未被其他程序占用。
- **GitHub Pages 更新缓慢**:
  - GitHub Pages 部署通常需要 1-5 分钟。`GITHUB_PAGES_MAX_RETRIES` 控制等待时间。
- **AI 摘要/标签生成失败**:
  - 验证 `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` 是否为您的 LLM 服务提供商正确配置。
  - 检查您的 LLM 服务账户是否有足够的额度或有效的订阅。
- **SingleFile 插件无法连接**:
  - 确认服务 IP 和端口配置正确，并且服务正在运行。
  - 检查防火墙设置，确保浏览器所在设备可以访问服务端口。

## 🙏 致谢 (Acknowledgements)

本项目灵感来源于并优化了 [goxofy/web_clipper](https://github.com/goxofy/web_clipper) 项目。感谢原作者的工作为本项目提供了坚实的基础。

## 📝 许可证 (License)

本项目采用 [MIT License](LICENSE) 开源。

###
纯ai战神，能不手写就不手写
###

# AgentBot

一个基于 LangChain 和 Streamlit 的智能对话助手，支持 RAG（检索增强生成）功能。

## 功能特性

- 🤖 智能对话：基于大语言模型的对话功能
- 📚 知识库检索：支持文档上传和检索增强生成
- 🖥️ Web 界面：基于 Streamlit 的用户友好界面
- 🔧 多模型支持：支持 OpenAI、Tongyi Qianwen、Ollama 等多种 LLM 提供商
- 📁 文件处理：支持 PDF、MD、TXT 等格式文档的自动分块和向量化

## 快速开始

### 环境要求

- Python 3.8+
- Git

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/AgentBot.git
   cd AgentBot
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   创建 `.env` 文件并设置 API keys：
   ```bash
   DASHSCOPE_API_KEY=your_dashscope_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   打开 configs/config.yaml，设置 chat_provider 和其他参数：
   chat_provider: openai  # 或 qwen, ollama, lmstudio
   其他参数根据需要调整，如 temperature、max_tokens 等

   ```

5. **初始化知识库(不用做，自己想要的文档添加进data/external,或者在web界面添加）**
   ```bash
   python scripts/init_db.py
   ```

6. **启动 Web 界面**
   ```bash
   # Windows
   run_web.bat
   # 或
   python run_web.py
   ```

   访问 `http://localhost:8502`

## 配置说明

### 主要配置文件

- `configs/config.yaml`：系统配置，包括 LLM 设置、RAG 参数等
- `configs/prompts/`：提示词模板
- `data/external/`：知识库文档存放目录

### 支持的 LLM 提供商

- **Tongyi Qianwen**：设置 `chat_provider: qwen`
- **OpenAI**：设置 `chat_provider: openai`
- **Ollama**：设置 `chat_provider: ollama`
- **LMStudio**：设置 `chat_provider: lmstudio`

## 项目结构

```
AgentBot/
├── app/                    # 应用核心代码
│   ├── agent/             # Agent 相关
│   ├── rag/               # RAG 功能
│   └── memory/            # 会话管理
├── configs/               # 配置文件
├── data/                  # 数据目录
├── infrastructure/        # 基础设施
├── logs/                  # 日志文件
├── scripts/               # 工具脚本
├── tests/                 # 测试代码
├── web/                   # Web 界面
├── requirements.txt       # 依赖列表
└── run_web.py            # 启动脚本
```

## 使用说明

1. **对话功能**：在主界面输入问题，与 AI 对话
2. **知识库管理**：
   - 侧边栏显示当前知识库文件
   - 点击"刷新知识库"更新向量库
   - 上传新文档到知识库
3. **参数调整**：在侧边栏调整 Temperature 等参数

## 开发说明

### 运行测试
```bash
python -m pytest tests/
```

### 添加新工具
在 `app/agent/tools/` 下添加新的工具类

### 扩展 RAG
修改 `app/rag/` 下的组件以扩展检索功能

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请通过 GitHub Issues 联系。

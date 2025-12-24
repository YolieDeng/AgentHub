# AgentHub

一个基于 LangGraph 的智能 AI Agent 应用，支持多轮对话、工具调用和长期记忆。

## 技术栈

### 后端
| 技术 | 用途 |
|------|------|
| **FastAPI** | 高性能 Web 框架 |
| **LangGraph** | 图工作流引擎，支持状态持久化 |
| **Ollama** | 本地 LLM 推理 (qwen2.5:3b) |
| **Mem0** | 长期记忆系统 (PgVector 向量存储) |
| **PostgreSQL** | 数据库 |
| **JWT** | 用户认证 |

### 前端
| 技术 | 用途 |
|------|------|
| **React 19** | UI 库 |
| **TypeScript** | 类型安全 |
| **Vite** | 构建工具 |
| **Tailwind CSS** | 样式框架 |
| **Radix UI** | 无障碍组件库 |

## 已实现功能

### 1. 用户认证
- 邮箱注册/登录
- JWT 令牌认证 (30天有效期)
- Bcrypt 密码加密

### 2. 智能对话
- 基于 LangGraph 的 Agent 工作流
- 流式响应 (Server-Sent Events)
- 对话状态持久化到 PostgreSQL

### 3. 工具调用
| 工具 | 功能 |
|------|------|
| `get_current_time` | 获取当前时间 |
| `calculate` | 数学表达式计算 |

### 4. 长期记忆
- 基于 Mem0 的向量记忆系统
- 跨会话的用户信息记忆
- 语义搜索相关记忆并注入到对话上下文

### 5. 会话管理
- 多会话支持
- 历史消息持久化
- 会话列表展示与切换

### 6. 响应式 UI
- 桌面端侧边栏导航
- 移动端抽屉式导航
- 深色主题

## 数据库表说明

| 表名 | 来源 | 用途 |
|------|------|------|
| `user` | 应用 | 用户账户信息 |
| `session` | 应用 | 聊天会话记录 |
| `checkpoints` | LangGraph | 对话状态快照 |
| `checkpoint_blobs` | LangGraph | 检查点二进制数据 |
| `checkpoint_migrations` | LangGraph | 检查点迁移记录 |
| `checkpoint_writes` | LangGraph | 检查点写入记录 |
| `longterm_memory` | Mem0 | 长期记忆向量存储 |
| `mem0migrations` | Mem0 | Mem0 迁移记录 |

## 项目结构

```
AgentHub/
├── app/                          # 后端
│   ├── api/                      # API 路由
│   │   ├── auth.py               # 认证接口
│   │   └── chat.py               # 聊天接口
│   ├── core/
│   │   ├── config.py             # 配置管理
│   │   ├── logging.py            # 日志系统
│   │   └── langgraph/
│   │       ├── graph.py          # Agent 工作流
│   │       └── tools.py          # 工具定义
│   ├── models/                   # 数据模型
│   ├── services/                 # 业务服务
│   │   ├── database.py           # 数据库服务
│   │   └── llm.py                # LLM 服务
│   └── main.py                   # 应用入口
├── frontend/                     # 前端
│   └── src/
│       ├── pages/                # 页面组件
│       ├── components/           # UI 组件
│       ├── contexts/             # React Context
│       └── services/             # API 服务
└── pyproject.toml
```

## API 接口

### 认证
| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| GET | `/api/auth/me` | 获取当前用户 |

### 聊天
| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/chat` | 发送消息 |
| POST | `/api/chat/stream` | 流式聊天 |
| GET | `/api/chat/sessions` | 获取会话列表 |
| GET | `/api/chat/history/{session_id}` | 获取会话历史 |
| DELETE | `/api/chat/history/{session_id}` | 清除会话 |

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- PostgreSQL (推荐使用 Supabase)
- Ollama (本地 LLM)

### 安装依赖

```bash
# 后端
uv sync

# 前端
cd frontend && npm install
```

### 配置环境变量

创建 `.env` 文件：

```env
# 数据库
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=54322
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_LLM_MODEL=qwen2.5:3b

# JWT
JWT_SECRET_KEY=your-secret-key
```

### 启动服务

```bash
# 后端
make dev

# 前端
cd frontend && npm run dev
```

访问 http://localhost:3000

## License

MIT

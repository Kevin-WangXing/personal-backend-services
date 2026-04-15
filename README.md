# FastAPI 演示服务器

一个简单的 FastAPI 后端服务，运行在端口 9000 上，支持 GET、POST、PUT、DELETE 请求。

## 功能特性

- FastAPI 框架，自动生成 OpenAPI 文档
- 运行在端口 9000
- 支持 RESTful API
- 包含健康检查端点
- 内存存储示例数据
- 完整的错误处理

## 安装和运行

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动服务器
```bash
python main.py
```

服务器将在 `http://localhost:9000` 启动。

### 3. 访问 API 文档
启动服务器后，可以通过以下地址访问交互式 API 文档：
- Swagger UI: http://localhost:9000/docs
- ReDoc: http://localhost:9000/redoc

## API 端点

### 根路径
- `GET /` - 服务器信息和可用端点列表

### 健康检查
- `GET /health` - 健康状态检查

### 项目管理
- `GET /items` - 获取所有项目
- `GET /items/{item_id}` - 获取单个项目
- `POST /items` - 创建新项目
- `PUT /items/{item_id}` - 更新项目
- `DELETE /items/{item_id}` - 删除项目

### 其他功能
- `POST /echo` - 回显接收到的数据

## 测试

### 1. 启动服务器
```bash
python main.py
```

### 2. 运行测试客户端（另一个终端）
```bash
python test_client.py
```

### 3. 手动测试示例

#### 使用 curl 测试：
```bash
# 获取根路径信息
curl http://localhost:9000/

# 健康检查
curl http://localhost:9000/health

# 获取所有项目
curl http://localhost:9000/items

# 获取单个项目
curl http://localhost:9000/items/1

# 创建新项目
curl -X POST http://localhost:9000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"测试项目","description":"描述","price":99.99,"tax":9.9}'

# 更新项目
curl -X PUT http://localhost:9000/items/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"更新名称","price":149.99}'

# 删除项目
curl -X DELETE http://localhost:9000/items/2

# 回显测试
curl -X POST http://localhost:9000/echo \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","number":42}'
```

## 项目结构
```
fastapi_demo/
├── main.py              # 主应用程序
├── requirements.txt     # Python 依赖
├── test_client.py       # REST API 测试客户端
├── ai_drawing_test.py   # AI绘图功能测试
├── README.md           # 主说明文档
├── README_AI_DRAWING.md # AI绘图功能详细文档
├── mvp_requirements.md  # MVP需求文档
├── .env.example        # 环境变量示例
├── .env               # 环境变量（不要提交）
└── venv/              # Python虚拟环境
```

## 依赖
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- pydantic==2.5.0
- requests>=2.31.0
- python-dotenv>=1.0.0

## AI绘图功能
项目已集成NVIDIA Stable Diffusion 3 AI绘图功能：

### 快速开始
1. 复制 `.env.example` 为 `.env`
2. 获取NVIDIA API密钥并填入 `.env` 文件
3. 启动服务器后即可使用AI绘图功能

### 主要端点
- `POST /ai/draw` - 创建绘图任务
- `GET /ai/draw/{task_id}/status` - 查询任务状态
- `GET /ai/draw/history` - 获取绘图历史

详细文档请参考 `README_AI_DRAWING.md`

## 注意事项
1. 确保端口 9000 未被占用
2. 数据存储在内存中，重启服务器后数据会丢失
3. 生产环境请添加适当的验证和安全措施
4. AI绘图功能需要有效的NVIDIA API密钥
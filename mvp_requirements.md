# MVP 需求文档：AI绘图功能集成

## 项目概述
在现有的 FastAPI 项目中集成英伟达（NVIDIA）Stable Diffusion 3 绘图模型，为用户提供 AI 绘图能力。

## 功能需求

### 1. 核心功能
1. **文本生成图片**：根据用户输入的 prompt 生成图片
2. **图片状态查询**：根据任务ID查询生成状态
3. **图片下载**：根据任务ID下载生成的图片
4. **历史任务查询**：查看用户的所有绘图任务

### 2. API 设计

#### 2.1 创建绘图任务
```http
POST /ai/draw
Content-Type: application/json

{
    "prompt": "Vintage, steampunk-inspired airship soaring above a sprawling, Victorian-era cityscape",
    "cfg_scale": 5,
    "aspect_ratio": "16:9",
    "seed": 0,
    "steps": 50,
    "negative_prompt": ""
}
```

**响应：**
```json
{
    "task_id": "uuid-string",
    "status": "queued",
    "message": "Task created successfully",
    "created_at": "2026-04-09T10:00:00Z"
}
```

#### 2.2 查询任务状态
```http
GET /ai/draw/{task_id}/status
```

**响应：**
```json
{
    "task_id": "uuid-string",
    "status": "completed",  // queued, processing, completed, failed
    "progress": 100,
    "estimated_seconds_remaining": 0,
    "result": {
        "image_url": "https://example.com/images/{task_id}.png",
        "download_url": "/ai/draw/{task_id}/download"
    }
}
```

#### 2.3 下载图片（所有图片）
```http
GET /ai/draw/{task_id}/download
```

**响应：**
- 如果只有一张图片：直接返回JPEG图片文件
- 如果有多张图片：返回JSON包含所有图片的下载链接

#### 2.4 下载特定图片
```http
GET /ai/draw/{task_id}/download/{filename}
```

**响应：** 返回指定的JPEG图片文件

#### 2.5 查询历史任务
```http
GET /ai/draw/history
```

**响应：**
```json
{
    "tasks": [
        {
            "task_id": "uuid-string",
            "prompt": "Vintage steampunk airship...",
            "status": "completed",
            "created_at": "2026-04-09T10:00:00Z",
            "completed_at": "2026-04-09T10:01:30Z"
        }
    ],
    "total": 1
}
```

### 3. 技术实现

#### 3.1 环境配置
```python
# .env 文件配置
NVIDIA_API_KEY=your_api_key_here
NVIDIA_API_BASE_URL=https://ai.api.nvidia.com/v1/genai
MODEL_NAME=stabilityai/stable-diffusion-3-medium

# 可选配置
MAX_STEPS=50
DEFAULT_CFG_SCALE=5
DEFAULT_ASPECT_RATIO="16:9"
```

#### 3.2 数据模型
```python
class DrawingRequest(BaseModel):
    prompt: str
    cfg_scale: float = 5
    aspect_ratio: str = "16:9"
    seed: int = 0
    steps: int = 50
    negative_prompt: str = ""

class DrawingTask(BaseModel):
    task_id: str
    prompt: str
    status: str  # queued, processing, completed, failed
    created_at: datetime
    updated_at: datetime
    result_url: Optional[str] = None
    error_message: Optional[str] = None
```

#### 3.3 任务状态机
```
queued → processing → completed
               ↓
            failed
```

### 4. 数据库设计（内存存储）
```python
# 任务存储
drawing_tasks = {
    "task_id": {
        "task_id": "uuid",
        "prompt": "prompt text",
        "status": "queued",
        "created_at": "timestamp",
        "updated_at": "timestamp",
        "result": "nvidia_api_response",
        "error_message": "optional_error",
        "image_files": [
            {
                "filename": "{task_id}_0.jpg",
                "filepath": "./storage/images/{task_id}_0.jpg",
                "url": "/ai/draw/{task_id}/download/{task_id}_0.jpg",
                "size_bytes": 123456,
                "format": "jpeg"
            }
        ]
    }
}
```

### 5. 日志系统
```python
# 日志文件结构
logs/
├── app_YYYYMMDD.log          # 应用主日志
├── ai_drawing_YYYYMMDD.log   # AI绘图专用日志
├── api_access_YYYYMMDD.log   # API访问日志
└── errors_YYYYMMDD.log       # 错误日志

# 日志级别
- INFO: 正常操作日志
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误
```

### 6. 错误处理
- **400**: 请求参数错误
- **404**: 任务不存在
- **429**: API调用频率限制
- **500**: 内部服务器错误
- **503**: NVIDIA API服务不可用

### 7. 异步处理
- 使用 FastAPI 的 `BackgroundTasks` 异步调用 NVIDIA API
- 定期轮询任务状态更新
- 支持Webhook回调（可选）

## 文件结构
```
fastapi_demo/
├── main.py                      # 主应用
├── ai_drawing.py               # AI绘图模块
├── storage/
│   ├── images/                 # 生成的图片
│   └── tasks.json             # 任务记录（可选）
├── requirements.txt            # 依赖
└── .env                       # 环境变量
```

## 依赖更新
需要在 `requirements.txt` 中添加：
```
requests>=2.31.0
python-dotenv>=1.0.0
uuid>=1.30
```

## MVP 实现优先级

### Phase 1（核心MVP）✅ 全部实现
1. ✅ 创建绘图任务API
2. ✅ 调用NVIDIA API生成图片
3. ✅ 返回任务ID和状态
4. ✅ 图片下载功能（支持单张/多张下载）
5. ✅ 图片链接返回
6. ✅ 完整日志系统
7. ✅ 历史任务查询

### Phase 2（增强功能）
1. 错误重试机制
2. 图片缓存和清理策略
3. 图片预览缩略图
4. 批量图片打包下载

### Phase 3（高级功能）
1. 批量绘图任务
2. 图片风格预设
3. Webhook回调通知
4. 用户认证和配额管理
5. 图片编辑和优化功能

## 安全性考虑
1. **API密钥管理**：使用环境变量，不在代码中硬编码
2. **输入验证**：对prompt进行长度和内容检查
3. **速率限制**：防止API滥用
4. **文件存储安全**：验证文件类型和大小
5. **敏感信息过滤**：在prompt中过滤敏感词汇

## 性能考虑
1. **异步处理**：长时间任务使用后台处理
2. **图片缓存**：减少重复生成
3. **数据库优化**：使用Redis或SQLite存储任务状态
4. **内存管理**：定期清理过期任务

## 部署要求
1. **环境变量**：必须设置 `NVIDIA_API_KEY`
2. **存储空间**：至少1GB用于图片存储
3. **网络访问**：需要能访问 `https://ai.api.nvidia.com`
4. **备份策略**：定期备份生成的图片和任务记录

## 监控和日志
1. **任务成功率**：记录成功/失败的任务数量
2. **API响应时间**：监控NVIDIA API的响应时间
3. **存储使用率**：监控图片存储空间使用情况
4. **错误日志**：详细记录错误信息便于调试

## 测试计划
1. **单元测试**：测试API端点和业务逻辑
2. **集成测试**：测试与NVIDIA API的集成
3. **性能测试**：测试高并发下的表现
4. **安全测试**：测试输入验证和API密钥保护
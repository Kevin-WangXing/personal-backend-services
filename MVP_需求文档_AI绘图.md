# MVP 需求文档：AI 绘图功能

> 基于 NVIDIA Stable Diffusion 3 Medium API 的图片生成服务

## 1. 项目概述

**功能：** 根据用户输入的 prompt 生成图片（JPEG 格式）  
**API 基础 URL：** `https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-3-medium`  
**认证：** 环境变量 `NVIDIA_API_KEY`

---

## 2. API 接口设计

### 2.1 创建绘图任务

```
POST /ai/draw
Content-Type: application/json
```

**请求参数：**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| prompt | string | ✅ | - | 绘图描述 |
| cfg_scale | float | ❌ | 5 | 引导强度 (1-10) |
| aspect_ratio | string | ❌ | "16:9" | 宽高比，支持 16:9 / 9:16 / 1:1 / 4:3 |
| seed | int | ❌ | 0 | 随机种子，0 表示随机 |
| steps | int | ❌ | 50 | 采样步数 |
| negative_prompt | string | ❌ | "" | 反向提示词 |

**响应 (200)：**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Drawing task created successfully",
  "created_at": "2026-04-15T10:30:00",
  "download_url": "/ai/draw/550e8400.../download",
  "status_url": "/ai/draw/550e8400.../status",
  "individual_download_urls": ["/ai/draw/550e8400.../download/{filename}"]
}
```

**错误响应：**
- `400` — 参数错误
- `500` — 服务器内部错误

---

### 2.2 查询任务状态

```
GET /ai/draw/{task_id}/status
```

**响应 (200)：**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "prompt": "Vintage steampunk airship...",
  "status": "completed",
  "created_at": "2026-04-15T10:30:00",
  "updated_at": "2026-04-15T10:31:00",
  "error_message": null,
  "image_count": 1,
  "download_links": ["/ai/draw/550e8400.../download/550e8400..._0.jpg"],
  "image_files": [
    {
      "filename": "550e8400..._0.jpg",
      "url": "/ai/draw/550e8400.../download/550e8400..._0.jpg",
      "size_bytes": 190440,
      "format": "jpeg"
    }
  ]
}
```

**status 状态值：**
- `queued` — 任务已创建，等待处理
- `processing` — 正在调用 NVIDIA API
- `completed` — 生成完成，可下载
- `failed` — 生成失败

**错误响应：**
- `404` — 任务不存在

---

### 2.3 下载图片（所有图片）

```
GET /ai/draw/{task_id}/download
```

**响应：**
- 单张图片：直接返回 JPEG 文件（`Content-Type: image/jpeg`）
- 多张图片：返回 JSON 包含所有图片信息

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "image_count": 1,
  "images": [...],
  "message": "Multiple images generated, please download individually",
  "individual_downloads": ["/ai/draw/550e8400.../download/550e8400..._0.jpg"]
}
```

**错误响应：**
- `400` — 任务未完成
- `404` — 任务或图片不存在

---

### 2.4 下载特定图片

```
GET /ai/draw/{task_id}/download/{filename}
```

**响应：** 直接返回 JPEG 文件（`Content-Type: image/jpeg`）

**错误响应：**
- `400` — 任务未完成
- `404` — 图片不存在

---

### 2.5 查询绘图历史

```
GET /ai/draw/history
```

**响应 (200)：**

```json
{
  "tasks": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "prompt": "Vintage steampunk airship...",
      "status": "completed",
      "created_at": "2026-04-15T10:30:00",
      "updated_at": "2026-04-15T10:31:00",
      "image_count": 1,
      "download_available": true,
      "download_urls": ["/ai/draw/550e8400.../download/550e8400..._0.jpg"]
    }
  ],
  "total": 1,
  "completed_count": 1,
  "failed_count": 0
}
```

---

## 3. 数据模型

### 3.1 请求模型

```python
class DrawingRequest(BaseModel):
    prompt: str                          # 必填，绘图描述
    cfg_scale: float = 5                # 引导强度 1-10
    aspect_ratio: str = "16:9"          # 16:9 / 9:16 / 1:1 / 4:3
    seed: int = 0                       # 随机种子，0=随机
    steps: int = 50                     # 采样步数
    negative_prompt: str = ""           # 反向提示词
```

### 3.2 任务存储结构（内存）

```python
drawing_tasks: Dict[str, Dict] = {
    "task_id": {
        "task_id": "uuid-string",
        "prompt": "...",
        "cfg_scale": 5,
        "aspect_ratio": "16:9",
        "seed": 0,
        "steps": 50,
        "negative_prompt": "",
        "status": "queued|processing|completed|failed",
        "created_at": "ISO8601 timestamp",
        "updated_at": "ISO8601 timestamp",
        "result": {...},                # NVIDIA API 原始响应
        "error_message": None,
        "image_files": [
            {
                "filename": "task_id_idx.jpg",
                "filepath": "storage/images/task_id_idx.jpg",
                "url": "/ai/draw/task_id/download/task_id_idx.jpg",
                "size_bytes": 190440,
                "format": "jpeg"
            }
        ]
    }
}
```

---

## 4. NVIDIA API 调用规范

### 4.1 请求格式

```python
import os
import requests

invoke_url = "https://ai.api.nvidia.com/v1/genai/stabilityai/stable-diffusion-3-medium"

headers = {
    "Authorization": f"Bearer {os.getenv('NVIDIA_API_KEY')}",
    "Accept": "application/json",
}

payload = {
    "prompt": "Vintage, steampunk-inspired airship...",
    "cfg_scale": 5,
    "aspect_ratio": "16:9",
    "seed": 0,
    "steps": 50,
    "negative_prompt": ""
}

response = requests.post(invoke_url, headers=headers, json=payload)
```

### 4.2 响应处理

NVIDIA API 返回的 `images` 字段是 base64 编码的 JPEG 数据：

```python
response_body = response.json()
image_data_list = response_body.get("images", [])

# base64 数据格式："/9j/4AAQ..." (无 data URI 前缀)
# 需要手动添加 "data:image/jpeg;base64," 前缀再解码
```

### 4.3 任务状态机

```
queued → processing → completed
                      ↓
                   failed
```

---

## 5. 日志机制

### 5.1 日志文件结构

```
logs/
├── app_YYYYMMDD.log           # 应用主日志
├── ai_drawing_YYYYMMDD.log    # AI 绘图专用日志
├── api_access_YYYYMMDD.log    # API 访问日志
└── errors_YYYYMMDD.log        # 错误日志
```

### 5.2 日志函数

| 函数 | 说明 |
|------|------|
| `log_api_access(endpoint, method, status_code)` | 记录 API 访问 |
| `log_ai_drawing_event(task_id, event, details)` | 记录 AI 绘图事件 |
| `log_error(error_type, message, exception)` | 记录错误 |

### 5.3 日志事件记录点

| 事件 | 级别 | 说明 |
|------|------|------|
| Task created | INFO | 任务创建 |
| Calling NVIDIA API | INFO | 开始调用 API |
| NVIDIA API response received | INFO | 收到 API 响应 |
| Image saved | INFO | 图片保存成功 |
| Completed successfully | INFO | 任务完成 |
| NVIDIA_API_ERROR | ERROR | API 调用失败 |
| IMAGE_SAVE_ERROR | ERROR | 图片保存失败 |
| CONFIG_ERROR | ERROR | 配置错误 |

---

## 6. 文件结构

```
fastapi_demo/
├── main.py                      # 主应用入口
├── logging_config.py            # 日志配置
├── ai_drawing_test.py           # 测试脚本
├── requirements.txt             # 依赖
├── storage/
│   └── images/                  # 生成的图片 (JPEG)
│       ├── {task_id}_0.jpg
│       └── {task_id}_1.jpg
└── logs/                        # 日志文件
    ├── app_YYYYMMDD.log
    ├── ai_drawing_YYYYMMDD.log
    ├── api_access_YYYYMMDD.log
    └── errors_YYYYMMDD.log
```

---

## 7. 环境配置

### 7.1 必需环境变量

```bash
export NVIDIA_API_KEY="your_api_key_here"
```

### 7.2 可选配置

```bash
export NVIDIA_API_BASE_URL="https://ai.api.nvidia.com/v1/genai"
export MODEL_NAME="stabilityai/stable-diffusion-3-medium"
```

---

## 8. 错误处理

| HTTP 状态码 | 场景 |
|-------------|------|
| 200 | 成功 |
| 400 | 请求参数错误 / 任务未完成 |
| 404 | 任务或图片不存在 |
| 429 | API 频率限制 |
| 500 | 服务器内部错误 |
| 503 | NVIDIA API 服务不可用 |

---

## 9. 依赖

```
fastapi>=0.110.0
uvicorn>=0.27.0
pydantic>=2.0.0
requests>=2.31.0
python-dotenv>=1.0.0
```

---

## 10. 启动方式

```bash
cd fastapi_demo
source venv/bin/activate
export NVIDIA_API_KEY="your_key"
python main.py
# 服务运行在 http://0.0.0.0:9000
```

---

## 11. 待扩展功能 (Phase 2)

- [ ] 错误重试机制
- [ ] 图片缓存和自动清理策略
- [ ] 批量打包下载（ZIP）
- [ ] Webhook 回调通知
- [ ] 用户认证和配额管理
# AI绘图功能集成指南

## 概述
本项目已集成英伟达（NVIDIA）Stable Diffusion 3 绘图模型，提供AI绘图API服务。

## 快速开始

### 1. 环境配置
```bash
# 克隆项目
git clone <repository>
cd fastapi_demo

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 NVIDIA API 密钥
```

### 2. 获取NVIDIA API密钥
1. 访问 https://build.nvidia.com/marketplace/api_keys
2. 注册/登录NVIDIA开发者账号
3. 创建API密钥
4. 复制密钥到 `.env` 文件的 `NVIDIA_API_KEY`

### 3. 启动服务器
```bash
python main.py
```

服务器将在 `http://localhost:9000` 启动。

## API 文档

### 基础端点
- `GET /` - 服务器信息和所有端点列表
- `GET /health` - 健康检查

### AI绘图端点

#### 1. 创建绘图任务
```http
POST /ai/draw
Content-Type: application/json

{
    "prompt": "A beautiful sunset over mountains",
    "cfg_scale": 5,          # 可选，默认5
    "aspect_ratio": "16:9",  # 可选，默认"16:9"
    "seed": 0,               # 可选，默认0
    "steps": 50,             # 可选，默认50
    "negative_prompt": ""    # 可选，默认空
}
```

**响应示例：**
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "queued",
    "message": "Drawing task created successfully",
    "created_at": "2026-04-09T10:00:00.000000"
}
```

#### 2. 查询任务状态
```http
GET /ai/draw/{task_id}/status
```

**响应状态：**
- `queued`: 任务已创建，等待处理
- `processing`: 正在调用NVIDIA API
- `completed`: 任务完成，结果在`result`字段
- `failed`: 任务失败，错误信息在`error_message`

**响应示例（成功）：**
```json
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "prompt": "A beautiful sunset over mountains",
    "status": "completed",
    "created_at": "2026-04-09T10:00:00.000000",
    "updated_at": "2026-04-09T10:01:30.000000",
    "result": {
        // NVIDIA API返回的完整结果
    },
    "error_message": null
}
```

#### 3. 获取绘图历史
```http
GET /ai/draw/history
```

**响应示例：**
```json
{
    "tasks": [
        {
            "task_id": "550e8400-e29b-41d4-a716-446655440000",
            "prompt": "A beautiful sunset over mountains",
            "status": "completed",
            "created_at": "2026-04-09T10:00:00.000000",
            "updated_at": "2026-04-09T10:01:30.000000",
            "result": {...},
            "error_message": null
        }
    ],
    "total": 1
}
```

## 测试方法

### 1. 使用测试脚本
```bash
# 确保服务器正在运行
python main.py

# 在另一个终端运行测试
python ai_drawing_test.py
```

### 2. 使用curl测试
```bash
# 创建绘图任务
curl -X POST http://localhost:9000/ai/draw \
  -H "Content-Type: application/json" \
  -d '{"prompt":"A cute kitten playing with yarn","steps":30}'

# 查询任务状态
curl http://localhost:9000/ai/draw/{task_id}/status

# 查看绘图历史
curl http://localhost:9000/ai/draw/history
```

### 3. 使用Python测试
```python
import requests
import time

base_url = "http://localhost:9000"

# 创建任务
response = requests.post(f"{base_url}/ai/draw", json={
    "prompt": "Fantasy dragon flying over castle",
    "steps": 40
})

task_id = response.json()["task_id"]
print(f"Task created: {task_id}")

# 轮询状态
while True:
    status_response = requests.get(f"{base_url}/ai/draw/{task_id}/status")
    status_data = status_response.json()
    
    print(f"Status: {status_data['status']}")
    
    if status_data['status'] in ['completed', 'failed']:
        print(f"Final result: {status_data}")
        break
    
    time.sleep(5)
```

## 参数说明

### prompt（必填）
- **描述**: 图片生成提示词
- **示例**: "A futuristic city at night with neon lights"
- **最佳实践**: 详细描述想要生成的场景、风格、颜色等

### cfg_scale（可选，默认5）
- **范围**: 1-10
- **作用**: 控制提示词的重要性
- **建议**: 5-7之间效果较好

### aspect_ratio（可选，默认"16:9"）
- **选项**: "1:1" (正方形), "4:3" (标准), "16:9" (宽屏), "9:16" (竖屏)
- **作用**: 控制图片宽高比

### seed（可选，默认0）
- **范围**: 0-4294967295
- **作用**: 控制随机种子，相同seed生成相同图片
- **说明**: 0表示随机

### steps（可选，默认50）
- **范围**: 10-100
- **作用**: 生成步骤数，影响图片质量
- **平衡**: 值越高质量越好，但时间越长

### negative_prompt（可选，默认空）
- **描述**: 不希望出现在图片中的内容
- **示例**: "blurry, distorted, watermark, text"

## 高级功能

### 1. 异步处理
- 所有绘图任务都在后台异步处理
- 立即返回任务ID，不阻塞请求
- 可以通过状态API查询进度

### 2. 任务管理
- 所有任务存储在内存中
- 支持任务状态查询
- 提供完整的历史记录

### 3. 错误处理
- NVIDIA API错误：返回详细错误信息
- 网络错误：自动重试机制
- 参数验证：自动验证输入参数

## 性能优化建议

### 1. 降低API调用频率
```python
# 避免频繁调用
# 错误做法：每1秒查询一次状态
# 正确做法：每5-10秒查询一次状态
```

### 2. 优化prompt
- 使用具体、描述性的语言
- 避免模糊的描述
- 指定风格（如："in the style of Van Gogh"）

### 3. 调整参数
- `steps=30-40`: 平衡质量和速度
- `cfg_scale=5-6`: 大多数场景的最佳范围
- 使用`seed`复现特定图片

## 故障排除

### 1. API密钥错误
```
错误: "NVIDIA_API_KEY environment variable not set"
解决: 确保.env文件正确设置，或使用export命令设置环境变量
```

### 2. 网络连接问题
```
错误: "NVIDIA API error: Connection refused"
解决: 检查网络连接，确保能访问https://ai.api.nvidia.com
```

### 3. 任务长时间处于processing状态
```
原因: NVIDIA API可能需要30-60秒处理请求
建议: 耐心等待，或降低steps参数
```

### 4. 图片质量不佳
```
建议: 增加steps到50-70，调整prompt，使用negative_prompt过滤不需要的元素
```

## 扩展功能（未来计划）

### 1. 图片下载
- 根据任务ID下载生成的图片文件
- 支持多种格式（PNG、JPEG）

### 2. 批量处理
- 一次提交多个prompt
- 批量返回结果

### 3. 图片编辑
- 基于现有图片进行编辑
- 风格迁移
- 图片修复

### 4. 用户系统
- 用户认证
- 使用配额限制
- 个人历史记录

## 安全性注意事项

1. **API密钥保护**：不要将.env文件提交到版本控制
2. **输入验证**：所有用户输入都经过验证
3. **速率限制**：考虑添加API调用频率限制
4. **内容审核**：考虑添加prompt内容审核机制

## 技术支持
- 查看服务器日志：`tail -f uvicorn.log`
- 访问API文档：`http://localhost:9000/docs`
- 查看健康状态：`http://localhost:9000/health`
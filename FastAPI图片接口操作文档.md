# FastAPI 图片接口操作文档

## 🌐 服务器信息
- **公网IP地址**: `43.159.169.8`
- **端口**: `9000`
- **访问地址**: `http://43.159.169.8:9000`
- **服务状态**: 需要确保服务器已启动

## 📍 基础信息

### 1. 健康检查
```http
GET http://43.159.169.8:9000/health

响应示例:
{
  "status": "healthy",
  "timestamp": "2026-04-10T16:07:00"
}
```

### 2. 查看所有端点
```http
GET http://43.159.169.8:9000/

响应中包含所有可用API端点列表
```

## 🎨 图片功能接口详细说明

### 1. 创建图片生成任务

**接口地址**: `POST http://43.159.169.8:9000/ai/draw`

**功能**: 提交AI绘图请求，返回任务ID用于后续查询

**请求示例**:
```
curl -X POST http://43.159.169.8:9000/ai/draw \
-H "Content-Type: application/json" \
-d '{
  "prompt": "一只可爱的蓝色蘑菇人，水彩风格",
  "cfg_scale": 7.0,
  "aspect_ratio": "16:9",
  "seed": 123456,
  "steps": 30,
  "negative_prompt": "模糊,低质量,变形"
}'
```

**返回示例**:
```json
{
  "task_id": "f47ac10b-58cc-4372-a567-0e02b579a456",
  "status": "queued",
  "message": "Drawing task created successfully",
  "created_at": "2026-04-10T16:07:00",
  "download_url": "/ai/draw/f47ac10b-58cc-4372-a567-0e02b579a456/download",
  "status_url": "/ai/draw/f47ac10b-58cc-4372-a567-0e02b579a456/status"
}
```

**参数说明**:
| 参数 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| prompt | string | ✅ | 图片描述文字，支持中英文 | - |
| cfg_scale | number | ❌ | 控制程度，1-20 | 5 |
| aspect_ratio | string | ❌ | 图片比例，支持"1:1", "16:9", "9:16" | "16:9" |
| seed | integer | ❌ | 随机种子，相同种子生成相同图片 | 0 |
| steps | integer | ❌ | 生成步数，1-50 | 50 |
| negative_prompt | string | ❌ | 负面提示，避免出现在图片中 | "" |

### 2. 查询任务状态

**接口地址**: `GET http://43.159.169.8:9000/ai/draw/{task_id}/status`

**功能**: 实时查询图片生成任务的进度和状态

**使用示例**:```
curl http://43.159.169.8:9000/ai/draw/f47ac10b-58cc-4372-a567-0e02b579a456/status

{
  "task_id": "f47ac10b-58cc-4372-a567-0e02b579a456",
  "prompt": "一只可爱的蓝色蘑菇人...",
  "status": "completed",
  "created_at": "2026-04-10T16:07:00",
  "updated_at": "2026-04-10T16:08:30",
  "image_count": 1,
  "download_links": ["/ai/draw/.../download/test_0.jpg"],
  "error_message": null
}
```

**状态说明**:
- `queued`: 任务已加入队列
- `processing`: 正在生成中
- `completed`: 生成完成
- `failed`: 生成失败

### 3. 图片下载接口

**3.1 根据任务ID下载**  
**接口地址**: `GET http://43.159.169.8:9000/ai/draw/{task_id}/download`

**功能**: 下载该任务生成的所有图片（单张直接返回，多张返回列表）

**使用示例**:
```
curl -O http://43.159.169.8:9000/ai/draw/f47ac10b-58cc-4372-a567-0e02b579a456/download
```

**3.2 下载指定图片文件**
**接口地址**: `GET http://43.159.169.8:9000/ai/draw/{task_id}/download/{filename}`

**功能**: 下载特定文件名对应的图片

**示例**:```
curl -O http://43.159.169.8:9000/ai/draw/f47ac10b-58cc-4372-a567-0e02b579a456/download/f47ac10b-58cc..._0.jpg
# 文件名从任务状态接口获取
```

### 4. 查看生成历史

**接口地址**: `GET http://43.159.169.8:9000/ai/draw/history`

**功能**: 查看所有生成过的图片任务历史

**使用示例**:
```
curl http://43.159.169.8:9000/ai/draw/history

{
  "tasks": [
    {
      "task_id": "f47ac10b-58cc-4372-a567-0e02b579a456",
      "prompt": "一只可爱的蓝色蘑菇人...",
      "status": "completed",
      "created_at": "2026-04-10T16:07:00",
      "image_count": 1,
      "download_available": true
    }
  ],
  "total": 3,
  "completed_count": 2,
  "failed_count": 1
}
```

## 🚀 快速开始示例

### 完整测试流程

1. **测试连通性**
```
curl http://43.159.169.8:9000/health
```

2. **生成第一个图片**
```
curl -X POST http://43.159.169.8:9000/ai/draw \
-H "Content-Type: application/json" \
-d '{
  "prompt": "一只可爱的蓝色蘑菇人，日系插画风格，柔和色彩",
  "cfg_scale": 8,
  "steps": 30,
  "aspect_ratio": "16:9"
}' > response.json

# 提取任务ID
TASK_ID=$(cat response.json | jq -r '.task_id')
echo "任务ID: $TASK_ID"
```

3. **轮询任务状态**
```
# 轮询直到完成（每分钟检查一次）
while true; do
    STATUS=$(curl -s "http://43.159.169.8:9000/ai/draw/$TASK_ID/status" | jq -r '.status')
    echo "状态: $STATUS"
    if [[ "$STATUS" == "completed" ]]; then
        echo "图片生成完成！"
        break
    elif [[ "$STATUS" == "failed" ]]; then
        echo "生成失败"
        break
    fi
    sleep 10
done
```

4. **下载图片**
```
# 获取图片文件名
curl "http://43.159.169.8:9000/ai/draw/$TASK_ID/status" | jq -r '.download_links[0]'

# 下载图片
curl -O "http://43.159.169.8:9000/ai/draw/$TASK_ID/download"
```

## 📋 常见问题

### 环境要求
```
# 需要在服务器预先启动服务
cd /root/.openclaw/workspace/fastapi_demo
source venv/bin/activate  
python main.py  # 默认9000端口
```

### 权限设置
```bash
# 如果需要监听公网IP，确保服务器防火墙开放9000端口
sudo ufw allow 9000
# 或配置云服务器安全组开放9000端口
```

### 错误处理
- **404错误**: 任务ID不存在
- **400错误**: 任务状态不正确（未完成时尝试下载）
- **500错误**: {{ν服务器内部错误，重试或联系管理员}}

### 测试命令集合
```bash
# 一键测试脚本
curl -s http://43.159.169.8:9000/health || echo "服务器未启动"

# 快速测试图片生成
curl -s -X POST http://43.159.169.8:9000/ai/draw \
  -H "Content-Type: application/json" \
  -d '{"prompt":"测试图片生成","cfg_scale":5,"steps":20}' \
  | jq '.task_id'
```

## 📝 HTTP状态码
- `200`: 请求成功
- `201`: 任务创建成功
- `404`: 资源未找到
- `400`: 请求参数无效
- `500`: 服务器内部错误
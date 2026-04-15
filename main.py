"""
FastAPI Demo Server
"""
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# 初始化日志（导入即初始化）
from utils.logger import setup_logging
setup_logging()

# 路由
from routes.drawing import router as drawing_router
from routes.wechat import router as wechat_router

app = FastAPI(
    title="FastAPI Demo Server",
    description="模块化 FastAPI 服务器，支持 AI 绘图等扩展功能",
    version="2.0.0"
)

# 注册路由
app.include_router(drawing_router)
app.include_router(wechat_router)

# ============ 原有 CRUD 功能（保留）============

items_db = [
    {"id": 1, "name": "Item 1", "description": "第一个示例项目"},
    {"id": 2, "name": "Item 2", "description": "第二个示例项目"},
    {"id": 3, "name": "Item 3", "description": "第三个示例项目"},
]


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tax: Optional[float] = None


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "欢迎使用 FastAPI Demo 服务器",
        "version": "2.0.0",
        "modules": ["AI 绘图 (ai_draw)", "微信公众号文章 (wechat)"],
        "endpoints": {
            "health": "/health",
            "items": "/items",
            "ai_draw": "/ai/draw",
            "ai_draw_status": "/ai/draw/{task_id}/status",
            "ai_draw_download": "/ai/draw/{task_id}/download",
            "ai_draw_history": "/ai/draw/history",
            "wechat_article": "/wechat/article (POST)",
        }
    }


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy"}


@app.get("/items", tags=["Items"])
async def get_items():
    return {"count": len(items_db), "items": items_db}


@app.get("/items/{item_id}", tags=["Items"])
async def get_item(item_id: int):
    for item in items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


@app.post("/items", tags=["Items"])
async def create_item(item: Item):
    new_id = max([i["id"] for i in items_db], default=0) + 1
    new_item = {
        "id": new_id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "tax": item.tax,
    }
    items_db.append(new_item)
    return {"message": "Item created", "item": new_item}


@app.put("/items/{item_id}", tags=["Items"])
async def update_item(item_id: int, item_update: ItemUpdate):
    for idx, item in enumerate(items_db):
        if item["id"] == item_id:
            update_data = item_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                items_db[idx][key] = value
            return {"message": f"Item {item_id} updated", "item": items_db[idx]}
    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


@app.delete("/items/{item_id}", tags=["Items"])
async def delete_item(item_id: int):
    for idx, item in enumerate(items_db):
        if item["id"] == item_id:
            deleted = items_db.pop(idx)
            return {"message": f"Item {item_id} deleted", "deleted_item": deleted}
    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


@app.post("/echo", tags=["System"])
async def echo_message(data: dict):
    return {"received_data": data, "message": "Data received"}


# ============ 启动 ===========

if __name__ == "__main__":
    # 确保存储目录存在
    os.makedirs("storage/images", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,
        log_level="info"
    )
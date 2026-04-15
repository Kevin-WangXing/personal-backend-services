#!/usr/bin/env python3
"""
AI绘图功能测试脚本
"""

import requests
import json
import time

BASE_URL = "http://localhost:9000"

def test_create_drawing_task():
    """测试创建绘图任务"""
    print("=== 测试创建绘图任务 ===")
    
    request_data = {
        "prompt": "A beautiful sunset over mountains with a lake in the foreground",
        "cfg_scale": 5,
        "aspect_ratio": "16:9",
        "seed": 42,
        "steps": 30,
        "negative_prompt": "blurry, distorted, low quality"
    }
    
    response = requests.post(f"{BASE_URL}/ai/draw", json=request_data)
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        task_id = response.json()["task_id"]
        print(f"任务ID: {task_id}")
        return task_id
    return None

def test_get_task_status(task_id: str):
    """测试获取任务状态"""
    print(f"\n=== 测试获取任务状态 (task_id: {task_id}) ===")
    
    response = requests.get(f"{BASE_URL}/ai/draw/{task_id}/status")
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    return response.json()

def test_get_drawing_history():
    """测试获取绘图历史"""
    print("\n=== 测试获取绘图历史 ===")
    
    response = requests.get(f"{BASE_URL}/ai/draw/history")
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_missing_task():
    """测试查询不存在的任务"""
    print("\n=== 测试查询不存在的任务 ===")
    
    response = requests.get(f"{BASE_URL}/ai/draw/nonexistent-task/status")
    
    print(f"状态码: {response.status_code}")
    if response.status_code != 200:
        print(f"错误信息: {response.json()}")

def test_different_prompts():
    """测试不同的prompt"""
    print("\n=== 测试不同风格的prompt ===")
    
    prompts = [
        {
            "prompt": "A cute cartoon cat sleeping on a windowsill",
            "aspect_ratio": "1:1"
        },
        {
            "prompt": "Futuristic cityscape with flying cars and neon lights",
            "aspect_ratio": "16:9"
        },
        {
            "prompt": "Peaceful Japanese garden with cherry blossoms",
            "aspect_ratio": "4:3"
        }
    ]
    
    task_ids = []
    for prompt_data in prompts:
        request_data = {
            "prompt": prompt_data["prompt"],
            "aspect_ratio": prompt_data["aspect_ratio"],
            "steps": 25,  # 减少步骤以加快测试
            "cfg_scale": 4.5
        }
        
        response = requests.post(f"{BASE_URL}/ai/draw", json=request_data)
        
        if response.status_code == 200:
            task_id = response.json()["task_id"]
            task_ids.append(task_id)
            print(f"创建任务: {prompt_data['prompt'][:50]}... -> task_id: {task_id}")
        else:
            print(f"创建失败: {response.json()}")

def run_all_tests():
    """运行所有测试"""
    print("开始测试AI绘图功能...")
    print("=" * 60)
    
    try:
        # 测试基础功能
        task_id = test_create_drawing_task()
        
        if task_id:
            # 等待几秒钟，让后台任务开始处理
            print("\n等待5秒让任务开始处理...")
            time.sleep(5)
            
            # 查询任务状态
            test_get_task_status(task_id)
            
            # 等待更多时间（NVIDIA API可能需要一些时间）
            print("\n等待10秒检查任务状态更新...")
            time.sleep(10)
            
            # 再次查询任务状态
            test_get_task_status(task_id)
        
        # 测试历史查询
        test_get_drawing_history()
        
        # 测试错误情况
        test_missing_task()
        
        # 测试多个任务
        test_different_prompts()
        
        print("\n" + "=" * 60)
        print("所有测试完成！")
        
        print("\n📌 注意事项:")
        print("1. 确保已设置 NVIDIA_API_KEY 环境变量")
        print("2. NVIDIA API可能需要30-60秒完成图片生成")
        print("3. 检查任务状态API可以监控生成进度")
        print("4. 生成的图片URL在任务完成后会出现在result字段")
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保服务器正在运行")
        print(f"尝试连接: {BASE_URL}")
        print("请先运行: python main.py")
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    run_all_tests()
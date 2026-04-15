#!/usr/bin/env python3
"""
测试图片下载和日志功能
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:9000"

def test_create_and_download():
    """测试创建任务并下载图片"""
    print("=== 测试创建任务并下载图片 ===")
    
    # 创建绘图任务
    request_data = {
        "prompt": "A beautiful mountain landscape with river and forest",
        "steps": 30,  # 减少步骤以加快测试
        "cfg_scale": 4.5
    }
    
    print("1. 创建绘图任务...")
    response = requests.post(f"{BASE_URL}/ai/draw", json=request_data)
    
    if response.status_code != 200:
        print(f"创建任务失败: {response.status_code}")
        print(response.json())
        return None
    
    task_data = response.json()
    task_id = task_data["task_id"]
    
    print(f"任务创建成功! Task ID: {task_id}")
    print(f"下载URL: {task_data.get('download_url')}")
    print(f"状态URL: {task_data.get('status_url')}")
    
    # 等待任务完成
    print("\n2. 等待任务完成...")
    for i in range(10):  # 最多等待50秒
        time.sleep(5)
        
        status_response = requests.get(f"{BASE_URL}/ai/draw/{task_id}/status")
        status_data = status_response.json()
        
        print(f"  轮询 {i+1}: 状态 = {status_data['status']}")
        
        if status_data['status'] == 'completed':
            print("  任务完成!")
            
            # 查看任务详情
            print(f"\n3. 任务详情:")
            print(f"  图片数量: {status_data.get('image_count', 0)}")
            print(f"  下载链接: {status_data.get('download_links', [])}")
            
            if status_data.get('image_files'):
                for img in status_data['image_files']:
                    print(f"  文件: {img['filename']} - {img['size_bytes']} bytes - {img['url']}")
            
            return task_id, status_data
        
        elif status_data['status'] == 'failed':
            print(f"  任务失败: {status_data.get('error_message')}")
            return None
    
    print("  任务超时!")
    return None

def test_download_all_images(task_id: str):
    """测试下载所有图片"""
    print(f"\n=== 测试下载所有图片 (Task: {task_id}) ===")
    
    response = requests.get(f"{BASE_URL}/ai/draw/{task_id}/download")
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        # 检查响应类型
        content_type = response.headers.get('content-type', '')
        
        if 'image/jpeg' in content_type:
            # 这是直接的图片文件
            file_size = len(response.content)
            print(f"下载成功! 图片大小: {file_size} bytes")
            
            # 保存文件
            filename = f"test_download_{task_id}.jpg"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"图片已保存到: {filename}")
        else:
            # 这是JSON响应（多个图片）
            try:
                data = response.json()
                print(f"下载信息: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except:
                print(f"响应内容: {response.text[:200]}...")
    else:
        print(f"下载失败: {response.json()}")

def test_download_specific_image(task_id: str, filename: str):
    """测试下载特定图片"""
    print(f"\n=== 测试下载特定图片 (Task: {task_id}, File: {filename}) ===")
    
    response = requests.get(f"{BASE_URL}/ai/draw/{task_id}/download/{filename}")
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        file_size = len(response.content)
        print(f"下载成功! 图片大小: {file_size} bytes")
        
        # 保存文件
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"图片已保存到: {filename}")
    else:
        print(f"下载失败: {response.json()}")

def test_log_files():
    """检查日志文件"""
    print("\n=== 检查日志文件 ===")
    
    log_dir = "logs"
    storage_dir = "storage/images"
    
    if os.path.exists(log_dir):
        print(f"日志目录存在: {log_dir}")
        log_files = os.listdir(log_dir)
        print(f"日志文件列表: {log_files}")
        
        # 读取最新的日志文件
        if log_files:
            latest_log = max([os.path.join(log_dir, f) for f in log_files], key=os.path.getmtime)
            print(f"\n最新日志文件: {latest_log}")
            
            try:
                with open(latest_log, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-10:]  # 最后10行
                    print("最后10行日志:")
                    for line in lines:
                        print(f"  {line.strip()}")
            except Exception as e:
                print(f"读取日志文件失败: {e}")
    else:
        print("日志目录不存在")
    
    if os.path.exists(storage_dir):
        print(f"\n存储目录存在: {storage_dir}")
        image_files = os.listdir(storage_dir)
        print(f"图片文件数量: {len(image_files)}")
        if image_files:
            print(f"示例文件: {image_files[:3]}")
    else:
        print("存储目录不存在")

def test_history_with_download_info():
    """测试包含下载信息的历史查询"""
    print("\n=== 测试包含下载信息的历史查询 ===")
    
    response = requests.get(f"{BASE_URL}/ai/draw/history")
    
    if response.status_code == 200:
        history_data = response.json()
        
        print(f"总任务数: {history_data['total']}")
        print(f"成功任务数: {history_data['completed_count']}")
        print(f"失败任务数: {history_data['failed_count']}")
        
        print("\n任务列表:")
        for task in history_data['tasks'][:3]:  # 只显示前3个
            print(f"  Task ID: {task['task_id']}")
            print(f"    提示: {task['prompt']}")
            print(f"    状态: {task['status']}")
            print(f"    图片数量: {task['image_count']}")
            print(f"    可下载: {task['download_available']}")
            
            if task['download_available'] and 'download_urls' in task:
                for url in task['download_urls']:
                    print(f"    下载URL: {url}")
            print()
    else:
        print(f"历史查询失败: {response.json()}")

def run_all_tests():
    """运行所有测试"""
    print("开始测试图片下载和日志功能...")
    print("=" * 60)
    
    try:
        # 测试创建和下载
        result = test_create_and_download()
        
        if result:
            task_id, status_data = result
            
            # 测试下载功能
            if status_data.get('image_count', 0) > 0:
                # 测试下载所有图片
                test_download_all_images(task_id)
                
                # 如果有特定文件，测试下载特定图片
                if status_data.get('image_files'):
                    for img in status_data['image_files'][:1]:  # 只测试第一个
                        test_download_specific_image(task_id, img['filename'])
            
            # 测试历史查询
            test_history_with_download_info()
        
        # 检查日志文件
        test_log_files()
        
        print("\n" + "=" * 60)
        print("测试完成!")
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保服务器正在运行")
        print(f"尝试连接: {BASE_URL}")
        print("请先运行: python main.py")
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    run_all_tests()
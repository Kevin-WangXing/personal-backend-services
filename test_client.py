import requests
import json

BASE_URL = "http://localhost:9000"

def test_root():
    """测试根路径"""
    print("=== 测试根路径 ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_health():
    """测试健康检查"""
    print("=== 测试健康检查 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_get_items():
    """测试获取所有项目"""
    print("=== 测试获取所有项目 ===")
    response = requests.get(f"{BASE_URL}/items")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_get_single_item():
    """测试获取单个项目"""
    print("=== 测试获取单个项目 (id=1) ===")
    response = requests.get(f"{BASE_URL}/items/1")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_create_item():
    """测试创建新项目"""
    print("=== 测试创建新项目 ===")
    new_item = {
        "name": "测试项目",
        "description": "这是一个测试项目",
        "price": 99.99,
        "tax": 9.9
    }
    response = requests.post(f"{BASE_URL}/items", json=new_item)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_update_item():
    """测试更新项目"""
    print("=== 测试更新项目 (id=1) ===")
    update_data = {
        "name": "更新后的项目",
        "price": 149.99
    }
    response = requests.put(f"{BASE_URL}/items/1", json=update_data)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_echo():
    """测试回显功能"""
    print("=== 测试回显功能 ===")
    test_data = {
        "message": "Hello FastAPI!",
        "timestamp": "2026-04-09T14:41:00",
        "number": 42,
        "list": [1, 2, 3]
    }
    response = requests.post(f"{BASE_URL}/echo", json=test_data)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_delete_item():
    """测试删除项目"""
    print("=== 测试删除项目 (id=2) ===")
    response = requests.delete(f"{BASE_URL}/items/2")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def run_all_tests():
    """运行所有测试"""
    print("开始测试 FastAPI 服务器...")
    print("=" * 50)
    
    try:
        test_root()
        test_health()
        test_get_items()
        test_get_single_item()
        test_create_item()
        test_update_item()
        test_echo()
        test_delete_item()
        test_get_items()  # 再次获取所有项目，查看变化
        
        print("所有测试完成！")
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保服务器正在运行")
        print(f"尝试连接: {BASE_URL}")
        print("请先运行: python main.py")
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    run_all_tests()
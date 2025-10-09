#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试QA表单页面的简单脚本
"""
import requests
import json

def test_qa_form():
    """测试QA表单页面和API"""
    base_url = "http://localhost:18000"
    
    print("🧪 测试QA表单页面...")
    
    # 测试页面访问
    try:
        response = requests.get(f"{base_url}/qa-form")
        if response.status_code == 200:
            print("✅ QA表单页面访问成功")
        else:
            print(f"❌ QA表单页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 无法访问QA表单页面: {e}")
        return
    
    # 测试API接口
    print("\n🧪 测试QA创建API...")
    
    test_data = {
        "kb_id": 1,  # 默认知识库ID
        "question": "测试问题：这款产品怎么样？",
        "answer": "测试答案：这是一款优质的产品，具有很好的性能。",
        "category_1": "产品咨询",
        "category_2": "产品评价",
        "point_id": 1001,
        "record_url": "https://example.com/test.mp3",
        "is_active": True
    }
    
    try:
        response = requests.post(
            f"{base_url}/qa/create",
            headers={"Content-Type": "application/json"},
            json=test_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API测试成功，创建了QA ID: {result.get('data', {}).get('id')}")
        else:
            print(f"❌ API测试失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ API测试出错: {e}")

if __name__ == "__main__":
    test_qa_form()

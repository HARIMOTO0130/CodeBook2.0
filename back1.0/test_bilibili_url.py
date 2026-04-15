#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Bilibili视频URL的可访问性
"""
import requests

# 测试有问题的Bilibili URL
TEST_URL = "https://www.bilibili.com/video/BV1wW4y197jQ/"

def test_url_accessibility(url):
    """测试URL的可访问性"""
    print(f"=== 测试URL: {url} ===")
    
    try:
        # 发送GET请求，设置合理的超时
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        
        print(f"状态码: {response.status_code}")
        print(f"内容长度: {len(response.content)} bytes")
        print(f"编码: {response.encoding}")
        print(f"内容类型: {response.headers.get('Content-Type')}")
        
        # 检查是否有内容编码相关的头部
        if 'Content-Encoding' in response.headers:
            print(f"内容编码: {response.headers['Content-Encoding']}")
        
        # 尝试解码内容
        try:
            content = response.text
            print("内容解码成功")
            # 打印前500个字符以检查内容
            print(f"内容预览: {content[:500]}...")
        except Exception as e:
            print(f"内容解码失败: {e}")
            
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_url_accessibility(TEST_URL)

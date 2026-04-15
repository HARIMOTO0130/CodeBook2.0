#!/usr/bin/env python3
"""
创建测试用户的脚本
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import User as CustomUser

def create_test_user():
    """创建测试用户"""
    # 检查是否已存在测试用户
    if CustomUser.objects.filter(username='testuser').exists():
        print("测试用户已存在")
        return
    
    # 创建测试用户
    user = CustomUser.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpassword123',
        role='student'
    )
    
    print(f"测试用户创建成功: {user.username}")
    print("用户名: testuser")
    print("密码: testpassword123")
    print("角色: student")

if __name__ == "__main__":
    create_test_user()

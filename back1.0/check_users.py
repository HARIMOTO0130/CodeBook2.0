#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查数据库中的用户数据"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User

# 检查用户数据
users = User.objects.all()
print('用户数量:', users.count())
print('用户列表:')
for user in users:
    print(f'  - {user.username} (角色: {user.role})')

# 检查特定用户
print('\n检查特定用户:')
try:
    test_user = User.objects.get(username='test')
    print(f'Test用户存在: {test_user.username}')
except User.DoesNotExist:
    print('Test用户不存在')

try:
    admin_user = User.objects.get(username='admin')
    print(f'Admin用户存在: {admin_user.username}')
except User.DoesNotExist:
    print('Admin用户不存在')
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查询数据库中的书籍和章节数据
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Book, Chapter

print('=== 数据库中的书籍和章节数据 ===')

# 统计书籍数量
book_count = Book.objects.count()
print(f'书籍数量: {book_count}')

# 统计章节数量
chapter_count = Chapter.objects.count()
print(f'章节数量: {chapter_count}')

# 遍历每本书及其章节
for book in Book.objects.all():
    print(f'\n书籍: {book.title}')
    print(f'  章节数: {book.chapters.count()}')
    
    # 遍历章节
    for chapter in book.chapters.all():
        print(f'  章节: {chapter.title}')
        print(f'    类型: {chapter.type}')
        print(f'    视频URL: {chapter.video_url}')
        print(f'    视频资源数: {chapter.media.filter(media_type="video").count()}')

print('\n=== 数据查询完成 ===')

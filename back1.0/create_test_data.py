#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建测试数据，用于测试视频教学功能
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Book, Chapter, ChapterMedia

# 创建测试书籍
book = Book.objects.create(
    title='测试书籍',
    author='测试作者',
    description='这是一本测试书籍，用于测试视频教学功能',
    status='published'
)

# 创建测试章节，包含视频URL
chapter1 = Chapter.objects.create(
    book=book,
    title='第一章：视频教学测试',
    type='video',
    description='这是一个视频教学章节',
    content='视频教学内容',
    video_url='https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4'
)

chapter2 = Chapter.objects.create(
    book=book,
    title='第二章：普通章节',
    type='reading',
    description='这是一个普通阅读章节',
    content='普通阅读内容'
)

# 为第一章添加视频资源
media1 = ChapterMedia.objects.create(
    chapter=chapter1,
    media_type='video',
    url='https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4',
    title='课程介绍',
    description='本视频介绍课程的基本内容和学习目标',
    order=0
)

media2 = ChapterMedia.objects.create(
    chapter=chapter1,
    media_type='video',
    url='https://sample-videos.com/video123/mp4/720/sample_720p_1mb.mp4',
    title='核心概念讲解',
    description='详细讲解课程的核心概念和理论基础',
    order=1
)

print('测试数据创建成功！')
print(f'书籍：{book.title}')
print(f'章节1：{chapter1.title}，视频URL：{chapter1.video_url}')
print(f'章节2：{chapter2.title}，视频URL：{chapter2.video_url}')
print(f'章节1的视频资源数量：{chapter1.media.filter(media_type="video").count()}')

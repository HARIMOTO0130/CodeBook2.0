#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中是否有包含特定Bilibili视频URL的章节
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Chapter, ChapterMedia

def check_bilibili_urls():
    """检查数据库中是否有包含Bilibili视频URL的章节"""
    print("=== 检查Bilibili视频URL ===")
    
    # 检查Chapter模型的video_url字段
    print("\n1. 检查Chapter模型的video_url字段:")
    chapters_with_url = Chapter.objects.filter(video_url__icontains='bilibili.com')
    print(f"找到 {chapters_with_url.count()} 个章节包含Bilibili URL")
    for chapter in chapters_with_url:
        print(f"  章节: {chapter.title}")
        print(f"  URL: {chapter.video_url}")
    
    # 检查ChapterMedia模型的url字段
    print("\n2. 检查ChapterMedia模型的url字段:")
    media_with_url = ChapterMedia.objects.filter(url__icontains='bilibili.com')
    print(f"找到 {media_with_url.count()} 个媒体资源包含Bilibili URL")
    for media in media_with_url:
        print(f"  资源: {media.title or media.get_media_type_display()}")
        print(f"  所属章节: {media.chapter.title}")
        print(f"  URL: {media.url}")
    
    # 检查特定的BV号
    print("\n3. 检查特定的BV号 BV1wW4y197jQ:")
    chapters_with_bv = Chapter.objects.filter(video_url__icontains='BV1wW4y197jQ')
    media_with_bv = ChapterMedia.objects.filter(url__icontains='BV1wW4y197jQ')
    
    print(f"在Chapter中找到 {chapters_with_bv.count()} 个匹配")
    for chapter in chapters_with_bv:
        print(f"  章节: {chapter.title}")
        print(f"  URL: {chapter.video_url}")
    
    print(f"在ChapterMedia中找到 {media_with_bv.count()} 个匹配")
    for media in media_with_bv:
        print(f"  资源: {media.title or media.get_media_type_display()}")
        print(f"  所属章节: {media.chapter.title}")
        print(f"  URL: {media.url}")

if __name__ == "__main__":
    check_bilibili_urls()

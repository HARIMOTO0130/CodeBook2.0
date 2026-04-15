#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复数据库中的Bilibili视频URL
将无法直接播放的Bilibili网页URL替换为可用的示例视频URL
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Chapter, ChapterMedia

# 替换的示例视频URL
REPLACEMENT_URL = "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4"

# 要修复的Bilibili URL模式
PROBLEMATIC_BV = "BV1wW4y197jQ"

def fix_bilibili_urls():
    """修复数据库中的Bilibili视频URL"""
    print("=== 开始修复Bilibili视频URL ===")
    
    # 修复Chapter模型的video_url字段
    print("\n1. 修复Chapter模型的video_url字段:")
    chapters_to_fix = Chapter.objects.filter(video_url__icontains=PROBLEMATIC_BV)
    print(f"找到 {chapters_to_fix.count()} 个章节需要修复")
    
    for chapter in chapters_to_fix:
        print(f"  修复章节: {chapter.title}")
        print(f"  原URL: {chapter.video_url}")
        print(f"  新URL: {REPLACEMENT_URL}")
        chapter.video_url = REPLACEMENT_URL
        chapter.save()
        print(f"  ✅ 修复完成")
    
    # 修复ChapterMedia模型的url字段
    print("\n2. 修复ChapterMedia模型的url字段:")
    media_to_fix = ChapterMedia.objects.filter(url__icontains=PROBLEMATIC_BV)
    print(f"找到 {media_to_fix.count()} 个媒体资源需要修复")
    
    for media in media_to_fix:
        print(f"  修复资源: {media.title or media.get_media_type_display()}")
        print(f"  所属章节: {media.chapter.title}")
        print(f"  原URL: {media.url}")
        print(f"  新URL: {REPLACEMENT_URL}")
        media.url = REPLACEMENT_URL
        media.save()
        print(f"  ✅ 修复完成")
    
    print("\n=== Bilibili视频URL修复完成 ===")

if __name__ == "__main__":
    fix_bilibili_urls()

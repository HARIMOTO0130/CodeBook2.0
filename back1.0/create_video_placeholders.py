#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建视频占位符文件并存储到media目录中
每本书每个章节最多三个视频
"""
import os
import django
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Book, Chapter, ChapterMedia

# 视频标题列表
VIDEO_TITLES = [
    "课程介绍",
    "核心概念讲解",
    "实践案例分析"
]

# 视频描述列表
VIDEO_DESCRIPTIONS = [
    "本视频介绍课程的基本内容和学习目标",
    "详细讲解课程的核心概念和理论基础",
    "通过实际案例展示如何应用所学知识"
]

def create_video_placeholder(save_path):
    """创建视频占位符文件"""
    try:
        # 创建一个小的MP4文件作为占位符
        with open(save_path, 'wb') as f:
            # 写入MP4文件头
            f.write(b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom')
        return True
    except Exception as e:
        print(f"创建视频占位符失败: {e}")
        return False

def create_video_resources():
    """为每个章节创建视频资源"""
    print("=== 开始创建视频资源 ===")
    
    # 确保media目录存在
    media_dir = os.path.join(os.path.dirname(__file__), 'media')
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    
    # 遍历所有书籍
    for book in Book.objects.all():
        print(f"\n处理书籍: {book.title}")
        
        # 遍历书籍的所有章节
        for chapter in book.chapters.all():
            print(f"  处理章节: {chapter.title}")
            
            # 检查当前章节的视频数量
            current_videos = chapter.media.filter(media_type="video").count()
            print(f"  当前视频数量: {current_videos}")
            
            # 如果已经有3个或更多视频，跳过
            if current_videos >= 3:
                print("  视频数量已达到上限，跳过")
                continue
            
            # 需要添加的视频数量
            videos_to_add = 3 - current_videos
            print(f"  需要添加的视频数量: {videos_to_add}")
            
            # 为章节添加视频
            for i in range(videos_to_add):
                video_title = VIDEO_TITLES[i % len(VIDEO_TITLES)]
                video_description = VIDEO_DESCRIPTIONS[i % len(VIDEO_DESCRIPTIONS)]
                
                print(f"  添加视频: {video_title}")
                
                # 创建存储路径
                year_month = datetime.now().strftime("%Y/%m")
                video_dir = os.path.join(media_dir, 'chapter_media', year_month)
                if not os.path.exists(video_dir):
                    os.makedirs(video_dir)
                
                # 生成文件名
                filename = f"video_{chapter.id}_{current_videos + i + 1}.mp4"
                save_path = os.path.join(video_dir, filename)
                
                # 创建视频占位符
                if create_video_placeholder(save_path):
                    # 创建ChapterMedia记录
                    media = ChapterMedia.objects.create(
                        chapter=chapter,
                        media_type="video",
                        url=f"/media/chapter_media/{year_month}/{filename}",
                        file=os.path.join('chapter_media', year_month, filename),
                        title=video_title,
                        description=video_description,
                        order=current_videos + i
                    )
                    print(f"  视频添加成功: {media.title}")
                else:
                    print(f"  视频添加失败: {video_title}")
            
            # 如果章节类型不是video，更新为video类型
            if chapter.type != 'video':
                chapter.type = 'video'
                chapter.save()
                print(f"  章节类型已更新为: video")
    
    print("\n=== 视频资源创建完成 ===")

if __name__ == "__main__":
    create_video_resources()

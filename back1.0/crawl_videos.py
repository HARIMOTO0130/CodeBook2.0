#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
爬取相关课程的视频并存储到media目录中
每本书每个章节最多三个视频
"""
import os
import django
import requests
from urllib.parse import urlparse
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Book, Chapter, ChapterMedia

# 视频源URL列表（使用免费的测试视频）
VIDEO_SOURCES = [
    "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4",
    "https://sample-videos.com/video123/mp4/720/sample_720p_1mb.mp4",
    "https://sample-videos.com/video123/mp4/720/sample_720p_2mb.mp4",
    "https://sample-videos.com/video123/mp4/720/sample_720p_5mb.mp4",
    "https://sample-videos.com/video123/mp4/720/sample_720p_10mb.mp4"
]

# 视频标题列表
VIDEO_TITLES = [
    "课程介绍",
    "核心概念讲解",
    "实践案例分析",
    "常见问题解答",
    "总结与展望"
]

# 视频描述列表
VIDEO_DESCRIPTIONS = [
    "本视频介绍课程的基本内容和学习目标",
    "详细讲解课程的核心概念和理论基础",
    "通过实际案例展示如何应用所学知识",
    "解答学习过程中常见的问题和疑惑",
    "总结课程内容并展望未来学习方向"
]

def download_video(url, save_path):
    """下载视频到指定路径"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"下载视频失败: {url}, 错误: {e}")
        return False

def crawl_videos():
    """爬取视频并存储到media目录中"""
    print("=== 开始爬取视频 ===")
    
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
                # 选择视频源
                video_index = (current_videos + i) % len(VIDEO_SOURCES)
                video_url = VIDEO_SOURCES[video_index]
                video_title = VIDEO_TITLES[video_index]
                video_description = VIDEO_DESCRIPTIONS[video_index]
                
                print(f"  添加视频: {video_title}")
                
                # 解析视频URL，获取文件名
                parsed_url = urlparse(video_url)
                filename = os.path.basename(parsed_url.path)
                
                # 创建存储路径
                year_month = datetime.now().strftime("%Y/%m")
                video_dir = os.path.join(media_dir, 'chapter_media', year_month)
                if not os.path.exists(video_dir):
                    os.makedirs(video_dir)
                
                # 保存视频文件
                save_path = os.path.join(video_dir, filename)
                
                # 下载视频
                if download_video(video_url, save_path):
                    # 创建ChapterMedia记录
                    media = ChapterMedia.objects.create(
                        chapter=chapter,
                        media_type="video",
                        url=video_url,
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
    
    print("\n=== 视频爬取完成 ===")

if __name__ == "__main__":
    crawl_videos()

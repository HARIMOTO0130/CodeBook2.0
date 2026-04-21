#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
视频爬取模块 V2.0
开发自动化爬虫程序，针对指定的相关书籍及其对应章节，精准爬取教学视频资源
确保每本书每个章节的视频都符合本章内容
"""
import os
import time
import random
import logging
import requests
import subprocess
import json
from urllib.parse import urljoin, urlparse, quote
from datetime import datetime
from django.db import transaction
from django.conf import settings

from .models import Book, Chapter, ChapterMedia
from .quality_assurance import QualityAssurance

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(settings.BASE_DIR, 'video_crawler.log')
)
logger = logging.getLogger('video_crawler')

class VideoCrawler:
    """视频爬虫类 V2.0"""

    def __init__(self):
        """初始化爬虫"""
        # B站API
        self.bilibili_api = {
            'search': 'https://api.bilibili.com/x/web-interface/search/type',
            'video_info': 'https://api.bilibili.com/x/web-interface/view',
            'playurl': 'https://api.bilibili.com/x/player/playurl'
        }

        # 模拟浏览器头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Origin': 'https://www.bilibili.com',
            'Referer': 'https://www.bilibili.com'
        }

        # 爬取进度记录
        self.progress = {}

        # 初始化质量保障实例
        self.qa = QualityAssurance()

        # 视频存储根目录
        self.video_root_dir = os.path.join(settings.MEDIA_ROOT, 'chapter_media')
        os.makedirs(self.video_root_dir, exist_ok=True)

    def random_delay(self, min_seconds=2, max_seconds=5):
        """随机延迟，避免被反爬"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def search_bilibili_videos(self, keyword, limit=5):
        """
        使用B站API搜索视频
        返回匹配的视频列表
        """
        try:
            # 构建搜索URL
            params = {
                'search_type': 'video',
                'keyword': keyword,
                'page': 1,
                'pagesize': limit,
                'order': 'totalrank',  # 按相关性排序
                'duration': 0  # 所有时长
            }

            logger.info(f"搜索B站视频: {keyword}")

            response = requests.get(
                self.bilibili_api['search'],
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data['code'] == 0 and data['data']['result']:
                    videos = []
                    for item in data['data']['result']:
                        videos.append({
                            'bvid': item.get('bvid', ''),
                            'title': item.get('title', '').replace('<em class="keyword">', '').replace('</em>', ''),
                            'author': item.get('author', ''),
                            'duration': item.get('duration', '00:00'),
                            'pubdate': item.get('pubdate', 0),
                            'description': item.get('description', ''),
                            'aid': item.get('aid', 0)
                        })
                    logger.info(f"搜索到 {len(videos)} 个视频")
                    return videos
                else:
                    logger.warning(f"搜索失败: {data.get('message', '未知错误')}")
                    return []
            else:
                logger.error(f"请求失败: HTTP {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"搜索视频时出错: {str(e)}")
            return []

    def get_video_info(self, bvid):
        """获取视频详细信息"""
        try:
            params = {'bvid': bvid}
            response = requests.get(
                self.bilibili_api['video_info'],
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data['code'] == 0:
                    return data['data']
            return None
        except Exception as e:
            logger.error(f"获取视频信息失败: {str(e)}")
            return None

    def get_chapter_video_dir(self, chapter):
        """获取章节视频存储目录"""
        book_id = chapter.book.id
        chapter_id = chapter.id
        chapter_dir = os.path.join(self.video_root_dir, f'book_{book_id}', f'chapter_{chapter_id}')
        os.makedirs(chapter_dir, exist_ok=True)
        return chapter_dir

    def download_and_merge_video(self, bvid, output_dir, filename):
        """
        下载并合并B站视频
        使用yt-dlp下载，使用ffmpeg合并
        """
        try:
            final_output = os.path.join(output_dir, f"{filename}.mp4")

            # 检查是否已有合并好的视频
            if os.path.exists(final_output):
                logger.info(f"视频已存在: {final_output}")
                return final_output

            # 清理之前的临时文件
            for file in os.listdir(output_dir):
                if filename in file and not file.endswith('.mp4'):
                    try:
                        os.remove(os.path.join(output_dir, file))
                    except:
                        pass

            # 使用yt-dlp下载最佳格式并自动合并
            # 选择包含视频和音频的格式
            output_template = os.path.join(output_dir, f"{filename}.%(ext)s")
            cmd = [
                'yt-dlp',
                '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
                '--merge-output-format', 'mp4',
                '-o', output_template,
                f'https://www.bilibili.com/video/{bvid}'
            ]

            logger.info(f"开始下载B站视频: {bvid}")
            logger.info(f"命令: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                # 查找下载的文件
                for file in os.listdir(output_dir):
                    if filename in file and file.endswith('.mp4'):
                        downloaded_file = os.path.join(output_dir, file)
                        # 如果文件名不是最终文件名，重命名
                        if downloaded_file != final_output:
                            import shutil
                            shutil.move(downloaded_file, final_output)
                        logger.info(f"视频下载成功: {final_output}")
                        return final_output

                logger.error("视频下载成功但未找到mp4文件")
                return None
            else:
                logger.error(f"视频下载失败: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"下载视频时出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def crawl_chapter_videos(self, chapter):
        """
        爬取章节相关的视频
        确保视频内容与章节标题匹配
        """
        try:
            # 构建搜索关键词 - 使用章节标题和书名
            search_keyword = f"{chapter.title}"
            logger.info(f"开始爬取章节视频: {search_keyword}")

            # 搜索B站视频
            videos = self.search_bilibili_videos(search_keyword, limit=3)

            if not videos:
                # 如果没有匹配结果，尝试只用章节标题
                search_keyword_simple = chapter.title.replace(f"第{chapter.order}章", "").strip()
                videos = self.search_bilibili_videos(search_keyword_simple, limit=3)

            # 记录爬取进度
            self.progress[chapter.id] = {
                'total': len(videos),
                'processed': 0,
                'status': 'in_progress'
            }

            # 获取章节视频存储目录
            chapter_dir = self.get_chapter_video_dir(chapter)

            # 保存视频到数据库
            saved_count = 0
            for i, video in enumerate(videos):
                if saved_count >= 3:  # 每个章节最多3个视频
                    break

                # 检查是否已经存在相同的视频
                existing = ChapterMedia.objects.filter(
                    chapter=chapter,
                    media_type='video'
                ).exists()

                if existing:
                    logger.info(f"章节已有视频，跳过")
                    continue

                # 生成文件名
                filename = f"video_{chapter.id}_{saved_count + 1}_{video['bvid']}"

                # 下载视频
                local_path = self.download_and_merge_video(
                    video['bvid'],
                    chapter_dir,
                    filename
                )

                with transaction.atomic():
                    # 构建媒体对象
                    media_data = {
                        'chapter': chapter,
                        'media_type': 'video',
                        'title': video['title'],
                        'description': f"{chapter.book.title} - {chapter.title}: {video['description'][:200] if video['description'] else ''}",
                        'order': saved_count,
                        'duration': video['duration'],
                        'video_format': 'mp4',
                        'file_size': '0'
                    }

                    # 设置URL
                    if local_path and os.path.exists(local_path):
                        # 生成相对URL
                        media_root_str = str(settings.MEDIA_ROOT)
                        relative_path = local_path.replace(media_root_str, '')
                        if not relative_path.startswith('/'):
                            relative_path = '/' + relative_path
                        relative_path = relative_path.replace('\\', '/')
                        media_data['url'] = relative_path

                        # 获取文件大小
                        file_size = os.path.getsize(local_path)
                        media_data['file_size'] = str(file_size)
                    else:
                        # 如果下载失败，使用B站链接
                        media_data['url'] = f"https://www.bilibili.com/video/{video['bvid']}/"

                    ChapterMedia.objects.create(**media_data)
                    saved_count += 1

                    logger.info(f"已保存视频: {video['title']}")

                # 更新进度
                self.progress[chapter.id]['processed'] = i + 1
                logger.info(f"爬取进度: {chapter.title} - {i+1}/{len(videos)}")

                # 下载间隔
                self.random_delay(3, 6)

            # 更新章节类型为视频
            if saved_count > 0 and chapter.type != 'video':
                chapter.type = 'video'
                chapter.save()

            # 完成爬取
            self.progress[chapter.id]['status'] = 'completed'
            logger.info(f"章节视频爬取完成: {chapter.title}, 保存了 {saved_count} 个视频")

            # 记录爬取日志
            self.qa.log_video_crawl(
                book_id=chapter.book.id,
                chapter_id=chapter.id,
                status='success' if saved_count > 0 else 'partial',
                message=f"爬取完成，保存了 {saved_count} 个视频",
                video_count=saved_count
            )

            return saved_count

        except Exception as e:
            logger.error(f"爬取章节视频失败 {chapter.title}: {str(e)}")
            if chapter.id in self.progress:
                self.progress[chapter.id]['status'] = 'failed'

            # 记录失败日志
            self.qa.log_video_crawl(
                book_id=chapter.book.id,
                chapter_id=chapter.id,
                status='failure',
                message=str(e),
                video_count=0
            )

            return 0

    def crawl_book_videos(self, book):
        """爬取整本书的视频"""
        try:
            chapters = book.chapters.filter(type__in=['reading', 'video'])
            total_chapters = chapters.count()
            processed_chapters = 0
            total_videos = 0

            logger.info(f"开始爬取书籍视频: {book.title}, 共 {total_chapters} 个章节")

            for chapter in chapters:
                videos_count = self.crawl_chapter_videos(chapter)
                total_videos += videos_count
                processed_chapters += 1

                logger.info(f"书籍爬取进度: {processed_chapters}/{total_chapters}, 已获取 {total_videos} 个视频")

                # 章节间延迟
                self.random_delay(5, 10)

            logger.info(f"书籍视频爬取完成: {book.title}, 共获取 {total_videos} 个视频")
            return total_videos

        except Exception as e:
            logger.error(f"爬取书籍视频失败 {book.title}: {str(e)}")
            return 0

    def crawl_all_books(self):
        """爬取所有书籍的视频"""
        try:
            books = Book.objects.filter(status='published')
            total_books = books.count()
            processed_books = 0
            total_videos = 0

            logger.info(f"开始爬取所有书籍视频, 共 {total_books} 本书")

            for book in books:
                book_videos = self.crawl_book_videos(book)
                total_videos += book_videos
                processed_books += 1

                logger.info(f"全局爬取进度: {processed_books}/{total_books}, 已获取 {total_videos} 个视频")

                # 书籍间延迟
                self.random_delay(10, 20)

            logger.info(f"所有书籍视频爬取完成, 共获取 {total_videos} 个视频")
            return total_videos

        except Exception as e:
            logger.error(f"爬取所有书籍视频失败: {str(e)}")
            return 0

    def get_progress(self):
        """获取爬取进度"""
        return self.progress

    def clear_progress(self):
        """清除爬取进度"""
        self.progress = {}


# 测试函数
def test_crawler():
    """测试爬虫功能"""
    crawler = VideoCrawler()

    # 测试搜索功能
    logger.info("测试搜索功能...")
    videos = crawler.search_bilibili_videos("Python基础教程")
    logger.info(f"搜索结果: {len(videos)} 个视频")
    for v in videos[:3]:
        logger.info(f"  - {v['title']} ({v['bvid']})")


if __name__ == "__main__":
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()

    # 运行测试
    test_crawler()
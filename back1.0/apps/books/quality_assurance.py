#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
质量保障模块
实现数据校验、文件完整性检查和日志系统
"""
import os
import logging
import hashlib
from datetime import datetime
from django.db import transaction
from django.conf import settings

from .models import ChapterMedia

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(settings.BASE_DIR, 'quality_assurance.log')
)
logger = logging.getLogger('quality_assurance')

class QualityAssurance:
    """质量保障类"""
    
    def __init__(self):
        """初始化质量保障类"""
        pass
    
    def validate_video_data(self, video_data):
        """验证视频数据的完整性和准确性"""
        try:
            # 检查必要字段
            required_fields = ['url', 'title', 'media_type']
            for field in required_fields:
                if field not in video_data:
                    logger.error(f"视频数据缺少必要字段: {field}")
                    return False, f"缺少必要字段: {field}"
            
            # 检查媒体类型
            if video_data['media_type'] != 'video':
                logger.error(f"媒体类型错误: {video_data['media_type']}")
                return False, "媒体类型必须为video"
            
            # 检查URL格式
            if not video_data['url'].startswith(('http://', 'https://')):
                logger.error(f"URL格式错误: {video_data['url']}")
                return False, "URL格式错误"
            
            # 检查标题长度
            if len(video_data['title']) > 200:
                logger.error(f"标题过长: {video_data['title']}")
                return False, "标题长度不能超过200个字符"
            
            logger.info(f"视频数据验证通过: {video_data['title']}")
            return True, "数据验证通过"
        except Exception as e:
            logger.error(f"验证视频数据失败: {str(e)}")
            return False, f"验证失败: {str(e)}"
    
    def check_file_integrity(self, file_path):
        """检查文件完整性"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False, "文件不存在"
            
            # 计算文件MD5值
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                # 分块读取文件
                for chunk in iter(lambda: f.read(4096), b''):
                    md5_hash.update(chunk)
            file_hash = md5_hash.hexdigest()
            
            logger.info(f"文件完整性检查通过: {file_path}, MD5: {file_hash}")
            return True, file_hash
        except Exception as e:
            logger.error(f"检查文件完整性失败: {str(e)}")
            return False, f"检查失败: {str(e)}"
    
    def validate_chapter_media(self, chapter_id):
        """验证章节媒体数据的完整性"""
        try:
            media_list = ChapterMedia.objects.filter(chapter_id=chapter_id)
            valid_count = 0
            invalid_count = 0
            
            for media in media_list:
                # 验证媒体数据
                video_data = {
                    'url': media.url or '',
                    'title': media.title or '',
                    'media_type': media.media_type
                }
                is_valid, message = self.validate_video_data(video_data)
                
                if is_valid:
                    valid_count += 1
                    # 如果有本地文件，检查文件完整性
                    if media.file and hasattr(media.file, 'path'):
                        file_path = media.file.path
                        self.check_file_integrity(file_path)
                else:
                    invalid_count += 1
                    logger.error(f"章节 {chapter_id} 的媒体数据无效: {message}")
            
            logger.info(f"章节 {chapter_id} 的媒体数据验证完成: 有效 {valid_count}, 无效 {invalid_count}")
            return valid_count, invalid_count
        except Exception as e:
            logger.error(f"验证章节媒体数据失败: {str(e)}")
            return 0, 0
    
    def log_video_crawl(self, book_id, chapter_id, status, message, video_count=0):
        """记录视频爬取日志"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'book_id': book_id,
                'chapter_id': chapter_id,
                'status': status,  # success, failure, partial
                'message': message,
                'video_count': video_count
            }
            
            logger.info(f"视频爬取日志: {log_entry}")
            return True
        except Exception as e:
            logger.error(f"记录视频爬取日志失败: {str(e)}")
            return False
    
    def log_frontend_access(self, user_id, book_id, chapter_id, action, status):
        """记录前端访问日志"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'book_id': book_id,
                'chapter_id': chapter_id,
                'action': action,  # view, play, download
                'status': status  # success, failure
            }
            
            logger.info(f"前端访问日志: {log_entry}")
            return True
        except Exception as e:
            logger.error(f"记录前端访问日志失败: {str(e)}")
            return False
    
    def clean_invalid_media(self):
        """清理无效的媒体数据"""
        try:
            # 查找无效的媒体数据
            invalid_media = ChapterMedia.objects.filter(
                media_type='video',
                url__isnull=True,
                file__isnull=True
            )
            
            count = invalid_media.count()
            if count > 0:
                with transaction.atomic():
                    invalid_media.delete()
                logger.info(f"清理了 {count} 条无效的媒体数据")
            else:
                logger.info("没有发现无效的媒体数据")
            
            return count
        except Exception as e:
            logger.error(f"清理无效媒体数据失败: {str(e)}")
            return 0

# 测试函数
def test_quality_assurance():
    """测试质量保障功能"""
    qa = QualityAssurance()
    
    # 测试视频数据验证
    test_video_data = {
        'url': 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4',
        'title': '测试视频',
        'media_type': 'video'
    }
    is_valid, message = qa.validate_video_data(test_video_data)
    print(f"视频数据验证: {is_valid}, {message}")
    
    # 测试前端访问日志
    qa.log_frontend_access(1, 1, 1, 'view', 'success')
    
    # 测试视频爬取日志
    qa.log_video_crawl(1, 1, 'success', '爬取成功', 3)
    
    # 测试清理无效媒体数据
    count = qa.clean_invalid_media()
    print(f"清理了 {count} 条无效的媒体数据")

if __name__ == "__main__":
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()
    
    # 运行测试
    test_quality_assurance()

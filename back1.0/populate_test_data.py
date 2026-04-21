#!/usr/bin/env python
"""
填充测试数据脚本
"""

import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User, UserPreferences
from apps.books.models import Book, Chapter, BookTag, BookCategory, BookReview
from apps.learning.models import LearningRecord, Note, WrongQuestion, Exercise
from apps.teacher.models import Student, StudentClass, Homework
from apps.toolkit.models import Tool, ToolCategory
from apps.review.models import ReviewTask, ManualReviewRecord, WorkflowLog, BookEditHistory
import datetime
import random


def create_users():
    """创建测试用户"""
    print("创建测试用户...")
    
    # 创建管理员用户
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
    
    # 创建普通用户
    user1, created = User.objects.get_or_create(
        username='student1',
        defaults={
            'email': 'student1@example.com',
            'first_name': 'Student',
            'last_name': 'One'
        }
    )
    if created:
        user1.set_password('student123')
        user1.save()
    
    user2, created = User.objects.get_or_create(
        username='teacher1',
        defaults={
            'email': 'teacher1@example.com',
            'first_name': 'Teacher',
            'last_name': 'One',
            'is_staff': True
        }
    )
    if created:
        user2.set_password('teacher123')
        user2.save()
    
    # 创建审核员用户
    reviewer, created = User.objects.get_or_create(
        username='reviewer1',
        defaults={
            'email': 'reviewer1@example.com',
            'first_name': 'Reviewer',
            'last_name': 'One',
            'role': 'reviewer',
            'is_staff': True
        }
    )
    if created:
        reviewer.set_password('reviewer123')
        reviewer.save()
    
    # 创建用户偏好设置
    for user in User.objects.all():
        UserPreferences.objects.get_or_create(
            user=user,
            defaults={
                'default_language': 'python',
                'code_theme': 'vs-dark',
                'auto_play_video': False,
                'keyboard_shortcuts': True,
                'show_line_numbers': True,
                'use_vim_mode': False,
                'learning_goals': [],
                'major_category': 'science',
                'learning_stage': 'beginner',
                'interests': [],
                'enable_learning_reminders': True,
                'reminder_time': '09:00',
                'daily_reminder': True,
                'deadline_reminder': True
            }
        )
    
    print("用户创建完成")


def create_books():
    """创建测试书籍"""
    print("创建测试书籍...")
    
    # 创建书籍分类
    categories = [
        {'name': '编程', 'slug': 'programming'},
        {'name': '数学', 'slug': 'math'},
        {'name': '英语', 'slug': 'english'},
        {'name': '物理', 'slug': 'physics'},
        {'name': '化学', 'slug': 'chemistry'}
    ]
    for cat_data in categories:
        BookCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'slug': cat_data['slug']}
        )
    
    # 创建书籍标签
    tags = ['入门', '进阶', '高级', '实战', '理论']
    for tag_name in tags:
        BookTag.objects.get_or_create(name=tag_name)
    
    # 创建测试书籍
    books_data = [
        {
            'title': 'Python编程基础',
            'subtitle': '从入门到精通',
            'author': '张三',
            'description': 'Python入门教程，适合零基础学习',
            'current_version': '1.0.0',
            'status': 'published'
        },
        {
            'title': 'Java核心技术',
            'subtitle': '卷I：基础知识',
            'author': '李四',
            'description': 'Java高级编程指南',
            'current_version': '2.0.0',
            'status': 'published'
        },
        {
            'title': 'Web前端开发',
            'subtitle': 'HTML/CSS/JavaScript',
            'author': '王五',
            'description': '现代Web前端开发技术',
            'current_version': '1.5.0',
            'status': 'published'
        },
        {
            'title': '数据结构与算法',
            'subtitle': 'Python实现',
            'author': '赵六',
            'description': '数据结构与算法的Python实现',
            'current_version': '1.2.0',
            'status': 'published'
        },
        {
            'title': '机器学习基础',
            'subtitle': '理论与实践',
            'author': '钱七',
            'description': '机器学习入门教程',
            'current_version': '1.0.0',
            'status': 'published'
        },
        # 新增两本待审核的教材
        {
            'title': '人工智能导论',
            'subtitle': '概念与应用',
            'author': '孙八',
            'description': '人工智能基础概念和实际应用',
            'current_version': '1.0.0',
            'status': 'pending_review'
        },
        {
            'title': '云计算技术',
            'subtitle': '原理与实践',
            'author': '周九',
            'description': '云计算技术的基本原理和实践应用',
            'current_version': '1.0.0',
            'status': 'pending_review'
        }
    ]
    
    for book_data in books_data:
        book, created = Book.objects.get_or_create(
            title=book_data['title'],
            defaults=book_data
        )
        
        # 添加分类和标签
        # 随机添加分类
        categories = BookCategory.objects.all()
        if categories and not book.categories.exists():
            book.categories.add(random.choice(categories))
        
        # 随机添加标签
        tags = BookTag.objects.all()
        if tags and not book.tag_objects.exists():
            for _ in range(random.randint(1, 3)):
                tag = random.choice(tags)
                book.tag_objects.add(tag)
        
        # 添加章节
        if not book.chapters.exists():
            for i in range(1, 6):
                Chapter.objects.create(
                    book=book,
                    title=f'第{i}章',
                    content=f'这是第{i}章的内容',
                    order=i
                )
    
    print("书籍创建完成")


def create_learning_data():
    """创建学习相关数据"""
    print("创建学习相关数据...")
    
    users = User.objects.all()
    books = Book.objects.all()
    
    # 创建学习记录
    for user in users:
        for book in books:
            # 获取书籍的章节
            chapters = book.chapters.all()
            if chapters:
                for chapter in chapters:
                    LearningRecord.objects.get_or_create(
                        user=user,
                        book=book,
                        chapter=chapter,
                        defaults={
                            'progress': random.randint(0, 100),
                            'last_learn_time': datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))
                        }
                    )
    
    # 创建笔记
    for user in users:
        for book in books:
            for i in range(1, 4):
                Note.objects.get_or_create(
                    user=user,
                    book=book,
                    defaults={
                        'title': f'{book.title}笔记{i}',
                        'content': f'这是{book.title}的第{i}条笔记',
                        'is_favorite': random.choice([True, False])
                    }
                )
    
    # 创建错题
    for user in users:
        for book in books:
            for i in range(1, 4):
                WrongQuestion.objects.get_or_create(
                    user=user,
                    book=book,
                    defaults={
                        'title': f'关于{book.title}的问题{i}',
                        'question_type': random.choice(['multiple_choice', 'fill_blank', 'short_answer']),
                        'attempt_time': datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30))
                    }
                )
    
    # 创建练习
    for i in range(1, 6):
        Exercise.objects.get_or_create(
            title=f'练习{i}',
            defaults={
                'description': f'第{i}套练习题',
                'question': f'问题{i}: 请编写一个函数实现...',
                'language': 'python',
                'difficulty': random.randint(1, 3),
                'category': 'python_basic'
            }
        )
    
    print("学习数据创建完成")


def create_teacher_data():
    """创建教师相关数据"""
    print("创建教师相关数据...")
    
    # 创建教师
    teacher_user, created = User.objects.get_or_create(
        username='teacher1',
        defaults={
            'email': 'teacher1@example.com',
            'first_name': 'Teacher',
            'last_name': 'One',
            'role': 'teacher'
        }
    )
    if created:
        teacher_user.set_password('teacher123')
        teacher_user.save()
    
    # 创建学生用户
    for i in range(1, 11):
        student_user, created = User.objects.get_or_create(
            username=f'student{i}',
            defaults={
                'email': f'student{i}@example.com',
                'first_name': f'学生{i}',
                'last_name': '',
                'role': 'student'
            }
        )
        if created:
            student_user.set_password(f'student{i}')
            student_user.save()
    
    print("教师数据创建完成")


def create_toolkit_data():
    """创建工具箱数据"""
    print("创建工具箱数据...")
    
    # 创建工具分类
    categories = [
        {'name': '文档处理', 'slug': 'document-processing'},
        {'name': '图像处理', 'slug': 'image-processing'},
        {'name': '数据处理', 'slug': 'data-processing'},
        {'name': '开发工具', 'slug': 'development-tools'},
        {'name': '其他', 'slug': 'other'}
    ]
    for cat_data in categories:
        ToolCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'slug': cat_data['slug']}
        )
    
    # 创建工具
    tools_data = [
        {
            'title': '批量重命名文件',
            'description': '批量重命名文件工具',
            'category': '文档处理',
            'is_active': True
        },
        {
            'title': 'Excel表格合并',
            'description': '合并多个Excel文件',
            'category': '数据处理',
            'is_active': True
        },
        {
            'title': '图片批量压缩',
            'description': '批量压缩图片文件',
            'category': '图像处理',
            'is_active': True
        },
        {
            'title': '文本内容提取',
            'description': '从文档中提取文本',
            'category': '文档处理',
            'is_active': True
        },
        {
            'title': '代码格式化',
            'description': '格式化代码文件',
            'category': '开发工具',
            'is_active': True
        }
    ]
    
    for tool_data in tools_data:
        category, _ = ToolCategory.objects.get_or_create(name=tool_data['category'])
        Tool.objects.get_or_create(
            title=tool_data['title'],
            defaults={
                'description': tool_data['description'],
                'category': category,
                'is_active': tool_data['is_active']
            }
        )
    
    print("工具箱数据创建完成")


def create_review_data():
    """创建教材审核相关数据"""
    print("创建教材审核相关数据...")
    
    # 获取所有书籍
    books = Book.objects.all()
    if not books:
        print("没有找到书籍，跳过审核数据创建")
        return
    
    # 获取审核员用户（使用admin作为审核员）
    reviewer = User.objects.filter(username='admin').first()
    if not reviewer:
        print("没有找到审核员用户，跳过审核数据创建")
        return
    
    # 为每本书创建审核记录
    for book in books:
        # 创建BookReview记录
        BookReview.objects.get_or_create(
            book=book,
            reviewer=reviewer,
            defaults={
                'status': random.choice(['pending', 'approved', 'rejected']),
                'comment': f'这是对《{book.title}》的审核意见'
            }
        )
        
        # 检查是否已存在ReviewTask记录
        existing_tasks = ReviewTask.objects.filter(book_id=book.id)
        if not existing_tasks.exists():
            # 创建ReviewTask记录
            ReviewTask.objects.create(
                book_id=book.id,
                book_title=book.title,
                book_subtitle=book.subtitle or '',
                book_author=book.author,
                status=random.choice(['pending', 'in_review', 'approved', 'rejected']),
                task_type=random.choice(['new_submission', 'edit_review']),
                priority=random.randint(0, 3),
                chapter_count=book.chapters.count(),
                description=book.description or '',
                category_name=book.categories.first().name if book.categories.exists() else '',
                tags=[tag.name for tag in book.tag_objects.all()]
            )
    
    # 获取所有审核任务
    tasks = ReviewTask.objects.all()
    for task in tasks:
        # 创建人工审核记录
        ManualReviewRecord.objects.get_or_create(
            task=task,
            reviewer=reviewer,
            defaults={
                'decision': random.choice(['approved', 'rejected', 'needs_revision']),
                'overall_comment': f'对任务 {task.book_title} 的人工审核意见',
                'content_quality_score': random.randint(60, 100),
                'accuracy_score': random.randint(60, 100),
                'completeness_score': random.randint(60, 100),
                'formatting_score': random.randint(60, 100),
                'language_score': random.randint(60, 100),
                'content_issues': ['内容问题1', '内容问题2'],
                'format_issues': ['格式问题1', '格式问题2'],
                'suggestions': '改进建议'
            }
        )
        
        # 创建工作流日志
        WorkflowLog.objects.create(
            task=task,
            action=random.choice(['created', 'assigned', 'claimed', 'ai_reviewed', 'manual_reviewed', 'approved', 'rejected']),
            actor_type='reviewer',
            from_status='pending',
            to_status=task.status,
            comment=f'工作流日志：{task.book_title}',
            actor=reviewer
        )
    
    # 创建教材编辑历史
    for book in books:
        BookEditHistory.objects.create(
            book_id=book.id,
            book_title=book.title,
            action=random.choice(['created', 'updated', 'submitted', 'approved', 'rejected', 'published']),
            action_display=f'对《{book.title}》的操作',
            actor_id=reviewer.id,
            actor_name=f'{reviewer.first_name} {reviewer.last_name}',
            actor_username=reviewer.username
        )
    
    print("教材审核数据创建完成")


def main():
    """主函数"""
    print("开始填充测试数据...")
    
    create_users()
    create_books()
    create_learning_data()
    create_teacher_data()
    create_toolkit_data()
    create_review_data()
    
    print("测试数据填充完成！")


if __name__ == '__main__':
    main()

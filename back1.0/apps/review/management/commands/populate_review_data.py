#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为审核端添加测试数据的管理命令
使用方法: python manage.py populate_review_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.review.models import ReviewTask, ManualReviewRecord, AIReviewRecord, TeacherProfile
from apps.users.models import User
import random
from datetime import timedelta


def create_teacher_profiles():
    """创建教师档案"""
    teachers = [
        {
            'username': 'teacher1',
            'email': 'teacher1@example.com',
            'employee_id': 'T001',
            'name': '张三',
            'department': '计算机科学与技术',
            'title': '副教授',
            'phone': '13800138001',
            'teaching_subjects': ['Python编程', '数据结构', '算法设计'],
            'research_areas': ['人工智能', '机器学习']
        },
        {
            'username': 'teacher2',
            'email': 'teacher2@example.com',
            'employee_id': 'T002',
            'name': '李四',
            'department': '数学与统计',
            'title': '教授',
            'phone': '13800138002',
            'teaching_subjects': ['高等数学', '线性代数', '概率统计'],
            'research_areas': ['应用数学', '数学建模']
        },
        {
            'username': 'teacher3',
            'email': 'teacher3@example.com',
            'employee_id': 'T003',
            'name': '王五',
            'department': '电子工程',
            'title': '讲师',
            'phone': '13800138003',
            'teaching_subjects': ['电路分析', '数字电路', '嵌入式系统'],
            'research_areas': ['嵌入式开发', '物联网']
        }
    ]
    
    created_profiles = []
    for teacher_data in teachers:
        # 检查用户是否存在
        user, created = User.objects.get_or_create(
            username=teacher_data['username'],
            defaults={
                'email': teacher_data['email'],
                'password': '123456'  # 注意：实际生产环境应该使用密码哈希
            }
        )
        
        # 检查教师档案是否存在
        profile, created = TeacherProfile.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': teacher_data['employee_id'],
                'name': teacher_data['name'],
                'department': teacher_data['department'],
                'title': teacher_data['title'],
                'email': teacher_data['email'],
                'phone': teacher_data['phone'],
                'teaching_subjects': teacher_data['teaching_subjects'],
                'research_areas': teacher_data['research_areas']
            }
        )
        
        created_profiles.append(profile)
        if created:
            print(f"已创建教师档案: {profile.name}")
        else:
            print(f"教师档案已存在: {profile.name}")
    
    return created_profiles


def create_review_tasks(teachers):
    """创建审核任务"""
    book_titles = [
        'Python编程基础',
        '数据结构与算法',
        '机器学习入门',
        '高等数学',
        '线性代数',
        '电路分析',
        '数字电路设计',
        '嵌入式系统开发',
        '数据库原理',
        '操作系统原理'
    ]
    
    task_types = ['new_submission', 'edit_review']
    statuses = ['pending', 'in_review', 'approved', 'rejected']
    priorities = [0, 1, 2, 3]
    
    created_tasks = []
    
    # 直接执行SQL插入，避免Django ORM的字段验证
    from django.db import connection
    
    for i, title in enumerate(book_titles):
        # 随机选择教师
        teacher = random.choice(teachers)
        
        # 准备SQL语句
        sql = """
        INSERT INTO review_task (
            book_id, book_title, book_author, book_language, book_word_count, task_type, priority, status,
            submitted_by_id, submitted_by_name, submitted_by_username,
            submitted_by_employee_id, submitted_by_department, submitted_by_email,
            submitted_by_phone, version_number, chapter_count, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        
        # 执行SQL
        with connection.cursor() as cursor:
            cursor.execute(sql, [
                i + 1,
                title,
                teacher.name,
                'zh-CN',
                random.randint(100000, 500000),
                random.choice(task_types),
                random.choice(priorities),
                random.choice(statuses),
                teacher.user.id,
                teacher.name,
                teacher.user.username,
                teacher.employee_id,
                teacher.department,
                teacher.email,
                teacher.phone,
                f'{random.randint(1, 2)}.{random.randint(0, 9)}.{random.randint(0, 9)}',
                random.randint(5, 15)
            ])
            
            # 获取刚插入的任务ID
            task_id = cursor.lastrowid
        
        # 创建一个简单的任务对象，只包含ID和标题
        class MockTask:
            def __init__(self, id, title):
                self.id = id
                self.book_title = title
        
        task = MockTask(task_id, title)
        created_tasks.append(task)
        print(f"已创建审核任务: {title}")
    
    return created_tasks


def create_review_records(tasks, teachers):
    """创建审核记录"""
    decisions = ['approved', 'rejected', 'needs_revision']
    
    created_records = []
    
    # 直接执行SQL插入，避免Django ORM的字段验证
    from django.db import connection
    
    for task in tasks:
        # 为每个任务创建AI审核记录
        ai_sql = """
        INSERT INTO review_ai_record (
            task_id, overall_score, risk_level, content_compliance_score,
            accuracy_score, completeness_score, readability_score,
            detected_issues, risk_items, suggestions, raw_response, model_version, status, processing_time,
            created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        
        with connection.cursor() as cursor:
            cursor.execute(ai_sql, [
                task.id,
                round(random.uniform(70, 95), 2),
                random.choice(['low', 'medium', 'high']),
                round(random.uniform(70, 95), 2),
                round(random.uniform(70, 95), 2),
                round(random.uniform(70, 95), 2),
                round(random.uniform(70, 95), 2),
                '[{"type": "content", "description": "部分内容需要更新"}, {"type": "format", "description": "格式需要调整"}]',
                '[{"level": "medium", "description": "内容准确性需要验证"}]',
                '["建议更新最新的技术内容", "建议改进章节结构"]',
                '{"result": "审核完成", "score": 85}',
                'v1.0',
                'completed',
                random.randint(1000, 5000)
            ])
        
        # 为每个任务创建人工审核记录
        reviewer = random.choice(teachers)
        manual_sql = """
        INSERT INTO review_manual_record (
            task_id, reviewer_id, decision, overall_comment,
            content_quality_score, accuracy_score, completeness_score,
            formatting_score, language_score, content_issues, format_issues,
            suggestions, started_at, completed_at, review_duration,
            created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """
        
        with connection.cursor() as cursor:
            cursor.execute(manual_sql, [
                task.id,
                reviewer.user.id,
                random.choice(decisions),
                '审核完成，建议按照要求进行修改。',
                random.randint(70, 95),
                random.randint(70, 95),
                random.randint(70, 95),
                random.randint(70, 95),
                random.randint(70, 95),
                '["部分章节内容不够详细", "需要增加更多实例"]',
                '["图表格式需要统一", "参考文献格式需要调整"]',
                '建议增加更多实践案例，提高教材的实用性。',
                timezone.now() - timedelta(hours=random.randint(1, 5)),
                timezone.now(),
                random.randint(60, 180)
            ])
        
        created_records.append((task.id, task.book_title))
        print(f"已创建审核记录: {task.book_title}")
    
    return created_records


def populate_all_data():
    """填充所有测试数据"""
    # 创建教师档案
    teachers = create_teacher_profiles()
    
    # 创建审核任务
    tasks = create_review_tasks(teachers)
    
    # 创建审核记录
    create_review_records(tasks, teachers)
    
    return len(tasks)


class Command(BaseCommand):
    """Django管理命令类"""
    help = '为审核端添加测试数据'

    def handle(self, *args, **options):
        self.stdout.write('开始为审核端添加测试数据...')
        task_count = populate_all_data()
        self.stdout.write(self.style.SUCCESS(f'\n数据填充完成！共创建了 {task_count} 个审核任务。'))

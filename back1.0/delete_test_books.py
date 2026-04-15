from apps.books.models import Book, Chapter, BookPermission, PermissionRequest

# 查找所有名为"测试书籍"的书籍
books = Book.objects.filter(title='测试书籍')
print(f'找到{len(books)}本名为"测试书籍"的书籍')

for book in books:
    print(f'删除书籍: {book.id} - {book.title}')
    # 删除相关的章节
    Chapter.objects.filter(book=book).delete()
    print('  - 已删除相关章节')
    # 删除相关的权限
    BookPermission.objects.filter(book=book).delete()
    print('  - 已删除相关权限')
    # 删除相关的权限申请
    PermissionRequest.objects.filter(book=book).delete()
    print('  - 已删除相关权限申请')
    # 删除书籍本身
    book.delete()
    print('  - 已删除书籍')

print('删除完成')

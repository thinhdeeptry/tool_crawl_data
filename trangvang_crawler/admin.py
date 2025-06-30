from django.contrib import admin
from .models import CrawlTask, BusinessData

@admin.register(CrawlTask)
class CrawlTaskAdmin(admin.ModelAdmin):
    # Các trường sẽ hiển thị trong danh sách
    list_display = ('id', 'url_filter', 'status', 'created_at', 'updated_at')
    # Thêm bộ lọc ở bên phải theo trạng thái
    list_filter = ('status',)
    # Thêm ô tìm kiếm
    search_fields = ('url_filter',)
    # Các trường chỉ cho phép đọc, không cho sửa
    readonly_fields = ('created_at', 'updated_at')

@admin.register(BusinessData)
class BusinessDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address', 'category', 'task')
    search_fields = ('name', 'address', 'phone')
    # Cho phép lọc dữ liệu theo task đã sinh ra nó
    list_filter = ('task',)
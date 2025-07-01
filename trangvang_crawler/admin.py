from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import CrawlTask, BusinessData

@admin.register(CrawlTask)
class CrawlTaskAdmin(admin.ModelAdmin):
    # Các trường sẽ hiển thị trong danh sách
    list_display = ('id', 'url_filter', 'status', 'created_at', 'updated_at', 'actions_column')
    # Thêm bộ lọc ở bên phải theo trạng thái
    list_filter = ('status',)
    # Thêm ô tìm kiếm
    search_fields = ('url_filter',)
    # Các trường chỉ cho phép đọc, không cho sửa
    readonly_fields = ('created_at', 'updated_at')

    def actions_column(self, obj):
        buttons = []
        # Nút "Run" chỉ hiển thị khi trạng thái là PENDING và task đã được lưu (có pk)
        if obj.pk and obj.status == 'PENDING':
            run_url = reverse('run_crawl_task', args=[obj.pk])
            buttons.append(f'<a class="button" href="{run_url}">Run</a>')

        # Nút "Export" hiển thị cho các trạng thái khác trừ WARNING, FAILED, PENDING
        if obj.pk and obj.status not in ['WARNING', 'FAILED', 'PENDING']:
            export_url = reverse('export_task_to_excel', args=[obj.pk])
            buttons.append(f'<a class="button" href="{export_url}">Export</a>')
        
        if not buttons:
            return "Không có hành động"
            
        return format_html(' '.join(buttons))

    actions_column.short_description = 'Hành động'
@admin.register(BusinessData)
class BusinessDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address', 'category', 'task')
    search_fields = ('name', 'address', 'phone')
    # Cho phép lọc dữ liệu theo task đã sinh ra nó
    list_filter = ('task',)
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import CrawlTask, BusinessData

@admin.register(CrawlTask)
class CrawlTaskAdmin(admin.ModelAdmin):
    # Các trường sẽ hiển thị trong danh sách
    list_display = ('id', 'url_filter', 'status', 'created_at', 'updated_at', 'export_button')
    # Thêm bộ lọc ở bên phải theo trạng thái
    list_filter = ('status',)
    # Thêm ô tìm kiếm
    search_fields = ('url_filter',)
    # Các trường chỉ cho phép đọc, không cho sửa
    readonly_fields = ('created_at', 'updated_at', 'export_button')
    def export_button(self, obj):
        # 'obj' ở đây là đối tượng CrawlTask hiện tại
        # Kiểm tra xem task có dữ liệu để export không (trạng thái là Done)
        if obj.status == 'DONE':
            # Tạo URL tới view export của chúng ta
            url = reverse('export_task_to_excel', args=[obj.pk])
            return format_html('<a class="button" href="{}">Export to Excel</a>', url)
        # Trả về chuỗi rỗng nếu không phải trạng thái DONE
        return "Chỉ export được khi task ở trạng thái DONE"
    # Đặt tên cho cột trong giao diện Admin
    export_button.short_description = 'Hành động'
@admin.register(BusinessData)
class BusinessDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address', 'category', 'task')
    search_fields = ('name', 'address', 'phone')
    # Cho phép lọc dữ liệu theo task đã sinh ra nó
    list_filter = ('task',)
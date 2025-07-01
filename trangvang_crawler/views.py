import pandas as pd
import io
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import CrawlTask
import subprocess
from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings

@staff_member_required
def run_crawl_task(request, task_id):
    task = get_object_or_404(CrawlTask, pk=task_id)
    if task.status == 'PENDING':
        try:
            command = [
                'python', 'manage.py', 'process_tasks', f'--task_id={task.id}'
            ]
            project_dir = settings.BASE_DIR
            subprocess.Popen(command, cwd=project_dir)
            messages.success(request, f"Đã bắt đầu chạy task crawling cho ID: {task.id}")
        except Exception as e:
            messages.error(request, f"Lỗi khi bắt đầu task: {e}")
    else:
        messages.warning(request, f"Task {task.id} không ở trạng thái PENDING.")
    
    return redirect('admin:trangvang_crawler_crawltask_changelist')

# Decorator này đảm bảo chỉ có user là staff (có quyền vào trang admin) mới có thể truy cập view này
@staff_member_required
def export_task_to_excel(request, task_id):
    """
    View này xử lý việc export dữ liệu của một task ra file Excel.
    """
    # 1. Lấy đối tượng Task hoặc trả về lỗi 404 nếu không tìm thấy
    task = get_object_or_404(CrawlTask, pk=task_id)

    # 2. Lấy tất cả dữ liệu doanh nghiệp liên quan đến task này
    # Dùng .values() để tăng hiệu suất và lấy dữ liệu dưới dạng dictionary
    businesses_data = task.businesses.all().values(
        'name', 'phone', 'address', 'category', 'website'
    )

    if not businesses_data:
        return HttpResponse("Không có dữ liệu doanh nghiệp nào để export cho task này.")

    # 3. Sử dụng Pandas để tạo DataFrame
    df = pd.DataFrame(list(businesses_data))

    # Đổi tên cột để file Excel dễ đọc hơn
    df.rename(columns={
        'name': 'Tên Công Ty',
        'phone': 'Số Điện Thoại',
        'address': 'Địa Chỉ',
        'category': 'Ngành Nghề',
        'website': 'Website'
    }, inplace=True)

    # 4. Tạo một buffer trong bộ nhớ để lưu file Excel
    # Điều này giúp tránh việc phải ghi file tạm ra đĩa
    excel_buffer = io.BytesIO()

    # 5. Ghi DataFrame vào buffer dưới định dạng Excel
    df.to_excel(excel_buffer, index=False, engine='openpyxl')

    # Di chuyển con trỏ về đầu buffer
    excel_buffer.seek(0)

    # 6. Tạo một HttpResponse để trả file về cho trình duyệt
    response = HttpResponse(
        excel_buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    # Thiết lập header để trình duyệt hiểu đây là một file cần tải xuống
    response['Content-Disposition'] = f'attachment; filename="task_{task.id}_data.xlsx"'

    return response 
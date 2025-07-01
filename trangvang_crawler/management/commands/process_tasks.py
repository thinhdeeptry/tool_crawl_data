import subprocess
from django.core.management.base import BaseCommand
from trangvang_crawler.models import CrawlTask
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Processes a pending crawl task'

    def handle(self, *args, **options):
        # 1. Tìm một task đang chờ xử lý
        task = CrawlTask.objects.filter(status__in=['PENDING', 'IN_PROGRESS']).order_by('created_at').first()

        if not task:
            self.stdout.write(self.style.SUCCESS('Không có task nào đang chờ.'))
            return

        self.stdout.write(f'Bắt đầu xử lý task ID: {task.id} với URL: {task.url_filter}')

        try:
            # 2. Cập nhật trạng thái thành "In Progress"
            task.status = 'IN_PROGRESS'
            task.save()
            self.stdout.write(f'Đã cập nhật task {task.id} sang trạng thái IN_PROGRESS.')

            # 3. Thực thi spider Scrapy
            # Xây dựng câu lệnh để chạy spider
            command = [
                'scrapy', 'crawl', 'trangvang',
                '-a', f'url_filter={task.url_filter}',
                '-a', f'task_id={task.id}'
            ]

            # Gọi Scrapy như một tiến trình con
            result = subprocess.run(command, check=True, cwd='./crawler')
            
            # dựa trên số lượng items đã crawl được
            self.stdout.write(self.style.SUCCESS(f'Đã chạy xong spider cho task {task.id}.'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Lỗi khi xử lý task {task.id}: {e}'))
            task.status = 'FAILED'
            task.save()
            self.stdout.write(self.style.ERROR(f'Đã cập nhật task {task.id} sang trạng thái FAILED.'))
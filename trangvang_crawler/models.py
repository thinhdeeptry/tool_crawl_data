from django.db import models

class CrawlTask(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'# tên hằng = 'giá trị db', 'nhãn hiển thị'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        DONE = 'DONE', 'Done'
        FAILED = 'FAILED', 'Failed'
        WARNING = 'WARNING', 'Warning'

    url_filter = models.URLField(max_length=1024, help_text="URL filter từ trangvangvietnam.com")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Task for {self.url_filter} ({self.status})"

class BusinessData(models.Model):
    task = models.ForeignKey(CrawlTask, on_delete=models.CASCADE, related_name='businesses')
    name = models.CharField(max_length=255, verbose_name="Tên công ty")
    phone = models.CharField(max_length=100, null=True, blank=True, verbose_name="Số điện thoại")
    address = models.TextField(null=True, blank=True, verbose_name="Địa chỉ")
    category = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ngành nghề")
    website = models.URLField(max_length=500, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    # Thêm các trường khác nếu cần, ví dụ:
    # source_url = models.URLField(max_length=1024, verbose_name="URL trang chi tiết")

    def __str__(self):
        return self.name
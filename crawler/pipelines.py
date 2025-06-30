# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from trangvang_crawler.models import BusinessData, CrawlTask
from asgiref.sync import sync_to_async
import asyncio

class CrawlerPipeline:
    def process_item(self, item, spider):
        return item

class DatabasePipeline:
    def process_item(self, item, spider):
        asyncio.create_task(self.save_to_db(item, spider))
        return item
    
    async def save_to_db(self, item, spider):
        try:
            # Lấy đối tượng Task từ task_id
            spider.logger.info(f"Đang lưu doanh nghiệp với task_id: {item['task_id']}")
            
            # Sử dụng sync_to_async để bọc các thao tác Django ORM
            @sync_to_async
            def get_task(task_id):
                try:
                    return CrawlTask.objects.get(id=task_id)
                except CrawlTask.DoesNotExist:
                    return None
            
            @sync_to_async
            def save_business(task, item):
                business = BusinessData(
                    task=task,
                    name=item.get("name", "").strip() if item.get("name") else "",
                    address=item.get("address", "").strip() if item.get("address") else "",
                    phone=item.get("phone", "").strip() if item.get("phone") else "",
                    website=item.get("website"),
                    email=item.get("email"),
                    category=item.get("category", ""),
                )
                business.save()
                return business.name
            
            # Thực hiện các thao tác bất đồng bộ
            task = await get_task(item["task_id"])
            if not task:
                spider.logger.error(f"Task with id {item['task_id']} does not exist.")
                return
            
            business_name = await save_business(task, item)
            spider.logger.info(f"Đã lưu doanh nghiệp '{business_name}' vào database.")
            
        except Exception as e:
            spider.logger.error(f"Lỗi khi lưu dữ liệu: {e}")
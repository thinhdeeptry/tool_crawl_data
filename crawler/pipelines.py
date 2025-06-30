# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class CrawlerPipeline:
    def process_item(self, item, spider):
        return item


from trangvang_crawler.models import BusinessData, CrawlTask


class DatabasePipeline:
    def process_item(self, item, spider):
        # Lấy đối tượng Task từ task_id
        try:
            task = CrawlTask.objects.get(id=item["task_id"])
        except CrawlTask.DoesNotExist:
            spider.logger.error(f"Task with id {item['task_id']} does not exist.")
            return item

        # Tạo và lưu đối tượng BusinessData
        business = BusinessData(
            task=task,
            name=item.get("name", "").strip() if item.get("name") else "",
            address=item.get("address", "").strip() if item.get("address") else "",
            phone=item.get("phone", "").strip() if item.get("phone") else "",
            website=item.get("website"),
            email=item.get("email"),
            # Nối các ngành nghề thành một chuỗi
            category=(
                ", ".join(item.get("category", []))
                if isinstance(item.get("category"), list)
                else item.get("category", "")
            ),
        )
        business.save()
        spider.logger.info(f"Đã lưu doanh nghiệp '{business.name}' vào database.")
        return item

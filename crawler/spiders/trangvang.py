from asgiref.sync import sync_to_async
import scrapy
from urllib.parse import urljoin
import re
from trangvang_crawler.models import CrawlTask

class TrangVangSpider(scrapy.Spider):
    # Tên định danh duy nhất của spider
    name = 'trangvang'

    # Hàm khởi tạo, nhận các tham số từ command line
    def __init__(self, url_filter=None, task_id=None, *args, **kwargs):
        super(TrangVangSpider, self).__init__(*args, **kwargs)
        # Kiểm tra và thiết lập URL bắt đầu
        if url_filter:
            self.start_urls = [url_filter]
            self.current_page = 1
        else:
            self.start_urls = ["https://trangvangvietnam.com/categories/100-nha-hang"]
            print("WARNING: Không có URL filter, sử dụng URL mặc định")
        
        # Kiểm tra và thiết lập task_id
        if task_id:
            self.task_id = task_id
        else:
            self.task_id = 1
            print("WARNING: Không có task_id, sử dụng task_id mặc định = 1")
        # 2. Khởi tạo một bộ đếm số item đã crawl được
        self.item_scraped_count = 0
        self.base_url = "https://trangvangvietnam.com"
        print(f"--- BẮT ĐẦU CRAWL TASK {self.task_id} VỚI URL: {url_filter} ---")

    # Phương thức bắt đầu gửi request
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    # Phương thức chính để xử lý và trích xuất dữ liệu
    def parse(self, response):
        # Selector để chọn tất cả các "card" doanh nghiệp trên trang
        business_cards = response.css('div.div_list_cty div.w-100.h-auto.shadow.rounded-3.bg-white.p-2.mb-3')

        print(f"--- Tìm thấy {len(business_cards)} doanh nghiệp trên trang: {response.url} ---")
        if not business_cards and response.request.url in self.start_urls:
            self.logger.warning(f"Không tìm thấy doanh nghiệp nào trên trang bắt đầu: {response.url}")

        for business in business_cards:
            # Trích xuất thông tin email từ href của thẻ a
            email_href = business.css('div.email_web_section a[href^="mailto:"]::attr(href)').get()
            email = None
            if email_href:
                # Trích xuất email từ href="mailto:email@example.com"
                email = email_href.replace('mailto:', '')
            
            # Trích xuất website
            website_element = business.css('div.email_web_section a[href^="http"]')
            website_url = website_element.css('::attr(href)').get()
            
            # Trích xuất ngành nghề
            category_text = business.css('div.logo_congty_diachi div:nth-child(1) span.nganh_listing_txt::text').get()
            if category_text:
                category = category_text.strip()
            else:
                category = None
            
            item = {
                'task_id': self.task_id,
                'name': business.css('div.listings_center h2.fs-5 a::text').get(),
                'address': business.css('div.logo_congty_diachi div:nth-child(2) small::text').get().strip() if business.css('div.logo_congty_diachi div:nth-child(2) small::text').get() else None,
                'phone': business.css('div.logo_congty_diachi div.listing_dienthoai a::text').get(),
                'website': website_url,
                'email': email,
                'category': category,
            }
            # In ra console để kiểm tra (mục tiêu của Task 3.1)
            yield item
            # 3. Tăng bộ đếm mỗi khi có một item được yield
            self.item_scraped_count += 1
            yield item

        # Tìm nút "Trang sau" và đi tiếp
        next_page = response.xpath('//div[@id="paging"]/a[text()="Tiếp"]/@href').get()
        #lấy trang cuối
        max_page_element = response.xpath('//div[@id="paging"]/a[text()="Tiếp"]/preceding-sibling::a[1]/text()').get()
        # Kiểm tra nếu là một số và chuyển đổi thành số nguyên
        max_page = None
        if max_page_element and max_page_element.isdigit():
            max_page = int(max_page_element)
            print(f"--- Trang cuối hiển thị: {max_page} ---")
        # Xác định trang hiện tại
        current_page_element = response.css('a.page_active::text').get()
        current_page = int(current_page_element) if current_page_element and current_page_element.isdigit() else 1

        if next_page and max_page and current_page < max_page:
            # Nối URL tương đối với domain để có URL tuyệt đối
            base_url = response.url.split('?')[0]
            next_page_url = urljoin(base_url, next_page)
            print(f"--- Đang chuyển tới trang kế tiếp: {next_page_url} ---")
            yield scrapy.Request(next_page_url, callback=self.parse)
        else:
            print("--- Đã crawl đến trang cuối cùng. ---")

    # 4. Phương thức này được Scrapy gọi khi spider kết thúc
    def closed(self, reason):
        # Phương thức này được gọi khi spider kết thúc
        # 2. Bọc các thao tác DB bằng sync_to_async
        @sync_to_async
        def update_task_status():
            try:
                task = CrawlTask.objects.get(id=self.task_id)
                if self.item_scraped_count > 0:
                    task.status = 'DONE'
                    self.logger.info(f"Crawl thành công cho task {self.task_id}. Đã cập nhật status thành DONE.")
                else:
                    task.status = 'WARNING'
                    self.logger.warning(f"Không có dữ liệu nào được crawl cho task {self.task_id}. Đã cập nhật status thành WARNING.")
                task.save()
                print(f"--- ĐÃ KẾT THÚC CRAWL TASK {task.status} ---")
            except CrawlTask.DoesNotExist:
                self.logger.error(f"Task với id {self.task_id} không tồn tại khi kết thúc spider.")
            except Exception as e:
                self.logger.error(f"Lỗi khi cập nhật status task lúc kết thúc spider: {e}")

        # 3. Gọi hàm bất đồng bộ từ Twisted's reactor (môi trường chạy của Scrapy)
        # Scrapy sẽ tự động xử lý việc chạy coroutine này
        return update_task_status()
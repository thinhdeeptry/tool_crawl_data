import scrapy
from urllib.parse import urljoin
import re

class TrangVangSpider(scrapy.Spider):
    # Tên định danh duy nhất của spider
    name = 'trangvang'

    # Hàm khởi tạo, nhận các tham số từ command line
    def __init__(self, url_filter=None, task_id=None, *args, **kwargs):
        super(TrangVangSpider, self).__init__(*args, **kwargs)
        # Kiểm tra và thiết lập URL bắt đầu
        if url_filter:
            self.start_urls = [url_filter]
        else:
            self.start_urls = ["https://trangvangvietnam.com/categories/100-nha-hang"]
            print("WARNING: Không có URL filter, sử dụng URL mặc định")
        
        # Kiểm tra và thiết lập task_id
        if task_id:
            self.task_id = task_id
        else:
            self.task_id = 1  # Gán giá trị mặc định cho task_id
            print("WARNING: Không có task_id, sử dụng task_id mặc định = 1")
            
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

        # Tìm nút "Trang sau" và đi tiếp
        # Sử dụng XPath thay vì CSS selector không được hỗ trợ
        next_page = response.xpath('//div[@id="paging"]/a[text()="Tiếp"]/@href').get()
        
        if next_page:
            # Nối URL tương đối với domain để có URL tuyệt đối
            base_url = response.url.split('?')[0]
            next_page_url = urljoin(base_url, next_page)
            print(f"--- Đang chuyển tới trang kế tiếp: {next_page_url} ---")
            yield scrapy.Request(next_page_url, callback=self.parse)
        else:
            print("--- Đã crawl đến trang cuối cùng. ---")
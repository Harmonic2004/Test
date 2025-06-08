import asyncio
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig, CacheMode
import pandas as pd
from pathlib import Path

async def crawl_local_file(local_file_path):
    config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, capture_console_messages=True)
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=local_file_path, config=config)
        if result.success:
            soup = BeautifulSoup(result.html, "html.parser")
            # Tìm tất cả các hàng trong tbody
            rows = soup.select('tbody#render-table-owner tr')

            data = []
            for row in rows:
                cols = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cols) == 11:
                    data.append({
                        'Ngày': cols[0],
                        'Giá đóng cửa': cols[1],
                        'Giá điều chỉnh': cols[2],
                        'Thay đổi': cols[3],
                        'KL khớp lệnh': cols[4],
                        'GT khớp lệnh (tỷ)': cols[5],
                        'KL thỏa thuận': cols[6],
                        'GT thỏa thuận (tỷ)': cols[7],
                        'Giá mở cửa': cols[8],
                        'Giá cao nhất': cols[9],
                        'Giá thấp nhất': cols[10],
                    })

            # Tạo DataFrame
            df = pd.DataFrame(data) 

            # Hiển thị
            print(df.head())

if __name__ == "__main__":
    script_dir = Path(__file__).parent.parent
    html_file_path = script_dir / "data/page_2.html"
    local_file_path =  f"file://{html_file_path.resolve()}" 
    asyncio.run(crawl_local_file(local_file_path))
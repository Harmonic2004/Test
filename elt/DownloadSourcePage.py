from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
import pandas as pd
import time
from datetime import datetime
import os

class DownloadSourcePage:
    def __init__(self):
        self.driver = self.init_driver()
    
    def init_driver(self):
        options = ChromeOptions()
        # options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-web-security")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--disable-blink-features=AutomationControlled")

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def download_source_summary(self, stock_code, url_vietstock, output_dir):
        """Lấy dữ liệu giao dịch từ trang web và gắn mã CK & tên công ty vào mỗi hàng."""
        wait = WebDriverWait(self.driver, 3)
        # url = f'https://finance.vietstock.vn/{stock_code}/financials.htm?tab=BCTT'
        try:
            self.driver.get(url_vietstock)
            time.sleep(2)

            page = 1
            select_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="finance-content"]/div/div/div[2]/div/div[2]/div[1]/div[1]/select[1]')))
            # Tạo đối tượng Select
            select = Select(select_element)

            # Chọn option "4 Period" theo value
            select.select_by_value("4")
            time.sleep(2)

            dropdown = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="finance-content"]/div/div/div[2]/div/div[2]/div[1]/div[1]/select[2]')))

            select__ = Select(dropdown)
            # Chọn "Year" theo giá trị (value)
            select__.select_by_value("NAM")
            time.sleep(2)

            select_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="finance-content"]/div/div/div[2]/div/div[2]/div[1]/div[1]/select[3]')))

            # Tạo đối tượng Select
            select_ = Select(select_element)

            # Chọn "Million Dong" theo giá trị value (1000000)
            select_.select_by_value("1000000")
            time.sleep(2)

            output_path = os.path.join(output_dir, 'BCTC', stock_code)
            os.makedirs(output_path, exist_ok=True)

            while True:
                filename = filename = os.path.join(output_path, f"page_{page}.html")
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print(f"Đã lưu {filename}")
                page += 1
                try:
                    # Chờ nút có thể nhấn được (tối đa 5 giây mỗi lần)
                    btn = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="finance-content"]/div/div/div[2]/div/div[1]/div[2]')))
                    btn_class = btn.get_attribute("class")

                    if "disabled" in btn_class:
                        break
                    btn.click()
                    time.sleep(3)
                except:
                    # Nếu nút không còn bấm được, thoát vòng lặp
                    break
                
        finally:
            self.driver.quit()

        

    def download_source_trans_his(self, stock_code, url_cafef, output_dir):
        wait = WebDriverWait(self.driver, 3)
        try:
            self.driver.get(url_cafef)
            time.sleep(2)
            page = 1
            output_path = os.path.join(output_dir, 'LSGD', stock_code)
            os.makedirs(output_path, exist_ok=True)
            while True:
                print(f"Trang {page}: đang tải...")
                try:
                    # Chờ bảng và lấy HTML
                    table = wait.until(EC.presence_of_element_located((By.ID, "owner-contents-table")))

                    # Lưu HTML vào file
                    filename = os.path.join(output_path, f"page_{page}.html")
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(self.driver.page_source)
                    print(f"Đã lưu {filename}")

                    # Kiểm tra xem có dữ liệu < 2017 không
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    stop = False

                    for row in rows:
                        cols = row.find_elements(By.TAG_NAME, "td")
                        if cols:
                            date_str = cols[0].text.strip()
                            try:
                                date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                                if date_obj.year < 2025:
                                    print("Phát hiện dữ liệu cũ hơn 2017, dừng lại.")
                                    stop = True
                                    break
                            except:
                                continue

                    if stop:
                        break

                    # Chuyển sang trang tiếp theo
                    page += 1
                    page_xpath = f"//div[contains(@class, 'pagination-item')]/p[@title='{page}']"

                    try:
                        page_button = wait.until(EC.element_to_be_clickable((By.XPATH, page_xpath)))
                        self.driver.execute_script("arguments[0].click();", page_button)
                        wait.until(EC.staleness_of(page_button))  # Đợi trang mới tải
                    except Exception as e:
                        print(f"Lỗi khi chuyển sang trang {page}: {e}")
                        break

                except Exception as e:
                    print("Lỗi trong khi xử lý trang:", e)
                    break

        finally:
            self.driver.quit()

    def download_stock_data_sequentially(self, stock_code, url_cafef, url_vietstock, output_dir):
        """Download lịch sử giao dịch trước, rồi đến báo cáo tài chính cho cùng 1 mã cổ phiếu."""
        
        try:
            print(f"Download transaction history for {stock_code}...")
            self.download_source_trans_his(stock_code, url_cafef, output_dir)

            # Cần reset driver vì 2 hàm đều gọi self.driver.quit()
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

            print(f"Download financial summary for {stock_code}...")
            self.download_source_summary(stock_code, url_vietstock, output_dir)
        
        finally:
            self.driver.quit()

    
if __name__ == "__main__":
    bot = DownloadSourcePage()
    stock_code = 'acb'
    url_cafef = f'https://cafef.vn/du-lieu/lich-su-giao-dich-{stock_code}-1.chn#data'
    url_vietstock = f'https://finance.vietstock.vn/{stock_code}/financials.htm?tab=BCTT'

    bot.download_stock_data_sequentially(stock_code, url_cafef, url_vietstock, '/home/hadoop/PORTFOLIO INVESTMENT/data')

import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import logging
import sys

class StockChecker:
    def __init__(self, telegram_bot_token, telegram_chat_id):
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # UTF-8 encoding ile logging ayarları
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('stock_checker.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)  # stdout için handler
            ]
        )
        self.logger = logging.getLogger(__name__)

    def send_telegram_message(self, message):
        """Telegram üzerinden mesaj gönderir."""
        telegram_api_url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(telegram_api_url, json=payload)
            response.raise_for_status()
            self.logger.info("Telegram mesajı başarıyla gönderildi")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Telegram mesajı gönderilemedi: {str(e)}")

    def check_stock(self, product_url):
        """Ürünün stok durumunu kontrol eder."""
        try:
            response = requests.get(product_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Not: Bu seçiciler Zara'nın web sitesi yapısına göre güncellenmeli
            stock_element = soup.select_one('button[class*="add-to-cart"]')
            product_name = soup.select_one('h1[class*="product-name"]')
            
            if stock_element and not 'disabled' in stock_element.get('class', []):
                return True, product_name.text if product_name else "Ürün"
            return False, product_name.text if product_name else "Ürün"
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Stok kontrolü sırasında hata: {str(e)}")
            return False, "Hata"

    def monitor_stock(self, product_url, check_interval=300):
        """Belirtilen aralıklarla stok durumunu kontrol eder."""
        self.logger.info(f"Stok takibi başlatıldı: {product_url}")
        previous_status = False

        while True:
            try:
                in_stock, product_name = self.check_stock(product_url)
                
                if in_stock and not previous_status:
                    message = (
                        f"🎉 <b>{product_name}</b> stoka girdi!\n\n"
                        f"🔗 <a href='{product_url}'>Ürüne git</a>\n"
                        f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
                    )
                    self.send_telegram_message(message)
                    previous_status = True
                elif not in_stock:
                    previous_status = False

                time.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"Beklenmeyen hata: {str(e)}")
                time.sleep(check_interval)

def main():
    
    TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"
    TELEGRAM_CHAT_ID = "TELEGRAM_CHAT_ID"
    
    
    PRODUCT_URL = "PRODUCT_URL"
    
    checker = StockChecker(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    checker.monitor_stock(PRODUCT_URL)

if __name__ == "__main__":
    main()
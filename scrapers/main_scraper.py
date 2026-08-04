import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

DATA_PATH = 'data/tenders.json'

def load_existing_data():
    """讀取本地已存在的 JSON 資料"""
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_data(data):
    """將資料寫回 JSON 檔案"""
    os.makedirs('data', exist_ok=True)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def classify_category(title):
    """標題關鍵字自動分類"""
    if any(k in title for k in ['工程', '建造', '維修', '冷氣', '供電']):
        return '工程'
    elif any(k in title for k in ['清潔', '保安', '人力', '外判', '營運']):
        return '人力'
    elif any(k in title for k in ['運輸', '物流', '搬運', '車輛']):
        return '物流'
    elif any(k in title for k in ['系統', '軟件', 'IT', '電腦', '網絡']):
        return 'IT及科技'
    else:
        return '物料供應'

def fetch_tenders():
    existing_tenders = load_existing_data()
    # 建立字典方便比對去重 (以 tender_ref 為 Key)
    tender_map = {item['tender_ref']: item for item in existing_tenders}

    # -------------------------------------------------------------
    # 爬蟲邏輯範例 (以政府採購為例，可擴充多個來源)
    # -------------------------------------------------------------
    url = "https://www.fstb.gov.hk/tc/treasury/gov_procurement/tender-notices.htm"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.find_all('tr')
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    ref = cols[0].text.strip()
                    title = cols[1].text.strip()
                    org = cols[2].text.strip()
                    close_date = cols[3].text.strip()

                    if not ref:
                        continue

                    # 組裝資料
                    new_item = {
                        "tender_ref": ref,
                        "title": title,
                        "category": classify_category(title),
                        "org_type": "政府部門",
                        "organization_name": org,
                        "publish_date": datetime.today().strftime('%Y-%m-%d'),
                        "close_date": close_date,
                        "award_date": "",
                        "winner_name": "",
                        "award_amount": None,
                        "original_url": url,
                        "status": "ACTIVE"
                    }

                    # 更新或新增 (不存在才覆蓋，保留中標等已填寫歷史)
                    if ref not in tender_map:
                        tender_map[ref] = new_item
                    else:
                        # 僅更新動態欄位，保留手動補上的 winner_name/award_amount
                        tender_map[ref]['status'] = new_item['status']
                        tender_map[ref]['close_date'] = new_item['close_date']

    except Exception as e:
        print(f"Error fetching data: {e}")

    # 轉換回 List 並寫入 JSON
    updated_list = list(tender_map.values())
    save_data(updated_list)
    print(f"Successfully updated data! Total tenders: {len(updated_list)}")

if __name__ == "__main__":
    fetch_tenders()

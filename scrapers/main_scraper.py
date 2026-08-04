import json
import os
import re
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

GLD_URL = "https://pcms2.gld.gov.hk/iprod/#/sta00305?lang-setting=zh-HK"

async def scrape_gld():
    tenders = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        
        print(f"前往 GLD 招標頁面: {GLD_URL}")
        await page.goto(GLD_URL, wait_until="networkidle")
        
        try:
            await page.wait_for_selector("table", timeout=20000)
            await page.wait_for_timeout(3000)
            
            rows = await page.query_selector_all("table tbody tr")
            print(f"找到 {len(rows)} 筆招標項目")
            
            for index, row in enumerate(rows):
                cols = await row.query_selector_all("td")
                if len(cols) >= 4:
                    code = (await cols[0].inner_text()).strip()
                    title = (await cols[1].inner_text()).strip()
                    
                    # 取出欄位純文字進行日期與部門匹配
                    col2_text = (await cols[2].inner_text()).strip()
                    col3_text = (await cols[3].inner_text()).strip()
                    
                    # 自動辨識哪一個欄位包含日期 (YYYY-MM-DD 或 DD/MM/YYYY)
                    date_str = ""
                    dept_str = ""
                    
                    date_pattern = r'(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})'
                    match2 = re.search(date_pattern, col2_text)
                    match3 = re.search(date_pattern, col3_text)
                    
                    if match2:
                        date_str = match2.group(1)
                        dept_str = col3_text
                    elif match3:
                        date_str = match3.group(1)
                        dept_str = col2_text
                    else:
                        date_str = datetime.now().strftime("%Y-%m-%d")
                        dept_str = col2_text
                    
                    # 日期格式化為 YYYY-MM-DD
                    if "/" in date_str:
                        d, m, y = date_str.split("/")
                        formatted_date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
                    else:
                        formatted_date = date_str

                    if title:
                        tenders.append({
                            "id": f"GLD-{code}",
                            "title": title,
                            "dept": dept_str,
                            "start": formatted_date,
                            "date": formatted_date,
                            "code": code,
                            "source": "政府物流服務署",
                            "desc": f"招標編號：{code}\n發布部門：{dept_str}\n截標日期：{formatted_date}\n詳情請至香港政府物流服務署電子警報系統查詢。"
                        })
        except Exception as e:
            print(f"爬取過程發生錯誤: {e}")
            
        await browser.close()
    return tenders

def main():
    new_tenders = asyncio.run(scrape_gld())
    os.makedirs("data", exist_ok=True)
    json_path = "data/tenders.json"
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(new_tenders, f, ensure_ascii=False, indent=2)
        
    print(f"成功儲存 {len(new_tenders)} 筆招標項目至 {json_path}")

if __name__ == "__main__":
    main()

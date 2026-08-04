import json
import os
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

GLD_URL = "https://pcms2.gld.gov.hk/iprod/#/sta00305?lang-setting=zh-HK"

async def scrape_gld():
    tenders = []
    async with async_playwright() as p:
        # 啟動無頭瀏覽器
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        
        print(f"前往 GLD 招標頁面: {GLD_URL}")
        await page.goto(GLD_URL, wait_until="networkidle")
        
        try:
            # 等待表格載入
            await page.wait_for_selector("table", timeout=15000)
            await page.wait_for_timeout(3000) # 給予 DOM 渲染時間
            
            rows = await page.query_selector_all("table tbody tr")
            print(f"找到 {len(rows)} 列資料")
            
            for row in rows:
                cols = await row.query_selector_all("td")
                if len(cols) >= 4:
                    code = (await cols[0].inner_text()).strip()
                    title = (await cols[1].inner_text()).strip()
                    dept = (await cols[2].inner_text()).strip()
                    deadline_str = (await cols[3].inner_text()).strip()
                    
                    if title and deadline_str:
                        # 格式化日期為 YYYY-MM-DD
                        clean_date = deadline_str.split(" ")[0]
                        if "/" in clean_date:
                            d, m, y = clean_date.split("/")
                            formatted_date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
                        else:
                            formatted_date = clean_date
                            
                        tenders.append({
                            "id": f"GLD-{code}",
                            "title": f"[{dept}] {title}",
                            "start": formatted_date, # FullCalendar 使用 start 欄位
                            "date": formatted_date,
                            "code": code,
                            "source": "政府物流服務署",
                            "url": GLD_URL
                        })
        except Exception as e:
            print(f"爬取 GLD 發生錯誤: {e}")
            
        await browser.close()
    return tenders

def main():
    # 執行非同步爬蟲
    new_tenders = asyncio.run(scrape_gld())
    
    # 確保 data 資料夾存在
    os.makedirs("data", exist_ok=True)
    json_path = "data/tenders.json"
    
    print(f"共抓取到 {len(new_tenders)} 筆招標資料。")
    
    # 寫入 data/tenders.json
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(new_tenders, f, ensure_ascii=False, indent=2)
        
    print(f"已成功更新 {json_path}")

if __name__ == "__main__":
    main()

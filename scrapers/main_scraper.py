import json
import os
import re
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

GLD_URL = "https://pcms2.gld.gov.hk/iprod/#/sta00305?lang-setting=zh-HK"

def parse_chinese_date(date_str):
    """ 將 '2026年8月6日' 轉為 '2026-08-06' """
    try:
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
        if match:
            y, m, d = match.groups()
            return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
        
        # 備用：處理 YYYY-MM-DD 或 DD/MM/YYYY
        match_std = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', date_str)
        if match_std:
            y, m, d = match_std.groups()
            return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
    except Exception as e:
        print(f"日期解析失敗: {date_str} -> {e}")
    return datetime.now().strftime("%Y-%m-%d")

async def scrape_gld():
    tenders = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 900})
        
        print(f"前往 GLD 招標頁面: {GLD_URL}")
        await page.goto(GLD_URL, wait_until="networkidle")
        
        try:
            await page.wait_for_selector("table", timeout=20000)
            await page.wait_for_timeout(3000)
            
            rows = await page.query_selector_all("table tbody tr")
            print(f"找到 {len(rows)} 筆招標項目")
            
            for row in rows:
                cols = await row.query_selector_all("td")
                # 根據 GLD 實際表格，至少要有 7 欄
                if len(cols) >= 7:
                    code = (await cols[0].inner_text()).strip()
                    title = (await cols[1].inner_text()).strip()
                    dept = (await cols[2].inner_text()).strip()
                    raw_date = (await cols[6].inner_text()).strip() # 第 7 欄為截標日期
                    
                    formatted_date = parse_chinese_date(raw_date)

                    if title:
                        tenders.append({
                            "id": f"GLD-{code}",
                            "title": title,
                            "dept": dept,
                            "start": formatted_date,
                            "date": formatted_date,
                            "code": code,
                            "source": "政府物流服務署",
                            "desc": f"招標編號：{code}\n發布部門：{dept}\n截標日期：{formatted_date} ({raw_date})\n來源：GLD 電子警報系統"
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
        
    print(f"成功更新 {len(new_tenders)} 筆招標項目至 {json_path}")

if __name__ == "__main__":
    main()

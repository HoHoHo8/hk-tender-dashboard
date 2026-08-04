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
        
        match_std = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', date_str)
        if match_std:
            y, m, d = match_std.groups()
            return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
    except Exception as e:
        pass
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

            # 💡 技巧 1：嘗試點擊左下角「100」切換為每頁顯示 100 筆
            try:
                page_100_btn = await page.query_selector("xpath=//a[text()='100'] | //span[text()='100']")
                if page_100_btn:
                    await page_100_btn.click()
                    print("已點擊切換為每頁 100 筆")
                    await page.wait_for_timeout(3000)
            except Exception as e:
                print(f"無法切換每頁筆數，繼續預設翻頁: {e}")

            page_num = 1
            while True:
                print(f"正在爬取第 {page_num} 頁...")
                rows = await page.query_selector_all("table tbody tr")
                
                for row in rows:
                    cols = await row.query_selector_all("td")
                    if len(cols) >= 7:
                        code = (await cols[0].inner_text()).strip()
                        title = (await cols[1].inner_text()).strip()
                        dept = (await cols[2].inner_text()).strip()
                        raw_date = (await cols[6].inner_text()).strip()
                        
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

                # 💡 技巧 2：尋找並點擊「下一頁」按鈕
                next_btn = await page.query_selector("xpath=//a[text()='下一頁'] | //span[text()='下一頁']")
                
                # 檢查「下一頁」是否能點擊（避免無效迴圈）
                if next_btn:
                    is_disabled = await next_btn.get_attribute("disabled") or await next_btn.get_attribute("class")
                    if is_disabled and ("disabled" in is_disabled or "inactive" in is_disabled):
                        print("已抵達最後一頁。")
                        break
                    
                    await next_btn.click()
                    page_num += 1
                    await page.wait_for_timeout(3000)
                else:
                    print("未找到下一頁按鈕，爬取結束。")
                    break

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
        
    print(f"🎉 成功爬取全頁面，共儲存 {len(new_tenders)} 筆招標項目至 {json_path}")

if __name__ == "__main__":
    main()

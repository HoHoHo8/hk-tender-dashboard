import json
import random
from datetime import datetime, timedelta

# 招標分類
CATEGORIES = [
    {"id": "construction", "name": "建築及工程", "color": "#3b82f6"},
    {"id": "cleaning", "name": "清潔及保安", "color": "#10b981"},
    {"id": "it", "name": "資訊科技及系統", "color": "#8b5cf6"},
    {"id": "supply", "name": "物料及設備採購", "color": "#f59e0b"},
    {"id": "consulting", "name": "專業諮詢服務", "color": "#ec4899"}
]

# 招標名稱範本
TEMPLATES = {
    "construction": [
        "香港科技園區新大樓建造工程", "離島區文娛中心翻新及加固工程", "啟德發展區道路改善工程",
        "公屋大廈電梯系統更換工程", "政府大樓空調系統更新項目", "新界西醫院聯網擴建工程"
    ],
    "cleaning": [
        "2026/27 年度校園清潔及保安服務", "市政大樓及街市清潔服務合約", "政府合署物業管理與保安服務",
        "公眾公園環境衛生及清潔合約", "醫療機構專用清潔及消毒服務"
    ],
    "it": [
        "智慧城市數據中心雲端架構升級", "政府部門網絡安全防禦系統維護", "公共服務行動應用程式 (App) 開發",
        "全港智慧交通燈系統軟體升級", "醫院管理局電子病歷系統擴充"
    ],
    "supply": [
        "2026年度辦公室設備及傢俬採購", "消防處救護車醫療器材採購合約", "環境保護署水質監測儀器採購",
        "教育局學校電子學習平板電腦採購", "警務處專用車輛零件供應合約"
    ],
    "consulting": [
        "可持續發展與碳中和策略可行性研究", "九龍東智慧交通規劃顧問服務", "企業數位轉型及資安審計諮詢",
        "大型基建項目環境影響評估顧問", "公共機構人力資源管理系統諮詢"
    ]
}

DEPARTMENTS = ["建築署", "機電工程署", "路政署", "環境保護署", "教育局", "醫院管理局", "香港科技園", "房屋署"]

def generate_full_year_tenders():
    tenders = []
    tender_id = 1001
    
    # 產生 2026 年 1 月至 12 月的招標數據
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 12, 31)
    
    current = start_date
    while current <= end_date:
        # 每個月隨機產生 8 ~ 15 個招標項目
        tenders_this_month = random.randint(8, 15)
        for _ in range(tenders_this_month):
            day = random.randint(1, 28)
            t_date = datetime(current.year, current.month, day)
            
            cat = random.choice(CATEGORIES)
            title = random.choice(TEMPLATES[cat["id"]])
            dept = random.choice(DEPARTMENTS)
            budget = f"HK$ {random.randint(5, 500) * 10}萬"
            
            tenders.append({
                "id": f"TEND-{tender_id}",
                "title": title,
                "category": cat["id"],
                "category_name": cat["name"],
                "color": cat["color"],
                "date": t_date.strftime("%Y-%m-%d"),
                "year": t_date.year,
                "month": t_date.month,
                "day": t_date.day,
                "department": dept,
                "budget": budget,
                "status": random.choice(["招標中", "截標中", "已開標"])
            })
            tender_id += 1
            
        # 下一個月
        if current.month == 12:
            break
        current = datetime(current.year, current.month + 1, 1)
        
    output = {
        "categories": CATEGORIES,
        "total_count": len(tenders),
        "tenders": tenders
    }
    
    with open("tenders.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        
    print(f"✅ 已成功生成全年 12 個月份共 {len(tenders)} 筆招標數據 (tenders.json)")

generate_full_year_tenders()

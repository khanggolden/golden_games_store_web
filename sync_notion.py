import os
import requests
import pandas as pd

NOTION_TOKEN = os.environ.get("NOTION_API_TOKEN")
OFFLINE_DB_ID = os.environ.get("NOTION_OFFLINE_DB_ID")
ONLINE_DB_ID = os.environ.get("NOTION_ONLINE_DB_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def extract_property_value(prop):
    """Tự động nhận diện và lấy dữ liệu từ các loại cột trên Notion"""
    p_type = prop.get("type")
    if p_type == "title":
        title_list = prop.get("title", [])
        return title_list[0]["plain_text"] if title_list else ""
    elif p_type == "rich_text":
        text_list = prop.get("rich_text", [])
        return text_list[0]["plain_text"] if text_list else ""
    elif p_type == "number":
        return prop.get("number", "")
    elif p_type == "select":
        select_obj = prop.get("select")
        return select_obj.get("name", "") if select_obj else ""
    elif p_type == "multi_select":
        return ", ".join([item["name"] for item in prop.get("multi_select", [])])
    elif p_type == "url":
        return prop.get("url", "")
    elif p_type == "status":
        status_obj = prop.get("status")
        return status_obj.get("name", "") if status_obj else ""
    return ""

def fetch_notion_db(db_id):
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    has_more = True
    start_cursor = None
    results = []

    while has_more:
        payload = {}
        if start_cursor:
            payload["start_cursor"] = start_cursor

        res = requests.post(url, headers=headers, json=payload)
        if res.status_code != 200:
            print(f"Lỗi kết nối Notion API ({res.status_code}): {res.text}")
            break
        
        data = res.json()
        results.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor", None)

    rows = []
    for page in results:
        props = page.get("properties", {})
        row_data = {}
        for col_name, prop_data in props.items():
            row_data[col_name] = extract_property_value(prop_data)
        rows.append(row_data)

    return pd.DataFrame(rows)

if __name__ == "__main__":
    if OFFLINE_DB_ID:
        print("Đang tải dữ liệu Game Offline...")
        df_offline = fetch_notion_db(OFFLINE_DB_ID)
        df_offline.to_csv("GAME OFFLINE.csv", index=False, encoding="utf-8-sig")
        print(f"✅ Đã tạo file 'GAME OFFLINE.csv' với {len(df_offline)} dòng.")

    if ONLINE_DB_ID:
        print("Đang tải dữ liệu Game Online...")
        df_online = fetch_notion_db(ONLINE_DB_ID)
        df_online.to_csv("GAME ONLINE.csv", index=False, encoding="utf-8-sig")
        print(f"✅ Đã tạo file 'GAME ONLINE.csv' với {len(df_online)} dòng.")

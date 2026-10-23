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
            print(f"Lỗi khi gọi API: {res.text}")
            break
        
        data = res.json()
        results.extend(data.get("results", []))
        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor", None)

    rows = []
    for page in results:
        props = page.get("properties", {})
        
        # Lấy tên game (Title)
        title_list = props.get("Title", {}).get("title", [])
        title = title_list[0]["text"]["content"] if title_list else ""
        
        # Lấy dung lượng
        size = props.get("Dung Lượng", {}).get("number", 0)
        
        # Lấy status
        status_obj = props.get("Status", {}).get("select", {})
        status = status_obj.get("name", "") if status_obj else ""
        
        # Lấy thời gian cập nhật
        updated_list = props.get("Cập Nhật Lần Cuối", {}).get("rich_text", [])
        updated = updated_list[0]["text"]["content"] if updated_list else ""

        # Lấy người tạo
        created_by_list = props.get("Được Tạo bởi", {}).get("rich_text", [])
        created_by = created_by_list[0]["text"]["content"] if created_by_list else ""

        rows.append({
            "Title": title,
            "Cập Nhật Lần Cuối": updated,
            "Dung Lượng": size,
            "Status": status,
            "Được Tạo bởi": created_by
        })

    return pd.DataFrame(rows)

if __name__ == "__main__":
    if OFFLINE_DB_ID:
        df_offline = fetch_notion_db(OFFLINE_DB_ID)
        df_offline.to_csv("GAME OFFLINE.csv", index=False, encoding="utf-8-sig")
        print(f"Đã cập nhật {len(df_offline)} game Offline thành công.")

    if ONLINE_DB_ID:
        df_online = fetch_notion_db(ONLINE_DB_ID)
        df_online.to_csv("GAME ONLINE.csv", index=False, encoding="utf-8-sig")
        print(f"Đã cập nhật {len(df_online)} game Online thành công.")
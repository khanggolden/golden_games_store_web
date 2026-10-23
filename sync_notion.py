import os
import csv
from notion_client import Client

# Lấy token trực tiếp từ GitHub Actions Secrets (đã cài ở Settings)
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
notion = Client(auth=NOTION_TOKEN)

DATABASE_OFFLINE_ID = "1c282f39-3481-8194-a23d-000b0e4c89b4"
DATABASE_ONLINE_ID  = "1c282f39-3481-81c7-9acc-000bea275dd5"

def fetch_and_write_csv(database_id, filename):
    print(f"Đang tải dữ liệu từ Database ID: {database_id}...")
    results = []
    has_more = True
    start_cursor = None

    while has_more:
        kwargs = {"database_id": database_id}
        if start_cursor:
            kwargs["start_cursor"] = start_cursor
        
        response = notion.databases.query(**kwargs)
        results.extend(response.get("results", []))
        has_more = response.get("has_more", False)
        start_cursor = response.get("next_cursor")

    if not results:
        print(f"Cảnh báo: Không tìm thấy dòng nào trong {filename}!")
        return

    # Lấy tiêu đề các cột
    first_page = results[0]["properties"]
    headers = list(first_page.keys())

    # Đưa cột Tên/Title lên đầu nếu có
    title_headers = [h for h, v in first_page.items() if v["type"] == "title"]
    if title_headers:
        main_title = title_headers[0]
        headers.remove(main_title)
        headers.insert(0, main_title)

    rows = []
    for page in results:
        props = page["properties"]
        row = {}
        for header in headers:
            prop = props.get(header, {})
            p_type = prop.get("type")
            val = ""

            if p_type == "title":
                texts = prop.get("title", [])
                val = "".join([t.get("plain_text", "") for t in texts])
            elif p_type == "rich_text":
                texts = prop.get("rich_text", [])
                val = "".join([t.get("plain_text", "") for t in texts])
            elif p_type == "select":
                sel = prop.get("select")
                val = sel.get("name", "") if sel else ""
            elif p_type == "multi_select":
                sels = prop.get("multi_select", [])
                val = ", ".join([s.get("name", "") for s in sels])
            elif p_type == "number":
                val = prop.get("number", "")
            elif p_type == "url":
                val = prop.get("url", "")
            elif p_type == "files":
                files = prop.get("files", [])
                urls = []
                for f in files:
                    if f.get("type") == "file":
                        urls.append(f.get("file", {}).get("url", ""))
                    elif f.get("type") == "external":
                        urls.append(f.get("external", {}).get("url", ""))
                val = ", ".join(urls)

            row[header] = val
        rows.append(row)

    # Ghi ra file CSV
    with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Thành công! Đã ghi {len(rows)} dòng vào {filename}.")

if __name__ == "__main__":
    fetch_and_write_csv(DATABASE_OFFLINE_ID, "GAME OFFLINE.csv")
    fetch_and_write_csv(DATABASE_ONLINE_ID, "GAME ONLINE.csv")

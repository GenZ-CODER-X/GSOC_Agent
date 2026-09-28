import requests
import json
from pathlib import Path
# from db.database import SessionLocal
from models import Organisation_entry

CACHE_FILE = Path("data/gsoc_organizations.json")

API_URL = "https://api.gsocorganizations.dev/organizations.json"


def get_org_details_gsoc_page(org_list: list[str]) -> dict:
    if CACHE_FILE.exists():
        with CACHE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        response = requests.get(API_URL, timeout=20)
        response.raise_for_status()

        data = response.json()

        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

        with CACHE_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    result = {}
    remaining = set(org_list)

    for org in data:
        org_name = org["name"]

        if org_name in remaining:
            result[org_name] = org
            remaining.remove(org_name)

            # All requested organizations found
            if not remaining:
                break

    return result
# db=SessionLocal()

# try:
#     organisations=db.query(Organisation_entry).all()
#     for db_org in organisations:
#         org_name=db_org.org_name
#         gsoc_org=get_gsoc_org_page(org_name)
#         if gsoc_org:
#             print(f"FOUND:{org_name}")
#             print(gsoc_org)
#         else:
#             print(f"NOT FOUND: {org_name}")
# finally:
#     db.close
if __name__ == "__main__":
    list_org=["Eclipse Foundation"]
    org = get_org_details_gsoc_page(list_org)
    print(org)
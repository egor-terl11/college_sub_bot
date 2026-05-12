import aiohttp
from bs4 import BeautifulSoup
import hashlib
import json
import os

DAY_IDS = {
    "monday": 169,
    "tuesday": 170,
    "wednesday": 171,
    "thursday": 172,
    "friday": 173,
}

BASE_URL = "https://bspc.bstu.by/ru/uchashchimsya/zamena-zanyatij"
HASH_FILE = "last_schedule_hash.json"

async def fetch_page(session, day_id):
    url = f"{BASE_URL}/{day_id}-zamena"
    async with session.get(url) as response:
        if response.status == 200:
            return await response.text()
        return None

def parse_replacements(html):
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")
    if not table:
        table = soup.find("div", class_="table-responsive")
        if table:
            table = table.find("table")
    if not table:
        return []

    rows = table.find_all("tr")
    if len(rows) < 2:
        return []

    replacements = []
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        group = cols[0].get_text(strip=True)
        pair_number = cols[1].get_text(strip=True)
        replaced_lesson = cols[2].get_text(strip=True)
        new_lesson = cols[3].get_text(strip=True)
        teacher = cols[4].get_text(strip=True)
        room = cols[5].get_text(strip=True)

        replacements.append({
            "group": group,
            "pair": pair_number,
            "replaced": replaced_lesson,
            "new": new_lesson,
            "teacher": teacher,
            "room": room
        })

    return replacements

def get_page_hash(html):
    return hashlib.md5(html.encode()).hexdigest()

def load_previous_hash():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            data = json.load(f)
            return data
    return {}

def save_hash(hash_dict):
    with open(HASH_FILE, "w") as f:
        json.dump(hash_dict, f)

async def check_all_days():
    previous_hashes = load_previous_hash()
    new_hashes = {}
    all_replacements = []

    async with aiohttp.ClientSession() as session:
        for day_name, day_id in DAY_IDS.items():
            html = await fetch_page(session, day_id)
            if not html:
                continue

            current_hash = get_page_hash(html)
            new_hashes[day_name] = current_hash

            if previous_hashes.get(day_name) != current_hash:
                day_replacements = parse_replacements(html)
                for r in day_replacements:
                    r["day"] = day_name
                all_replacements.extend(day_replacements)

    save_hash(new_hashes)
    return all_replacements
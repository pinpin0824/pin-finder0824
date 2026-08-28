"""
Pin Registry - データ取得・精査 統合スクリプト

このスクリプトは以下を1回の実行で全て行う:
1. eBay Browse APIから複数キーワードでデータ取得(ページネーション対応)
2. 重複統合(名寄せ)
3. パーク・Collection・キャラクター・LE数・Edition Type・Rarity・Color・品質ステータスの分類
4. 既知の公式シリーズデータ(all_official_series.json)との照合
5. data/pins_data.json として出力

GitHub Actions から1時間ごとに自動実行される想定。
eBay APIキーは環境変数(EBAY_APP_ID, EBAY_CERT_ID)から読み込む(コードに直書きしない)。
"""

import base64
import csv
import datetime
import io
import json
import os
import re
import time
from collections import Counter, defaultdict

import requests

# ============================================
# CONFIG
# ============================================
APP_ID = os.environ.get("EBAY_APP_ID", "")
CERT_ID = os.environ.get("EBAY_CERT_ID", "")

OAUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"
BROWSE_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"

SEARCH_QUERIES = [
    "Disney pin trading limited edition",
    "Walt Disney World pin LE",
    "Disneyland pin LE",
    "Disney Hidden Mickey pin",
    "Disney cast exclusive pin",
    "Disney pin trading cast lanyard",
    "Disney World annual passholder pin",
    "Disneyland 60th anniversary pin",
    "Disney D23 expo pin",
    "Disney park pin jumbo LE",
    "Disney Mickey Mouse pin LE",
    "Disney Princess pin LE",
    "Disney Star Wars pin LE",
    "Disney Marvel pin LE",
    "Disney Pixar pin LE",
    "Disney Villains pin LE",
    "Disney Halloween pin LE",
    "Disney Christmas pin LE",
    "Disney holiday pin limited",
    "Disney park anniversary pin",
    "Disney World 50th anniversary pin",
    "Disney Store exclusive pin",
    "Disney artist series pin",
    "Disney chaser pin",
    "Disney mystery pin set",
    "D23 Expo 2026 pin",
    "Hidden Disney 2026 pin",
    # データ量拡充のために追加(季節もの・シリーズもの・作品別)
    "Disney Loungefly pin LE",
    "Disney Epcot Food Wine Festival pin",
    "Disney Flower Garden Festival pin",
    "Disney Frozen pin LE",
    "Disney Lion King pin LE",
    "Disney Lilo Stitch pin LE",
    "Disney Nightmare Before Christmas pin LE",
    "Disney Alice in Wonderland pin LE",
    "Disney Winnie the Pooh pin LE",
    "Disney Haunted Mansion pin LE",
    "Disney Zootopia pin LE",
    "Disney Encanto pin LE",
    "Disney Moana pin LE",
    "Disney park attraction pin LE",
    "Disney Tokyo DisneySea pin",
    "Disney Shanghai Disneyland pin",
    "Disney Hong Kong Disneyland pin",
    "Disney Paris pin trading",
    "Disney cruise line pin LE",
    "Disney World 2026 pin new",
    "Disneyland 2026 pin new",
]

MAX_PER_QUERY = 2000
CATEGORY_MAX_ITEMS = 10000
PAGE_SIZE = 200
REQUEST_DELAY = 1.0

# 複数のeBayマーケットプレイスを対象にする(米国以外の出品も拾う)
MARKETPLACES = ["EBAY_US", "EBAY_GB", "EBAY_AU", "EBAY_DE", "EBAY_CA"]

TAXONOMY_URL = "https://api.ebay.com/commerce/taxonomy/v1/category_tree/0/get_category_suggestions"

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OFFICIAL_SERIES_FILE = os.path.join(DATA_DIR, "all_official_series.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "pins_data.json")
TOP_CHARACTERS_FILE = os.path.join(DATA_DIR, "top_characters.json")
ARCHIVE_FILE = os.path.join(DATA_DIR, "archive_data.json")


# ============================================
# STEP 1: eBay からのデータ取得
# ============================================
def get_access_token():
    if not APP_ID or not CERT_ID:
        raise RuntimeError("EBAY_APP_ID / EBAY_CERT_ID が環境変数に設定されていません")
    credentials = f"{APP_ID}:{CERT_ID}"
    encoded = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded}",
    }
    data = {"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"}
    resp = requests.post(OAUTH_URL, headers=headers, data=data, timeout=30)
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_disney_pins_category_id(token):
    """
    eBay Taxonomy APIで「ディズニーピン」カテゴリの正確なIDを取得する。
    取得できない場合はNoneを返し、呼び出し側はキーワード検索のみにフォールバックする。
    """
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": "disney pin trading"}
    try:
        resp = requests.get(TAXONOMY_URL, headers=headers, params=params, timeout=30)
        if resp.status_code != 200:
            print(f"  [WARN] Taxonomy API status={resp.status_code}")
            return None
        data = resp.json()
        suggestions = data.get("categorySuggestions", [])
        for s in suggestions:
            category = s.get("category", {})
            name = category.get("categoryName", "")
            cid = category.get("categoryId", "")
            # 「Pins, Patches & Buttons」に一致するものを最優先で採用する
            if "pin" in name.lower() and cid:
                print(f"  [OK] カテゴリ特定: '{name}' (ID: {cid})")
                return cid
        # ピン専用カテゴリが見つからなければ、最初の候補を使う
        if suggestions:
            category = suggestions[0].get("category", {})
            cid = category.get("categoryId", "")
            name = category.get("categoryName", "")
            print(f"  [OK] カテゴリ候補(先頭)を採用: '{name}' (ID: {cid})")
            return cid
    except requests.RequestException as e:
        print(f"  [WARN] Taxonomy API呼び出し失敗: {e}")
    return None


def search_by_category(token, category_id, marketplace, max_items=10000, page_size=200):
    """カテゴリID全体を対象に検索する(キーワードの表記ゆれに左右されない、網羅的な取得方法)"""
    headers = {"Authorization": f"Bearer {token}", "X-EBAY-C-MARKETPLACE-ID": marketplace}
    all_items = []
    offset = 0
    total_available = None

    while len(all_items) < max_items:
        remaining = max_items - len(all_items)
        limit = min(page_size, remaining)
        params = {"category_ids": category_id, "limit": limit, "offset": offset}

        try:
            resp = requests.get(BROWSE_URL, headers=headers, params=params, timeout=30)
        except requests.RequestException as e:
            print(f"    [WARN] リクエスト失敗: {e}")
            break

        if resp.status_code != 200:
            print(f"    [WARN] status={resp.status_code} offset={offset}")
            break

        data = resp.json()
        items = data.get("itemSummaries", [])
        total_available = data.get("total")

        if not items:
            break

        all_items.extend(items)
        offset += limit
        time.sleep(REQUEST_DELAY)

        if total_available is not None and offset >= total_available:
            break
        if offset >= 10000:
            break

    return all_items


def search_items_paginated(token, query, max_items=500, page_size=200, marketplace="EBAY_US"):
    headers = {"Authorization": f"Bearer {token}", "X-EBAY-C-MARKETPLACE-ID": marketplace}
    all_items = []
    offset = 0
    total_available = None

    while len(all_items) < max_items:
        remaining = max_items - len(all_items)
        limit = min(page_size, remaining)
        params = {"q": query, "limit": limit, "offset": offset}

        try:
            resp = requests.get(BROWSE_URL, headers=headers, params=params, timeout=30)
        except requests.RequestException as e:
            print(f"  [WARN] リクエスト失敗: {e}")
            break

        if resp.status_code != 200:
            print(f"  [WARN] status={resp.status_code} offset={offset}")
            break

        data = resp.json()
        items = data.get("itemSummaries", [])
        total_available = data.get("total")

        if not items:
            break

        all_items.extend(items)
        offset += limit
        time.sleep(REQUEST_DELAY)

        if total_available is not None and offset >= total_available:
            break
        if offset >= 10000:
            break

    return all_items


def extract_fields(item, query):
    return {
        "search_query": query,
        "title": item.get("title", ""),
        "price": item.get("price", {}).get("value", ""),
        "currency": item.get("price", {}).get("currency", ""),
        "condition": item.get("condition", ""),
        "image_url": item.get("image", {}).get("imageUrl", ""),
        "item_web_url": (item.get("itemWebUrl", "") or "").split("?")[0],
        "seller_username": item.get("seller", {}).get("username", ""),
        "item_id": item.get("itemId", ""),
    }


def fetch_all_ebay_data(full=True):
    """
    full=True  : 1日1回用。カテゴリ全体+複数国+多めのキーワード上限で、集められる最大量を取得する。
    full=False : 毎時用。軽量に、USのみ・既存キーワードだけで最新の変動を素早く反映する。
    """
    print(f"=== eBay データ取得開始 (mode={'FULL' if full else 'LIGHT'}) ===")
    token = get_access_token()
    print("[OK] トークン取得成功")

    seen_ids = set()
    rows = []

    marketplaces = MARKETPLACES if full else ["EBAY_US"]
    max_per_query = MAX_PER_QUERY if full else 500
    # 軽量モードは、拡充前からある基本キーワード(27個)だけを使い、API呼び出し回数を抑える。
    # フルモード(1日1回)だけ、拡充した全キーワードを使う
    queries = SEARCH_QUERIES if full else SEARCH_QUERIES[:27]

    # ① カテゴリ全体を対象にした網羅的な取得(最も効果が大きい方法。フルモードのみ)
    if full:
        category_id = get_disney_pins_category_id(token)
        if category_id:
            for marketplace in marketplaces:
                print(f"--- カテゴリ検索: category_id={category_id} marketplace={marketplace} ---")
                items = search_by_category(token, category_id, marketplace, CATEGORY_MAX_ITEMS, PAGE_SIZE)
                new_count = 0
                for item in items:
                    item_id = item.get("itemId", "")
                    if item_id and item_id not in seen_ids:
                        seen_ids.add(item_id)
                        rows.append(extract_fields(item, f"category:{category_id}"))
                        new_count += 1
                print(f"  -> 新規追加: {new_count}件")
        else:
            print("[WARN] カテゴリIDが取得できなかったため、カテゴリ検索はスキップします")

    # ② キーワード検索(カテゴリ検索を補完する、既存の網羅策)
    for marketplace in marketplaces:
        for query in queries:
            print(f"--- 検索: '{query}' marketplace={marketplace} ---")
            items = search_items_paginated(token, query, max_per_query, PAGE_SIZE, marketplace)
            new_count = 0
            for item in items:
                item_id = item.get("itemId", "")
                if item_id and item_id not in seen_ids:
                    seen_ids.add(item_id)
                    rows.append(extract_fields(item, query))
                    new_count += 1
            print(f"  -> 新規追加: {new_count}件")

    print(f"=== 合計取得件数(重複除去後): {len(rows)}件 ===")
    return rows


# ============================================
# STEP 2: 名寄せ(重複統合)
# ============================================
def normalize_title(title):
    t = title.lower()
    t = re.sub(r"[\U0001F000-\U0001FFFF\u2600-\u27BF]", "", t)
    t = t.replace("&", "and")
    t = re.sub(r"[^a-z0-9 ]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def infer_park(title):
    t = title.lower()
    if "tokyo" in t:
        return "Tokyo Disneyland"
    if "disneyland paris" in t or "dlp" in t:
        return "Disneyland Paris"
    if "hong kong" in t or "hkdl" in t:
        return "Hong Kong Disneyland"
    if "shanghai" in t:
        return "Shanghai Disneyland"
    if "d23" in t:
        return "D23 Expo"
    if ("walt disney world" in t or "wdw" in t or "magic kingdom" in t or "epcot" in t
            or "animal kingdom" in t or "hollywood studios" in t):
        return "Walt Disney World"
    if "disneyland" in t or "dlr" in t or "california adventure" in t or "dca" in t:
        return "Disneyland Resort"
    if ("disney store" in t or "shopdisney" in t or "company store" in t or "boxlunch" in t
            or ("loungefly" in t and "disney parks" not in t)):
        return "Disney Store / Online Exclusive"
    if "sdcc" in t or "comic con" in t:
        return "Convention Exclusive (SDCC等)"
    if "disney parks" in t:
        return "Disney Parks (Shared/Unspecified)"
    return "Other / Unknown"


def dedupe_and_group(rows):
    groups = defaultdict(list)
    for r in rows:
        key = normalize_title(r["title"])
        groups[key].append(r)

    output = []
    for key, items in groups.items():
        prices = []
        for it in items:
            try:
                prices.append(float(it["price"]))
            except (ValueError, KeyError):
                pass
        if not prices:
            continue

        representative = max(items, key=lambda x: len(x["title"]))
        title = representative["title"]

        output.append({
            "title": title,
            "count": len(items),
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_price": round(sum(prices) / len(prices), 2),
            "le_count": "",
            "characters": "",
            "series": "",
            "image_url": representative.get("image_url", ""),
            "park": infer_park(title),
            "url": items[0].get("item_web_url", ""),
        })

    return output


# ============================================
# STEP 3: 各種タグ付け(Collection / Characters / LE数 / Edition Type / Rarity / Color)
# ============================================
ALL_CHARACTERS = {
    "mickey": "Mickey Mouse", "minnie": "Minnie Mouse", "donald": "Donald Duck", "daisy": "Daisy Duck",
    "goofy": "Goofy", "pluto": "Pluto", "chip": "Chip", "dale": "Dale", "figaro": "Figaro",
    "duffy": "Duffy", "shelliemay": "ShellieMay", "gelatoni": "Gelatoni", "stellalou": "StellaLou",
    "cookieann": "CookieAnn", "linabell": "LinaBell", "olaf": "Olaf", "anna": "Anna", "elsa": "Elsa",
    "rapunzel": "Rapunzel", "belle": "Belle", "beast": "Beast", "aurora": "Aurora", "jasmine": "Jasmine",
    "aladdin": "Aladdin", "genie": "Genie", "ariel": "Ariel", "ursula": "Ursula", "flounder": "Flounder",
    "woody": "Woody", "buzz": "Buzz Lightyear", "jessie": "Jessie", "sulley": "Sulley", "sully": "Sulley",
    "mike wazowski": "Mike Wazowski", "baymax": "Baymax", "hiro": "Hiro Hamada", "stitch": "Stitch",
    "angel": "Angel", "scrump": "Scrump", "scar": "Scar", "hades": "Hades", "maleficent": "Maleficent",
    "cruella": "Cruella de Vil", "captain hook": "Captain Hook", "peter pan": "Peter Pan",
    "wendy": "Wendy", "tigger": "Tigger", "eeyore": "Eeyore", "piglet": "Piglet",
    "snow white": "Snow White", "evil queen": "Evil Queen", "gaston": "Gaston",
    "flynn rider": "Flynn Rider", "vanellope": "Vanellope", "judy hopps": "Judy Hopps",
    "nick wilde": "Nick Wilde", "groot": "Groot", "grogu": "Grogu", "darth vader": "Darth Vader",
    "bb-8": "BB-8", "bb8": "BB-8",
    "simba": "Simba", "rafiki": "Rafiki", "timon": "Timon", "pumbaa": "Pumbaa", "nala": "Nala",
    "mufasa": "Mufasa", "jack skellington": "Jack Skellington", "sally": "Sally",
    "oogie boogie": "Oogie Boogie", "sora": "Sora",
    "marie": "Marie", "duchess": "Duchess", "dumbo": "Dumbo", "hercules": "Hercules",
    "megara": "Megara", "pegasus": "Pegasus", "pinocchio": "Pinocchio", "jiminy cricket": "Jiminy Cricket",
    "bambi": "Bambi", "thumper": "Thumper", "robin hood": "Robin Hood", "little john": "Little John",
    "baloo": "Baloo", "mowgli": "Mowgli", "kaa": "Kaa",
    "quasimodo": "Quasimodo", "esmeralda": "Esmeralda",
    "yzma": "Yzma", "kuzco": "Kuzco", "kronk": "Kronk",
    "moana": "Moana", "maui": "Maui", "tiana": "Tiana", "naveen": "Naveen",
    "mulan": "Mulan", "mushu": "Mushu", "mirabel": "Mirabel",
    "luca": "Luca", "alberto": "Alberto", "remy": "Remy", "emile": "Emile",
    "wall-e": "WALL-E", "eve": "EVE", "nemo": "Nemo", "dory": "Dory", "merida": "Merida",
    "joy": "Joy", "sadness": "Sadness", "disgust": "Disgust",
    "miguel": "Miguel", "dante": "Dante",
    "figment": "Figment", "orange bird": "Orange Bird", "big al": "Big Al",
    "spider-man": "Spider-Man", "spiderman": "Spider-Man", "iron man": "Iron Man", "captain america": "Captain America",
    "thor": "Thor", "hulk": "Hulk", "black widow": "Black Widow", "loki": "Loki",
    "black panther": "Black Panther", "doctor strange": "Doctor Strange", "venom": "Venom",
    "rocket raccoon": "Rocket Raccoon", "star-lord": "Star-Lord",
    "yoda": "Yoda", "chewbacca": "Chewbacca", "boba fett": "Boba Fett", "r2-d2": "R2-D2", "r2d2": "R2-D2",
    "c-3po": "C-3PO", "stormtrooper": "Stormtrooper", "mandalorian": "The Mandalorian",
    "ahsoka": "Ahsoka", "kylo ren": "Kylo Ren", "finn": "Finn",
    "leia": "Princess Leia", "han solo": "Han Solo", "luke skywalker": "Luke Skywalker",
    "kermit": "Kermit the Frog", "miss piggy": "Miss Piggy", "fozzie": "Fozzie Bear", "fozzy": "Fozzie Bear",
    "gonzo": "Gonzo",
    "tinker bell": "Tinker Bell", "cinderella": "Cinderella", "fairy godmother": "Fairy Godmother",
    "gus": "Gus (Cinderella)", "jaq": "Jaq",
    "winnie the pooh": "Winnie the Pooh", "pooh": "Winnie the Pooh",
    "mad hatter": "Mad Hatter", "cheshire cat": "Cheshire Cat", "white rabbit": "White Rabbit", "alice": "Alice",
    "queen of hearts": "Queen of Hearts", "jafar": "Jafar", "iago": "Iago",
    "zootopia": "Zootopia", "chernabog": "Chernabog", "dr facilier": "Dr. Facilier",
    "pocahontas": "Pocahontas", "john smith": "John Smith", "meeko": "Meeko",
    "boo": "Boo", "randall": "Randall",
    "violet": "Violet Parr", "dash parr": "Dash Parr", "jack-jack": "Jack-Jack",
    "zurg": "Emperor Zurg",
    "tarzan": "Tarzan", "terk": "Terk", "jane porter": "Jane Porter",
    "gogo tomago": "GoGo Tomago", "wasabi": "Wasabi", "honey lemon": "Honey Lemon",
    "marlin": "Marlin", "crush": "Crush",
    "sven": "Sven", "kristoff": "Kristoff",
    "prince eric": "Prince Eric",
    "carl fredricksen": "Carl Fredricksen", "russell": "Russell (Up)",
    "rex": "Rex (Toy Story)", "hamm": "Hamm",
    "dewey": "Dewey", "huey": "Huey", "louie": "Louie",
}


def extract_characters(title):
    t = title.lower()
    found = []
    for key, display in ALL_CHARACTERS.items():
        pattern = r"\b" + re.escape(key) + r"\b"
        if re.search(pattern, t) and display not in found:
            found.append(display)
    # Rex(Toy Story)がStar Wars関連の誤検出になる場合は除外
    if "Rex (Toy Story)" in found and ("star wars" in t or "droid" in t or "captain rex" in t or "dj rex" in t):
        found.remove("Rex (Toy Story)")
    return "; ".join(found) if found else ""


def infer_collection(title, characters):
    t = (title + " " + (characters or "")).lower()
    checks = [
        (["star wars", "darth vader", "bb-8", "bb8", "grogu", "mandalorian", "yoda", "stormtrooper",
          "jedi", "r2-d2", "c-3po", "skywalker", "chewbacca", "boba fett", "ahsoka", "kylo ren",
          " rey ", "han solo"], "Star Wars"),
        (["marvel", "avengers", "spider-man", "spiderman", "iron man", "captain america", "thor",
          "hulk", "black widow", "groot", "guardians of the galaxy", "loki", "black panther",
          "venom", "doctor strange", "rocket raccoon", "star-lord"], "Marvel"),
        (["pixar", "toy story", "monsters inc", "monsters university", "woody", "buzz lightyear",
          "sulley", "sully", "mike wazowski", " up ", "coco ", "luca", "soul", "incredibles", "cars ",
          "finding nemo", "finding dory", "inside out", "ratatouille", "brave", "wall-e", "turning red",
          "onward", "elemental", "joy", "sadness", "remy", "emile", "merida", "boo", "randall",
          "hamm", "emperor zurg", "marlin", "crush", "carl fredricksen", "russell (up)"], "Pixar"),
        (["villains", "maleficent", "ursula", "scar", "hades", "cruella", "evil queen", "jafar",
          "gaston", "captain hook", "dr facilier", "chernabog", "iago"], "Villains"),
        (["winnie the pooh", " pooh ", "piglet", "tigger", "eeyore", "christopher robin"],
         "Winnie the Pooh & Friends"),
        (["alice in wonderland", "mad hatter", "cheshire cat", "white rabbit", " alice ",
          "queen of hearts"], "Alice in Wonderland"),
        (["muppets", "kermit", "fozzy", "fozzie", "miss piggy", "electric mayhem", "gonzo", " animal "],
         "Muppets"),
        (["peter pan", "tinker bell", "neverland", "never land", "wendy", "captain hook"],
         "Peter Pan / Neverland"),
        (["lilo", "stitch", "scrump", "angel "], "Lilo & Stitch"),
        (["lion king", "simba", "rafiki", "timon", "pumbaa", "nala", "mufasa"], "The Lion King"),
        (["nightmare before christmas", "jack skellington", "sally", "oogie boogie", "zero the dog"],
         "Nightmare Before Christmas"),
        (["kingdom hearts", "sora "], "Kingdom Hearts"),
        (["zootopia", "judy hopps", "nick wilde"], "Zootopia"),
        (["aristocats", "marie ", "duchess", "thomas o'malley"], "Aristocats"),
        (["dumbo"], "Dumbo"),
        (["hercules", "megara", "pegasus"], "Hercules"),
        (["big hero 6", "baymax", "hiro hamada", "gogo tomago", "wasabi", "honey lemon"], "Big Hero 6"),
        (["tarzan", "terk", "jane porter"], "Tarzan"),
        (["pinocchio", "atlantis", "emperor's new groove", "jungle book", "hunchback of notre dame",
          "bambi", "robin hood", "fox and the hound", "sword in the stone", "brother bear", "bolt",
          "chicken little", "great mouse detective", "yzma", "kuzco", "kronk", "quasimodo",
          "esmeralda", "baloo", "mowgli"], "Classic Disney Animation"),
        (["encanto", "wish ", "raya", "wreck-it ralph", "wreck it ralph", "mirabel", "vanellope"],
         "Modern Disney Animation"),
        (["princess", "cinderella", "snow white", "aurora", "belle", "jasmine", "ariel", "rapunzel",
          "moana", "tiana", "mulan", "elsa", "anna ", "frozen", "sleeping beauty", "aladdin", "genie",
          "beauty and the beast", "little mermaid", "tangled", "flynn rider", "naveen", "mushu",
          "fairy godmother", "pocahontas", "john smith", "meeko", "sven", "kristoff", "prince eric"],
         "Princesses"),
        (["haunted mansion", "small world", "country bear", "space mountain", "tower of terror",
          "jungle cruise", "pirates of the caribbean", "splash mountain", "big thunder", "matterhorn",
          "figment", "spaceship earth", "dumbo the flying elephant", "mad tea party", "main street usa",
          "expedition everest", "kilimanjaro"], "Attractions"),
        (["mickey", "minnie", "donald", "daisy", "goofy", "pluto", "chip", "dale", "figaro"],
         "Mickey & Friends"),
    ]
    for kws, label in checks:
        for kw in kws:
            if kw in t:
                return label
    return "Other"


# 実在が確認できる代表的なLE数(PinPics等の実例に基づく)。
# ここに含まれない、かつ25の倍数でもない中途半端な数字(LE6, LE24, LE26等)は、
# タイトル内の無関係な数字(発売年、セット数等)の誤検出である可能性が高いため採用しない
KNOWN_LE_VALUES = {12, 15, 20, 25, 30, 40, 50, 75, 100, 125, 150, 175, 200, 250, 300, 350, 400, 450, 500,
                    600, 650, 700, 750, 800, 850, 900, 1000, 1200, 1250, 1500, 1750, 1850, 2000, 2250, 2500,
                    2750, 3000, 3500, 4000, 4500, 5000, 6000, 7500, 8000, 10000, 15000, 20000, 25000}


def is_plausible_le(val):
    """実在するLE数のパターンに一致するか検証する(存在しない数値を誤って載せないため)"""
    if val in KNOWN_LE_VALUES:
        return True
    # 一般的に流通しているLE数のほとんどは25の倍数
    if val % 25 == 0:
        return True
    return False


def is_anniversary_context(title, end_pos):
    """
    数字の直後が「20th」「25th」のような序数(周年記念)や、
    「Anniversary」という単語であれば、それはLE数ではなく周年記念の数字なので除外する。
    (例: "LE 60th Anniversary" の"60"はLE数ではなく60周年のこと)
    """
    following = title[end_pos:end_pos + 15].lower().strip()
    if re.match(r"^(st|nd|rd|th)\b", following):
        return True
    if following.startswith("anniversary"):
        return True
    return False


def extract_le_number(title):
    t_lower = title.lower()
    # Fantasy Pin(非公式ファンメイド)は、公式の標準的なLE数とは違う
    # 独自の小ロット数を使うことが多いため、妥当性チェックを免除する
    fantasy_phrases = ["fantasy pin", "fantasy series pin", "custom fantasy", "unofficial fantasy",
                        "fantasy trader pin", "faux pin"]
    is_fantasy = any(ph in t_lower for ph in fantasy_phrases)

    # 'LE ### of ###' 形式(2つ目の数字が本当の限定数)
    m = re.search(r"\ble\s*\d+\s*of\s*([\d,]+)", title, re.IGNORECASE)
    if m and not is_anniversary_context(title, m.end()):
        num = m.group(1).replace(",", "")
        if num.isdigit():
            val = int(num)
            if 20 <= val <= 50000 and (is_fantasy or is_plausible_le(val)):
                return val
    # 'LE ##/###' 形式(スラッシュ区切り。例: "LE 37/150" → 37番目/全150個 → 総数150を採用)
    # これを見落とすと、個体番号(37)の方を誤って総数として扱ってしまうバグがあった
    m = re.search(r"\ble\s*\d+\s*/\s*([\d,]+)", title, re.IGNORECASE)
    if m and not is_anniversary_context(title, m.end()):
        num = m.group(1).replace(",", "")
        if num.isdigit():
            val = int(num)
            if 20 <= val <= 50000 and (is_fantasy or is_plausible_le(val)):
                return val
    # 'LE ##k' 形式(例: LE 5k → 5000。1000の倍数なので常に妥当とみなす)
    m = re.search(r"\ble\s*(\d+)\s*k\b", title, re.IGNORECASE)
    if m:
        return int(m.group(1)) * 1000
    # 'LE of ###' / 'LE ###' 形式
    # 重要: \b (単語境界)を付けないと、"Castle 2026"の"le"に反応して
    # 2026を誤ってLE数だと誤認識してしまう(実際に発生していたバグ)
    for p in [r"\ble\s*of\s*([\d,]+)", r"\ble\s*([\d,]+)"]:
        m = re.search(p, title, re.IGNORECASE)
        if m:
            end_pos = m.end()
            following = title[end_pos:end_pos + 3].lower()
            if following.startswith("-d") or following.startswith("d "):
                continue
            # 「LE 20th Anniversary」のような周年記念の数字を除外する。
            # 20や25等は「実在するLE数」にも該当するため、妥当性チェックだけでは
            # すり抜けてしまう。これを塞ぐための追加チェック
            if is_anniversary_context(title, end_pos):
                continue
            num = m.group(1).replace(",", "")
            if num.isdigit():
                val = int(num)
                # 実在しないパターンの数値(LE6, LE24, LE26等)は、
                # 誤検出とみなして採用しない(Unknownのままにする)
                if 20 <= val <= 50000 and (is_fantasy or is_plausible_le(val)):
                    return val
    m = re.search(r"\blimited edition\s*(?:of)?\s*([\d,]+)", title, re.IGNORECASE)
    if m and not is_anniversary_context(title, m.end()):
        num = m.group(1).replace(",", "")
        if num.isdigit():
            val = int(num)
            if 20 <= val <= 50000 and (is_fantasy or is_plausible_le(val)):
                return val
    return None


SERIES_TAGS = ["D23", "MOG", "WDI", "Anniversary", "Cast Exclusive", "Hidden Mickey", "Imagineering",
               "Annual Passholder", "Artist Series", "Mystery", "Chaser", "Jumbo", "Halloween",
               "Holiday", "Windows of Attraction", "Enchanted Doors", "Icons of the Galaxy",
               "Disneyland Is Your Land", "Play Along", "Eyeconic Park Views", "Eye-Conic Park Views",
               "Magical Theater", "Digitize Disney", "Premier Collection", "Game Changers",
               "Point of View", "Fantasmic", "A-2-Z", "Pin Trading Night", "Attraction Map",
               "Very Merry Christmas Party", "Not So Scary", "Superheroes Transformation",
               "Character Carousel", "Inkwells of Evil", "Wondrous Worlds", "Fairy Tale Moments",
               "Dining with Disney", "Reflections", "Pocket Parks", "Top Hat Treats",
               "Diamond Celebration", "50th Anniversary", "60th Anniversary"]


def compute_series_tags(title):
    t = title.lower()
    return "; ".join([tag for tag in SERIES_TAGS if tag.lower() in t])


def infer_edition_type(pin):
    t = pin["title"].lower()
    if pin.get("le_count"):
        return "Limited Edition (LE)"
    if re.search(r"\ble\b", t) or "limited edition" in t:
        # 「LE」という単語はあるが、具体的な限定数がタイトルに書かれていないケース。
        # 精度を偽らないため、確定LEとは別の表記にする。
        return "LE (Count Unknown)"
    if re.search(r"\blr\b", t) or "limited release" in t:
        return "Limited Release (LR)"
    if re.search(r"\boe\b", t) or "open edition" in t:
        return "Open Edition (OE)"
    if ("cast lanyard" in t or "hidden mickey" in t or "hidden disney" in t
            or "cast exclusive" in t or "cast member" in t):
        return "Cast Member Trading"
    if "mystery" in t or "chaser" in t or "blind box" in t or "blind bag" in t or "mystery pouch" in t:
        return "Mystery / Chaser"
    if ("annual passholder" in t or "passholder exclusive" in t or "ap passholder" in t
            or "passholder pin" in t or "passholder" in t):
        return "Annual Passholder Exclusive"
    return "Unknown"


def infer_rarity(pin):
    et = pin.get("edition_type", "")
    le = pin.get("le_count", "")
    if le:
        try:
            val = int(str(le).replace(",", ""))
            if val <= 300:
                return "Legendary"
            elif val <= 1000:
                return "Rare"
            elif val <= 3000:
                return "Uncommon"
            else:
                return "Common"
        except ValueError:
            pass
    if et == "Cast Member Trading":
        return "Rare"
    if et == "Mystery / Chaser":
        return "Rare"
    if et == "Annual Passholder Exclusive":
        return "Uncommon"
    if et == "Open Edition (OE)":
        return "Common"
    if et == "Limited Release (LR)":
        return "Uncommon"
    return "Unknown"


CHARACTER_COLOR = {
    "Mickey Mouse": "Red", "Minnie Mouse": "Pink", "Donald Duck": "Blue", "Daisy Duck": "Purple",
    "Goofy": "Orange", "Pluto": "Yellow", "Chip": "Brown", "Dale": "Brown", "Figaro": "Black",
    "Duffy": "Brown", "ShellieMay": "Pink", "Gelatoni": "Green", "StellaLou": "Purple",
    "CookieAnn": "Pink", "LinaBell": "Pink", "Olaf": "White", "Anna": "Green", "Elsa": "Blue",
    "Rapunzel": "Purple", "Belle": "Yellow", "Beast": "Blue", "Aurora": "Pink", "Jasmine": "Aqua",
    "Aladdin": "Purple", "Genie": "Blue", "Ariel": "Aqua", "Ursula": "Purple", "Flounder": "Orange",
    "Woody": "Brown", "Buzz Lightyear": "Green", "Jessie": "Red", "Sulley": "Blue",
    "Mike Wazowski": "Green", "Baymax": "White", "Stitch": "Blue", "Angel": "Pink",
    "Scrump": "Yellow", "Scar": "Orange", "Hades": "Blue", "Maleficent": "Purple",
    "Cruella de Vil": "Black", "Captain Hook": "Red", "Peter Pan": "Green", "Wendy": "Blue",
    "Tigger": "Orange", "Eeyore": "Blue", "Piglet": "Pink", "Snow White": "Red",
    "Evil Queen": "Purple", "Gaston": "Red", "Flynn Rider": "Brown", "Vanellope": "Green",
    "Judy Hopps": "Blue", "Nick Wilde": "Green", "Groot": "Brown", "Grogu": "Green",
    "Darth Vader": "Black", "BB-8": "Orange", "Simba": "Orange", "Timon": "Yellow",
    "Pumbaa": "Brown", "Nala": "Orange", "Mufasa": "Orange", "Jack Skellington": "Black",
    "Sally": "Purple", "Oogie Boogie": "Brown", "Marie": "White", "Duchess": "White",
    "Dumbo": "Blue", "Hercules": "Yellow", "Megara": "Purple", "Pegasus": "White",
    "Pinocchio": "Blue", "Jiminy Cricket": "Green", "Bambi": "Brown", "Robin Hood": "Green",
    "Little John": "Brown", "Baloo": "Brown", "Mowgli": "Red", "Kaa": "Green",
    "Quasimodo": "Brown", "Esmeralda": "Green", "Yzma": "Purple", "Kuzco": "Yellow",
    "Kronk": "Brown", "Moana": "Red", "Maui": "Brown", "Tiana": "Green", "Naveen": "Blue",
    "Mulan": "Red", "Mushu": "Red", "Mirabel": "Yellow", "Luca": "Blue", "Alberto": "Orange",
    "Remy": "Brown", "Emile": "Brown", "WALL-E": "Yellow", "EVE": "White", "Nemo": "Orange",
    "Dory": "Blue", "Merida": "Blue", "Joy": "Yellow", "Sadness": "Blue", "Disgust": "Green",
    "Miguel": "Red", "Dante": "Brown", "Figment": "Purple", "Orange Bird": "Orange",
    "Big Al": "Brown", "Spider-Man": "Red", "Iron Man": "Red", "Captain America": "Blue",
    "Thor": "Red", "Hulk": "Green", "Black Widow": "Black", "Loki": "Green",
    "Black Panther": "Black", "Doctor Strange": "Red", "Venom": "Black",
    "Rocket Raccoon": "Brown", "Star-Lord": "Red", "Yoda": "Green", "Chewbacca": "Brown",
    "Boba Fett": "Green", "R2-D2": "Blue", "C-3PO": "Yellow", "Stormtrooper": "White",
    "Ahsoka": "Orange", "Kylo Ren": "Black", "Finn": "Black", "Leia": "White",
    "Han Solo": "Brown", "Kermit the Frog": "Green", "Miss Piggy": "Pink",
    "Fozzie Bear": "Orange", "Gonzo": "Blue", "Tinker Bell": "Green", "Cinderella": "Blue",
    "Fairy Godmother": "Pink", "Gus (Cinderella)": "Brown", "Jaq": "Brown",
    "Winnie the Pooh": "Yellow", "Mad Hatter": "Orange", "Cheshire Cat": "Purple",
    "White Rabbit": "White", "Alice": "Blue", "Queen of Hearts": "Red", "Jafar": "Red",
    "Iago": "Red", "Chernabog": "Black", "Dr. Facilier": "Purple", "Pocahontas": "Brown",
    "John Smith": "Blue", "Meeko": "Brown", "Boo": "Pink", "Randall": "Purple",
    "Violet Parr": "Purple", "Dash Parr": "Red", "Jack-Jack": "Red", "Emperor Zurg": "Purple",
    "Tarzan": "Brown", "Terk": "Brown", "Jane Porter": "Blue", "GoGo Tomago": "Pink",
    "Wasabi": "Green", "Honey Lemon": "Pink", "Marlin": "Orange", "Crush": "Green",
    "Sven": "Brown", "Kristoff": "Blue", "Prince Eric": "Blue", "Carl Fredricksen": "Blue",
    "Russell (Up)": "Orange", "Rex (Toy Story)": "Green", "Hamm": "Pink",
}

COLLECTION_COLOR_FALLBACK = {
    "Princesses": "Pink", "Villains": "Purple", "Star Wars": "Black", "Marvel": "Red",
    "Pixar": "Blue", "Alice in Wonderland": "Blue", "Nightmare Before Christmas": "Black",
    "Winnie the Pooh & Friends": "Yellow", "Muppets": "Green", "The Lion King": "Orange",
    "Lilo & Stitch": "Blue", "Aristocats": "White", "Dumbo": "Blue", "Hercules": "Yellow",
    "Big Hero 6": "Red", "Zootopia": "Blue", "Kingdom Hearts": "Black", "Tarzan": "Brown",
}


def infer_color(pin):
    chars = pin.get("characters", "")
    if chars:
        first = chars.split(";")[0].strip()
        if first in CHARACTER_COLOR:
            return CHARACTER_COLOR[first]
    return COLLECTION_COLOR_FALLBACK.get(pin.get("collection"), "Multi")


# ============================================
# STEP 4: 品質ステータス判定(Fantasy Pin / Non-Tradeable / Not a Pin等)
# ============================================
NOT_A_PIN_KW = ["pin holder", "pin display", "pin case", "pin album", "pin stand"]
AMBIGUOUS_KW = ["pin board", "pin bag", "pin book", "trading bag"]
CONFIRMED_PIN_EDITIONS = ["Limited Edition (LE)", "LE (Count Unknown)", "Open Edition (OE)", "Limited Release (LR)",
                          "Cast Member Trading", "Annual Passholder Exclusive", "Mystery / Chaser"]
UNOFFICIAL_KW = ["fan made", "fan-made", "custom pin", "unofficial", "non-disney", "non disney",
                 "bootleg", "counterfeit", "homemade", "handmade", "artist made", "artist-made",
                 "inspired by"]
STRONG_SIGNALS = ["trading pin", "pin trading", "cast lanyard", "cast member", "cast exclusive",
                   "pin trading event", "grand opening", "annual passholder", "disney store",
                   "walt disney world", "disneyland resort", "shanghai disney", "tokyo disney",
                   "hong kong disney", "disneyland paris", "limited edition", "disney auctions",
                   "disney catalog", "artist collection", "artist series"]
PARK_ABBR = ["disneyland", "dlr", "wdw", "hkdl", "dca", "disney parks", "disney world", "epcot",
             "magic kingdom", "animal kingdom", "hollywood studios", "disneysea", "disney fairies",
             "disney vault", "disney auctions"]
FINAL_SIGNALS = ["supporting cast", "passholder", "dec twdcs", "dssh", "dcl pin",
                 "employee center", "pins lot of", "pin lot", "disney employee"]


def classify_quality(pin):
    title = pin["title"]
    t = title.lower()
    has_confirmed_edition = bool(pin.get("le_count")) or pin.get("edition_type") in CONFIRMED_PIN_EDITIONS

    for kw in NOT_A_PIN_KW:
        if re.search(r"\b" + re.escape(kw) + r"\b", t):
            return "Not a Pin"
    if not has_confirmed_edition:
        for kw in AMBIGUOUS_KW:
            if re.search(r"\b" + re.escape(kw) + r"\b", t):
                return "Not a Pin"

    # Fantasy Pin(非公式ファンメイド)の判定。
    # 「Fantasyland」「Fantasy Faire」等は実在の公式エリア名なので、
    # 単独の「fantasy」ではなく、明確にファンメイドを示すフレーズのみで判定する
    fantasy_phrases = ["fantasy pin", "fantasy series pin", "custom fantasy", "unofficial fantasy",
                        "fantasy trader pin", "faux pin"]
    if any(ph in t for ph in fantasy_phrases):
        return "Fantasy Pin"

    is_artist_series = "artist series" in t
    for kw in UNOFFICIAL_KW:
        if kw in t:
            if "artist" in kw and is_artist_series:
                continue
            return "Unofficial"

    if pin.get("park") in ("Disney Store / Online Exclusive", "Convention Exclusive (SDCC等)"):
        return "Non-Tradeable"
    if "not for trade" in t or "nfte" in t or "employee only" in t:
        return "Non-Tradeable"

    # Funko Pop!ピンは、Disney公式のピントレーディングプログラムとは別物で、
    # 裏側にディズニーの公式刻印がないため、キャストメンバーとトレードできない。
    # (\bを使い、"Mary Poppins"等を誤って検出しないよう注意している)
    funko_patterns = [r"\bfunko\b", r"\bpop!\s*pin\b", r"\bpop\s+pin\b", r"\bfunko\s*pop\b"]
    if any(re.search(p, t) for p in funko_patterns):
        return "Non-Tradeable"

    if pin.get("official"):
        return "Official"

    has_strong_signal = any(s in t for s in STRONG_SIGNALS)
    has_le = bool(pin.get("le_count"))
    has_park_abbr = any(p in t for p in PARK_ABBR)
    has_final_signal = any(s in t for s in FINAL_SIGNALS)

    # 「Likely Official」と断定するには、確信度の高いシグナルが2つ以上必要とする。
    # 1つだけの弱いシグナルでは「Unverified」に留める方が、
    # 誤ったデータを載せないという方針に合う
    signal_count = sum([
        bool(pin.get("series")),
        has_le,
        has_strong_signal,
        has_park_abbr,
        has_final_signal,
    ])

    # LE数が具体的な数値まで確認できている場合は、それ単体でも十分信頼できるシグナルとする
    if has_le and pin.get("le_count"):
        return "Likely Official"

    if signal_count >= 2:
        return "Likely Official"

    return "Unverified"


# ============================================
# STEP 5: 公式データ照合
# ============================================
STOPWORDS = {"disney", "pin", "pins", "hidden", "parks", "park", "walt", "world", "resort",
             "wave", "year", "series", "set", "the", "and", "of", "a", "d", "store"}


def get_key_words(series_name):
    wave_match = re.search(r"wave\s*[ab]\b", series_name, re.IGNORECASE)
    wave_token = wave_match.group(0).lower().replace(" ", "") if wave_match else None
    words = re.sub(r"[^a-zA-Z0-9 ]", " ", series_name.lower()).split()
    key_words = [w for w in words if len(w) > 3 and w not in STOPWORDS]
    return key_words, wave_token


def location_conflicts(title_lower, origin):
    origin_l = (origin or "").lower()
    has_dlr = "disneyland" in title_lower or " dlr" in title_lower
    has_wdw = "walt disney world" in title_lower or " wdw" in title_lower or "magic kingdom" in title_lower
    if "disneyland resort" in origin_l and "walt disney world" not in origin_l and has_wdw and not has_dlr:
        return True
    if "walt disney world" in origin_l and "disneyland" not in origin_l and has_dlr and not has_wdw:
        return True
    return False


def matches_official(title_lower, series):
    series_name = series["series_name"]
    key_words, wave_token = get_key_words(series_name)
    if not key_words:
        return False
    if wave_token:
        title_wave = re.sub(r"wave\s*([ab])\b", r"wave\1", title_lower)
        if wave_token not in title_wave:
            return False
    if not all(kw in title_lower for kw in key_words):
        return False
    if location_conflicts(title_lower, series.get("origin", "")):
        return False
    return True


def match_official_data(pins, official_list):
    matched = 0
    for p in pins:
        title_lower = p["title"].lower()
        p["official"] = None
        for series in official_list:
            if matches_official(title_lower, series):
                p["official"] = series
                matched += 1
                break
    print(f"[OK] 公式データ一致: {matched}件")


# ============================================
# MAIN
# ============================================
def merge_into_archive(pins):
    """
    毎回上書きする「今の在庫スナップショット」とは別に、
    一度見つけたピンは売れても消さず蓄積し続ける「データベース」を育てる。

    - 既存アーカイブを読み込む
    - 今回見つかったピンは、既存レコードがあれば情報を更新(価格帯・出品数など)
      なければ新規追加し、そのPin IDは以後ずっと固定される
    - 今回見つからなかった過去のピンは「is_currently_listed: false」に変わるだけで、
      レコード自体は削除しない
    """
    archive = {}
    next_id_num = 1

    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, encoding="utf-8") as f:
            existing = json.load(f)
        for p in existing:
            key = normalize_title(p["title"])
            archive[key] = p
            try:
                num = int(p["archive_id"].replace("ARC", ""))
                next_id_num = max(next_id_num, num + 1)
            except (KeyError, ValueError):
                pass

    today = datetime.date.today().isoformat()
    seen_keys = set()

    for p in pins:
        key = normalize_title(p["title"])
        seen_keys.add(key)
        if key in archive:
            # 既存レコードを更新(価格帯・出品数・ステータス等は最新化)
            existing_id = archive[key]["archive_id"]
            first_seen = archive[key].get("first_seen_date", today)
            p_copy = dict(p)
            p_copy["archive_id"] = existing_id
            p_copy["pin_id"] = existing_id
            p_copy["first_seen_date"] = first_seen
            p_copy["last_seen_date"] = today
            p_copy["is_currently_listed"] = True
            archive[key] = p_copy
        else:
            # 新規発見のピン。IDを新規採番して永久固定する
            p_copy = dict(p)
            p_copy["archive_id"] = f"ARC{next_id_num:06d}"
            p_copy["pin_id"] = p_copy["archive_id"]
            next_id_num += 1
            p_copy["first_seen_date"] = today
            p_copy["last_seen_date"] = today
            p_copy["is_currently_listed"] = True
            archive[key] = p_copy

    # 今回見つからなかった過去のピンは「現在は出品なし」に変更するだけで残す
    for key, p in archive.items():
        if key not in seen_keys:
            p["is_currently_listed"] = False

    archive_list = list(archive.values())
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(archive_list, f, ensure_ascii=False)

    currently_listed = sum(1 for p in archive_list if p.get("is_currently_listed"))
    print(f"[OK] {ARCHIVE_FILE} 更新完了: 累計{len(archive_list)}件(うち現在出品中: {currently_listed}件)")
    return archive_list


def main():
    import sys
    os.makedirs(DATA_DIR, exist_ok=True)

    # コマンドライン引数 --light が指定されたら軽量モード(毎時用)、
    # 指定なしならフルモード(1日1回、最大量を取得)
    full_mode = "--light" not in sys.argv
    rows = fetch_all_ebay_data(full=full_mode)
    pins = dedupe_and_group(rows)
    print(f"名寄せ後: {len(pins)}件")

    # 公式データ読み込み(このファイルはリポジトリに手動で蓄積した調査データ)
    official_list = []
    if os.path.exists(OFFICIAL_SERIES_FILE):
        with open(OFFICIAL_SERIES_FILE, encoding="utf-8") as f:
            official_list = json.load(f)

    # タグ付け一式
    for p in pins:
        p["characters"] = extract_characters(p["title"])
        p["collection"] = infer_collection(p["title"], p["characters"])
        le = extract_le_number(p["title"])
        if le:
            p["le_count"] = str(le)
        p["series"] = compute_series_tags(p["title"])

    match_official_data(pins, official_list)

    for p in pins:
        p["edition_type"] = infer_edition_type(p)
        p["rarity"] = infer_rarity(p)
        p["color_tag"] = infer_color(p)
        p["quality_status"] = classify_quality(p)

    # Pin ID 採番(タイトルのアルファベット順で確定)。これは「今の在庫スナップショット」専用のID。
    sorted_pins = sorted(pins, key=lambda p: p["title"].lower())
    for i, p in enumerate(sorted_pins, start=1):
        p["pin_id"] = f"DPI{i:06d}"
    id_map = {p["title"]: p["pin_id"] for p in sorted_pins}
    for p in pins:
        p["pin_id"] = id_map[p["title"]]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(pins, f, ensure_ascii=False)
    print(f"[OK] {OUTPUT_FILE} に {len(pins)}件を保存しました")

    # 累積データベース(データベースページ用)を育てる
    merge_into_archive(pins)

    # トップキャラクターリスト(A-Z順)
    counter = Counter()
    for p in pins:
        if p["characters"]:
            for c in p["characters"].split(";"):
                counter[c.strip()] += 1
    top_chars = sorted(counter.keys())
    with open(TOP_CHARACTERS_FILE, "w", encoding="utf-8") as f:
        json.dump(top_chars, f, ensure_ascii=False)
    print(f"[OK] {TOP_CHARACTERS_FILE} に {len(top_chars)}件のキャラクターを保存しました")

    # サマリー表示
    status_counter = Counter(p["quality_status"] for p in pins)
    print("\n=== Status内訳 ===")
    for status, cnt in status_counter.most_common():
        print(f"  {status}: {cnt}件")


if __name__ == "__main__":
    main()

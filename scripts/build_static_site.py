"""
Pin Registry サイトを生成する(軽量版)。

これまでの「静的HTML1ファイルに全カードを埋め込む」方式は、
ファイルサイズが肥大化しGitHubの25MB制限に抵触したため、
以下の方式に変更した:

1. データは docs/pins_data.json という別ファイルに保存
2. docs/index.html は「枠組み(HTML/CSS/JS)」だけの軽量ファイル
3. ページを開いたときに、JSが pins_data.json を読み込んでカードを描画する
"""

import json
import os
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
DOCS_DIR = os.path.join(SCRIPT_DIR, "..", "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

with open(os.path.join(DATA_DIR, "pins_data.json"), encoding="utf-8") as f:
    pins = json.load(f)

with open(os.path.join(DATA_DIR, "top_characters.json"), encoding="utf-8") as f:
    TOP_CHARACTERS = json.load(f)

pins.sort(key=lambda p: p["count"], reverse=True)

# 「report(報告)」ボタンで作成されるメールの宛先。
# ★ここを、あなたが報告を受け取りたいメールアドレスに書き換えてください★
REPORT_EMAIL = "your-email@example.com"

PARKS = ["All", "D23 Expo", "Walt Disney World", "Disneyland Resort", "Disney Parks (Shared/Unspecified)",
         "Disney Store / Online Exclusive", "Tokyo Disneyland", "Disneyland Paris",
         "Hong Kong Disneyland", "Shanghai Disneyland", "Convention Exclusive (SDCC等)", "Other / Unknown"]
COLLECTIONS = ["All", "Mickey & Friends", "Princesses", "Star Wars", "Marvel", "Pixar", "Villains",
               "Attractions", "Winnie the Pooh & Friends", "Alice in Wonderland", "Muppets",
               "Peter Pan / Neverland", "Lilo & Stitch", "The Lion King", "Nightmare Before Christmas",
               "Aristocats", "Dumbo", "Hercules", "Big Hero 6", "Zootopia", "Kingdom Hearts", "Tarzan",
               "Classic Disney Animation", "Modern Disney Animation", "Other"]
EDITION_TYPES = ["All", "Limited Edition (LE)", "LE (Count Unknown)", "Limited Release (LR)", "Open Edition (OE)",
                 "Mystery / Chaser", "Cast Member Trading", "Unknown"]
STATUS_LEVELS = ["All", "Official", "Likely Official", "Unverified", "Fantasy Pin",
                 "Non-Tradeable", "Unofficial", "Not a Pin"]
COLOR_TAGS = ["All", "Red", "Pink", "Blue", "Aqua", "Green", "Yellow", "Orange",
              "Purple", "Brown", "Black", "White", "Multi"]
SERIES_KEYWORDS = ["All", "D23", "MOG", "WDI", "Anniversary", "Cast Exclusive", "Hidden Mickey",
                   "Imagineering", "Annual Passholder", "Artist Series", "Mystery", "Chaser",
                   "Jumbo", "Halloween", "Holiday", "Windows of Attraction", "Enchanted Doors",
                   "Magical Theater", "Digitize Disney", "Premier Collection", "Game Changers",
                   "Play Along", "Character Carousel", "Diamond Celebration", "50th Anniversary",
                   "60th Anniversary"]

total = len(pins)


PARK_LABELS_JA = {
    "All": "すべて", "D23 Expo": "D23 Expo", "Walt Disney World": "ウォルト・ディズニー・ワールド",
    "Disneyland Resort": "ディズニーランド・リゾート", "Disney Parks (Shared/Unspecified)": "ディズニーパークス(共通)",
    "Disney Store / Online Exclusive": "ディズニーストア/オンライン限定", "Tokyo Disneyland": "東京ディズニーランド",
    "Disneyland Paris": "ディズニーランド・パリ", "Hong Kong Disneyland": "香港ディズニーランド",
    "Shanghai Disneyland": "上海ディズニーランド", "Convention Exclusive (SDCC等)": "コンベンション限定(SDCC等)",
    "Other / Unknown": "その他/不明",
}
COLLECTION_LABELS_JA = {
    "All": "すべて", "Mickey & Friends": "ミッキー&フレンズ", "Princesses": "プリンセス",
    "Star Wars": "スター・ウォーズ", "Marvel": "マーベル", "Pixar": "ピクサー", "Villains": "ヴィランズ",
    "Attractions": "アトラクション", "Winnie the Pooh & Friends": "くまのプーさん&フレンズ",
    "Alice in Wonderland": "ふしぎの国のアリス", "Muppets": "マペッツ", "Peter Pan / Neverland": "ピーター・パン/ネバーランド",
    "Lilo & Stitch": "リロ&スティッチ", "The Lion King": "ライオン・キング",
    "Nightmare Before Christmas": "ナイトメアー・ビフォア・クリスマス", "Aristocats": "おしゃれキャット",
    "Dumbo": "ダンボ", "Hercules": "ヘラクレス", "Big Hero 6": "ベイマックス", "Zootopia": "ズートピア",
    "Kingdom Hearts": "キングダム ハーツ", "Tarzan": "ターザン", "Classic Disney Animation": "クラシック作品",
    "Modern Disney Animation": "近年の作品", "Other": "その他",
}
EDITION_LABELS_JA = {
    "All": "すべて", "Limited Edition (LE)": "数量限定(LE・数値確認済み)",
    "LE (Count Unknown)": "数量限定(LE・数値不明)", "Limited Release (LR)": "期間限定(LR)",
    "Open Edition (OE)": "通常販売(OE)", "Mystery / Chaser": "ミステリー/チェイサー",
    "Cast Member Trading": "キャスト用トレーディング", "Unknown": "不明",
}
STATUS_LABELS_JA = {
    "All": "すべて", "Official": "公式確認済み", "Likely Official": "公式の可能性が高い",
    "Unverified": "未確認", "Fantasy Pin": "ファンタジーピン(非公式)", "Non-Tradeable": "トレード対象外",
    "Unofficial": "非公式", "Not a Pin": "ピン以外の商品",
}
COLOR_LABELS_JA = {
    "All": "すべて", "Red": "赤", "Pink": "ピンク", "Blue": "青", "Aqua": "水色", "Green": "緑",
    "Yellow": "黄", "Orange": "オレンジ", "Purple": "紫", "Brown": "茶", "Black": "黒", "White": "白",
    "Multi": "多色/その他",
}
SERIES_LABELS_JA = {
    "All": "すべて", "D23": "D23", "MOG": "MOG", "WDI": "WDI", "Anniversary": "アニバーサリー",
    "Cast Exclusive": "キャスト限定", "Hidden Mickey": "ハイドン・ミッキー", "Imagineering": "イマジニアリング",
    "Annual Passholder": "年間パスポート限定", "Artist Series": "アーティストシリーズ", "Mystery": "ミステリー",
    "Chaser": "チェイサー", "Jumbo": "ジャンボ", "Halloween": "ハロウィン", "Holiday": "ホリデー",
    "Windows of Attraction": "Windows of Attraction", "Enchanted Doors": "Enchanted Doors",
    "Magical Theater": "Magical Theater", "Digitize Disney": "Digitize Disney",
    "Premier Collection": "プレミアコレクション", "Game Changers": "Game Changers",
    "Play Along": "Play Along", "Character Carousel": "Character Carousel",
    "Diamond Celebration": "ダイヤモンド・セレブレーション", "50th Anniversary": "50周年",
    "60th Anniversary": "60周年",
}


def opts(values, label_map=None):
    label_map = label_map or {}
    return "".join(
        f'<option value="{v}">{label_map.get(v, v)}</option>' for v in values
    )


park_options = opts(PARKS, PARK_LABELS_JA)
collection_options = opts(COLLECTIONS, COLLECTION_LABELS_JA)
edition_options = opts(EDITION_TYPES, EDITION_LABELS_JA)
status_options = opts(STATUS_LEVELS, STATUS_LABELS_JA)
series_options = opts(SERIES_KEYWORDS, SERIES_LABELS_JA)
color_options = opts(COLOR_TAGS, COLOR_LABELS_JA)
CHARACTER_LABELS_JA = {
    "Mickey Mouse": "ミッキーマウス", "Minnie Mouse": "ミニーマウス", "Donald Duck": "ドナルドダック",
    "Daisy Duck": "デイジーダック", "Goofy": "グーフィー", "Pluto": "プルート", "Chip": "チップ",
    "Dale": "デール", "Figaro": "フィガロ", "Duffy": "ダッフィー", "ShellieMay": "シェリーメイ",
    "Gelatoni": "ジェラトーニ", "StellaLou": "ステラ・ルー", "CookieAnn": "クッキー・アン",
    "LinaBell": "リーナ・ベル", "Olaf": "オラフ", "Anna": "アナ", "Elsa": "エルサ",
    "Rapunzel": "ラプンツェル", "Belle": "ベル", "Beast": "野獣", "Aurora": "オーロラ姫",
    "Jasmine": "ジャスミン", "Aladdin": "アラジン", "Genie": "ジーニー", "Ariel": "アリエル",
    "Ursula": "アースラ", "Flounder": "フランダー", "Woody": "ウッディ", "Buzz Lightyear": "バズ・ライトイヤー",
    "Jessie": "ジェシー", "Sulley": "サリー", "Mike Wazowski": "マイク・ワゾウスキー",
    "Baymax": "ベイマックス", "Hiro Hamada": "ヒロ・ハマダ", "Stitch": "スティッチ", "Angel": "エンジェル",
    "Scrump": "スクランプ", "Scar": "スカー", "Hades": "ハデス", "Maleficent": "マレフィセント",
    "Cruella de Vil": "クルエラ・ド・ヴィル", "Captain Hook": "フック船長", "Peter Pan": "ピーター・パン",
    "Wendy": "ウェンディ", "Tigger": "ティガー", "Eeyore": "イーヨー", "Piglet": "ピグレット",
    "Snow White": "白雪姫", "Evil Queen": "女王", "Gaston": "ガストン", "Flynn Rider": "フリン・ライダー",
    "Vanellope": "ヴァネロペ", "Judy Hopps": "ジュディ・ホップス", "Nick Wilde": "ニック・ワイルド",
    "Groot": "グルート", "Grogu": "グローグー", "Darth Vader": "ダース・ベイダー",
    "Simba": "シンバ", "Rafiki": "ラフィキ", "Timon": "ティモン", "Pumbaa": "プンバァ", "Nala": "ナラ",
    "Mufasa": "ムファサ", "Jack Skellington": "ジャック・スケリントン", "Sally": "サリー(NBC)",
    "Marie": "マリー", "Duchess": "ダッチェス", "Dumbo": "ダンボ", "Hercules": "ヘラクレス",
    "Megara": "メグ", "Pinocchio": "ピノキオ", "Bambi": "バンビ", "Moana": "モアナ", "Maui": "マウイ",
    "Tiana": "ティアナ", "Mulan": "ムーラン", "Mushu": "ムーシュー", "Mirabel": "ミラベル",
    "Luca": "ルカ", "Remy": "レミー", "WALL-E": "ウォーリー", "EVE": "イヴ", "Nemo": "ニモ",
    "Dory": "ドリー", "Merida": "メリダ", "Joy": "ヨロコビ", "Sadness": "カナシミ",
    "Figment": "フィグメント", "Orange Bird": "オレンジバード", "Spider-Man": "スパイダーマン",
    "Iron Man": "アイアンマン", "Captain America": "キャプテン・アメリカ", "Thor": "ソー",
    "Hulk": "ハルク", "Black Widow": "ブラック・ウィドウ", "Loki": "ロキ", "Black Panther": "ブラックパンサー",
    "Yoda": "ヨーダ", "Chewbacca": "チューバッカ", "Boba Fett": "ボバ・フェット",
    "Stormtrooper": "ストームトルーパー", "The Mandalorian": "マンダロリアン", "Ahsoka": "アソーカ",
    "Kylo Ren": "カイロ・レン", "Finn": "フィン", "Princess Leia": "レイア姫", "Han Solo": "ハン・ソロ",
    "Luke Skywalker": "ルーク・スカイウォーカー", "Kermit the Frog": "カーミット", "Miss Piggy": "ミス・ピギー",
    "Fozzie Bear": "フォジー・ベア", "Gonzo": "ゴンゾー", "Tinker Bell": "ティンカー・ベル",
    "Cinderella": "シンデレラ", "Fairy Godmother": "フェアリー・ゴッドマザー",
    "Winnie the Pooh": "くまのプーさん", "Mad Hatter": "帽子屋", "Cheshire Cat": "チェシャ猫",
    "White Rabbit": "白うさぎ", "Alice": "アリス", "Queen of Hearts": "ハートの女王",
    "Jafar": "ジャファー", "Zootopia": "ズートピア", "Chernabog": "チェルナボーグ",
    "Pocahontas": "ポカホンタス", "Boo": "ブー", "Violet Parr": "バイオレット・パー",
    "Tarzan": "ターザン", "Sven": "スヴェン", "Kristoff": "クリストフ", "Prince Eric": "エリック王子",
    "Rex (Toy Story)": "レックス", "Hamm": "ハム",
    "Alberto": "アルベルト", "BB-8": "BB-8", "Baloo": "バルー", "Big Al": "ビッグ・アル",
    "C-3PO": "C-3PO", "Carl Fredricksen": "カール・フレドリクセン", "Crush": "クラッシュ",
    "Dante": "ダンテ", "Dewey": "ヒューイ・デューイ・ルーイ(デューイ)", "Disgust": "イカリ",
    "Doctor Strange": "ドクター・ストレンジ", "Dr. Facilier": "ドクター・ファシリエ",
    "Emile": "エミール", "Emperor Zurg": "ザーグ皇帝", "Esmeralda": "エスメラルダ",
    "Gus (Cinderella)": "ガス", "Huey": "ヒューイ", "Iago": "イアーゴ", "Jaq": "ジャック",
    "Jiminy Cricket": "ジミニー・クリケット", "John Smith": "ジョン・スミス", "Kaa": "カー",
    "Kronk": "クロンク", "Kuzco": "クズコ", "Louie": "ルーイ", "Meeko": "ミーコ",
    "Miguel": "ミゲル", "Mowgli": "モーグリ", "Naveen": "ナヴィーン王子",
    "Oogie Boogie": "ブギーマン", "Pegasus": "ペガサス", "R2-D2": "R2-D2",
    "Randall": "ランドール", "Robin Hood": "ロビン・フッド", "Roz": "ロズ",
    "Russell (Up)": "ラッセル", "Terk": "ターク", "Thumper": "とんすけ",
    "Venom": "ヴェノム", "Yzma": "イズマ",
}
def format_character_label(c):
    ja = CHARACTER_LABELS_JA.get(c)
    return f"{ja} - {c}" if ja else c


character_options = '<option value="All">すべて</option>' + "".join(
    f'<option value="{c}">{format_character_label(c)}</option>' for c in TOP_CHARACTERS
)

RARITY_LABELS_MAP = [
    ("All", "すべて"),
    ("Legendary", "伝説級(LE300以下)"),
    ("Rare", "レア(LE1000以下)"),
    ("Uncommon", "やや珍しい(LE3000以下)"),
    ("Common", "一般(LE3000超 / OE)"),
    ("Unknown", "不明"),
]
rarity_options = "".join(f'<option value="{v}">{label}</option>' for v, label in RARITY_LABELS_MAP)

RECENCY_LABELS_MAP = [
    ("all", "すべて"),
    ("7", "過去7日以内"),
    ("30", "過去30日以内"),
    ("month", "今月"),
    ("year", "今年"),
]
recency_options = "".join(f'<option value="{v}">{label}</option>' for v, label in RECENCY_LABELS_MAP)

html_doc = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pin Finder — Disney Collectible Pin Database</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --navy: #7B6FC4; --navy-deep: #5C4FA8; --gold: #E8A9C9; --gold-light: #F3C9DE;
    --red: #E0687A; --teal: #5CC7B8; --cream: #FFF8FB; --cream-dim: #FBEFF5;
    --ink: #4A3F5C; --ink-soft: #8B7F9E; --line: #F0DCE8;
    --mint: #A8E6CF; --sky: #A9D6F5; --butter: #FFE7A0;
    --bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0; color: var(--ink); font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased;
    background-color: var(--cream);
    background-image:
      url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%22520%22%20height%3D%22520%22%20viewBox%3D%220%200%20520%20520%22%3E%0A%20%20%3Cdefs%3E%0A%20%20%20%20%3CradialGradient%20id%3D%22balloonPink%22%20cx%3D%2235%25%22%20cy%3D%2228%25%22%20r%3D%2275%25%22%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%23FFE3F0%22/%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%23F0B8D6%22/%3E%0A%20%20%20%20%3C/radialGradient%3E%0A%20%20%20%20%3CradialGradient%20id%3D%22balloonBlue%22%20cx%3D%2235%25%22%20cy%3D%2228%25%22%20r%3D%2275%25%22%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%23E3F3FF%22/%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%23B8D8F0%22/%3E%0A%20%20%20%20%3C/radialGradient%3E%0A%20%20%20%20%3CradialGradient%20id%3D%22balloonGold%22%20cx%3D%2235%25%22%20cy%3D%2228%25%22%20r%3D%2275%25%22%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%23FFF6DC%22/%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%23F0DBA0%22/%3E%0A%20%20%20%20%3C/radialGradient%3E%0A%20%20%20%20%3CradialGradient%20id%3D%22balloonMint%22%20cx%3D%2235%25%22%20cy%3D%2228%25%22%20r%3D%2275%25%22%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%23E4FBF1%22/%3E%0A%20%20%20%20%20%20%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%23B8E8D0%22/%3E%0A%20%20%20%20%3C/radialGradient%3E%0A%20%20%3C/defs%3E%0A%0A%20%20%3Cg%20opacity%3D%220.4%22%3E%0A%20%20%20%20%3Cellipse%20cx%3D%2270%22%20cy%3D%2260%22%20rx%3D%2222%22%20ry%3D%2227%22%20fill%3D%22url%28%23balloonPink%29%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2270%22%20y1%3D%2287%22%20x2%3D%2266%22%20y2%3D%22110%22%20stroke%3D%22%23D9A8C4%22%20stroke-width%3D%221.5%22/%3E%0A%20%20%20%20%3Cellipse%20cx%3D%22380%22%20cy%3D%2250%22%20rx%3D%2219%22%20ry%3D%2223%22%20fill%3D%22url%28%23balloonBlue%29%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%22380%22%20y1%3D%2273%22%20x2%3D%22377%22%20y2%3D%2293%22%20stroke%3D%22%23A0C4E0%22%20stroke-width%3D%221.5%22/%3E%0A%20%20%20%20%3Cellipse%20cx%3D%22470%22%20cy%3D%22260%22%20rx%3D%2217%22%20ry%3D%2221%22%20fill%3D%22url%28%23balloonMint%29%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%22470%22%20y1%3D%22281%22%20x2%3D%22468%22%20y2%3D%22299%22%20stroke%3D%22%239CD0B4%22%20stroke-width%3D%221.5%22/%3E%0A%20%20%20%20%3Cellipse%20cx%3D%2240%22%20cy%3D%22300%22%20rx%3D%2218%22%20ry%3D%2222%22%20fill%3D%22url%28%23balloonBlue%29%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2240%22%20y1%3D%22322%22%20x2%3D%2237%22%20y2%3D%22341%22%20stroke%3D%22%23A0C4E0%22%20stroke-width%3D%221.5%22/%3E%0A%20%20%20%20%3Cellipse%20cx%3D%22180%22%20cy%3D%22400%22%20rx%3D%2221%22%20ry%3D%2226%22%20fill%3D%22url%28%23balloonPink%29%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%22180%22%20y1%3D%22426%22%20x2%3D%22176%22%20y2%3D%22448%22%20stroke%3D%22%23D9A8C4%22%20stroke-width%3D%221.5%22/%3E%0A%20%20%20%20%3Cellipse%20cx%3D%22440%22%20cy%3D%22420%22%20rx%3D%2218%22%20ry%3D%2222%22%20fill%3D%22url%28%23balloonGold%29%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%22440%22%20y1%3D%22442%22%20x2%3D%22437%22%20y2%3D%22461%22%20stroke%3D%22%23D4BE84%22%20stroke-width%3D%221.5%22/%3E%0A%20%20%3C/g%3E%0A%0A%20%20%3C%21--%20%E3%81%8B%E3%82%8F%E3%81%84%E3%81%84%E3%81%8A%E5%9F%8E%28%E6%B1%8E%E7%94%A8%E3%82%B7%E3%83%AB%E3%82%A8%E3%83%83%E3%83%88%E3%80%81%E7%89%B9%E5%AE%9A%E4%BD%9C%E5%93%81%E3%82%92%E6%A8%A1%E5%80%A3%E3%81%97%E3%81%AA%E3%81%84%29%20--%3E%0A%20%20%3Cg%20transform%3D%22translate%28150%2C150%29%22%20opacity%3D%220.30%22%20fill%3D%22none%22%20stroke%3D%22%23B49BD8%22%20stroke-width%3D%222.4%22%20stroke-linejoin%3D%22round%22%3E%0A%20%20%20%20%3Crect%20x%3D%220%22%20y%3D%2240%22%20width%3D%2270%22%20height%3D%2238%22%20rx%3D%222%22/%3E%0A%20%20%20%20%3Crect%20x%3D%228%22%20y%3D%2210%22%20width%3D%2216%22%20height%3D%2230%22/%3E%0A%20%20%20%20%3Cpolygon%20points%3D%228%2C10%2016%2C-6%2024%2C10%22/%3E%0A%20%20%20%20%3Crect%20x%3D%2246%22%20y%3D%2210%22%20width%3D%2216%22%20height%3D%2230%22/%3E%0A%20%20%20%20%3Cpolygon%20points%3D%2246%2C10%2054%2C-6%2062%2C10%22/%3E%0A%20%20%20%20%3Crect%20x%3D%2227%22%20y%3D%22-4%22%20width%3D%2216%22%20height%3D%2244%22/%3E%0A%20%20%20%20%3Cpolygon%20points%3D%2227%2C-4%2035%2C-24%2043%2C-4%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%2235%22%20y1%3D%22-24%22%20x2%3D%2235%22%20y2%3D%22-32%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%2235%22%20cy%3D%22-34%22%20r%3D%222.4%22%20fill%3D%22%23B49BD8%22/%3E%0A%20%20%20%20%3Crect%20x%3D%2228%22%20y%3D%2258%22%20width%3D%2214%22%20height%3D%2220%22/%3E%0A%20%20%20%20%3Cpath%20d%3D%22M28%2058%20a7%207%200%200%201%2014%200%22/%3E%0A%20%20%3C/g%3E%0A%0A%20%20%3C%21--%20%E3%81%8B%E3%82%8F%E3%81%84%E3%81%84%E8%A6%B3%E8%A6%A7%E8%BB%8A%20--%3E%0A%20%20%3Cg%20transform%3D%22translate%28330%2C300%29%22%20opacity%3D%220.30%22%20fill%3D%22none%22%20stroke%3D%22%238FB8D8%22%20stroke-width%3D%222.4%22%20stroke-linecap%3D%22round%22%3E%0A%20%20%20%20%3Ccircle%20cx%3D%220%22%20cy%3D%220%22%20r%3D%2236%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%220%22%20cy%3D%220%22%20r%3D%223%22%20fill%3D%22%238FB8D8%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%220%22%20y1%3D%22-36%22%20x2%3D%220%22%20y2%3D%2236%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%22-36%22%20y1%3D%220%22%20x2%3D%2236%22%20y2%3D%220%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%22-25%22%20y1%3D%22-25%22%20x2%3D%2225%22%20y2%3D%2225%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%22-25%22%20y1%3D%2225%22%20x2%3D%2225%22%20y2%3D%22-25%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%220%22%20cy%3D%22-36%22%20r%3D%224%22%20fill%3D%22%238FB8D8%22%20stroke%3D%22none%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%220%22%20cy%3D%2236%22%20r%3D%224%22%20fill%3D%22%238FB8D8%22%20stroke%3D%22none%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%22-36%22%20cy%3D%220%22%20r%3D%224%22%20fill%3D%22%238FB8D8%22%20stroke%3D%22none%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%2236%22%20cy%3D%220%22%20r%3D%224%22%20fill%3D%22%238FB8D8%22%20stroke%3D%22none%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%22-25%22%20cy%3D%22-25%22%20r%3D%224%22%20fill%3D%22%238FB8D8%22%20stroke%3D%22none%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%2225%22%20cy%3D%2225%22%20r%3D%224%22%20fill%3D%22%238FB8D8%22%20stroke%3D%22none%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%22-25%22%20cy%3D%2225%22%20r%3D%224%22%20fill%3D%22%238FB8D8%22%20stroke%3D%22none%22/%3E%0A%20%20%20%20%3Ccircle%20cx%3D%2225%22%20cy%3D%22-25%22%20r%3D%224%22%20fill%3D%22%238FB8D8%22%20stroke%3D%22none%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%220%22%20y1%3D%2236%22%20x2%3D%22-10%22%20y2%3D%2250%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%220%22%20y1%3D%2236%22%20x2%3D%2210%22%20y2%3D%2250%22/%3E%0A%20%20%20%20%3Cline%20x1%3D%22-10%22%20y1%3D%2250%22%20x2%3D%2210%22%20y2%3D%2250%22/%3E%0A%20%20%3C/g%3E%0A%3C/svg%3E");
    background-repeat: repeat; background-size: 480px 480px; background-attachment: fixed;
  }
  h1, h2, .display { font-family: 'Baloo 2', sans-serif; letter-spacing: -0.01em; }
  .mono { font-family: 'IBM Plex Mono', monospace; }
  a { color: inherit; text-decoration: none; }

  header {
    position: relative; padding: 28px 24px 60px; overflow: hidden; color: var(--cream);
    background: var(--navy-deep);
  }
  .header-collage {
    position: absolute; inset: 0; z-index: 0;
    display: grid; grid-template-columns: repeat(7, 1fr); gap: 0;
    background: var(--navy-deep);
  }
  .header-collage img {
    width: 100%; height: 100%; object-fit: contain; display: block; filter: saturate(0.9);
  }
  .header-overlay {
    position: absolute; inset: 0; z-index: 1;
    background: linear-gradient(180deg, rgba(232,201,109,0.55) 0%, rgba(196,158,70,0.70) 60%, rgba(150,115,40,0.82) 100%);
  }
  .header-inner { max-width: 1100px; margin: 0 auto; position: relative; z-index: 2; }
  .brand-row { display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 34px; }
  .brand { font-size: 22px; font-weight: 700; display: flex; align-items: center; gap: 10px; color: #ffffff; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000; }
  .brand .badge-dot { width: 12px; height: 12px; border-radius: 50%; background: var(--gold); }
  .brand-tag { font-size: 12px; color: rgba(255,255,255,0.85); letter-spacing: 0.08em; text-transform: uppercase; text-shadow: 0 1px 3px rgba(0,0,0,0.4); }
  .refresh-btn {
    background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.4); color: white;
    padding: 5px 12px; border-radius: 999px; font-size: 12px; cursor: pointer; font-weight: 600;
    transition: transform 0.3s var(--bounce), background 0.2s;
  }
  .refresh-btn:hover { background: rgba(255,255,255,0.28); transform: scale(1.1) rotate(-8deg); }
  .hero-title { font-size: clamp(22px, 3.6vw, 48px); font-weight: 700; line-height: 1.1; max-width: 100%; margin: 0 0 14px; white-space: nowrap; color: #ffffff; text-shadow: -1.5px -1.5px 0 #000, 1.5px -1.5px 0 #000, -1.5px 1.5px 0 #000, 1.5px 1.5px 0 #000, 0 0 8px rgba(0,0,0,0.5); }
  .hero-sub { font-size: 15px; color: #ffffff; max-width: 560px; margin: 0 0 28px; line-height: 1.6; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000, 0 0 6px rgba(0,0,0,0.4); }
  #search { width: 100%; max-width: 620px; padding: 14px 20px; font-size: 16px; border-radius: 999px; border: none; background: white; color: var(--ink); }
  .search-note { font-size: 11.5px; color: rgba(255,255,255,0.85); margin: 8px 0 0; max-width: 620px; text-shadow: 0 1px 3px rgba(0,0,0,0.4); }
  .stat-strip { display: flex; gap: 26px; margin-top: 26px; flex-wrap: wrap; }
  .stat .num { font-family: 'Baloo 2', sans-serif; font-size: 24px; color: var(--gold-light); font-weight: 700; }
  .stat .label { font-size: 10.5px; letter-spacing: 0.06em; text-transform: uppercase; color: rgba(255,255,255,0.55); }

  .filter-bar { max-width: 1100px; margin: -30px auto 0; padding: 0 24px; position: relative; z-index: 2; }
  .chip-row { background: white; border-radius: 28px; padding: 18px 22px; box-shadow: 0 10px 26px rgba(90,26,110,0.12); display: flex; gap: 18px; flex-wrap: wrap; align-items: center; }
  .chip-group { display: flex; flex-direction: column; gap: 6px; }
  .chip-group-label { font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--ink-soft); font-weight: 700; }
  .filter-select, .le-input { padding: 7px 12px; border-radius: 999px; border: 1px solid var(--line); background: white; font-size: 13px; min-width: 140px; transition: transform 0.25s var(--bounce); }
  .filter-select:hover, .le-input:hover { transform: scale(1.03); }
  .status-toggle-row { display: flex; align-items: center; flex-wrap: wrap; gap: 14px; margin-top: 12px; padding-top: 12px; border-top: 1px dashed var(--line); }
  .status-toggle-label { font-size: 11.5px; font-weight: 700; color: var(--ink-soft); }
  .status-toggle { display: flex; align-items: center; gap: 5px; font-size: 12px; color: var(--ink-soft); cursor: pointer; }

  main { max-width: 1100px; margin: 0 auto; padding: 44px 24px 100px; }
  .section-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 10px; border-bottom: 2px solid var(--ink); padding-bottom: 8px; }
  .section-title { font-size: 22px; font-weight: 700; }
  .section-count { font-size: 12.5px; color: var(--ink-soft); }
  .sort-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; font-size: 12.5px; color: var(--ink-soft); }
  .sort-bar select { padding: 6px 10px; border-radius: 6px; border: 1px solid var(--line); font-size: 12.5px; }

  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 18px; margin-bottom: 30px; }

  .pin-card {
    background: #fff; border-radius: 28px; box-shadow: 0 4px 14px rgba(123,111,196,0.14);
    cursor: pointer; transition: transform 0.35s var(--bounce), box-shadow 0.35s var(--bounce);
    position: relative; border: 1px solid var(--line); display: flex; flex-direction: column;
    overflow: hidden;
  }
  .pin-card::before {
    content: ""; position: absolute; top: 8px; left: 16px; width: 46%; height: 22px; z-index: 3;
    background: radial-gradient(ellipse at center, rgba(255,255,255,0.55) 0%, rgba(255,255,255,0) 70%);
    border-radius: 50%; pointer-events: none;
  }
  .pin-card:hover { transform: translateY(-8px) scale(1.035) rotate(-0.6deg); box-shadow: 0 18px 34px rgba(123,111,196,0.26); }
  .hang-hole { position: absolute; top: 6px; left: 50%; transform: translateX(-50%); width: 36px; height: 22px; z-index: 2; }
  .hh-face { position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 24px; height: 14px; border-radius: 50%; background: var(--cream); border: 1px solid #e2dcc8; }
  .hh-ear { position: absolute; top: 0; width: 13px; height: 13px; border-radius: 50%; background: var(--cream); border: 1px solid #e2dcc8; }
  .hh-ear-l { left: 2px; } .hh-ear-r { right: 2px; }
  .rarity-badge { position: absolute; top: 10px; left: 10px; z-index: 2; font-size: 10px; font-weight: 700; padding: 4px 10px; border-radius: 999px; }
  .new-badge {
    position: absolute; top: 38px; left: 10px; z-index: 2; font-size: 10px; font-weight: 800;
    padding: 4px 10px; border-radius: 999px; color: white;
    background: linear-gradient(120deg, #FF8FA3, #FF6B8B);
    box-shadow: 0 2px 6px rgba(255,107,139,0.4);
    animation: newPulse 2s ease-in-out infinite;
  }
  .new-badge-soft {
    background: linear-gradient(120deg, #C9B8E8, #B49BD8);
    box-shadow: 0 2px 6px rgba(180,155,216,0.35);
    animation: none;
  }
  @keyframes newPulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.06); } }
  .rarity-legendary { background: #f0c419; color: #5a4300; }
  .rarity-rare { background: #c9a7f0; color: #3a1a5c; }
  .rarity-uncommon { background: #8fd4c1; color: #0b3d31; }
  .rarity-common { background: #d8d2c2; color: #59523e; }
  .rarity-unknown { background: #e2e2e2; color: #888; }
  .corner-fav-btn { position: absolute; top: 8px; right: 8px; z-index: 4; width: 26px; height: 26px; border-radius: 50%; border: 1px solid var(--line); background: rgba(255,255,255,0.9); font-size: 14px; cursor: pointer; transition: transform 0.3s var(--bounce); }
  .corner-fav-btn:hover { transform: scale(1.25) rotate(-12deg); }
  .corner-fav-btn:active { transform: scale(0.85); }
  .corner-fav-btn.active { background: #fff3d6; border-color: var(--gold); color: #b8860b; }
  .fantasy-banner { position: absolute; top: 32px; left: 0; right: 0; z-index: 3; background: linear-gradient(120deg, #a94fd6, #7b2fb0); color: white; text-align: center; font-size: 10px; font-weight: 800; padding: 5px 4px; }
  .pin-img-frame { aspect-ratio: 1/1; background: #f4f1e8; display: flex; align-items: center; justify-content: center; padding: 20px; flex-shrink: 0; }
  .pin-img-frame img { max-width: 100%; max-height: 100%; object-fit: contain; }
  .pin-body { padding: 14px 14px 0; flex: 1 1 auto; }
  .pin-title-link { font-size: 14px; font-weight: 700; line-height: 1.35; color: #7b2fb0; height: 38px; overflow: hidden; margin-bottom: 10px; }
  .action-row { display: flex; gap: 8px; margin-bottom: 10px; }
  .action-btn { border: 1px solid var(--line); background: white; border-radius: 999px; padding: 7px 10px; font-size: 12px; font-weight: 700; color: var(--ink-soft); cursor: pointer; transition: transform 0.25s var(--bounce), background 0.2s; }
  .action-btn:hover { transform: scale(1.06); }
  .action-btn:active { transform: scale(0.94); }
  .own-btn { flex: 1; }
  .own-btn.active { background: rgba(92,199,184,0.18); border-color: var(--teal); color: #167367; }
  .iso-btn-group { flex: 1; display: flex; position: relative; }
  .iso-btn { flex: 1; border-radius: 999px 0 0 999px; border-right: none; }
  .iso-btn.active { background: rgba(224,104,122,0.14); border-color: var(--red); color: var(--red); }
  .iso-caret { border: 1px solid var(--line); border-radius: 0 999px 999px 0; background: white; padding: 7px 9px; font-size: 12px; cursor: pointer; transition: transform 0.25s var(--bounce); }
  .iso-caret:hover { transform: scale(1.1); }
  .status-dropdown { display: none; position: fixed; z-index: 100; background: white; border: 1px solid var(--line); border-radius: 10px; box-shadow: 0 10px 24px rgba(90,26,110,0.18); min-width: 220px; }
  .status-dropdown.open { display: block; }
  .status-option { padding: 11px 16px; font-size: 13px; text-align: center; cursor: pointer; border-bottom: 1px solid #f5eefa; }
  .status-option:last-child { border-bottom: none; }
  .status-option:hover { background: var(--cream-dim); }
  .status-option.status-own { color: #1a8f5c; font-weight: 700; }
  .status-option.status-iso { color: #c99a1a; font-weight: 700; }
  .status-option.status-trade { color: #2f6fb0; font-weight: 700; }
  .status-option.status-grail { color: #b8860b; font-weight: 800; }
  .status-option.status-clear { color: var(--ink-soft); font-size: 11.5px; }
  .status-tag { display: inline-block; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 999px; margin-left: 6px; }
  .status-tag.status-trade { background: rgba(47,111,176,0.14); color: #2f6fb0; }
  .status-tag.status-grail { background: rgba(184,134,11,0.14); color: #b8860b; }
  .series-box { background: var(--cream-dim); border-radius: 16px; padding: 8px 12px; margin-bottom: 10px; }
  .series-label { font-size: 9.5px; letter-spacing: 0.06em; color: var(--ink-soft); font-weight: 700; }
  .series-value { font-size: 12.5px; font-weight: 700; color: #7b2fb0; }
  .pin-price { font-family: 'IBM Plex Mono', monospace; font-size: 13.5px; color: var(--red); font-weight: 700; padding: 4px 14px 12px; flex-shrink: 0; }
  .pin-meta { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 6px; }
  .tag { font-size: 10px; padding: 3px 8px; border-radius: 999px; background: var(--cream-dim); color: var(--ink-soft); cursor: pointer; }
  .tag.park { background: rgba(92,199,184,0.18); color: #167367; }
  .tag.le { background: rgba(224,104,122,0.12); color: var(--red); }
  .tag.official { background: rgba(232,169,201,0.3); color: #8a2a5c; font-weight: 700; }
  .status-tag-official { background: rgba(26,143,92,0.16); color: #1a8f5c; font-weight: 700; }
  .status-tag-likely-official { background: rgba(47,111,176,0.14); color: #2f6fb0; font-weight: 700; }
  .status-tag-unverified { background: rgba(224,104,122,0.1); color: var(--red); font-weight: 700; }
  .status-tag-fantasy-pin { background: linear-gradient(120deg, #f0c9f7, #d9a7f0); color: #5a1a6e; font-weight: 800; }
  .status-tag-non-tradeable { background: rgba(90,90,90,0.12); color: #5b5347; font-weight: 700; }
  .status-tag-not-a-pin { background: rgba(90,90,90,0.18); color: #444; font-weight: 700; }
  .status-tag-unofficial { background: rgba(224,104,122,0.14); color: var(--red); font-weight: 700; }
  .release-bar { display: flex; justify-content: space-between; align-items: center; background: var(--cream-dim); border-top: 1px solid var(--line); border-radius: 0 0 17px 17px; padding: 8px 14px; font-size: 11px; color: var(--ink-soft); flex-shrink: 0; }
  .pin-id-small { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--gold); font-weight: 700; cursor: pointer; }
  .empty-msg { text-align: center; padding: 50px 20px; color: var(--ink-soft); display: none; }
  .loading-msg { text-align: center; padding: 60px 20px; color: var(--ink-soft); }
  .list-controls-bar { display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 16px; margin: 20px 0 8px; padding: 10px 18px; background: white; border-radius: 999px; border: 1px solid var(--line); font-size: 12.5px; }
  .page-numbers { display: flex; flex-wrap: wrap; justify-content: center; gap: 5px; }
  .page-num-btn { min-width: 32px; height: 32px; border-radius: 50%; border: 1px solid var(--line); background: white; font-size: 12.5px; cursor: pointer; transition: transform 0.25s var(--bounce); }
  .page-num-btn:hover { transform: scale(1.15); }
  .page-num-btn.current { background: var(--navy); color: white; border-color: var(--navy); font-weight: 700; }
  .page-num-btn.ellipsis { border: none; background: none; cursor: default; color: var(--ink-soft); }
  .page-summary { font-size: 12px; color: var(--ink-soft); text-align: center; margin-bottom: 40px; }
  .jump-control input { width: 70px; padding: 6px 10px; border-radius: 999px; border: 1px solid var(--line); }
  .jump-control button { padding: 6px 14px; border-radius: 999px; border: none; background: var(--navy); color: white; cursor: pointer; transition: transform 0.25s var(--bounce); }
  .jump-control button:hover { transform: scale(1.08); }
  .overlay { display: none; position: fixed; inset: 0; background: rgba(90,26,110,0.5); z-index: 50; align-items: flex-start; justify-content: center; padding: 40px 16px; overflow-y: auto; }
  .overlay.open { display: flex; }
  .modal { background: var(--cream); max-width: 600px; width: 100%; border-radius: 16px; overflow: hidden; position: relative; }
  .modal-top { background: #f4f1e8; padding: 30px; display: flex; justify-content: center; }
  .modal-top img { max-width: 240px; max-height: 240px; object-fit: contain; }
  .modal-body { padding: 24px 28px 28px; }
  .modal-close { position: absolute; top: 14px; right: 14px; width: 32px; height: 32px; border-radius: 50%; background: rgba(0,0,0,0.12); border: none; cursor: pointer; }
  .detail-row { display: flex; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid var(--line); font-size: 13.5px; }
  .modal-link { display: block; margin-top: 18px; text-align: center; background: var(--navy); color: white; padding: 13px; border-radius: 10px; font-weight: 700; }
  .report-btn { width: 100%; border: none; cursor: pointer; font-size: 14px; background: rgba(224,104,122,0.12); color: var(--red); margin-top: 10px; transition: transform 0.25s var(--bounce); }
  .report-btn:hover { transform: scale(1.02); background: rgba(224,104,122,0.2); }
  footer { text-align: center; padding: 28px; color: var(--ink-soft); font-size: 11.5px; }
  @media (max-width: 640px) {
    .header-collage { grid-template-columns: repeat(4, 1fr); }
    .header-collage img:nth-child(3), .header-collage img:nth-child(5), .header-collage img:nth-child(7) {
      display: none;
    }
    header { padding: 20px 16px 32px; }
    .brand-row { margin-bottom: 18px; }
    .hero-title { margin: 0 0 8px; }
    .hero-sub { margin: 0 0 14px; }
    .stat-strip { margin-top: 14px; gap: 16px; }
    .filter-bar { margin-top: -20px; }
  }
</style>
</head>
<body>

<header>
  <div class="header-collage">
    <img src="images/header-2.jpg" alt="">
    <img src="images/header-1.jpg" alt="">
    <img src="images/header-5.jpg" alt="">
    <img src="images/header-4.jpg" alt="">
    <img src="images/header-6.jpg" alt="">
    <img src="images/header-3.jpg" alt="">
    <img src="images/header-7.jpg" alt="">
  </div>
  <div class="header-overlay"></div>
  <div class="header-inner">
    <div class="brand-row">
      <div class="brand"><span class="badge-dot"></span>Pin Finder</div>
      <button id="refreshBtn" class="refresh-btn" title="最新データに更新">⟳ 更新</button>
      <a href="database/" class="refresh-btn" style="text-decoration:none;">📚 累積データベースを見る</a>
      <div class="brand-tag">Collector's Database</div>
    </div>
    <h1 class="hero-title">探していたピン、ここで見つかるかも。</h1>
    <p class="hero-sub">ディズニーピンを、キャラクター・パーク・シリーズ・限定数などから探せます。</p>
    <input type="text" id="search" placeholder="ピン名・キャラクター・シリーズ・Pin ID で検索…">
    <p class="search-note">※ 検索はeBay出品タイトル(英語表記)が対象です。カタカナでは検索結果に出てこない場合があります。</p>
    <div class="stat-strip" id="statStrip"></div>
  </div>
</header>

<div class="filter-bar">
  <div class="chip-row">
    <div class="chip-group"><div class="chip-group-label">パーク</div><select class="filter-select" id="parkSelect">__PARK_OPTIONS__</select></div>
    <div class="chip-group"><div class="chip-group-label">作品/コレクション</div><select class="filter-select" id="collectionSelect">__COLLECTION_OPTIONS__</select></div>
    <div class="chip-group"><div class="chip-group-label">エディション種別</div><select class="filter-select" id="editionSelect">__EDITION_OPTIONS__</select></div>
    <div class="chip-group"><div class="chip-group-label">シリーズ</div><select class="filter-select" id="seriesSelect">__SERIES_OPTIONS__</select></div>
    <div class="chip-group"><div class="chip-group-label">カラー</div><select class="filter-select" id="colorSelect">__COLOR_OPTIONS__</select></div>
    <div class="chip-group"><div class="chip-group-label">キャラクター</div><select class="filter-select" id="characterSelect">__CHARACTER_OPTIONS__</select></div>
    <div class="chip-group"><div class="chip-group-label">レアリティ(LE数目安)</div><select class="filter-select" id="raritySelect">__RARITY_OPTIONS__</select></div>
    <div class="chip-group"><div class="chip-group-label">🆕 新着</div><select class="filter-select" id="recencySelect">__RECENCY_OPTIONS__</select></div>
  </div>
  <div class="status-toggle-row">
    <button id="resetFiltersBtn" class="refresh-btn" style="background:rgba(26,143,92,0.15); border-color:rgba(26,143,92,0.4); color:#1a8f5c;">↺ 初期設定に戻す</button>
    <div class="status-toggle-label">表示するステータス:</div>
    <label class="status-toggle"><input type="checkbox" data-toggle-status="Official" checked> 公式確認済み</label>
    <label class="status-toggle"><input type="checkbox" data-toggle-status="Likely Official" checked> 公式の可能性が高い</label>
    <label class="status-toggle"><input type="checkbox" data-toggle-status="Unverified"> 未確認</label>
    <label class="status-toggle"><input type="checkbox" data-toggle-status="Fantasy Pin"> ファンタジーピン</label>
    <label class="status-toggle"><input type="checkbox" data-toggle-status="Non-Tradeable"> トレード対象外</label>
    <label class="status-toggle"><input type="checkbox" data-toggle-status="Unofficial"> 非公式</label>
    <label class="status-toggle"><input type="checkbox" data-toggle-status="Not a Pin"> ピン以外</label>
    <label class="status-toggle"><input type="checkbox" id="favOnlyToggle"> ★ お気に入りのみ表示</label>
  </div>
</div>

<main>
  <div class="section-head">
    <div class="section-title">Trending — 出品数が多いピン</div>
    <div class="section-count" id="resultCount"></div>
  </div>
  <div class="sort-bar">
    <label for="sortSelect">並び替え:</label>
    <select id="sortSelect">
      <option value="default" selected>Default(出品数順)</option>
      <option value="price_desc">価格が高い順</option>
      <option value="price_asc">価格が安い順</option>
      <option value="le_asc">LE数が少ない順(レア順)</option>
      <option value="rarity">レアリティ順</option>
      <option value="az">タイトル A-Z</option>
      <option value="newest">🆕 新着順(発売日が新しい順)</option>
    </select>
  </div>
  <div id="loadingMsg" class="loading-msg">読み込み中…</div>
  <div class="grid" id="pinGrid"></div>
  <div class="empty-msg" id="emptyMsg">条件に一致するピンが見つかりませんでした。</div>
  <div class="list-controls-bar">
    <div class="chip-group"><div class="chip-group-label">表示件数</div>
      <select class="filter-select" id="perPage">
        <option value="10" selected>10件</option>
        <option value="20">20件</option>
        <option value="40">40件</option>
        <option value="60">60件</option>
        <option value="100">100件</option>
        <option value="200">200件</option>
      </select>
    </div>
    <div class="page-numbers" id="pageNumbers"></div>
    <div class="jump-control">
      <input type="number" id="jumpPage" min="1" placeholder="ページ番号">
      <button id="jumpBtn">移動</button>
    </div>
  </div>
  <div class="page-summary" id="pageSummary"></div>
</main>

<footer>Pin Finder — データ出典: eBay Browse API（米国市場） / 表示価格は出品時点の参考値です / 1時間ごと自動更新</footer>

<div class="overlay" id="overlay">
  <div class="modal">
    <button class="modal-close" onclick="closeModal()">✕</button>
    <div class="modal-top"><img id="modalImg" src="" alt=""></div>
    <div class="modal-body" id="modalBody"></div>
  </div>
</div>

<div class="status-dropdown" id="sharedStatusDropdown">
  <div class="status-option status-own" data-status="own">すでに<b>持っている</b></div>
  <div class="status-option status-iso" data-status="iso"><b>探している</b>(ISO)</div>
  <div class="status-option status-trade" data-status="trade"><b>トレード</b>可能</div>
  <div class="status-option status-grail" data-status="grail">レアな<b>お宝ピン</b></div>
  <div class="status-option status-clear" data-status="">ステータスを解除</div>
</div>

<script>
const REPORT_EMAIL = "__REPORT_EMAIL__";
let allPins = [];
const state = { query:'', park:'All', collection:'All', edition:'All', series:'All',
                 color:'All', character:'All', rarity:'All', recency:'all', favOnly:false, page:1, perPage:10,
                 sort:'default', hiddenStatuses:new Set(['Unverified','Fantasy Pin','Non-Tradeable','Unofficial','Not a Pin']) };
let matchingPins = [];

const STORAGE_KEY = 'pinRegistryCollection';
function loadCollection() { try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } catch(e) { return {}; } }
function saveCollection(d) { localStorage.setItem(STORAGE_KEY, JSON.stringify(d)); }
let collection = loadCollection();

function esc(s) {
  if (!s) return '';
  return String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

function cardHtml(p, idx) {
  const rarity = p.rarity || 'Unknown';
  const rarityClass = rarity.toLowerCase();
  const status = p.quality_status || 'Unverified';
  const statusClass = status.toLowerCase().replace(/ /g, '-');
  const collectionVal = p.collection || 'Other';
  const editionType = p.edition_type || 'Unknown';
  const le = p.le_count || '';
  let releaseDate = '';
  if (p.official && p.official.notes) {
    const m = p.official.notes.match(/発売日[:：]\s*([\d\-]+)/);
    if (m) releaseDate = m[1];
  }
  // NEW判定は発売日のみを基準にする(発見日は使わない)。
  // 発売日が確認できない場合のみ、タイトルの年号(今年)を控えめな代替指標として使う
  const newInfo = getNewInfo(p);
  let newBadge = '';
  if (newInfo.isNew && newInfo.confirmed) {
    newBadge = '<div class="new-badge">🆕 NEW</div>';
  } else if (newInfo.isNew) {
    newBadge = '<div class="new-badge new-badge-soft">🆕 今年の新作</div>';
  }
  const officialBadge = p.official ? '<span class="tag official">✓ 公式情報あり</span>' : '';
  const fantasyBanner = status === 'Fantasy Pin' ? '<div class="fantasy-banner">✦ ファンタジーピン(非公式ファンメイド)✦</div>' : '';
  const seriesDisplay = (p.series || '').split(';')[0].trim();
  const entry = collection[p.pin_id] || {};
  // カード上のタグ表記は英語のまま(フィルターのプルダウンだけ日本語)
  const rarityLabel = rarity;
  const statusLabel = status;
  const parkLabel = p.park;
  const editionLabel = editionType;
  const collectionLabel = collectionVal;

  return `
    <div class="pin-card" data-idx="${idx}">
      <div class="hang-hole"><span class="hh-ear hh-ear-l"></span><span class="hh-ear hh-ear-r"></span><span class="hh-face"></span></div>
      <div class="rarity-badge rarity-${rarityClass}">${rarityLabel}</div>
      ${newBadge}
      <button class="corner-fav-btn ${entry.favorite ? 'active' : ''}" data-pin-id="${p.pin_id}" data-action="favorite">${entry.favorite ? '★' : '☆'}</button>
      ${fantasyBanner}
      <div class="pin-img-frame"><img src="${esc(p.image_url)}" loading="lazy" onerror="this.style.display='none'"></div>
      <div class="pin-body">
        <div class="pin-title-link">${esc(p.title)}</div>
        <div class="action-row">
          <div class="iso-btn-group">
            <button class="iso-btn action-btn ${(entry.status==='iso'||entry.status==='trade'||entry.status==='grail')?'active':''}" data-pin-id="${p.pin_id}" data-action="iso">🔍 探してる${entry.status==='trade'?' <span class="status-tag status-trade">トレード可</span>':''}${entry.status==='grail'?' <span class="status-tag status-grail">お宝</span>':''}</button>
            <button class="iso-caret" data-pin-id="${p.pin_id}">▾</button>
          </div>
          <button class="own-btn action-btn ${entry.status==='own'?'active':''}" data-pin-id="${p.pin_id}" data-action="own">✓ 持ってる</button>
        </div>
        <div class="series-box"><div class="series-label">シリーズ</div><div class="series-value">${esc(seriesDisplay) || '—'}</div></div>
        <div class="pin-meta">
          <span class="tag status-tag-${statusClass}" data-filter-type="status" data-filter-value="${status}">${statusLabel}</span>
          <span class="tag park" data-filter-type="park" data-filter-value="${p.park}">${parkLabel}</span>
          ${le ? `<span class="tag le" data-filter-type="le" data-filter-value="${le}">LE ${le}</span>` : ''}
          <span class="tag" data-filter-type="edition" data-filter-value="${editionType}">${editionLabel}</span>
          <span class="tag" data-filter-type="collection" data-filter-value="${collectionVal}">${collectionLabel}</span>
          ${officialBadge}
        </div>
      </div>
      <div class="pin-price">$${p.min_price.toFixed(2)} – $${p.max_price.toFixed(2)}</div>
      <div class="release-bar">
        <span class="pin-id-small" data-pin-id="${p.pin_id}">${p.pin_id}</span>
        <span>発売日: ${releaseDate || '不明'}</span>
      </div>
    </div>`;
}

const RARITY_ORDER = { 'Legendary':0,'Rare':1,'Uncommon':2,'Common':3,'Unknown':4 };
const RARITY_LABELS_JA = { 'Legendary':'伝説級','Rare':'レア','Uncommon':'やや珍しい','Common':'一般','Unknown':'不明' };
const PARK_LABELS_JA_JS = {
  'D23 Expo':'D23 Expo','Walt Disney World':'ウォルト・ディズニー・ワールド','Disneyland Resort':'ディズニーランド・リゾート',
  'Disney Parks (Shared/Unspecified)':'ディズニーパークス(共通)','Disney Store / Online Exclusive':'ディズニーストア/オンライン限定',
  'Tokyo Disneyland':'東京ディズニーランド','Disneyland Paris':'ディズニーランド・パリ','Hong Kong Disneyland':'香港ディズニーランド',
  'Shanghai Disneyland':'上海ディズニーランド','Convention Exclusive (SDCC等)':'コンベンション限定(SDCC等)','Other / Unknown':'その他/不明',
};
const COLLECTION_LABELS_JA_JS = {
  'Mickey & Friends':'ミッキー&フレンズ','Princesses':'プリンセス','Star Wars':'スター・ウォーズ','Marvel':'マーベル',
  'Pixar':'ピクサー','Villains':'ヴィランズ','Attractions':'アトラクション','Winnie the Pooh & Friends':'くまのプーさん&フレンズ',
  'Alice in Wonderland':'ふしぎの国のアリス','Muppets':'マペッツ','Peter Pan / Neverland':'ピーター・パン/ネバーランド',
  'Lilo & Stitch':'リロ&スティッチ','The Lion King':'ライオン・キング','Nightmare Before Christmas':'ナイトメアー・ビフォア・クリスマス',
  'Aristocats':'おしゃれキャット','Dumbo':'ダンボ','Hercules':'ヘラクレス','Big Hero 6':'ベイマックス','Zootopia':'ズートピア',
  'Kingdom Hearts':'キングダム ハーツ','Tarzan':'ターザン','Classic Disney Animation':'クラシック作品','Modern Disney Animation':'近年の作品','Other':'その他',
};
const EDITION_LABELS_JA_JS = {
  'Limited Edition (LE)':'数量限定(LE)','Limited Release (LR)':'期間限定(LR)','Open Edition (OE)':'通常販売(OE)',
  'Mystery / Chaser':'ミステリー/チェイサー','Cast Member Trading':'キャスト用トレーディング','Unknown':'不明',
};
const STATUS_LABELS_JA_JS = {
  'Official':'公式確認済み','Likely Official':'公式の可能性が高い','Unverified':'未確認','Fantasy Pin':'ファンタジーピン',
  'Non-Tradeable':'トレード対象外','Unofficial':'非公式','Not a Pin':'ピン以外の商品',
};
const COLOR_THEMES = {
  'Red':{bg:'linear-gradient(180deg,#fff0f0 0%,#fdf3df 100%)',accent:'#e0687a'},
  'Pink':{bg:'linear-gradient(180deg,#fff0f7 0%,#fdf3df 100%)',accent:'#e08bb8'},
  'Blue':{bg:'linear-gradient(180deg,#eef5ff 0%,#fdf3df 100%)',accent:'#5b8fd6'},
  'Aqua':{bg:'linear-gradient(180deg,#eafcfa 0%,#fdf3df 100%)',accent:'#3fb8ae'},
  'Green':{bg:'linear-gradient(180deg,#eefaf0 0%,#fdf3df 100%)',accent:'#5cb87a'},
  'Yellow':{bg:'linear-gradient(180deg,#fffbea 0%,#fdf3df 100%)',accent:'#e0b23f'},
  'Orange':{bg:'linear-gradient(180deg,#fff2e6 0%,#fdf3df 100%)',accent:'#e08a3f'},
  'Purple':{bg:'linear-gradient(180deg,#f5eefc 0%,#fdf3df 100%)',accent:'#a06fd6'},
  'Brown':{bg:'linear-gradient(180deg,#f7f0e6 0%,#fdf3df 100%)',accent:'#a97c50'},
  'Black':{bg:'linear-gradient(180deg,#f0f0f2 0%,#fdf3df 100%)',accent:'#5a5a68'},
  'White':{bg:'linear-gradient(180deg,#fbfbfb 0%,#fdf3df 100%)',accent:'#b0aca0'},
};

function getReleaseDateMs(p) {
  if (p.official && p.official.notes) {
    const m = p.official.notes.match(/発売日[:：]\s*([\d\-]+)/);
    if (m) {
      const d = new Date(m[1]);
      if (!isNaN(d.getTime())) return d.getTime();
    }
  }
  return null;
}

function getTitleYear(title) {
  const m = (title || '').match(/\b(20\d{2})\b/);
  return m ? parseInt(m[1], 10) : null;
}

// NEW判定は「発売日」のみを基準にする(発見日は使わない)。
// 発売日が確認できない場合のみ、タイトルの年号(今年)を控えめな代替指標として使う。
function getNewInfo(p) {
  const releaseMs = getReleaseDateMs(p);
  if (releaseMs !== null) {
    const daysSince = (Date.now() - releaseMs) / (1000*60*60*24);
    return { isNew: daysSince >= 0 && daysSince <= 30, confirmed: true, sortValue: releaseMs };
  }
  const currentYear = new Date().getFullYear();
  const titleYear = getTitleYear(p.title);
  if (titleYear === currentYear) {
    return { isNew: true, confirmed: false, sortValue: new Date(titleYear, 0, 1).getTime() };
  }
  return { isNew: false, confirmed: false, sortValue: -Infinity };
}

// 「新着」プルダウンの範囲判定(7日/30日/今月/今年)。
// 発売日が確認できるものはそれを使い、確認できないものはタイトルの年号を控えめな代替指標にする
function matchesRecency(p, recency) {
  if (recency === 'all') return true;
  const releaseMs = getReleaseDateMs(p);
  const now = new Date();

  if (releaseMs !== null) {
    const d = new Date(releaseMs);
    const daysSince = (Date.now() - releaseMs) / (1000*60*60*24);
    if (recency === '7') return daysSince >= 0 && daysSince <= 7;
    if (recency === '30') return daysSince >= 0 && daysSince <= 30;
    if (recency === 'month') return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth();
    if (recency === 'year') return d.getFullYear() === now.getFullYear();
    return false;
  }
  // 発売日不明の場合、年号だけは「今年」の判定にのみ使う(週・月単位の精度はないため)
  if (recency === 'year') {
    return getTitleYear(p.title) === now.getFullYear();
  }
  return false;
}

function applyFilters() {
  matchingPins = allPins.filter(p => {
    const t = (p.title + ' ' + p.pin_id).toLowerCase();
    if (state.query && !t.includes(state.query)) return false;
    if (state.park !== 'All' && p.park !== state.park) return false;
    if (state.collection !== 'All' && p.collection !== state.collection) return false;
    if (state.edition !== 'All' && p.edition_type !== state.edition) return false;
    if (state.series !== 'All' && !(p.series||'').includes(state.series)) return false;
    if (state.hiddenStatuses.has(p.quality_status)) return false;
    if (state.color !== 'All' && p.color_tag !== state.color) return false;
    if (state.character !== 'All' && !(p.characters||'').toLowerCase().includes(state.character.toLowerCase())) return false;
    if (state.rarity !== 'All' && (p.rarity || 'Unknown') !== state.rarity) return false;
    if (!matchesRecency(p, state.recency)) return false;
    if (state.favOnly) {
      const e = collection[p.pin_id];
      if (!e || !e.favorite) return false;
    }
    return true;
  });

  if (state.sort !== 'default') {
    matchingPins = matchingPins.slice().sort((a,b) => {
      if (state.sort==='price_desc') return b.max_price - a.max_price;
      if (state.sort==='price_asc') return a.min_price - b.min_price;
      if (state.sort==='le_asc') {
        const la = parseInt(a.le_count,10), lb = parseInt(b.le_count,10);
        return (isNaN(la)?Infinity:la) - (isNaN(lb)?Infinity:lb);
      }
      if (state.sort==='rarity') return (RARITY_ORDER[a.rarity]??9) - (RARITY_ORDER[b.rarity]??9);
      if (state.sort==='az') return a.title.localeCompare(b.title);
      if (state.sort==='newest') {
        return getNewInfo(b).sortValue - getNewInfo(a).sortValue;
      }
      return 0;
    });
  } else {
    matchingPins = matchingPins.slice().sort((a,b) => b.count - a.count);
  }

  const totalPages = Math.max(1, Math.ceil(matchingPins.length / state.perPage));
  if (state.page > totalPages) state.page = totalPages;
  if (state.page < 1) state.page = 1;
  const start = (state.page - 1) * state.perPage;
  const pagePins = matchingPins.slice(start, start + state.perPage);

  document.getElementById('pinGrid').innerHTML = pagePins.map(p => cardHtml(p, allPins.indexOf(p))).join('');
  attachCardEvents();

  document.getElementById('resultCount').textContent =
    `${matchingPins.length.toLocaleString()}件中 ${matchingPins.length===0?0:start+1}–${Math.min(start+state.perPage, matchingPins.length)}件を表示 / 全${allPins.length.toLocaleString()}件`;
  document.getElementById('emptyMsg').style.display = matchingPins.length === 0 ? 'block' : 'none';
  renderPageNumbers(state.page, totalPages);
  document.getElementById('pageSummary').textContent = `Page ${state.page} of ${totalPages.toLocaleString()} — ${matchingPins.length.toLocaleString()} Results`;
}

function goToPage(n) {
  state.page = n;
  applyFilters();
  document.querySelector('.filter-bar').scrollIntoView({behavior:'smooth', block:'start'});
}

function renderPageNumbers(current, total) {
  const container = document.getElementById('pageNumbers');
  const items = [];
  if (current > 1) items.push({label:'‹', page:current-1});
  const pages = new Set([1, total]);
  for (let i=current-2; i<=current+2; i++) if (i>=1 && i<=total) pages.add(i);
  const sorted = Array.from(pages).sort((a,b)=>a-b);
  let prev = null;
  for (const p of sorted) {
    if (prev !== null && p - prev > 1) items.push({ellipsis:true});
    items.push({label:p.toLocaleString(), page:p, current:p===current});
    prev = p;
  }
  if (current < total) items.push({label:'›', page:current+1});
  container.innerHTML = items.map(it => it.ellipsis
    ? '<span class="page-num-btn ellipsis">…</span>'
    : `<button class="page-num-btn ${it.current?'current':''}" data-page="${it.page}">${it.label}</button>`
  ).join('');
  container.querySelectorAll('button[data-page]').forEach(btn => {
    btn.addEventListener('click', () => goToPage(parseInt(btn.dataset.page,10)));
  });
}

function refreshCardState(pinId) {
  document.querySelectorAll('.pin-card').forEach(card => {
    const idSpan = card.querySelector('.pin-id-small');
    if (!idSpan || idSpan.dataset.pinId !== pinId) return;
    const entry = collection[pinId] || {};
    const favBtn = card.querySelector('.corner-fav-btn');
    const isoBtn = card.querySelector('.iso-btn');
    const ownBtn = card.querySelector('.own-btn');
    if (favBtn) { favBtn.classList.toggle('active', !!entry.favorite); favBtn.textContent = entry.favorite?'★':'☆'; }
    if (isoBtn) {
      let label = '🔍 探してる';
      if (entry.status==='trade') label += ' <span class="status-tag status-trade">トレード可</span>';
      if (entry.status==='grail') label += ' <span class="status-tag status-grail">お宝</span>';
      isoBtn.innerHTML = label;
      isoBtn.classList.toggle('active', ['iso','trade','grail'].includes(entry.status));
    }
    if (ownBtn) ownBtn.classList.toggle('active', entry.status==='own');
  });
}

function attachCardEvents() {
  document.querySelectorAll('.pin-card').forEach(card => {
    card.addEventListener('click', () => {
      const p = allPins[parseInt(card.dataset.idx,10)];
      openModal(p);
    });
  });
  document.querySelectorAll('.tag[data-filter-type]').forEach(tag => {
    tag.addEventListener('click', (e) => {
      e.stopPropagation();
      jumpToFilter(tag.dataset.filterType, tag.dataset.filterValue);
    });
  });
  document.querySelectorAll('.corner-fav-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const pid = btn.dataset.pinId;
      if (!collection[pid]) collection[pid] = {};
      collection[pid].favorite = !collection[pid].favorite;
      saveCollection(collection);
      refreshCardState(pid);
    });
  });
  document.querySelectorAll('.own-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      setStatus(btn.dataset.pinId, 'own');
    });
  });
  document.querySelectorAll('.iso-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      setStatus(btn.dataset.pinId, 'iso');
    });
  });
  document.querySelectorAll('.iso-caret').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const pid = btn.dataset.pinId;
      const alreadyOpen = sharedDropdown.classList.contains('open') && sharedDropdown.dataset.pid === pid;
      sharedDropdown.classList.remove('open');
      if (alreadyOpen) return;
      const rect = btn.getBoundingClientRect();
      const w = 220;
      let left = Math.max(8, Math.min(rect.right - w, window.innerWidth - w - 8));
      let top = rect.bottom + 6;
      if (top + 220 > window.innerHeight) top = rect.top - 226;
      sharedDropdown.style.left = left + 'px';
      sharedDropdown.style.top = top + 'px';
      sharedDropdown.dataset.pid = pid;
      sharedDropdown.classList.add('open');
    });
  });
  document.querySelectorAll('.pin-id-small').forEach(el => {
    el.addEventListener('click', (e) => {
      e.stopPropagation();
      navigator.clipboard.writeText(el.dataset.pinId).then(() => {
        const orig = el.textContent;
        el.textContent = '✓ Copied!';
        setTimeout(() => { el.textContent = orig; }, 1000);
      }).catch(()=>{});
    });
  });
}

function setStatus(pid, status) {
  if (!collection[pid]) collection[pid] = {};
  collection[pid].status = (collection[pid].status === status) ? '' : status;
  saveCollection(collection);
  refreshCardState(pid);
}

const sharedDropdown = document.getElementById('sharedStatusDropdown');
sharedDropdown.querySelectorAll('.status-option').forEach(opt => {
  opt.addEventListener('click', (e) => {
    e.stopPropagation();
    const pid = sharedDropdown.dataset.pid;
    if (!pid) return;
    if (!collection[pid]) collection[pid] = {};
    collection[pid].status = opt.dataset.status;
    saveCollection(collection);
    refreshCardState(pid);
    sharedDropdown.classList.remove('open');
  });
});
document.addEventListener('click', () => sharedDropdown.classList.remove('open'));
window.addEventListener('scroll', () => sharedDropdown.classList.remove('open'), {passive:true});
sharedDropdown.addEventListener('click', e => e.stopPropagation());

function jumpToFilter(type, value) {
  state.page = 1;
  if (type==='park') { state.park=value; document.getElementById('parkSelect').value=value; }
  else if (type==='collection') { state.collection=value; document.getElementById('collectionSelect').value=value; }
  else if (type==='edition') { state.edition=value; document.getElementById('editionSelect').value=value; }
  else if (type==='status') {
    // ステータスタグをクリックしたら、そのステータスだけを表示するようチェックボックスを切り替える
    const all = ['Official','Likely Official','Unverified','Fantasy Pin','Non-Tradeable','Unofficial','Not a Pin'];
    state.hiddenStatuses = new Set(all.filter(s => s !== value));
    document.querySelectorAll('[data-toggle-status]').forEach(cb => { cb.checked = cb.dataset.toggleStatus === value; });
  }
  else if (type==='le') {
    // LEタグクリックで、そのレアリティ帯を選択する
    const leVal = parseInt(value, 10);
    let r = 'Unknown';
    if (!isNaN(leVal)) {
      if (leVal <= 300) r = 'Legendary';
      else if (leVal <= 1000) r = 'Rare';
      else if (leVal <= 3000) r = 'Uncommon';
      else r = 'Common';
    }
    state.rarity = r;
    document.getElementById('raritySelect').value = r;
  }
  applyFilters();
  document.querySelector('.filter-bar').scrollIntoView({behavior:'smooth', block:'start'});
}

function reportPin() {
  if (!currentModalPin) return;
  const p = currentModalPin;
  const subject = encodeURIComponent(`ピン情報の報告: ${p.pin_id}`);
  const body = encodeURIComponent(
    `以下のピンについて、違和感・誤り・不適切な内容の可能性を報告します。\n\n` +
    `Pin ID: ${p.pin_id}\n` +
    `タイトル: ${p.title}\n` +
    `現在のステータス: ${p.quality_status}\n` +
    `LE数: ${p.le_count || '不明'}\n` +
    `URL: ${p.url}\n\n` +
    `【報告理由(自由に記入してください)】\n\n`
  );
  window.location.href = `mailto:${REPORT_EMAIL}?subject=${subject}&body=${body}`;
}

let currentModalPin = null;

function openModal(p) {
  currentModalPin = p;
  document.getElementById('modalImg').src = p.image_url;
  let officialHtml = '';
  if (p.official) {
    officialHtml = `<div style="margin-top:16px;padding:14px;background:rgba(232,169,201,0.15);border-radius:10px;border:1px solid rgba(232,169,201,0.4);">
      <div style="font-weight:700;font-size:13px;color:#8a2a5c;margin-bottom:8px;">✓ 公式シリーズ情報</div>
      <div class="detail-row"><span>シリーズ名</span><span>${esc(p.official.series_name)}</span></div>
      <div class="detail-row"><span>発売元</span><span>${esc(p.official.origin)}</span></div>
      <div class="detail-row"><span>エディション種別</span><span>${esc(p.official.edition_type)}</span></div>
      ${p.official.edition_count ? `<div class="detail-row"><span>限定数</span><span>${p.official.edition_count}</span></div>` : ''}
      ${p.official.original_price ? `<div class="detail-row"><span>発売時価格</span><span>$${p.official.original_price}</span></div>` : ''}
    </div>`;
  }
  document.getElementById('modalBody').innerHTML = `
    <div class="mono" style="font-size:12px;color:var(--gold);font-weight:700;margin-bottom:6px;">${p.pin_id}</div>
    <h2>${esc(p.title)}</h2>
    <div class="detail-row"><span>パーク</span><span>${p.park}</span></div>
    <div class="detail-row"><span>エディション種別</span><span>${p.edition_type||'—'}</span></div>
    <div class="detail-row"><span>価格帯</span><span>$${p.min_price.toFixed(2)} – $${p.max_price.toFixed(2)}</span></div>
    <div class="detail-row"><span>平均価格</span><span>$${p.avg_price.toFixed(2)}</span></div>
    <div class="detail-row"><span>LE数</span><span>${p.le_count||'—'}</span></div>
    <div class="detail-row"><span>キャラクター</span><span>${esc(p.characters)||'—'}</span></div>
    <div class="detail-row"><span>シリーズ</span><span>${esc(p.series)||'—'}</span></div>
    <div class="detail-row"><span>出品件数</span><span>${p.count}</span></div>
    ${officialHtml}
    <a class="modal-link" href="${p.url}" target="_blank">eBayで見る →</a>
    <button class="modal-link report-btn" onclick="reportPin()">🚩 このピン情報を報告する</button>
  `;
  document.getElementById('overlay').classList.add('open');
}
function closeModal() { document.getElementById('overlay').classList.remove('open'); }
document.getElementById('overlay').addEventListener('click', e => { if (e.target.id==='overlay') closeModal(); });

document.getElementById('search').addEventListener('input', e => { state.query=e.target.value.toLowerCase(); state.page=1; applyFilters(); });
document.getElementById('parkSelect').addEventListener('change', e => { state.park=e.target.value; state.page=1; applyFilters(); });
document.getElementById('collectionSelect').addEventListener('change', e => { state.collection=e.target.value; state.page=1; applyFilters(); });
document.getElementById('editionSelect').addEventListener('change', e => { state.edition=e.target.value; state.page=1; applyFilters(); });
document.getElementById('seriesSelect').addEventListener('change', e => { state.series=e.target.value; state.page=1; applyFilters(); });
document.getElementById('characterSelect').addEventListener('change', e => { state.character=e.target.value; state.page=1; applyFilters(); });
document.getElementById('raritySelect').addEventListener('change', e => { state.rarity=e.target.value; state.page=1; applyFilters(); });
document.getElementById('recencySelect').addEventListener('change', e => { state.recency=e.target.value; state.page=1; applyFilters(); });
document.getElementById('sortSelect').addEventListener('change', e => { state.sort=e.target.value; state.page=1; applyFilters(); });
document.getElementById('perPage').addEventListener('change', e => { state.perPage=parseInt(e.target.value,10); state.page=1; applyFilters(); });
document.getElementById('favOnlyToggle').addEventListener('change', e => { state.favOnly=e.target.checked; state.page=1; applyFilters(); });

// 「初期設定に戻す」ボタン: 全てのフィルターを初期状態(公式2種類のみ表示)にリセットする
document.getElementById('resetFiltersBtn').addEventListener('click', () => {
  state.query = ''; document.getElementById('search').value = '';
  state.park = 'All'; document.getElementById('parkSelect').value = 'All';
  state.collection = 'All'; document.getElementById('collectionSelect').value = 'All';
  state.edition = 'All'; document.getElementById('editionSelect').value = 'All';
  state.series = 'All'; document.getElementById('seriesSelect').value = 'All';
  state.color = 'All'; document.getElementById('colorSelect').value = 'All';
  state.character = 'All'; document.getElementById('characterSelect').value = 'All';
  state.rarity = 'All'; document.getElementById('raritySelect').value = 'All';
  state.recency = 'all'; document.getElementById('recencySelect').value = 'all';
  state.favOnly = false; document.getElementById('favOnlyToggle').checked = false;
  state.sort = 'default'; document.getElementById('sortSelect').value = 'default';
  document.body.style.background = '';
  document.documentElement.style.setProperty('--gold', '#E8A9C9');

  const trusted = ['Official', 'Likely Official'];
  const all = ['Official', 'Likely Official', 'Unverified', 'Fantasy Pin', 'Non-Tradeable', 'Unofficial', 'Not a Pin'];
  state.hiddenStatuses = new Set(all.filter(s => !trusted.includes(s)));
  document.querySelectorAll('[data-toggle-status]').forEach(cb => {
    cb.checked = trusted.includes(cb.dataset.toggleStatus);
  });
  state.page = 1;
  applyFilters();
});
document.getElementById('refreshBtn').addEventListener('click', () => {
  // キャッシュを無視して強制的に最新版を再取得する
  window.location.reload(true);
});

document.getElementById('jumpBtn').addEventListener('click', () => {
  const v = parseInt(document.getElementById('jumpPage').value,10);
  if (!isNaN(v) && v>=1) goToPage(v);
});
document.getElementById('jumpPage').addEventListener('keydown', e => { if (e.key==='Enter') document.getElementById('jumpBtn').click(); });
document.querySelectorAll('[data-toggle-status]').forEach(cb => {
  cb.addEventListener('change', e => {
    const s = e.target.dataset.toggleStatus;
    if (e.target.checked) state.hiddenStatuses.delete(s); else state.hiddenStatuses.add(s);
    state.page=1; applyFilters();
  });
});
document.getElementById('colorSelect').addEventListener('change', e => {
  state.color = e.target.value; state.page=1;
  const theme = COLOR_THEMES[state.color];
  if (theme) { document.body.style.background = theme.bg; document.documentElement.style.setProperty('--gold', theme.accent); }
  else { document.body.style.background=''; document.documentElement.style.setProperty('--gold', '#E8A9C9'); }
  applyFilters();
});

// データ読み込み
fetch('pins_data.json')
  .then(r => r.json())
  .then(data => {
    allPins = data;
    document.getElementById('loadingMsg').style.display = 'none';
    const totalListings = allPins.reduce((s,p)=>s+p.count,0);
    const parksCovered = new Set(allPins.map(p=>p.park)).size;
    document.getElementById('statStrip').innerHTML = `
      <div class="stat"><div class="num mono">${allPins.length.toLocaleString()}</div><div class="label">Unique Pins</div></div>
      <div class="stat"><div class="num mono">${totalListings.toLocaleString()}</div><div class="label">Listings Tracked</div></div>
      <div class="stat"><div class="num mono">${parksCovered}</div><div class="label">Parks / Events</div></div>
    `;
    applyFilters();
  })
  .catch(err => {
    document.getElementById('loadingMsg').textContent = 'データの読み込みに失敗しました。しばらくしてから再度お試しください。';
    console.error(err);
  });
</script>
</body>
</html>
"""

html_doc = (html_doc
    .replace("__PARK_OPTIONS__", park_options)
    .replace("__COLLECTION_OPTIONS__", collection_options)
    .replace("__EDITION_OPTIONS__", edition_options)
    .replace("__STATUS_OPTIONS__", status_options)
    .replace("__SERIES_OPTIONS__", series_options)
    .replace("__COLOR_OPTIONS__", color_options)
    .replace("__CHARACTER_OPTIONS__", character_options)
    .replace("__RARITY_OPTIONS__", rarity_options)
    .replace("__RECENCY_OPTIONS__", recency_options)
    .replace("__REPORT_EMAIL__", REPORT_EMAIL)
)

with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_doc)

shutil.copy(os.path.join(DATA_DIR, "pins_data.json"), os.path.join(DOCS_DIR, "pins_data.json"))

# ヘッダー用のコラージュ写真をコピー(assets/header_photos → docs/images)
ASSETS_DIR = os.path.join(SCRIPT_DIR, "..", "assets", "header_photos")
IMAGES_OUT_DIR = os.path.join(DOCS_DIR, "images")
os.makedirs(IMAGES_OUT_DIR, exist_ok=True)
if os.path.isdir(ASSETS_DIR):
    for fname in os.listdir(ASSETS_DIR):
        shutil.copy(os.path.join(ASSETS_DIR, fname), os.path.join(IMAGES_OUT_DIR, fname))
    print(f"[OK] ヘッダー写真 {len(os.listdir(ASSETS_DIR))}枚を docs/images/ にコピーしました")

print(f"[OK] 軽量版サイト生成完了: {total}件")
print(f"[OK] index.html サイズ: {os.path.getsize(os.path.join(DOCS_DIR, 'index.html')) / 1024:.1f} KB")
print(f"[OK] pins_data.json サイズ: {os.path.getsize(os.path.join(DOCS_DIR, 'pins_data.json')) / 1024 / 1024:.2f} MB")

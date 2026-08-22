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

PARKS = ["All", "D23 Expo", "Walt Disney World", "Disneyland Resort", "Disney Parks (Shared/Unspecified)",
         "Disney Store / Online Exclusive", "Tokyo Disneyland", "Disneyland Paris",
         "Hong Kong Disneyland", "Shanghai Disneyland", "Convention Exclusive (SDCC等)", "Other / Unknown"]
COLLECTIONS = ["All", "Mickey & Friends", "Princesses", "Star Wars", "Marvel", "Pixar", "Villains",
               "Attractions", "Winnie the Pooh & Friends", "Alice in Wonderland", "Muppets",
               "Peter Pan / Neverland", "Lilo & Stitch", "The Lion King", "Nightmare Before Christmas",
               "Aristocats", "Dumbo", "Hercules", "Big Hero 6", "Zootopia", "Kingdom Hearts", "Tarzan",
               "Classic Disney Animation", "Modern Disney Animation", "Other"]
EDITION_TYPES = ["All", "Limited Edition (LE)", "Limited Release (LR)", "Open Edition (OE)",
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


def opts(values):
    return "".join(f'<option value="{v}">{v}</option>' for v in values)


park_options = opts(PARKS)
collection_options = opts(COLLECTIONS)
edition_options = opts(EDITION_TYPES)
status_options = opts(STATUS_LEVELS)
series_options = opts(SERIES_KEYWORDS)
color_options = opts(COLOR_TAGS)
character_options = '<option value="All">All</option>' + "".join(
    f'<option value="{c}">{c}</option>' for c in TOP_CHARACTERS
)

html_doc = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pin Registry — Disney Collectible Pin Database</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --navy: #7B6FC4; --navy-deep: #5C4FA8; --gold: #E8A9C9; --gold-light: #F3C9DE;
    --red: #E0687A; --teal: #5CC7B8; --cream: #FFF8FB; --cream-dim: #FBEFF5;
    --ink: #4A3F5C; --ink-soft: #8B7F9E; --line: #F0DCE8;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body { margin: 0; background: var(--cream); color: var(--ink); font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased; }
  h1, h2, .display { font-family: 'Baloo 2', sans-serif; letter-spacing: -0.01em; }
  .mono { font-family: 'IBM Plex Mono', monospace; }
  a { color: inherit; text-decoration: none; }

  header { background: linear-gradient(180deg, var(--navy) 0%, var(--navy-deep) 100%); color: var(--cream); padding: 28px 24px 60px; position: relative; overflow: hidden; }
  .header-inner { max-width: 1100px; margin: 0 auto; position: relative; z-index: 1; }
  .brand-row { display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 34px; }
  .brand { font-size: 22px; font-weight: 700; display: flex; align-items: center; gap: 10px; }
  .brand .badge-dot { width: 12px; height: 12px; border-radius: 50%; background: var(--gold); }
  .brand-tag { font-size: 12px; color: rgba(255,255,255,0.6); letter-spacing: 0.08em; text-transform: uppercase; }
  .hero-title { font-size: clamp(28px, 5vw, 48px); font-weight: 700; line-height: 1.1; max-width: 720px; margin: 0 0 14px; }
  .hero-sub { font-size: 15px; color: rgba(255,255,255,0.75); max-width: 560px; margin: 0 0 28px; line-height: 1.6; }
  #search { width: 100%; max-width: 620px; padding: 14px 20px; font-size: 16px; border-radius: 999px; border: none; background: white; color: var(--ink); }
  .stat-strip { display: flex; gap: 26px; margin-top: 26px; flex-wrap: wrap; }
  .stat .num { font-family: 'Baloo 2', sans-serif; font-size: 24px; color: var(--gold-light); font-weight: 700; }
  .stat .label { font-size: 10.5px; letter-spacing: 0.06em; text-transform: uppercase; color: rgba(255,255,255,0.55); }

  .filter-bar { max-width: 1100px; margin: -30px auto 0; padding: 0 24px; position: relative; z-index: 2; }
  .chip-row { background: white; border-radius: 16px; padding: 16px 18px; box-shadow: 0 10px 26px rgba(90,26,110,0.12); display: flex; gap: 18px; flex-wrap: wrap; align-items: center; }
  .chip-group { display: flex; flex-direction: column; gap: 6px; }
  .chip-group-label { font-size: 10px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--ink-soft); font-weight: 700; }
  .filter-select, .le-input { padding: 7px 10px; border-radius: 8px; border: 1px solid var(--line); background: white; font-size: 13px; min-width: 140px; }
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

  .pin-card { background: #fff; border-radius: 18px; box-shadow: 0 3px 10px rgba(123,111,196,0.10); cursor: pointer; transition: transform 0.15s, box-shadow 0.15s; position: relative; border: 1px solid var(--line); display: flex; flex-direction: column; }
  .pin-card:hover { transform: translateY(-4px) scale(1.01); box-shadow: 0 12px 26px rgba(123,111,196,0.20); }
  .hang-hole { position: absolute; top: 6px; left: 50%; transform: translateX(-50%); width: 36px; height: 22px; z-index: 2; }
  .hh-face { position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 24px; height: 14px; border-radius: 50%; background: var(--cream); border: 1px solid #e2dcc8; }
  .hh-ear { position: absolute; top: 0; width: 13px; height: 13px; border-radius: 50%; background: var(--cream); border: 1px solid #e2dcc8; }
  .hh-ear-l { left: 2px; } .hh-ear-r { right: 2px; }
  .rarity-badge { position: absolute; top: 10px; left: 10px; z-index: 2; font-size: 10px; font-weight: 700; padding: 4px 10px; border-radius: 999px; }
  .rarity-legendary { background: #f0c419; color: #5a4300; }
  .rarity-rare { background: #c9a7f0; color: #3a1a5c; }
  .rarity-uncommon { background: #8fd4c1; color: #0b3d31; }
  .rarity-common { background: #d8d2c2; color: #59523e; }
  .rarity-unknown { background: #e2e2e2; color: #888; }
  .corner-fav-btn { position: absolute; top: 8px; right: 8px; z-index: 2; width: 26px; height: 26px; border-radius: 50%; border: 1px solid var(--line); background: rgba(255,255,255,0.9); font-size: 14px; cursor: pointer; }
  .corner-fav-btn.active { background: #fff3d6; border-color: var(--gold); color: #b8860b; }
  .fantasy-banner { position: absolute; top: 32px; left: 0; right: 0; z-index: 3; background: linear-gradient(120deg, #a94fd6, #7b2fb0); color: white; text-align: center; font-size: 10px; font-weight: 800; padding: 5px 4px; }
  .pin-img-frame { aspect-ratio: 1/1; background: #f4f1e8; display: flex; align-items: center; justify-content: center; padding: 20px; flex-shrink: 0; }
  .pin-img-frame img { max-width: 100%; max-height: 100%; object-fit: contain; }
  .pin-body { padding: 14px 14px 0; flex: 1 1 auto; }
  .pin-title-link { font-size: 14px; font-weight: 700; line-height: 1.35; color: #7b2fb0; height: 38px; overflow: hidden; margin-bottom: 10px; }
  .action-row { display: flex; gap: 8px; margin-bottom: 10px; }
  .action-btn { border: 1px solid var(--line); background: white; border-radius: 8px; padding: 7px 10px; font-size: 12px; font-weight: 700; color: var(--ink-soft); cursor: pointer; }
  .own-btn { flex: 1; }
  .own-btn.active { background: rgba(92,199,184,0.18); border-color: var(--teal); color: #167367; }
  .iso-btn-group { flex: 1; display: flex; position: relative; }
  .iso-btn { flex: 1; border-radius: 8px 0 0 8px; border-right: none; }
  .iso-btn.active { background: rgba(224,104,122,0.14); border-color: var(--red); color: var(--red); }
  .iso-caret { border: 1px solid var(--line); border-radius: 0 8px 8px 0; background: white; padding: 7px 9px; font-size: 12px; cursor: pointer; }
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
  .series-box { background: var(--cream-dim); border-radius: 8px; padding: 8px 10px; margin-bottom: 10px; }
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
  .list-controls-bar { display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 16px; margin: 20px 0 8px; padding: 10px 18px; background: white; border-radius: 10px; border: 1px solid var(--line); font-size: 12.5px; }
  .page-numbers { display: flex; flex-wrap: wrap; justify-content: center; gap: 5px; }
  .page-num-btn { min-width: 32px; height: 32px; border-radius: 6px; border: 1px solid var(--line); background: white; font-size: 12.5px; cursor: pointer; }
  .page-num-btn.current { background: var(--navy); color: white; border-color: var(--navy); font-weight: 700; }
  .page-num-btn.ellipsis { border: none; background: none; cursor: default; color: var(--ink-soft); }
  .page-summary { font-size: 12px; color: var(--ink-soft); text-align: center; margin-bottom: 40px; }
  .jump-control input { width: 70px; padding: 6px; border-radius: 6px; border: 1px solid var(--line); }
  .jump-control button { padding: 6px 12px; border-radius: 6px; border: none; background: var(--navy); color: white; cursor: pointer; }
  .overlay { display: none; position: fixed; inset: 0; background: rgba(90,26,110,0.5); z-index: 50; align-items: flex-start; justify-content: center; padding: 40px 16px; overflow-y: auto; }
  .overlay.open { display: flex; }
  .modal { background: var(--cream); max-width: 600px; width: 100%; border-radius: 16px; overflow: hidden; position: relative; }
  .modal-top { background: #f4f1e8; padding: 30px; display: flex; justify-content: center; }
  .modal-top img { max-width: 240px; max-height: 240px; object-fit: contain; }
  .modal-body { padding: 24px 28px 28px; }
  .modal-close { position: absolute; top: 14px; right: 14px; width: 32px; height: 32px; border-radius: 50%; background: rgba(0,0,0,0.12); border: none; cursor: pointer; }
  .detail-row { display: flex; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid var(--line); font-size: 13.5px; }
  .modal-link { display: block; margin-top: 18px; text-align: center; background: var(--navy); color: white; padding: 13px; border-radius: 10px; font-weight: 700; }
  footer { text-align: center; padding: 28px; color: var(--ink-soft); font-size: 11.5px; }
</style>
</head>
<body>

<header>
  <div class="header-inner">
    <div class="brand-row">
      <div class="brand"><span class="badge-dot"></span>Pin Registry</div>
      <div class="brand-tag">Collector's Database</div>
    </div>
    <h1 class="hero-title">すべてのディズニーピンを、ひとつの場所で。</h1>
    <p class="hero-sub">相場・限定数・パーク・シリーズから探せる、ディズニーコレクター向けピンデータベース。</p>
    <input type="text" id="search" placeholder="ピン名・キャラクター・シリーズ・Pin ID で検索…">
    <div class="stat-strip" id="statStrip"></div>
  </div>
</header>

<div class="filter-bar">
  <div class="chip-row">
    <div class="chip-group"><div class="chip-group-label">Park</div><select class="filter-select" id="parkSelect">__PARK_OPTIONS__</select></div>
    <div class="chip-group"><div class="chip-group-label">Collection</div><select class="filter-select" id="collectionSelect">__COLLECTION_OPTIONS__</select></div>
    <div class="chip-group"><div class="chip-group-label">Edition Type</div><select class="filter-select" id="editionSelect">__EDITION_OPTIONS__</select></div>
    <div class="chip-group"><div class="chip-group-label">Status</div><select class="filter-select" id="statusSelect">__STATUS_OPTIONS__</select></div>
    <div class="chip-group"><div class="chip-group-label">Series</div><select class="filter-select" id="seriesSelect">__SERIES_OPTIONS__</select></div>
    <div class="chip-group"><div class="chip-group-label">Color</div><select class="filter-select" id="colorSelect">__COLOR_OPTIONS__</select></div>
    <div class="chip-group"><div class="chip-group-label">Character</div><select class="filter-select" id="characterSelect">__CHARACTER_OPTIONS__</select></div>
    <div class="chip-group"><div class="chip-group-label">LE Number (以下)</div><input type="number" id="leMax" placeholder="例: 2500" class="le-input"></div>
  </div>
  <div class="status-toggle-row">
    <div class="status-toggle-label">表示するステータス:</div>
    <label class="status-toggle"><input type="checkbox" data-toggle-status="Official" checked> Official</label>
    <label class="status-toggle"><input type="checkbox" data-toggle-status="Likely Official" checked> Likely Official</label>
    <label class="status-toggle"><input type="checkbox" data-toggle-status="Unverified" checked> Unverified</label>
    <label class="status-toggle"><input type="checkbox" data-toggle-status="Fantasy Pin" checked> Fantasy Pin</label>
    <label class="status-toggle"><input type="checkbox" data-toggle-status="Non-Tradeable" checked> Non-Tradeable</label>
    <label class="status-toggle"><input type="checkbox" data-toggle-status="Unofficial"> Unofficial</label>
    <label class="status-toggle"><input type="checkbox" data-toggle-status="Not a Pin"> Not a Pin</label>
    <label class="status-toggle"><input type="checkbox" id="favOnlyToggle"> ★ お気に入りのみ表示</label>
  </div>
</div>

<main>
  <div class="section-head">
    <div class="section-title">Trending — 出品数が多いピン</div>
    <div class="section-count" id="resultCount"></div>
  </div>
  <div class="sort-bar">
    <label for="sortSelect">Sort:</label>
    <select id="sortSelect">
      <option value="default" selected>Default(出品数順)</option>
      <option value="price_desc">価格が高い順</option>
      <option value="price_asc">価格が安い順</option>
      <option value="le_asc">LE数が少ない順(レア順)</option>
      <option value="rarity">レアリティ順</option>
      <option value="az">タイトル A-Z</option>
    </select>
  </div>
  <div id="loadingMsg" class="loading-msg">読み込み中…</div>
  <div class="grid" id="pinGrid"></div>
  <div class="empty-msg" id="emptyMsg">条件に一致するピンが見つかりませんでした。</div>
  <div class="list-controls-bar">
    <div class="chip-group"><div class="chip-group-label">表示件数</div>
      <select class="filter-select" id="perPage">
        <option value="20" selected>20件</option>
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

<footer>Pin Registry — データ出典: eBay Browse API（米国市場） / 表示価格は出品時点の参考値です / 1時間ごと自動更新</footer>

<div class="overlay" id="overlay">
  <div class="modal">
    <button class="modal-close" onclick="closeModal()">✕</button>
    <div class="modal-top"><img id="modalImg" src="" alt=""></div>
    <div class="modal-body" id="modalBody"></div>
  </div>
</div>

<div class="status-dropdown" id="sharedStatusDropdown">
  <div class="status-option status-own" data-status="own">You already <b>OWN</b></div>
  <div class="status-option status-iso" data-status="iso">You're In Search Of <b>(ISO)</b></div>
  <div class="status-option status-trade" data-status="trade">You're willing to <b>TRADE</b></div>
  <div class="status-option status-grail" data-status="grail">Hard-to-find <b>GRAILS</b></div>
  <div class="status-option status-clear" data-status="">ステータスを解除</div>
</div>

<script>
let allPins = [];
const state = { query:'', park:'All', collection:'All', edition:'All', series:'All', status:'All',
                 color:'All', character:'All', favOnly:false, leMax:null, page:1, perPage:20,
                 sort:'default', hiddenStatuses:new Set(['Unofficial','Not a Pin']) };
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
  const officialBadge = p.official ? '<span class="tag official">✓ 公式情報あり</span>' : '';
  const fantasyBanner = status === 'Fantasy Pin' ? '<div class="fantasy-banner">✦ FANTASY PIN(非公式ファンメイド)✦</div>' : '';
  const seriesDisplay = (p.series || '').split(';')[0].trim();
  const entry = collection[p.pin_id] || {};

  return `
    <div class="pin-card" data-idx="${idx}">
      <div class="hang-hole"><span class="hh-ear hh-ear-l"></span><span class="hh-ear hh-ear-r"></span><span class="hh-face"></span></div>
      <div class="rarity-badge rarity-${rarityClass}">${rarity}</div>
      <button class="corner-fav-btn ${entry.favorite ? 'active' : ''}" data-pin-id="${p.pin_id}" data-action="favorite">${entry.favorite ? '★' : '☆'}</button>
      ${fantasyBanner}
      <div class="pin-img-frame"><img src="${esc(p.image_url)}" loading="lazy" onerror="this.style.display='none'"></div>
      <div class="pin-body">
        <div class="pin-title-link">${esc(p.title)}</div>
        <div class="action-row">
          <div class="iso-btn-group">
            <button class="iso-btn action-btn ${(entry.status==='iso'||entry.status==='trade'||entry.status==='grail')?'active':''}" data-pin-id="${p.pin_id}" data-action="iso">🔍 ISO${entry.status==='trade'?' <span class="status-tag status-trade">TRADE</span>':''}${entry.status==='grail'?' <span class="status-tag status-grail">GRAIL</span>':''}</button>
            <button class="iso-caret" data-pin-id="${p.pin_id}">▾</button>
          </div>
          <button class="own-btn action-btn ${entry.status==='own'?'active':''}" data-pin-id="${p.pin_id}" data-action="own">✓ OWN</button>
        </div>
        <div class="series-box"><div class="series-label">SERIES</div><div class="series-value">${esc(seriesDisplay) || '—'}</div></div>
        <div class="pin-meta">
          <span class="tag status-tag-${statusClass}" data-filter-type="status" data-filter-value="${status}">${status}</span>
          <span class="tag park" data-filter-type="park" data-filter-value="${p.park}">${p.park}</span>
          ${le ? `<span class="tag le" data-filter-type="le" data-filter-value="${le}">LE ${le}</span>` : ''}
          <span class="tag" data-filter-type="edition" data-filter-value="${editionType}">${editionType}</span>
          <span class="tag" data-filter-type="collection" data-filter-value="${collectionVal}">${collectionVal}</span>
          ${officialBadge}
        </div>
      </div>
      <div class="pin-price">$${p.min_price.toFixed(2)} – $${p.max_price.toFixed(2)}</div>
      <div class="release-bar">
        <span class="pin-id-small" data-pin-id="${p.pin_id}">${p.pin_id}</span>
        <span>Released: ${releaseDate || 'Unknown'}</span>
      </div>
    </div>`;
}

const RARITY_ORDER = { 'Legendary':0,'Rare':1,'Uncommon':2,'Common':3,'Unknown':4 };
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

function applyFilters() {
  matchingPins = allPins.filter(p => {
    const t = (p.title + ' ' + p.pin_id).toLowerCase();
    if (state.query && !t.includes(state.query)) return false;
    if (state.park !== 'All' && p.park !== state.park) return false;
    if (state.collection !== 'All' && p.collection !== state.collection) return false;
    if (state.edition !== 'All' && p.edition_type !== state.edition) return false;
    if (state.series !== 'All' && !(p.series||'').includes(state.series)) return false;
    if (state.status !== 'All' && p.quality_status !== state.status) return false;
    if (state.hiddenStatuses.has(p.quality_status)) return false;
    if (state.color !== 'All' && p.color_tag !== state.color) return false;
    if (state.character !== 'All' && !(p.characters||'').toLowerCase().includes(state.character.toLowerCase())) return false;
    if (state.favOnly) {
      const e = collection[p.pin_id];
      if (!e || !e.favorite) return false;
    }
    if (state.leMax !== null && !isNaN(state.leMax)) {
      const le = parseInt(p.le_count, 10);
      if (isNaN(le) || le > state.leMax) return false;
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
      let label = '🔍 ISO';
      if (entry.status==='trade') label += ' <span class="status-tag status-trade">TRADE</span>';
      if (entry.status==='grail') label += ' <span class="status-tag status-grail">GRAIL</span>';
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
  else if (type==='status') { state.status=value; document.getElementById('statusSelect').value=value; }
  else if (type==='le') { state.leMax=parseInt(value,10); document.getElementById('leMax').value=value; }
  applyFilters();
  document.querySelector('.filter-bar').scrollIntoView({behavior:'smooth', block:'start'});
}

function openModal(p) {
  document.getElementById('modalImg').src = p.image_url;
  let officialHtml = '';
  if (p.official) {
    officialHtml = `<div style="margin-top:16px;padding:14px;background:rgba(232,169,201,0.15);border-radius:10px;border:1px solid rgba(232,169,201,0.4);">
      <div style="font-weight:700;font-size:13px;color:#8a2a5c;margin-bottom:8px;">✓ 公式シリーズ情報</div>
      <div class="detail-row"><span>Series</span><span>${esc(p.official.series_name)}</span></div>
      <div class="detail-row"><span>Origin</span><span>${esc(p.official.origin)}</span></div>
      <div class="detail-row"><span>Edition Type</span><span>${esc(p.official.edition_type)}</span></div>
      ${p.official.edition_count ? `<div class="detail-row"><span>Edition Count</span><span>${p.official.edition_count}</span></div>` : ''}
      ${p.official.original_price ? `<div class="detail-row"><span>Original Price</span><span>$${p.official.original_price}</span></div>` : ''}
    </div>`;
  }
  document.getElementById('modalBody').innerHTML = `
    <div class="mono" style="font-size:12px;color:var(--gold);font-weight:700;margin-bottom:6px;">${p.pin_id}</div>
    <h2>${esc(p.title)}</h2>
    <div class="detail-row"><span>Park</span><span>${p.park}</span></div>
    <div class="detail-row"><span>Edition Type</span><span>${p.edition_type||'—'}</span></div>
    <div class="detail-row"><span>Price Range</span><span>$${p.min_price.toFixed(2)} – $${p.max_price.toFixed(2)}</span></div>
    <div class="detail-row"><span>Average Price</span><span>$${p.avg_price.toFixed(2)}</span></div>
    <div class="detail-row"><span>LE Count</span><span>${p.le_count||'—'}</span></div>
    <div class="detail-row"><span>Characters</span><span>${esc(p.characters)||'—'}</span></div>
    <div class="detail-row"><span>Series</span><span>${esc(p.series)||'—'}</span></div>
    <div class="detail-row"><span>Listings Seen</span><span>${p.count}</span></div>
    ${officialHtml}
    <a class="modal-link" href="${p.url}" target="_blank">eBayで見る →</a>
  `;
  document.getElementById('overlay').classList.add('open');
}
function closeModal() { document.getElementById('overlay').classList.remove('open'); }
document.getElementById('overlay').addEventListener('click', e => { if (e.target.id==='overlay') closeModal(); });

document.getElementById('search').addEventListener('input', e => { state.query=e.target.value.toLowerCase(); state.page=1; applyFilters(); });
document.getElementById('parkSelect').addEventListener('change', e => { state.park=e.target.value; state.page=1; applyFilters(); });
document.getElementById('collectionSelect').addEventListener('change', e => { state.collection=e.target.value; state.page=1; applyFilters(); });
document.getElementById('editionSelect').addEventListener('change', e => { state.edition=e.target.value; state.page=1; applyFilters(); });
document.getElementById('statusSelect').addEventListener('change', e => { state.status=e.target.value; state.page=1; applyFilters(); });
document.getElementById('seriesSelect').addEventListener('change', e => { state.series=e.target.value; state.page=1; applyFilters(); });
document.getElementById('characterSelect').addEventListener('change', e => { state.character=e.target.value; state.page=1; applyFilters(); });
document.getElementById('leMax').addEventListener('input', e => { state.leMax = e.target.value===''?null:parseInt(e.target.value,10); state.page=1; applyFilters(); });
document.getElementById('sortSelect').addEventListener('change', e => { state.sort=e.target.value; state.page=1; applyFilters(); });
document.getElementById('perPage').addEventListener('change', e => { state.perPage=parseInt(e.target.value,10); state.page=1; applyFilters(); });
document.getElementById('favOnlyToggle').addEventListener('change', e => { state.favOnly=e.target.checked; state.page=1; applyFilters(); });
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
)

with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_doc)

shutil.copy(os.path.join(DATA_DIR, "pins_data.json"), os.path.join(DOCS_DIR, "pins_data.json"))

print(f"[OK] 軽量版サイト生成完了: {total}件")
print(f"[OK] index.html サイズ: {os.path.getsize(os.path.join(DOCS_DIR, 'index.html')) / 1024:.1f} KB")
print(f"[OK] pins_data.json サイズ: {os.path.getsize(os.path.join(DOCS_DIR, 'pins_data.json')) / 1024 / 1024:.2f} MB")

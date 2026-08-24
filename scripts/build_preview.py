"""
build_static_site.py でデプロイ用ファイル(docs/index.html, docs/pins_data.json)を
生成した後に実行する。プレビュー用の自己完結HTML(site_preview.html)を作る。

画像・データを全部埋め込むため、このチャット上でそのままプレビューできる。
GitHubには反映されない、確認専用のファイル。
"""

import base64
import os

REPO_DIR = os.path.dirname(os.path.abspath(__file__)) + "/.."
DOCS_DIR = os.path.join(REPO_DIR, "docs")
IMG_DIR = os.path.join(REPO_DIR, "assets", "header_photos")
OUTPUT_FILE = os.path.join(REPO_DIR, "..", "site_preview.html")

with open(os.path.join(DOCS_DIR, "index.html"), encoding="utf-8") as f:
    html = f.read()

with open(os.path.join(DOCS_DIR, "pins_data.json"), encoding="utf-8") as f:
    pins_json_str = f.read()

# 画像をbase64データURIとして埋め込む
for fname in sorted(os.listdir(IMG_DIR)):
    with open(os.path.join(IMG_DIR, fname), "rb") as imgf:
        b64 = base64.b64encode(imgf.read()).decode("ascii")
    html = html.replace(f"images/{fname}", f"data:image/jpeg;base64,{b64}")

# プレビュー版限定: ページ間リンクは実際のフォルダ構造がないと機能しないため、説明表示に差し替える
html = html.replace(
    '<a href="database/" class="refresh-btn" style="text-decoration:none;">📚 累積データベースを見る</a>',
    '<a href="#" onclick="alert(\'このリンクは実際にGitHub Pagesへ公開した後、正しく動作します(プレビューでは無効です)\'); return false;" class="refresh-btn" style="text-decoration:none;">📚 累積データベースを見る</a>'
)

fetch_block = """// データ読み込み
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
  });"""

embed_block = """// データ読み込み(プレビュー用: 埋め込み済みデータを直接使用)
allPins = JSON.parse(document.getElementById('embedded-pin-data').textContent);
document.getElementById('loadingMsg').style.display = 'none';
{
  const totalListings = allPins.reduce((s,p)=>s+p.count,0);
  const parksCovered = new Set(allPins.map(p=>p.park)).size;
  document.getElementById('statStrip').innerHTML = `
    <div class="stat"><div class="num mono">${allPins.length.toLocaleString()}</div><div class="label">Unique Pins</div></div>
    <div class="stat"><div class="num mono">${totalListings.toLocaleString()}</div><div class="label">Listings Tracked</div></div>
    <div class="stat"><div class="num mono">${parksCovered}</div><div class="label">Parks / Events</div></div>
  `;
  applyFilters();
}"""

if fetch_block not in html:
    raise RuntimeError("fetchブロックが見つかりませんでした。build_static_site.pyの構造が変わった可能性があります。")

html = html.replace(fetch_block, embed_block)

# データ埋め込み用scriptタグは、それを読み込むメインscriptタグより
# 「前」に置く必要がある(HTMLは上から順に実行されるため)
embed_script = f'<script id="embedded-pin-data" type="application/json">{pins_json_str}</script>\n<script>'
if html.count("<script>") < 1:
    raise RuntimeError("メインの<script>タグが見つかりませんでした。")
html = html.replace("<script>", embed_script, 1)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print(f"[OK] プレビュー版生成完了: {os.path.getsize(OUTPUT_FILE) / 1024 / 1024:.2f} MB")

# Pin Registry — Disney Collectible Pin Database

eBayのデータを1時間ごとに自動取得し、精査・分類した上でサイトを自動更新するプロジェクトです。

## 仕組み

```
GitHub Actions (1時間ごと)
    → scripts/fetch_and_process.py (eBay取得・精査)
    → data/pins_data.json (データ保存)
    → scripts/build_static_site.py (サイト生成)
    → docs/index.html (公開サイト)
    → GitHub Pages で自動公開
```

## セットアップ手順

### 1. eBay APIキーをSecretsに登録

1. このリポジトリの `Settings` → `Secrets and variables` → `Actions` を開く
2. `New repository secret` をクリック
3. 以下の2つを登録:
   - `EBAY_APP_ID`(eBay Developer Programで取得したApp ID)
   - `EBAY_CERT_ID`(同じくCert ID)

### 2. GitHub Pagesを有効化

1. `Settings` → `Pages` を開く
2. `Source` を `Deploy from a branch` に設定
3. `Branch` を `main` / フォルダを `/docs` に設定して `Save`

### 3. 動作確認

1. `Actions` タブを開く
2. `Update Pin Registry` ワークフローを選択
3. `Run workflow` ボタンで手動実行して、正常に動くか確認

これで、以降は1時間ごとに自動実行されます。

## ファイル構成

- `scripts/fetch_and_process.py` — eBayからのデータ取得・精査・分類の全処理
- `scripts/build_static_site.py` — サイト(HTML)の生成
- `data/all_official_series.json` — 手作業で調査した公式シリーズデータ(Disney Pins Blog等より)
- `data/pins_data.json` — 自動生成されるピンデータ(自動更新)
- `docs/index.html` — 公開されるサイト本体(自動更新)

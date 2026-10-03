# PMO の MCP サーバ

`pmo mcp` は、PMO の既存の処理（記録、訂正、検索、一覧の作り直し、点検）を MCP のツールとして公開します。新しい処理やデータの置き場所は作りません。正本は今までどおり Vault の Markdown です。

MCP を接続したセッションでは、AI は PMO を前提に動きます。接続を外せば、PMO の指示もツールも一切入りません。

## できること

| ツール | 内容 | 書き込み |
|---|---|---|
| `pmo_bootstrap` | GUARDRAILS（訂正）、MEMORY、NOW、保存方針、`custom_rules.md` をまとめて返す。記録が一覧より新しければ、先に一覧を作り直す | 一覧のみ |
| `pmo_search` | 記録を全文検索する | なし |
| `pmo_read_file` | Vault 内の `.md`／`.yaml` を 1 つ読む（Vault の外は読めない） | なし |
| `pmo_record_memory` | 記憶を 1 件追記する。`supersedes` で置き換え、`status: archived` で引退 | 追記 |
| `pmo_record_correction` | 訂正を 1 件追記する。`trigger` 付きにもできる | 追記 |
| `pmo_rebuild` | 一覧と検索用データを作り直す | 一覧のみ |
| `pmo_doctor` | Vault を点検する | なし |

接続すると、サーバの指示文（instructions）が AI に渡ります。中身は次のとおりです。

- 最初に `pmo_bootstrap` を呼ぶ
- 訂正を最優先する
- 保存は頼まれたものか、保存方針が許すものだけにする
- ファイルを手で書かず、ツールで記録する

細かいルールは、Vault の `START_HERE.md` と Protocol が正本です。

Vault が見つからない場合（Google ドライブのアプリが止まっているときなど）でも、サーバは起動します。そのときは `pmo_bootstrap` が `available: false` を返し、ほかの作業の邪魔はしません。

## インストール

MCP を使うには、追加の依存を入れます。

```bash
uv tool install --python 3.12 "/path/to/personal-memory-os[mcp]"
# または: python -m pip install "/path/to/personal-memory-os[mcp]"
```

## 登録：すべての新しいセッションでオンにする

### Claude Code

ユーザー全体（`--scope user`）に登録すると、どのフォルダで始めたセッションでも接続されます。

```bash
claude mcp add --scope user pmo -- pmo mcp --vault "/path/to/PMO"
```

`/path/to/PMO` は Vault の実際の場所です。Google ドライブの場合は、たとえば `~/Library/CloudStorage/GoogleDrive-<アカウント>/マイドライブ/PMO` になります。`pmo` が PATH にない環境では、`pmo` の絶対パスを書きます。

### Codex

```bash
codex mcp add pmo -- pmo mcp --vault "/path/to/PMO"
```

### Vault の場所を環境変数で渡す

`--vault` の代わりに、環境変数 `PMO_VAULT` でも指定できます（`claude mcp add ... -e PMO_VAULT=/path/to/PMO -- pmo mcp`）。

## オフにする

| 方法 | 範囲 |
|---|---|
| Claude Code で `/mcp` を開き、`pmo` を無効にする | そのプロジェクト（無効にした状態が残る） |
| Claude デスクトップアプリで、セッションのコネクタから `pmo` をオフにする | そのセッション |
| `claude mcp remove --scope user pmo` | 登録そのものを外す |
| `codex mcp remove pmo` | Codex の登録を外す |

## 注意点

- 書き込みは追記だけです。既存の記録の編集や削除はしません。変えたいときは、新しい記録で置き換えます。
- 保存してよいかどうかは、ツールではなく保存方針（`memory.auto_save`）と AI の判断に任せています。ツールは書式と検証を保証するだけです。
- 検索用データはパソコン側（`~/.personal-memory-os/`）に作ります。サーバ起動後の最初の検索と、書き込みの後に作り直します。
- スマホのアプリなど、このパソコンの外の AI からは使えません。

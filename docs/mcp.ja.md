# PMO の MCP サーバ

`pmo mcp` は、PMO の既存の処理（記録、訂正、検索、一覧の作り直し、点検）を MCP のツールとして公開します。新しい処理やデータの置き場所は作りません。正本は今までどおり Vault の Markdown です。

MCP を接続したセッションでは、AI は PMO を前提に動きます。接続を外せば、PMO の指示もツールも一切入りません。

## できること

| ツール | 内容 | 書き込み |
|---|---|---|
| `pmo_bootstrap` | **global** の訂正（全部）、今のこと（NOW）、global の大事な記憶、保存方針、`custom_rules.md`、**分野の一覧**を、文字数の上限内でまとめて返す。記録が一覧より新しければ、先に一覧を作り直す | 一覧のみ |
| `pmo_category_context` | 指定した分野（複数可）の訂正（全部）と大事な記憶を返す。親の分野の記録も含む | なし |
| `pmo_search` | 記録を全文検索する | なし |
| `pmo_read_file` | Vault 内の `.md`／`.yaml` を 1 つ読む（Vault の外は読めない） | なし |
| `pmo_record_memory` | 記憶を 1 件追記する。`scope` で分野を指定。`supersedes` で置き換え、`status: archived` で引退 | 追記 |
| `pmo_record_correction` | 訂正を 1 件追記する。`scope`、`trigger` も指定できる | 追記 |
| `pmo_set_scope` | 既存の記録の分野（scope）だけを、その場で書き換える。本文や他の項目は変えない | scope の行のみ |
| `pmo_rebuild` | 一覧と検索用データを作り直す | 一覧のみ |
| `pmo_doctor` | Vault を点検する | なし |

接続すると、サーバの指示文（instructions）が AI に渡ります。中身は次のとおりです。

- 最初に `pmo_bootstrap` を呼ぶ
- 訂正を最優先する
- 保存は頼まれたものか、保存方針が許すものだけにする
- ファイルを手で書かず、ツールで記録する

細かいルールは、Vault の `START_HERE.md` と Protocol が正本です。

Vault が見つからない場合（Google ドライブのアプリが止まっているときなど）でも、サーバは起動します。そのときは `pmo_bootstrap` が `available: false` を返し、ほかの作業の邪魔はしません。

## 分野（scope）ごとの読み込み

訂正と記憶には `scope` を付けられます。

- `global`：すべての会話で使う（振る舞い全般のルール、あなたの基本的な情報）。`scope` がない古い記録も global 扱い
- 分野のパス（例：`digital/video-editing`、`daily-life/health`）：その分野の会話でだけ使う。親の分野（`digital`）の記録は子の分野でも使う

分野の一覧はリポジトリで決めていません。記録に付いた `scope` から自動で集めます（`INDEX.md` の Categories と `pmo_bootstrap` の `categories`）。AI は記録するときに既存の分野を使い、合うものがなければ新しい分野を作ります。分野の分割・統合・付け直しは `pmo-organize` が提案し、承認されたものを `pmo set-scope`／`pmo_set_scope` で反映します。scope は分類のための付帯情報なので、記録を置き換えずにその場で書き換えます。

セッション開始時は global だけを読み込みます。会話が分野に入ったら、AI が `pmo_category_context` でその分野（複数可）の訂正と記憶を読み込みます。分野の狭い訂正（特定の商品の話など）が毎回読み込まれることはありません。

## `pmo_bootstrap` が返す量

セッション開始時の負担を抑えるため、`pmo_bootstrap` は次の順で、文字数の上限（既定 8,000 文字）まで詰めて返します。

1. **global の訂正は必ず全部返します。** 上限を超えても削りません。
2. **今のこと（NOW）** は新しい順に、残りの枠の 4 割までを使います。
3. **global の記憶** は、重要度が高い順（同じなら新しい順）に詰めます。NOW に入ったものは繰り返しません。
4. 記憶で余った枠は、NOW の続きに回します。

1 件が長い記録は 400 文字で切り、続きを読めるようにファイルの場所を付けます。入りきらなかった件数は `omitted` で返し、AI には `pmo_search` などで探すよう案内します。

上限は、登録時に `pmo mcp --max-context-chars 12000` のように変えられます。AI が呼び出すときに `max_chars` を指定することもできます。

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

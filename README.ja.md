日本語 | [English](README.md)

# Personal Memory OS（PMO）

**ChatGPT や Claude など、どの AI からでも使える「自分の記憶」を、自分の Google ドライブに持つための仕組みです。**

AI に覚えてもらった好みや決めたこと、訂正した内容は、ふつうはその AI の中にしか残りません。別の AI を使うと、同じ説明をもう一度することになります。

PMO は、その記憶を**自分のドライブに Markdown ファイルとして保存**します。ChatGPT で覚えたことを Claude も使えます。AI を乗り換えても、記憶は手元に残ります。

> **開発の初期段階です。** 記憶の保存形式とルール、パソコン用のコマンド（`pmo`）、AI に初期設定を任せる手順書は使えます。ChatGPT から Google ドライブへの初期設定は動作を確認しました。ほかのアプリでの動作や、AI どうしで記憶を共有する一連の流れは、まだ検証中です。くわしくは「[今できること](#今できること)」を見てください。

## 始め方（ChatGPT の場合）

パソコンへのインストールは不要です。ChatGPT に頼むだけで、ドライブに PMO の初期設定ができます。

### 1. 準備

ChatGPT で Google ドライブを接続し、ファイルの作成と読み書きができる状態にしておきます。

### 2. 次の 1 行を ChatGPT に送る

```text
https://github.com/massuru-mi/personal-memory-os/blob/main/skills/pmo-setup/SKILL.md を読み、その手順どおりに私の Google ドライブの「マイドライブ/PMO」に PMO をセットアップしてください。
```

セットアップは複数ステップで進みます。途中で ChatGPT の返答が途切れたら、「続けて」と送ってください。作ったものを確かめて、続きから再開します（重複して作ることはありません）。

保存先を変えたいときは、「マイドライブ/PMO」の部分を書き換えます。保存先を書かずに送った場合、ChatGPT は「マイドライブ/PMO」でよいかを確認してから作業を始めます。

ChatGPT は手順書（[`skills/pmo-setup/SKILL.md`](skills/pmo-setup/SKILL.md)）に沿って、次のことを行います。

- フォルダとファイルを作る
- 作ったファイルを読み戻して確認する
- 確認できた `START_HERE.md` のリンクを教えてくれる
- カスタム指示に貼る文面を作ってくれる

すでに PMO があるフォルダを指定した場合は、二重には作らず、足りないものだけを補います。もとからあるファイルを消したり上書きしたりはしません。

### 3. カスタム指示に貼る

ChatGPT が出した文面を、ChatGPT のカスタム指示に貼ります。中身は「新しいチャットを始めたら、まず `START_HERE.md` を読む」という短い指示だけです。

細かいルールは、ドライブ上の `START_HERE.md` と `_system/` 内のルール文書に書かれています。カスタム指示には書きません。そのため、PMO を更新すれば、指示を貼り直さなくても新しいルールが使われます。

### Claude の場合

同じ 1 行を Claude に送れば、同じ手順で初期設定できるように作っています。ただし、Claude アプリからの初期設定はまだ確認していません。カスタム指示は、すべての会話で使うなら「プロフィール」に、特定のプロジェクトだけで使うなら「プロジェクトの指示」に貼ります。

## ふだんの使い方

いつもどおり AI と話すだけです。

| やりたいこと | 話しかけ方の例 |
|---|---|
| 覚えてもらう | 「回答は簡潔な日本語がいい、と覚えておいて」 |
| 訂正する | 「それは違う。正しくは〜。覚えておいて」 |
| 場面つきで訂正する | 「Claude Code の機能を案内するときは、私の契約で使えるかを先に確認して」 |
| 整理する | 「記憶を整理して」 |
| 壊れていないか確認する | 「PMO を点検して」 |

- **はじめは、頼んだことだけを保存します。** それ以外は「これを保存しますか？」と提案するだけで、勝手には保存しません。自動保存や日々の記録（Daily）は、設定で有効にできます。
- **訂正は、ふつうの記憶より優先されます。** 一度訂正したことを、AI が繰り返さないようにするためです。
- **AI の推測は、事実とは区別して扱います。**
- **整理は提案から始まります。** 重複や矛盾、終わった用事などを一覧にして見せ、了承したものだけを反映します。元の記録は消さず、新しい記録で置き換えます。

AI はこうした依頼を、ドライブ上の手順書（`_system/skills/`）に沿って処理します。

## 今できること

| 機能 | 状態 |
|---|---|
| ChatGPT からの初期設定 | 確認済み |
| Claude アプリからの初期設定 | 手順書はあるが、未確認 |
| 記憶と訂正の保存 | 使える。手順書 [`pmo-remember`](skills/pmo-remember/SKILL.md) あり |
| 訂正に「どんな場面で効くか」（Trigger）を付ける | 使える。GUARDRAILS に表示される |
| 訂正と記憶を分野ごとに分ける（global／分野） | 使える。分野は記録から自動で集まり、必要に応じて増える。MCP では global だけを毎回読み込み、分野の分は話題が合ったときに読み込む |
| 記憶の整理（重複・矛盾・終わった用事） | 使える。手順書 [`pmo-organize`](skills/pmo-organize/SKILL.md) あり。提案して、了承されたものだけ反映 |
| 壊れた記録の点検と修復 | 使える。手順書 [`pmo-doctor-repair`](skills/pmo-doctor-repair/SKILL.md) あり。意味を変えない修復だけを自動で行う |
| Claude Code・Codex からの利用 | 使える。PMO フォルダで起動すると `AGENTS.md`（`CLAUDE.md`）を自動で読み、`pmo` コマンドで記録する |
| どのフォルダのセッションでも PMO を使う（MCP） | 使える。`pmo mcp` を登録すると、接続中のセッションだけ PMO 前提で動く。外せばオフ |
| 古い記憶を新しい記憶で置き換える | 使える。置き換えられた古い記憶は一覧から外れる |
| 推測と、はっきり言われたことの区別 | 使える。推測は確信度が基準を満たしたときだけ一覧に出し、「推測」と表示する |
| 一覧ファイル（MEMORY・NOW・GUARDRAILS・INDEX）の作り直し | 使える。パソコンでは `pmo rebuild`、AI からは手順書 [`pmo-refresh-views`](skills/pmo-refresh-views/SKILL.md) に従う |
| 会話ログと 1 日のまとめ | パソコンのコマンドで使える。初期設定ではオフで、オフの間は会話ログを作らない |
| 検索、重複の検出、バックアップ | パソコンのコマンドで使える |
| PMO 本体の更新 | 使える。手順書 [`pmo-update`](skills/pmo-update/SKILL.md) あり。下の「注意点」に既知の課題あり |
| Gemini など、ほかの AI | 将来の対象。動作は保証しない |
| すべての AI での自動記憶、裏での自動処理 | 提供していない |

AI がドライブに記憶を書き足しても、一覧ファイルや検索用データは自動では更新されません。必要なときに作り直します（AI に「一覧を更新して」と頼むか、パソコンで `pmo rebuild` を実行）。定期的に実行する設定は要りません。

## なぜ作ったか

### Obsidian だけでは足りない理由

Markdown で知識を自分で持ち、Obsidian と AI を組み合わせる方法は、PMO の土台でもあります。Claude Code や Codex なら、パソコン内のファイルを直接扱えます。

ただ、AI と話すのはパソコンの前だけではありません。通勤中はスマホの ChatGPT、考えごとは Claude、作業中は Claude Code や Codex、と使い分けることがあります。PMO は、**スマホ、クラウド、パソコンのどの AI からでも、同じ記憶を使える**ことを目指しています。Obsidian は、その記憶を自分で読んだり整理したりする道具として使えます。

```text
ChatGPT / Claude / Gemini / Codex / Claude Code
                      ↕
            Personal Memory OS
        共通のルール・保存形式・道具
                      ↕
        自分の Markdown ファイル ←→ Obsidian
           自分のドライブ（非公開）
```

これは目指している形です。図のすべての AI につながる、という意味ではありません。

### オープンソースにした理由

AI と一緒に使う記憶の仕組みを作ろうとすると、保存以外にも決めることがたくさんあります。

- どんなフォルダに分け、何を長く残すか
- AI の推測を、どこまで記憶にしてよいか
- 訂正を、古い記憶よりどう優先するか
- 複数の AI が同時に書くとき、どう衝突を減らすか
- 日々の会話をどうまとめるか
- 検索やバックアップをどうするか。仕組みを更新するとき、過去の記憶をどう守るか

これを一人ひとりがゼロから考える必要はありません。**誰かが一度解決した部分は、次の人がそのまま使えるようにしたい。** それがオープンソースにした理由です。

GitHub で公開しているのは「仕組み」だけです（ルール、保存形式、テンプレート、更新の道具）。一人ひとりの記憶は、それぞれのドライブに非公開で置きます。

```text
GitHub（公開）: PMO の仕組み
    │  初期設定・更新で配置
    ▼
自分のドライブ（非公開）
    ├─ 記憶
    ├─ プロジェクト
    ├─ 知識
    └─ 日々の記録
```

## ドライブの中身

| 区分 | 中身 | 誰のものか |
|---|---|---|
| System（`_system/`、`START_HERE.md`、`AGENTS.md`、`CLAUDE.md`） | ルール、保存形式、テンプレート、手順書 | PMO が配置・更新する。AI はふだん変更しない |
| Config（`_config/`） | 言語や保存方針などの設定、自分用の追加ルール | 自分のもの。PMO を更新しても残る |
| Data（`10_Memory/` など） | 記憶、訂正、プロジェクト、会話ログ | 自分のもの。PMO の更新で上書きされない |
| Runtime | 検索用データ、ロック | パソコンだけに置く使い捨てのデータ。ドライブには置かない |

```text
PMO/
├─ START_HERE.md        # AI が最初に読む入口
├─ AGENTS.md / CLAUDE.md  # Codex・Claude Code 向けの入口（START_HERE を指すだけ）
├─ SYSTEM_VERSION.md
├─ MEMORY.md / NOW.md / GUARDRAILS.md / INDEX.md  # 記憶から作り直せる一覧
├─ _system/             # ルール・テンプレート・手順書（skills）
├─ _config/             # 自分の設定（settings.yaml）と追加ルール（custom_rules.md）
├─ 10_Memory/
│  ├─ Events/           # 記憶（1 件 1 ファイル。好み・事実・決定などは種類で区別）
│  └─ Corrections/      # 訂正（1 件 1 ファイル）
├─ 50_Daily/            # 会話ログ（有効にした場合）
└─ 80_Archive/
```

| 一覧ファイル | 中身 |
|---|---|
| `GUARDRAILS.md` | 訂正の一覧。AI はこれを最優先で読む |
| `MEMORY.md` | 長く使う記憶の一覧 |
| `NOW.md` | 最近の関心と進行中のこと |
| `INDEX.md` | 目次 |

会話ログは `50_Daily/日付/<AI名>_<会話ID>_<話題>.md` のように、会話ごとに別ファイルにします。同じファイルへの同時書き込みを減らすためです。ただし、これで同期の衝突が完全になくなるわけではありません。

## パソコンのコマンドで使う（任意）

ChatGPT などから使うだけなら、この節は不要です。パソコンで検索や一覧の作り直しをしたい場合や、Claude Code・Codex から使う場合に便利です。

### Claude Code・Codex から使う

PMO フォルダで Claude Code や Codex（Obsidian のプラグイン Claudian 経由を含む）を起動すると、フォルダ直下の `AGENTS.md`（Claude Code は `CLAUDE.md`）を自動で読みます。中身は「`START_HERE.md` を読む」「記録は `pmo` コマンドで行い、ファイルを手で書かない」という入口だけです。下の `pmo` コマンドを入れておくと、記録の書式が崩れません。

自分用のルールは `_config/custom_rules.md` に書きます。`AGENTS.md` と `CLAUDE.md` は PMO の更新で置き換わるので、直接は編集しません。もともと自分の `AGENTS.md` や `CLAUDE.md` があるフォルダに PMO を入れた場合、PMO はそれを上書きせず、スキップしたことを知らせます。

### どのフォルダからでも使う（MCP）

PMO フォルダ以外で作業しているときも PMO を使いたい場合は、MCP サーバ `pmo mcp` を登録します。

- **オン・オフが簡単**：接続しているセッションでは、AI が最初に訂正と記憶を読み込み、記録は PMO のツールで行います。接続を外せば、PMO の指示もツールも入りません。
- **デフォルトでオンにできる**：Claude Code でユーザー全体に登録すると、すべての新しいセッションで有効になります。オフにしたいプロジェクトでは `/mcp` から無効にします。

```bash
claude mcp add --scope user pmo -- pmo mcp --vault "/path/to/PMO"
```

MCP を使うには、コマンドを `personal-memory-os[mcp]` として入れます。Codex への登録方法やオフにする方法は、[MCP の説明](docs/mcp.ja.md)を見てください。

### コマンドを入れる

Python 3.11 以上が必要です。このリポジトリを取得し、記憶のフォルダとは別の場所で実行します。

```bash
python -m pip install .
pmo install /path/to/PMO
pmo record /path/to/PMO --type preference --content "例：回答は簡潔な日本語がよい"
pmo rebuild /path/to/PMO
pmo search /path/to/PMO "簡潔"
pmo doctor /path/to/PMO
```

`/path/to/PMO` は実際の保存先に置き換えます。ドライブ上の PMO を使う場合は、Google ドライブのパソコン版アプリを入れて、ふつうのフォルダとして読み書きできるようにします。すでにドライブに PMO がある場合は、`pmo install` は不要です。Obsidian で見る場合も、このフォルダを開きます。

主なコマンド：

| コマンド | 内容 |
|---|---|
| `pmo record` | 記憶を 1 件保存する |
| `pmo correct <vault> --wrong "..." --correct "..." [--trigger "..."]` | 訂正を保存する（`--trigger` で効く場面も付けられる） |
| `pmo rebuild` | 一覧ファイルと検索用データを作り直す |
| `pmo search` | 記憶を検索する |
| `pmo doctor` | 壊れたファイルや設定のずれがないか調べる |
| `pmo status` | PMO のバージョンと、仕組みのファイルが書き換えられていないかを表示する |
| `pmo update` | PMO の新しい仕組みをドライブに反映する（先にバックアップを取る） |
| `pmo backup` | まるごと zip でバックアップする |
| `pmo duplicates` | 重複した記憶を探す |
| `pmo set-scope <vault> <ID>… --scope <分野>` | 既存の記録の分野だけを書き換える |
| `pmo daily <vault> YYYY-MM-DD` | その日のまとめを作り直す |
| `pmo ingest-turn <vault> turn.json` | AI が整理した記憶と会話ログをまとめて取り込む（記憶の置き換え `supersedes` もこれで指定する） |

`ingest-turn` は、AI が整理済みのデータを受け取るための入口です。会話を自動で読み取ったり、会話から記憶を自動で抜き出したりはしません。

## 設定と注意点

**設定**：`_config/settings.yaml` で、保存方針（自動保存するか）、Daily の有効・無効、言語などを決めます。コマンドが実際に使うのは、タイムゾーン、推測を一覧に出す確信度の基準、NOW に載せる期間です。言語の設定は AI への指示で、コマンドが出す見出しは今は英語です。自動アーカイブなど、設定項目はあってもまだ動かないものがあります。

**更新**：`pmo update` は、**パソコンに入っている PMO を**ドライブに反映するコマンドです。GitHub から最新版を取ってくることはしません。先にパソコンの PMO を新しくしてから実行します。ドライブ上の PMO より古い版で更新しないでください。実行前に、ドライブ上の PMO の隣にある `PMO-Backups` へ自動でバックアップを取ります。仕組みのファイルが手で書き換えられていると、更新は止まります。手順は [`pmo-update`](skills/pmo-update/SKILL.md) にまとめてあります。

**検索**：検索用データはパソコンの `~/.personal-memory-os/` に作られ、Markdown からいつでも作り直せます。記憶を書き足したあとに検索する場合は、先に `pmo rebuild` を実行します。

**既知の課題**：

- 管理ファイル（manifest）がない場合、更新時の保護が効かない
- Windows では、タイムゾーンの扱いに追加の準備が要る
- `ingest-turn` が途中で失敗したときの再実行が整っていない
- Daily の同時更新に弱い

衝突や更新失敗への対策は、まだ完成していません。くわしくは[設計と受け入れ条件](docs/local-optional-design.ja.md#実装状況と受け入れ条件)を見てください。

## 開発に参加する

自分の記憶、会話の書き出し、パスワードや API キーなどは、このリポジトリや Issue に載せないでください。

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
```

- [アーキテクチャ](docs/architecture.md) / [保存の約束事](docs/storage-contract.md)
- [AI との連携](docs/ai-integration.md) / [記憶のルール](docs/memory-protocol.md)
- 手順書：[初期設定](skills/pmo-setup/SKILL.md) / [記録](skills/pmo-remember/SKILL.md) / [整理](skills/pmo-organize/SKILL.md) / [点検と修復](skills/pmo-doctor-repair/SKILL.md) / [更新](skills/pmo-update/SKILL.md) / [一覧の作り直し](skills/pmo-refresh-views/SKILL.md)
- [MCP の説明](docs/mcp.ja.md) / [クラウドでの使い方](docs/local-optional-design.ja.md) / [カスタム指示の文面](docs/custom-instructions.ja.md) / [今後の拡張の設計メモ](docs/agent-integration-proposals.ja.md)
- [Contributing](CONTRIBUTING.md) / [Security](SECURITY.md)

## ライセンス

MIT。くわしくは [LICENSE](LICENSE) を見てください。

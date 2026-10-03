# エージェント連携・ノート拡張の設計メモ

ステータス：提案（未実装）
作成日：2026-10-03

Claude × Obsidian の連携ルール（動画で紹介された構成）、Obsidian プラグイン Claudian（YishenTu/claudian）、類似プロジェクト claudian.app との比較から挙がった拡張案を整理し、PMO の不変条件と実際の利用状況に照らして採否を判断する。

## 判断の前提

- **不変条件**：Markdown が正本。System／Config／Data／Runtime の境界を保つ。System 更新は Data を上書きしない。生成ビューは作り直せる。特定の AI 向けの連携は、共通の PMO プロトコルに合わせる。
- **利用実態（作者の Vault、2026-10-03 時点）**：記憶イベント 47 件、訂正 4 件。`20_Projects`、`30_Knowledge`、`40_Decisions`、`50_Daily`、`00_Inbox` は 0 件。`10_Memory/Self`、`10_Memory/Preferences`、`10_Memory/Decisions` は作られるだけで、どのコードも使っていない。
- **主な書き手**：ChatGPT（Drive 経由）と Claude Code／Codex。実際に起きた書式崩れは、すべて ChatGPT が書いたファイルだった。Protocol を直して対処済み（#5、#6）。
- **既知の未解決課題**（README 記載）：manifest がない場合の更新保護、ターン取り込みが途中で止まったときの扱い、Daily の同時更新。

新機能はこれらの課題と工数を取り合う。新機能は「実際に困っていること」に紐づくものを優先する。

### 各フォルダの実装状況（0 件の理由）

| フォルダ | 状態 | 0 件の理由 |
|---|---|---|
| `50_Daily` | 経路あり（`pmo ingest-turn` と Daily Protocol） | `_config/settings.yaml` で `daily.enabled: false` になっており、設定どおり |
| `20_Projects`、`30_Knowledge`、`40_Decisions` | フォルダだけ | 書き込むコマンド、Protocol、テンプレートのどれもない。コードでは INDEX.md からフォルダへのリンクを張っているだけ |
| `10_Memory/Self`、`Preferences`、`Decisions` | フォルダだけ | インストール時に作られるだけで、どのコードも使っていない |

**好みと作業スタイルの保存先**：記憶イベントとして `10_Memory/Events/` に `type: preference` で保存され、MEMORY.md の Preference 見出しの下に表示される。作者の Vault では 6 件ある。同じく `knowledge`（6）、`decision`（9）、`project_progress`（5）も記憶イベントとして記録済み。つまり、知識・決定・進捗は記録されていて、0 件なのはそれらをまとめて育てるノートのフォルダのほう。空の `10_Memory/Preferences/` があることで、保存先が紛らわしくなっている（→ H）。

### 判明した不整合：`ingest-turn` が `daily.enabled` を無視する

`pmo ingest-turn` は、`daily.enabled` を確認せずに毎回 Daily のセッションファイルを書く（`ingest.py` の `write_session` 呼び出し）。START_HERE と Daily Protocol の「`daily.enabled: false` なら Daily を作らない」と矛盾する。作者の Vault ではこのコマンドを使っていないため、実害はない。修正方針：設定がオフなら書かず、戻り値の `session` を `null` にする。テストも足す。小さなバグ修正として、新機能より先に対応する。

## 提案一覧と判断

| # | 提案 | 価値 | コスト・リスク | 判断 |
|---|---|---|---|---|
| A | Vault に `AGENTS.md`／`CLAUDE.md` を配置 | 高 | 低 | **採用・最優先** |
| B | 訂正に `trigger` を追加 | 中 | 低 | **採用** |
| C | 記録に `related` を追加し、`[[ ]]` で表示 | 中 | 低〜中 | **採用（最小限）** |
| D | 既存の決定的処理を MCP で包む | 中 | 中 | **条件付き・保留** |
| E | Knowledge／Decisions／Projects のノート用 Protocol とスキーマ | 中〜高 | 高 | **段階的に。まず文書のみ** |
| F | Preferences の分類ごとの生成ビュー | 低 | 中 | **見送り** |
| G | 関連ノートの検索とリンク提案ツール | 中 | 中 | **保留（C・D の後）** |
| H | 使われていない `10_Memory` 配下のフォルダの整理 | 中 | 低 | **採用** |
| — | リモート MCP（スマホ対応） | 高 | 非常に高 | **対象外** |

### A. `AGENTS.md`／`CLAUDE.md` の配置（採用・最優先）

Claude Code・Codex・Claudian は、作業フォルダの `AGENTS.md` や `CLAUDE.md` を自動で読む。これらはローカルのエージェントにとって、カスタム指示に相当する入口になる。

- **中身は最小限**：新しいセッションの開始時に `START_HERE.md` を読む。書き込みは `pmo`（または将来の MCP）を使い、手で書かない。`_system/` と生成ビューは編集しない。ユーザー独自のルールは `_config/custom_rules.md` に書く。詳細ルールは書かない（正本は START_HERE と Protocol）。
- **本体は `AGENTS.md`**：`CLAUDE.md` は `@AGENTS.md` の 1 行にする。中身を 1 か所に保ち、特定の AI に依存しない。
- **System 側の管理ファイル**：インストールで配置し、`pmo update` で更新し、手で書き換えたら改変として検知する。
- **既存ファイルは上書きしない**：ユーザーがすでに `AGENTS.md` や `CLAUDE.md` を持っている場合は、そこで止まって知らせ、PMO への参照 1 行を足すよう案内する。
- **`_config/custom_rules.md` をインストール時に空で作る**：Write Boundary の文書で触れているが、今は作られていない。

効果は小さくない。コーディングエージェントがファイルを直接書く道を、文面のうえで塞げる。コストはほぼ文書だけで済む。

### B. 訂正の `trigger`（採用）

動画の `mistakes.md` にある「Trigger（このルールが適用される状況）」を、`pmo.correction/v1` に任意項目として足す。GUARDRAILS では本文の横に表示する。

- 任意項目なので、既存の訂正 4 件の移行は不要。
- `pmo correct --trigger` と、スキーマ、テンプレート、Protocol を更新する。

### C. `related` と `[[ ]]`（採用・最小限）

- 記憶と訂正のスキーマに、任意項目 `related`（Vault 内の相対パスの一覧）を足す。
- 生成ビューでは `[[path]]` として表示する。ビュー側ではすでに、元の記録へのリンクを `[[ ]]` で付けている（`views.py` の `_fmt_link`）。
- 正本は Obsidian の記法に依存させない。`related` はパスで持ち、`[[ ]]` は表示用とする。
- リンク先が存在しない場合は `pmo doctor` で警告する（エラーにはしない）。

Obsidian はまだ日常的には使われていない。グラフビューの価値は使い始めてから出てくる。今は項目を用意するだけにとどめ、自動提案（G）はしない。

### D. MCP で包む（条件付き・保留）

`pmo` の決定的処理（記録、訂正、検索、作り直し、診断）を、`pmo mcp`（stdio）として包む。依存は `personal-memory-os[mcp]` のオプションにする。

- **効果がある場面**：シェルを持たないデスクトップの AI アプリ（Claude Desktop のチャットなど）。それと、ツールの型や選択肢の制約で引数の間違いを防げる点。
- **効果が小さい場面**：主な書き手の Claude Code／Codex は、すでに `pmo` CLI を実行できる。直接編集を止めるのは A の役割で、MCP では止められない。
- **届かない場面**：スマホのアプリ。

**着手の条件**：A を入れたあとも、コーディングエージェントが手書きや引数の間違いを起こす。または、シェルを持たないアプリから書き込みたい場面が実際に出てくる。条件を満たしたら着手する。実装自体は薄く、既存関数の呼び出しに限る。

### E. ノート用の Protocol とスキーマ（段階的に）

Knowledge、Decisions、Projects は、追記型の記憶イベントと違い、書き直して育てるノートになる。

- **段階 1（文書のみ）**：Protocol とテンプレートを足す。命名規則（`topic-subtopic.md`、`YYYY-MM-DD-topic.md`、`project-name.md`）、Knowledge は原因と解決策をペアで書く、Decisions は選択肢と理由を書く、という書き方を決める。保存方針は既存の「明示的に頼まれたときだけ」に従い、動画の「その場で必ず書く」は持ち込まない。
- **段階 2（実際に使われてから）**：`pmo.note/v1` スキーマ、検証、`pmo note` コマンドを足す。

**今は段階 1 にとどめる理由**：該当フォルダの利用が 0 件で、必要性を裏付けるデータがない。また、書き換え型のノートは Drive 同期での競合リスクが追記型より高い。設計するなら、同時に編集されたときの扱いもあわせて検討が要る。

**あわせて決めること**：`10_Memory/Decisions` と `40_Decisions` の役割の線引き。短い決定の事実は記憶イベント（`type: decision`）、背景や比較を含む判断の記録は `40_Decisions` のノートとする。

### F. Preferences の分類ごとの生成ビュー（見送り）

MEMORY.md は、すでに `type` ごと（Preference を含む）に見出しを分けている。分類ごとのファイルを生成するには、分類の体系を新たに決める必要がある。生成ファイルが増えると、Drive 同期の負荷も増える。今の件数では、価値がコストに見合わない。記憶が増えて MEMORY.md が読みにくくなったら再検討する。

### G. 関連ノートの検索とリンク提案（保留）

全文検索の上に作れる。前提として、リンクを持つ項目（C）と呼び出し口（A または D）が要る。書き込む前に、必ずユーザーへ提案する形にする。C の `related` が実際に使われ始めてから着手する。

### H. 使われていないフォルダの整理（採用）

`10_Memory/Self`、`10_Memory/Preferences`、`10_Memory/Decisions` は、作られるだけで使われていない。ユーザーや AI が「ここに書くもの」と誤解する原因になる。インストールで作らないようにし、既存の Vault では空なら残す（Data なので削除はしない）。そのうえで、Storage Contract に「使わない」と明記する。E の線引きと一緒に決める。

### リモート MCP（対象外）

スマホからの書き込みには HTTP サーバ、OAuth、Drive への書き込み権限が必要になる。サーバの運用、セキュリティ、第三者サーバを個人データが通ることが、「サーバ不要・ユーザーが所有する」という前提とぶつかる。類似の claudian.app（Windows 専用、クローズド化予定）はこの方向を選んでいる。PMO では別の判断事項として扱い、このメモの範囲外とする。

## スキルの追加方針

今あるスキルは、`pmo-setup`（初めてのセットアップ）と `pmo-refresh-views`（生成ビューの作り直し）の 2 つだけ。最も頻繁な操作である記録と、実際に手作業で行った修復・更新の手順がスキルになっていない。

以下の 6 つを追加する方針とする。

| スキル | 中身 | 優先度 |
|---|---|---|
| `pmo-remember` | 記憶と訂正を記録する。`pmo record`／`pmo correct`（将来は MCP）が使えればそれを使い、使えなければテンプレートどおりに書いて読み戻す。訂正の見出し、`supersedes`、`repeat_error_count`、`trigger`（B）を含める | 高 |
| `pmo-doctor-repair` | `pmo doctor` で問題を見つける。バックアップを取ってから、中身を変えない修復だけを行う（BOM と CRLF の正規化、訂正の本文見出しへの移し替え）。意味が変わる修正はしない | 高 |
| `pmo-update` | PMO 本体を、Vault と同じかより新しいバージョンで入れ直す。改変の確認、`pmo update`（自動バックアップ）、`pmo doctor`、読み戻しを行う。改変が見つかったら止まる | 中 |
| `pmo-organize` | 重複、古くなった `open_loop`、置き換え漏れ、確信度の低い推測を洗い出して提案する。了承を得たら、`supersedes` を付けた新しい記録を追記する。既存の記録は書き換えない。START_HERE の「organize my memory」への対応手順にする | 中 |
| `pmo-recall` | 質問に関係する記録を検索して読み、参照した記録を示す。`pmo search` が使えればそれを使い、使えなければコネクタの検索を使う。GUARDRAILS を先に確認する | 低〜中 |
| `pmo-daily` | `daily.enabled: true` のときだけ、セッションファイルを更新し、`pmo daily` でその日のまとめを作る。オフなら何もしない | 低 |

共通の方針：

- 置き場所は既存と同じ `skills/<name>/SKILL.md`。Vault の `_system/skills/` にも配置し、System 側の管理ファイルとして扱う。
- Claude Code と Codex はスキルとして読み込む。ChatGPT や Claude アプリには、START_HERE から該当するスキルのファイルを読むよう案内する。
- スキルは手順書にとどめる。正しさの保証は `pmo` の決定的処理と Protocol が担う。スキル固有のルールは作らず、Protocol を参照する。
- 各スキルに、`pmo-refresh-views` と同様の契約テスト（配置されること、START_HERE から参照されること、重要な制約の文言）を付ける。
- Knowledge などのノート用スキルは、E の段階 2 が決まるまで作らない。

## 実施順

0. `ingest-turn` が `daily.enabled` を無視する不整合の修正
1. A（`AGENTS.md`／`CLAUDE.md`、`custom_rules.md`）
2. B（`trigger`）と H（使われていないフォルダの整理）、スキル `pmo-remember` と `pmo-doctor-repair`
3. スキル `pmo-update` と `pmo-organize`
4. C（`related` の最小実装）
5. E 段階 1（ノート用の Protocol とテンプレートの文書化、Decisions の線引き）
6. 既知の未解決課題（manifest がない場合の更新保護など）を、上の新機能と同列で優先度を判断する
7. D・G・E 段階 2 は、着手の条件を満たしたら着手する
8. スキル `pmo-recall`（D か検索の口が整ってから）と `pmo-daily`（Daily を有効にするとき）

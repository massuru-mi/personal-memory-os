# クラウド／ローカル運用設計

状態：AI向け初期構築手順は `skills/pmo-setup/SKILL.md` として実装済み。Driveコネクターの実能力はアプリ・アカウントごとに実行時確認が必要。ChatGPT↔Claudeを含む全経路のE2E保証はまだ行わない。

## 基本方針

PMOの利用にユーザーPC、Python、Drive for Desktop、定期ジョブを必須にしない。共通のMarkdown原本を、対応するクラウドAIとローカルCLIの両方から扱えるようにする。

役割は三層に分ける。

1. **セットアップSKILL** — PMOをどこへ、どう安全に初期構築するか。
2. **START_HERE.md** — 初期構築後、AIがPMOをどう読む・書くか。
3. **アプリのカスタム指示** — 各新規チャットでSTART_HEREを読むための薄い入口。

詳細ルールをカスタム指示へ複製しない。ルール変更はPMO側へ集約する。

## Google Driveへの初期構築

正式な手順は [`skills/pmo-setup/SKILL.md`](../skills/pmo-setup/SKILL.md) を正本とする。

### 保存先の承認

Driveへの最初の書き込み前に、セットアップAIは次のどちらかを満たさなければならない。

- ユーザーが依頼時に作成先フォルダ、パス、URLを明示している。
- AIが作成候補を提示し、ユーザーが了承している。

保存先が未指定なら、既定候補は `マイドライブ/PMO`。**承認前にフォルダを作成しない。**

ユーザーが既存フォルダを指定した場合は、その中身を確認してから作業する。既存データを勝手に削除・上書きしない。同じ場所にPMOらしい構造があれば、新しいPMOを重複作成せず、既存インストールとして検査する。

### 標準ルート名

新規作成するPMOの標準ルート名は `PMO`。

```text
PMO/
├─ START_HERE.md
├─ SYSTEM_VERSION.md
├─ MEMORY.md
├─ NOW.md
├─ GUARDRAILS.md
├─ INDEX.md
├─ _system/
├─ _config/
├─ 00_Inbox/
├─ 10_Memory/
├─ 50_Daily/
└─ 80_Archive/
```

### セットアップ処理

セットアップAIは現在のmainまたはユーザーが指定したreleaseを読み、versionとcommit SHAを固定する。READMEだけで構造を推測せず、`deploy.py`、`constants.py`、`resources.py`、`views.py`、配布Systemファイルを確認し、現在の `pmo install` と同等の内容をDriveへ配置する。

配置後は、少なくとも次をDrive側から再確認する。

- PMOルート
- `_config/settings.yaml`
- `_system/SYSTEM_MANIFEST.json`
- `_system/adapters/`
- `_system/protocols/`
- `_system/schemas/`
- `_system/templates/`
- `START_HERE.md`
- `SYSTEM_VERSION.md`
- 生成ビュー

作成APIの成功だけでは完了としない。重要ファイルをDriveから読み戻し、一時テストファイルがあれば削除する。

## 初期保存ポリシー

安全な初期値は次の通り。

- 明示された「覚えて」「訂正して」「記憶を整理して」は実行する。
- それ以外の記憶候補は、`memory.auto_save: false` の間は勝手に確定記憶へ保存せず提案する。
- ユーザーが自動保存を明示的に有効化した場合だけ、その設定範囲で保存する。
- AI推測だけでユーザー事実を確定しない。
- Dailyは初期状態では無効。ユーザーが有効化した場合だけSession Protocolに従う。
- バックグラウンド処理はPMO単体では発生しない。

## Runtime bootstrap

各AIのカスタム指示は [`custom-instructions.ja.md`](custom-instructions.ja.md) の最小文を使う。

各新規チャットの開始時に `START_HERE.md` を一度読み、そのセッションでは取得したルールに従う。毎ターンSTART_HEREを再取得する必要はない。ただしユーザーがPMO更新を依頼した場合や、ルールが変わった可能性が明確な場合は再取得してよい。

## 原本と生成ビュー

`MEMORY.md`、`NOW.md`、`GUARDRAILS.md`、`INDEX.md` は生成ビューであり正本ではない。

意味を変える更新では、先に `10_Memory/` 等の原本へイベント・訂正を保存し、その後ビューを更新する。ビュー更新だけに変更を残さない。書き込み後は可能な範囲で読み戻す。

Drive接続だけでは完全な原子的更新やローカルFTSの再生成を保証できない。できない処理は未完了として区別して報告する。

## ローカルCLI

ローカルCLIは同じschemaと原本を扱う追加の運用手段である。高速な再生成、FTS検索、doctor、backup、updateを提供する。

```bash
pmo install /path/to/PMO
pmo record /path/to/PMO --type preference --content "..."
pmo rebuild /path/to/PMO
pmo doctor /path/to/PMO
```

クラウドで既に作成されたPMOへローカルCLIを追加する場合、既存Dataを上書きしてはいけない。version、manifest、driftを確認してから扱う。

## 未完了として扱うケース

次のどれかが確認できない場合、セットアップAIは「完了」と断言しない。

- GitHubの対象version／commit
- Driveの保存先承認
- 必要なDrive書き込み能力
- System／Config／Data構造の配置
- manifest／version
- Drive側からの一覧・読み戻し
- 一時ファイルの除去
- 既存データを破壊していないこと

接続機能の不足をローカルPC必須の手順へ黙って切り替えない。利用可能な範囲と不足操作を明示する。

## 今後の検証

- ChatGPTで「初期構築→記憶追加→別チャットで参照→訂正→ビュー更新」。
- Claudeで同じ流れ。
- ChatGPTで構築したPMOをClaudeが利用する方向と、その逆。
- クラウド運用途中にローカルCLIを追加しても原本・Configが壊れないこと。
- 複数AIが並行利用した際の競合と再試行。

これらのE2E検証が完了するまでは、全AI・全アカウントで同一のDrive操作が可能とは案内しない。

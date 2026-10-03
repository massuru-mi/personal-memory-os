日本語 | [English](README.md)

# Personal Memory OS

**AIごとに分断された「自分の記憶」を、ユーザー自身の手に戻すためのオープンなMemory OS。**

ChatGPT、Claude、Geminiなど、私たちが日常的に使うAIは増え続けています。一方で、それぞれの会話履歴やMemoryが、そのまま他のAIにも共有されるわけではありません。あるAIと積み上げた自分についての理解や過去の意思決定を、別のAIへ説明し直す場面があります。

長いチャットの中では、重要な意思決定やプロジェクトの進捗、過去に訂正した内容も埋もれていきます。「以前説明したことをもう一度説明する」「以前訂正した間違いをAIが繰り返す」。こうした負担を減らしたいと考えています。

Personal Memory OS（PMO）は、**AIとは独立した、ユーザー自身が所有する共通のMemory Layer**を作るプロジェクトです。記憶の原本を私有ストレージのMarkdownとして保ち、利用するAIが変わっても持ち運べることを目指します。

> 現在は初期開発段階です。Markdownのプロトコル、Python CLI、AIがGoogle Driveへ初期構築するためのセットアップSKILLを実装しています。アプリごとに利用できるDrive操作は異なり、AI間のE2E検証は継続中です。以下の将来像と、[現在使える機能](#現在使える機能と開発中の機能)を分けてご覧ください。

## なぜObsidianだけではないのか

ObsidianとAIを組み合わせ、Markdownの知識を自分で所有する方法は、PMOにとっても大切な土台です。Claude CodeやCodexなどからローカルのvaultを扱えば、検索・編集・整理を柔軟に行えます。

しかし、日常のAIとの対話はPCの前だけではありません。通勤中はiPhoneのChatGPT、考えを整理するときはClaude、PCで作業するときはCodexやClaude Code、と使い分けることがあります。

PMOは、Obsidianを利用できる環境に加え、**モバイルAI、クラウドAI、ローカルAIからも、同じ「自分の記憶」を利用できる状態**を目指しています。Obsidianはその記憶を人が読み、整理するための選択肢です。

```text
ChatGPT / Claude / Gemini / Codex / Claude Code
                      ↕
            Personal Memory OS
        共通のプロトコル・保存形式・ツール
                      ↕
        User-owned Markdown ←→ Obsidian
              私有ストレージ
```

これは目指す構成です。図中の全サービスとの接続が実装済みという意味ではありません。

## なぜOSSなのか

AIを使った個人メモリ基盤を作ろうとすると、記憶を保存する以外にも、多くの設計が必要になります。

- どんなフォルダ構成にして、何を長期記憶として残すか。
- AIの推測をどこまで記憶してよいか。
- ユーザーによる訂正を、古い記憶よりどう優先するか。
- 複数のAIによる書き込みの競合をどう減らすか。
- 日々のチャットをどう整理するか。
- 検索・バックアップ・Migrationをどう扱い、仕組みの更新時に過去の記憶をどう守るか。

これらを一人ひとりがゼロから設計し、同じ問題を繰り返し解決する必要はないと考えています。

**一度誰かが解決した個人メモリ基盤の共通部分を、次の人がもう一度作り直さなくてよいようにする。** それがPMOをOSSとして公開する目的の一つです。

各ユーザーのMemoryそのものはPrivateなストレージに残します。GitHubで共有するのは、Memoryを扱うためのProtocol、Schema、Template、Updater、Migrationなどの「仕組み」です。

```text
GitHub: Personal Memory OS
    │  OSSとして共有
    ▼
System / Protocol / Schema / Templates / Tools
    │  私有ストレージへ配置
    ▼
Your Private Storage
    ├─ Memory
    ├─ Projects
    ├─ Knowledge
    └─ Daily
```

## Personal Memory OSが目指すもの

理想的には、記憶の管理のために毎回特別な操作をする必要はありません。

いつも通りAIと話す。ユーザーが選んだ保存方針に沿って、重要なことが記憶される。AIを訂正すれば、次からその訂正が優先される。その日に何を考え、何を決め、何を進めたかも残る。

ChatGPTで保存した記憶をClaudeも利用できる。将来別のAIへ乗り換えても、それまでの記憶を失わない。そして原本は、特定のAIサービス内だけに閉じず、ユーザーが所有するMarkdownとして残り続ける。

**「AIがユーザーを記憶する世界」から、「ユーザーが自分の記憶を持ち、それを好きなAIに使わせる世界」へ。** PMOはそのためのオープンな基盤を目指しています。

自動保存はユーザーが選ぶ運用です。初期方針の案は「明示的な保存・訂正の指示は実行、それ以外は会話中に更新候補を提案」。必要に応じて、承諾した範囲の自動保存やDaily記録を有効にします。

## AI＋Google Driveで始める

ユーザーのPCへPythonや同期ソフトを導入しなくても、対応するAIからPMOを初期構築できます。AI向けの正式な初期設定手順は [`skills/pmo-setup/SKILL.md`](skills/pmo-setup/SKILL.md) です。

1. ChatGPT、Claudeなど、GitHubとGoogle Driveを扱えるAIにセットアップSKILLを読ませてPMOの初期設定を依頼します。
2. **Driveへ最初に書き込む前に、セットアップAIは保存先についてユーザーの承認を得ます。** ユーザーが依頼時に保存先フォルダやパスを指定済みなら、それを承認として扱います。指定がなければ `マイドライブ/PMO` を既定候補として提示し、了承を得てから作成します。
3. セットアップAIは対象versionとcommitを固定し、現在の `pmo install` と同等のSystem／Config／Data構造を、承認された保存先へ配置します。
4. 配置後にDriveを再一覧・読み戻しし、確認済みのPMOフォルダURL、`START_HERE.md` URL、そのAI向けの最小カスタム指示を提示します。

標準のルートフォルダ名は **`PMO`** です。運用ルールの詳細をカスタム指示へ複製せず、配置された `START_HERE.md`、Protocol、Configを正本にします。カスタム指示は「各新規チャットの開始時にSTART_HEREを読む」ための薄いブートストラップだけにします。

セットアップSKILLを読ませただけでDrive権限やバックグラウンド自動処理が有効になるわけではありません。必要なDrive操作を実行できない場合、AIは完了したように装わず未完了項目を報告します。

`MEMORY.md`などの生成ビューを編集する依頼では、原本へ追加・訂正してから可能な範囲でビューへ反映します。外部から原本を追加してもローカルFTS indexは自動更新されないため、CLI利用時は必要に応じて `pmo rebuild` を実行します。

## 現在使える機能と開発中の機能

| 項目 | 現在の状態 |
|---|---|
| 記憶・訂正のMarkdown保存 | CLIと共通schemaを実装 |
| 訂正・置き換えの反映 | `supersedes`を解決し、古い項目を現在のビューから除外 |
| 推測と明示情報の区別 | MEMORY／NOWで設定された確信度を使い、採用した推測にラベルを表示 |
| MEMORY／NOW／GUARDRAILS／INDEX | CLIで再生成可能 |
| 会話ログ・日次要約 | ターン取り込みと、指定日の要約生成を実装 |
| ローカル検索・重複検出・バックアップ | CLIで実行可能 |
| System更新・Migration | 配置・変更検出・バックアップ・schema移行の基盤を実装。下記の既知課題あり |
| ChatGPT／Claudeアプリからの初期構築 | `skills/pmo-setup/SKILL.md`を実装。各アプリでDriveの書き込み・読み戻し能力を実行時に確認する |
| クラウドでの記憶整理・更新提案・一覧更新 | 運用ルールは`START_HERE.md`へ集約。実際の書き込み・再生成能力は接続機能に依存 |
| Geminiなど他のAIとの連携 | 共通プロトコルを利用する将来の接続対象。動作保証なし |
| 全AIでの自動記憶・バックグラウンド処理 | 提供していない。個別の連携と保存方針が必要 |

現在、外部から原本を追加しても生成ビューや検索インデックスは自動更新されません。CLI運用では必要なときに`pmo rebuild`を実行します。定期ジョブを設定する必要はありません。

## 保存の仕組み

| 層 | 内容 | 所有・更新方針 |
|---|---|---|
| System | 共通プロトコル・schema・テンプレート | 配布版から配置。AIによる通常の記憶更新では変更しない |
| Config | 言語・保存・表示などの個人設定 | ユーザー所有。System更新時も維持する |
| Data | 記憶・訂正・プロジェクト・会話ログ | 私有の原本。System更新の上書き対象にしない |
| Runtime | 検索DB・ロックなど | ローカルの使い捨て領域。同期vaultの外に置く |

```text
PMO/
├─ START_HERE.md
├─ SYSTEM_VERSION.md
├─ MEMORY.md / NOW.md / GUARDRAILS.md / INDEX.md  # 再生成できる一覧
├─ _system/
├─ _config/
├─ 00_Inbox/
├─ 10_Memory/
│  ├─ Events/
│  └─ Corrections/
├─ 20_Projects/
├─ 30_Knowledge/
├─ 40_Decisions/
├─ 50_Daily/
└─ 80_Archive/
```

会話ログは`50_Daily/YYYY-MM-DD/<provider>_<session-id>_<topic>.md`へ分け、共有ファイルへの書き込み集中を減らします。これだけで同期競合がなくなるわけではなく、一覧の更新や同時書き込みには調整が必要です。

## ローカルCLIで試す

Python 3.11以上が必要です。このREADMEと`pyproject.toml`を含むブランチまたはリリースを取得し、私有vaultとは別のソースディレクトリで実行します。開発中のPRを試す場合は、そのPRのブランチをチェックアウトしてください。

```bash
python -m pip install .
pmo install /path/to/PMO
pmo record /path/to/PMO --type preference --content "例：回答は簡潔な日本語がよい"
pmo rebuild /path/to/PMO
pmo search /path/to/PMO "回答は簡潔な日本語がよい"
pmo doctor /path/to/PMO
```

`/path/to/PMO`は実際の保存先に置き換えます。Driveを使う場合、ローカルCLIには通常のファイルとして読み書きできるミラーが必要です。Obsidianで利用する場合も、この私有フォルダを開きます。

その他のコマンド：

```bash
pmo correct <vault> --wrong "..." --correct "..."
pmo ingest-turn <vault> turn.json
pmo daily <vault> YYYY-MM-DD
pmo status <vault>
pmo duplicates <vault>
pmo backup <vault>
pmo update <vault>
```

`ingest-turn`は、エージェントが構造化した記憶と会話ログを受け取る入口です。会話サービスへ自動接続したり、入力から記憶候補を自動抽出したりする機能ではありません。

## 設定・更新と現在の制約

`_config/settings.yaml`には、AI向けの希望とCLIが読む値が含まれます。タイムゾーン、推測の最低確信度、NOWの対象期間はCLIで参照します。言語指定はAI向けの指示であり、CLIの見出しは現在英語です。自動アーカイブなど、設定名があっても未実装の処理があります。

`pmo update`は**インストール済みのパッケージをvaultへ展開する操作**です。GitHubから最新版を取得する操作は含みません。先に選んだ版のパッケージを更新し、その後vaultを更新します。バックアップは標準でvaultの隣の`PMO-Backups`へ保存します。

検索DBは`~/.personal-memory-os/`配下に作成され、Markdownから再生成できます。原本を追加した後の検索には、明示的な`pmo rebuild`が必要です。

既知の残課題には、マニフェスト欠損時の更新保護、Windowsのタイムゾーン依存、ターン取り込みの部分保存・再試行、Dailyの同時更新があります。現在の版を、競合や更新失敗への対策が完成したものとしては扱わないでください。[仕様案と受け入れ条件](docs/local-optional-design.ja.md#実装状況と受け入れ条件)に整理しています。

## 開発と参加

自分の記憶は私有ストレージに置き、公開リポジトリやissueへ実際の記憶・会話の書き出し・認証情報を追加しないでください。

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
```

- [アーキテクチャ](docs/architecture.md) / [ストレージ契約](docs/storage-contract.md)
- [AI連携](docs/ai-integration.md) / [記憶プロトコル](docs/memory-protocol.md)
- [AIセットアップSKILL](skills/pmo-setup/SKILL.md) / [クラウド運用](docs/local-optional-design.ja.md) / [最小指示文](docs/custom-instructions.ja.md)
- [Contributing](CONTRIBUTING.md) / [Security](SECURITY.md)

## ライセンス

MIT。詳しくは[LICENSE](LICENSE)を参照してください。

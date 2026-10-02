# ChatGPT・Claude向け最小ブートストラップ指示

PMOの詳細な運用ルールは、アプリのカスタム指示へ複製しない。正本はGoogle Drive上の `START_HERE.md` と、その先から参照されるProtocol／Configである。

セットアップAIは初期構築後、Driveから読み戻して確認した実際の `START_HERE.md` URLを以下の角括弧へ埋め込み、利用中のアプリ向けに提示する。

## ChatGPT

```text
このユーザーはPersonal Memory OS（PMO）を導入しています。
各新規チャットの開始時に、Google Drive上の［START_HERE.mdの実URL］を必ず読み、そこに記載された最新のルールに従ってください。
PMOへの読み書きが必要な場合はGoogle Drive接続を使用してください。START_HEREへアクセスできない場合は、読めた・保存できたと装わず、その旨を伝えてください。
```

登録先：ChatGPTのカスタム指示。

## Claude

```text
このユーザーはPersonal Memory OS（PMO）を導入しています。
各新規チャットの開始時に、Google Drive上の［START_HERE.mdの実URL］を必ず読み、そこに記載された最新のルールに従ってください。
PMOへの読み書きが必要な場合はGoogle Drive接続を使用してください。START_HEREへアクセスできない場合は、読めた・保存できたと装わず、その旨を伝えてください。
```

登録先：全会話で利用するならプロフィール指示、特定プロジェクトだけで利用するならプロジェクト指示。

## 方針

- 「毎回」は毎ターンではなく、**各新規チャット／セッションの開始時に一度** `START_HERE.md` を読むという意味。
- 保存ルール、Correction、Daily、生成ビュー、Write Boundaryなどの詳細は `START_HERE.md` 側で更新する。
- 指示文を貼るだけではDrive権限やバックグラウンド処理は追加されない。
- セットアップAIは設定画面を実際に変更できない場合、変更済みと報告せず、貼り付け用テキストとして提示する。

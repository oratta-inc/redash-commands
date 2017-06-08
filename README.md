# redash-commands

## 概要
KPIツールRedashに対するユーティリティコマンドをまとめたプロジェクト。

----

## 環境構築方法
(サーバ配置時に記載予定)

----

## ディレクトリ構成

```
redash-commands/
├ documents/          このプロジェクトに対するドキュメント。
├ commands/           Redashに対するコマンドをまとめたディレクトリ。
├ config/             設定ファイルをまとめたディレクトリ。
├ lib/                コマンドの処理を実現するユーティリティクラスをまとめたディレクトリ。
├ tests/              テストケースをまとめたディレクトリ。
├ .github/            プルリクテンプレートなどをまとめたディレクトリ。
├ .editorconfig       editorconfig用の設定ファイル。
├ .gitignore
├ README.md
├ requirements.txt    このプロジェクトが依存するパッケージの一覧。
└ setup.cfg           このプロジェクトに関する設定。

```

----

## 各コマンド仕様

#### execute_queries コマンド

###### 概要
`execute_queries.py [options] [search_text] [file_format] [output_dir]`

search_textに合致するクエリをまとめて実行し、結果をoutput_dirに出力するコマンド。

* search_text: 検索したいテキスト。※Redashの仕様上、単語を空白で区切ったand検索やor検索はできない。
* file_format: 結果として出力するファイルフォーマット。現状csvのみ受け付ける。
* output_dir : 結果を出力するディレクトリ。

| オプション | 用途 |
|:-----------|:------------|
|-p --parameters|クエリ実行時のクエリパラメータ部分のkey-valueをまとめた文字列。以下に例を示す。<br/>'start_time:2017-01-01 00:00:00, end_time:2017-02-01 00:00:00'|
※ その他のオプションは、末尾の共通オプションを参照。

###### 実行例

```sh
# プレイヤー数に関するクエリをまとめて実行し、csv形式で保存する。日付部分のパラメタは置換する。
python3 ./commands/execute_queries.py -p 'start_time:2017-01-01 00:00:00, end_time:2017-02-01 00:00:00' 'プレイヤー数' csv ~/redash_queries_result
```

#### archive_queries コマンド

###### 概要
`archive_queries.py [options] [search_text]`

search_textに合致するクエリをまとめてアーカイブ(Redash上での削除)を行うコマンド。

* search_text: 検索したいテキスト。※Redashの仕様上、単語を空白で区切ったand検索やor検索はできない。

※ オプションは、末尾の共通オプションを参照。

###### 実行例

```sh
# プレイヤー数というキーワードを含むクエリを、まとめてアーカイブする。
python3 ./commands/archive_queries.py 'プレイヤー数'
```

#### fork_queries コマンド

###### 概要
`fork_queries.py [options] [search_text] [target_data_source_id]`

search_textに合致するクエリのコピーを、target_data_source_idしたデータソースに対してまとめて作成するコマンド。

* search_text: 検索したいテキスト。※Redashの仕様上、単語を空白で区切ったand検索やor検索はできない。
* target_data_source_id: コピー先となるデータソースのidを指定する。

※ オプションは、末尾の共通オプションを参照。

###### 実行例

```sh
# プレイヤー数というキーワードを含むクエリを、まとめてアーカイブする。
python3 ./commands/archive_queries.py 'プレイヤー数'
```

#### 全コマンドに共通する書式

###### オプション

| オプション | 用途 |
|:-----------|:------------|
|-a --api-key|接続に使うAPIキー。省略した場合config/connection_info.yamlファイルの設定値を使う。|
|-e --end-point|接続先のエンドポイント。省略した場合config/connection_info.yamlファイルの設定値を使う。|
|-l --log-dir|ログの出力先。省略した場合/tmpディレクトリ以下に出力する。|

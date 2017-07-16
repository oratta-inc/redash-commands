# redash-commands

## 概要
KPIツールRedashに対するユーティリティコマンドをまとめたプロジェクト。

----

## 環境構築方法
```sh
###
# リポジトリの初回設定
# (github上のアカウントに、サーバの公開鍵を登録しておくこと。)
###
git clone git@github.com:oratta-inc/redash-commands.git

# 設定ファイルに、Redashサーバの接続情報を記載する。
vi redash-commands/config/connection_info.yaml


###
# pyenvをインストールして、リポジトリ直下だけpython3.5.2が使えるようにする
###
git clone https://github.com/yyuu/pyenv.git ~/.pyenv

# bash_profileに以下を記載
#   export PYENV_ROOT=$HOME/.pyenv
#   export PATH=$PYENV_ROOT/bin:$PATH
#   eval "$(pyenv init -)"
vi ~/.bash_profile
source ~/.bash_profile

# 3.5.2をインストール&有効化
pyenv install 3.5.2
cd redash-commands
pyenv local 3.5.2


###
# virtualenvで、リポジトリが動作する環境を作る
###
pip install virtualenv
virtualenv command_env
source command_env/bin/activate
pip install -r requirements.txt
```

----

## ディレクトリ構成

```
redash-commands/
├ .circleci/          CircleCIの設定情報。
├ .github/            プルリクテンプレートなどをまとめたディレクトリ。
├ command/            各種コマンドスクリプトを配置したディレクトリ。
├ config/             設定ファイルをまとめたディレクトリ。
├ documents/          このプロジェクトに対するドキュメント。
├ lib/                各ユーティリティクラスをまとめたディレクトリ。
├ tests/              lib/以下に対するテストケースをまとめたディレクトリ。
├ .coveragerc         coverageモジュールによるカバレッジ集計に関する設定情報。
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

* search_text: 検索したいテキスト。
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

* search_text: 検索したいテキスト。

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

* search_text: 検索したいテキスト。
* target_data_source_id: コピー先となるデータソースのidを指定する。

※ オプションは、末尾の共通オプションを参照。

###### 実行例

```sh
# プレイヤー数というキーワードを含むクエリを、まとめて2番のデータソースにコピーする。
python3 ./commands/fork_queries.py 'プレイヤー数' 2
```

#### 全コマンドに共通する書式

###### オプション

| オプション | 用途 |
|:-----------|:------------|
|-a --api-key|接続に使うAPIキー。省略した場合config/connection_info.yamlファイルの設定値を使う。|
|-e --end-point|接続先のエンドポイント。省略した場合config/connection_info.yamlファイルの設定値を使う。|
|-l --log-dir|ログの出力先。省略した場合/tmpディレクトリ以下に出力する。|

----

## その他運用上の注意点
* Redashの仕様上、以下のような制約があるので注意。
    * search_textオプションでは、単語を空白で区切ったand検索やor検索はできない。
    * Publishしているクエリのみ、コマンドの実行対象となる。
    * TreasureDataのジョブ停止にはバグがあり、Redash上でジョブを停止しても、対応するTreasureData上のジョブは止まらない。。

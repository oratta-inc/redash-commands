# -*- coding: utf-8 -*-
u"""
以下クラスを提供するモジュール。

* BaseCommand
  ├ ExecuteQueriesCommand
  ├ ArchiveQueriesCommand
  └ ForkQueriesCommand
"""

from argparse import ArgumentParser, Namespace
from os import linesep
from os.path import dirname, join
from re import compile
from typing import Any, Dict, List

from lib.redash_util import ConnectionInfo, JobManager, QueryList

from yaml import load


def parse_parameter_string(parameter_string: str) -> Dict[str, Any]:
    u"""
    パラメータを表す文字列をパースして、辞書形式で返す。

    :param parameter_string: 各パラメータを、コロンとカンマで連結した文字列。
                             ex) 'date: 2017-01-01, table_name: hoge'
    :return: 各パラメータ情報を表す辞書。
             ex) {'date': '2017-01-01', 'table_name': 'hoge'}
    """
    if not parameter_string:
        return {}

    # この時点で、各要素に' date : 2017-01-01 00:00:00 'といった値が入る。
    key_and_values = parameter_string.split(u',')

    # 正規表現で、以下のように抽出する。
    #   key   コロン以外の文字列
    #   value 任意の文字列
    r = compile(r'^([^:]+):(.+)$')

    parameters_dict = {}
    for key_and_value in key_and_values:
        # 正規表現でマッチ部分を検索。
        m = r.search(key_and_value)

        if not m:
            raise ValueError()

        # 前後の空白を除去。
        key = m.group(1).strip()
        value = m.group(2).strip()

        parameters_dict[key] = value

    return parameters_dict


def parse_file_format(file_format: str) -> str:
    u"""
    ファイル拡張子を表す文字列の形式チェック & 先頭のカンマ部分の削除を行う。

    :param file_format: ファイルの拡張子。
    :return: ファイルの拡張子。
             先頭にカンマが付与されていた場合、削除する。
             また、期待する拡張子以外を文字列を指定した場合、ValueErrorを送出する。
    """
    r = compile(r'^(\.?)(.+)$')
    m = r.search(file_format)

    if not m:
        raise ValueError()
    if m.group(2) not in [u'csv', u'json', u'yml', u'yaml']:
        raise ValueError()

    return m.group(2)


class BaseCommand:
    u"""
    コマンド実行に関する処理を行う基底クラス。

    このクラスとその派生クラスは、以下の責務を持つ。
      * コマンド引数をパースし、このインスタンスのプロパティとして保持しておく。
      * YAMLファイルから接続情報をパースする(必要に応じて)。
      * redash_util内の各クラスを使って、コマンドの具体的な処理を実現する。

    このクラスでは、全ての派生クラスで共通のコマンド仕様を実装している。
    派生クラス側では、パーサへの引数の追加用メソッドや、executeメソッドなどを実装すること。

    TODO:
    このクラスは、多くの責務を持ち、多くの副作用を伴う処理を実行する。
    そのため、このクラス内の処理は、実装のレイヤに責務を持つクラスに委譲する必要がある。
    """

    def __init__(
        self,
        args: List[Any],
    ) -> None:
        """
        コンストラクタ。

        コマンド引数のパース、接続情報をYAMLからリード、委譲用のインスタンスの生成を行う。
        また、コマンドに渡す引数が誤っていた場合、内部で利用しているargparseモジュールの仕様に従い、
        コマンドの仕様例を出力して、SystemExit例外を送出する。
        :param args: コマンドラインから渡された引数(ただし、実行ファイル名を保持する0番目の要素は含まない)。
        """
        # インスタンス生成前のフック処理を実施する。
        self.before_init()

        # ArgumentParserインスタンスを生成し、このクラスのコマンド名とコマンド概要を登録する。
        self.parser = self.create_parser()

        # ArgumentParserインスタンスに、固定引数を追加。
        self.add_positional_arguments()

        # ArgumentParserインスタンスに、オプション引数を追加。
        self.add_optional_arguments()

        # コマンド引数を展開する。
        self.ns = self.parser.parse_args(args)

        # 接続情報をYamlファイルからパースする(コマンド引数に接続情報が含まれていない場合のみ)。
        self.load_connection_info_from_yaml()

        # 委譲で保持しておくべきインスタンスを生成する。
        self.connection_info\
            = ConnectionInfo(self.ns.end_point, self.ns.api_key)
        self.query_list = QueryList(self.connection_info)
        self.job_manager = JobManager()

        # インスタンス生成後のフック処理を実施する。
        self.after_init()

    def before_init(self) -> None:
        u"""
        コンストラクタ開始直後のフック用メソッド(派生クラス側で、必要に応じて実装すること)。

        :return:
        """
        pass

    def after_init(self) -> None:
        u"""
        コンストラクタ終了直後のフック用メソッド(派生クラス側で、必要に応じて実装すること)。

        :return:
        """
        pass

    def create_parser(self) -> 'ArgumentParser':
        u"""
        このクラスが内部で利用するパーサを生成する(派生クラス側でパーサにコマンドの仕様を渡す処理を実装すること)。

        :return:
        """
        return ArgumentParser()

    def add_positional_arguments(self) -> None:
        u"""
        このクラスがサポートするコマンド引数のうち、必須の固定引数をパーサに追加する。

        :return:
        """
        self.parser.add_argument(
            u'search_text',                           # パース時に展開される変数名。
            metavar=u'search-text',                   # ヘルプに表示する変数名。
            type=str,                                 # パース時に変換される型。
            help=u'検索条件となるテキストを指定します。',  # ヘルプに表示する文言。
        )

    def add_optional_arguments(self) -> None:
        """
        このクラスがサポートするコマンド引数のうち、任意のオプション引数をパーサに追加する。

        :return:
        """
        self.parser.add_argument(
            u'-a', u'--api-key',  # オプション引数。
            help=u'接続に使うAPIキーを指定します。'
                 + linesep
                 + u'省略した場合、config/connection_info.yamlファイルの設定値を使います。',
            dest=u'api_key',      # パース時に展開される変数名(オプション引数の場合)。
        )
        self.parser.add_argument(
            u'-e', u'--end-point',
            help=u'接続に使うAPIキーを指定します。'
                 + linesep
                 + u'省略した場合、config/connection_info.yamlファイルの設定値を使います。',
            dest=u'end_point',
        )
        self.parser.add_argument(
            u'-l', u'--log-dir',
            default=u'/tmp',  # 省略した場合のデフォルト値。
            help=u'ログの出力先を指定します。'
                 + linesep
                 + u'省略した場合、/tmpディレクトリ以下にログが出力されます。',
            dest=u'log_dir',
        )

    def load_connection_info_from_yaml(self) -> None:
        u"""
        Yamlファイルから、サーバへの接続情報を読み取る。

        コマンド引数にサーバへの接続情報が指定されていなかった場合のみ実行される。
        当然、ファイルの読み取りに失敗した場合はOSErrorが送出されるし、
        ファイル内にキーの設定が足りない場合はKeyErroが送出されるので注意。

        TODO:
        必ずconfigディレクトリ以下のyamlファイルから設定情報をreadするのは、
        仕様としてあまり好ましくないため、要改善である。
        :return:
        """
        if not self.ns.api_key or not self.ns.end_point:
            path = dirname(__file__) + u'/../../config/connection_info.yaml'
            with open(path, u'r') as file:
                con_info = load(file)
                self.ns.api_key   = con_info[u'api_key']
                self.ns.end_point = con_info[u'end_point']

    def execute(self) -> None:
        """
        このコマンドで行う業務ロジックを実行する(派生クラス側で処理を実装すること)。

        :return:
        """
        pass


class ExecuteQueriesCommand(BaseCommand):
    u"""execute_queriesコマンドに対応する処理を行うクラス。"""

    def create_parser(self) -> 'ArgumentParser':
        return ArgumentParser(
            prog=u'execute_queries.py',
            description=u'search_textに合致するクエリをまとめて実行し、結果をoutput_dirに出力します。'
        )

    def add_positional_arguments(self) -> None:
        super().add_positional_arguments()
        self.parser.add_argument(
            u'file_format',
            metavar=u'file-format',
            type=parse_file_format,
            help=u'結果として出力するファイルのフォーマットを指定します。',
        )
        self.parser.add_argument(
            u'output_dir',
            metavar=u'output-dir',
            type=str,
            help=u'結果の出力先を指定します。',
        )

    def add_optional_arguments(self) -> None:
        super().add_optional_arguments()
        self.parser.add_argument(
            u'-p', u'--parameters',
            type=parse_parameter_string,  # typeプロパティに、パース用の関数を渡すことができる。
            default=u'',
            help=u'クエリ実行時のクエリパラメータ部分のkey-valueをまとめた文字列。'
                 + u'以下のような形式で指定します。'
                 + linesep
                 + u'\'start_date:2017-01-01, end_date:2017-02-01\'',
            dest=u'parameters'
        )

    def execute(self) -> None:
        # 検索条件に合致するクエリを探し、QueryListにセットする。
        self.query_list.search_queries_by(self.ns.search_text)

        # クエリのパラメータ部分に実際の変数をバインドして、サーバ上のクエリを更新する。
        if self.ns.parameters:
            self.query_list.bind_values_in_bulk(self.ns.parameters)
            self.query_list.update_in_bulk()

        # 全てのクエリを実行する。
        job_list = self.query_list.execute_in_bulk()

        # バインドしたクエリを元に戻す。
        if self.ns.parameters:
            self.query_list.unbind_values_in_bulk()
            self.query_list.update_in_bulk()

        # 全てのジョブの状態を更新する。
        self.job_manager.add(job_list)
        while not self.job_manager.finished():
            self.job_manager.update()

        # ジョブと対応するQueryResultオブジェクト配列を、指定のファイルにシリアライズする。
        result_list = self.job_manager.get_query_result_list()
        for result in result_list:
            output_path = join(
                self.ns.output_dir,
                result.get_query_name() + u'.' + self.ns.file_format)
            result.serialize(output_path, self.ns.file_format)


class ArchiveQueriesCommand(BaseCommand):
    u"""archive_queriesコマンドに対応する処理を行うクラス。"""

    def create_parser(self) -> 'ArgumentParser':
        return ArgumentParser(
            prog=u'archive_queries.py',
            description=u'search_textに合致するクエリをまとめてアーカイブします。'
        )

    def execute(self) -> None:
        # 検索条件に合致するクエリを探し、QueryListにセットする。
        self.query_list.search_queries_by(self.ns.search_text)

        # 全てのクエリをアーカイブする。
        self.query_list.archive_in_bulk()


class ForkQueriesCommand(BaseCommand):
    u"""archive_queriesコマンドに対応する処理を行うクラス。"""

    def create_parser(self) -> 'ArgumentParser':
        return ArgumentParser(
            prog=u'fork_queries.py',
            description=u'search_textに合致するクエリを、'
                        + u'target_data_source_idしたデータソースに対してまとめてフォークします。'
        )

    def add_positional_arguments(self) -> None:
        super().add_positional_arguments()
        self.parser.add_argument(
            u'target_data_source_id',
            metavar=u'target-data-source-id',
            type=int,
            help=u'フォーク対象となるdata-sourceのidを指定します。',
        )

    def execute(self) -> None:
        # 検索条件に合致するクエリを探し、QueryListにセットする。
        self.query_list.search_queries_by(self.ns.search_text)

        # 全てのクエリをフォークする。
        fork_queries = self.query_list.fork_in_bulk()

        # フォークしたクエリを、新規のQueryListインスタンスに格納する。
        fork_query_list = QueryList(self.connection_info)
        fork_query_list.set_queries(fork_queries)

        # フォークしたクエリのdata_source_idを書き換えて、サーバ上のインスタンスを更新。
        fork_query_list.set_properties_in_bulk({
            u'data_source_id': self.ns.target_data_source_id})
        fork_query_list.update_in_bulk()

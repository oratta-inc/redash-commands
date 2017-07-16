# -*- coding: utf-8 -*-
u"""
以下クラスを提供するモジュール。

* Query
* QueryList
"""

from json import dumps, load
from os import path
from re import match, sub
from typing import Any, Dict, List, TYPE_CHECKING

from lib.file_io_util import list_files_in

from .gateway import Gateway
from .job import Job


if TYPE_CHECKING:
    from .connection_info import ConnectionInfo


class Query:
    u"""Redash上のクエリを表すクラス。"""

    def __init__(
        self,
        query_id: int=0,
        connection_info: 'ConnectionInfo'=None
    ) -> None:
        u"""
        コンストラクタ。

        :param id: Redash上でこのクエリを一意に識別するid。
        :param connection_info: 接続情報を保持するオブジェクト。
        """
        self.id = query_id
        self.__gateway = Gateway(connection_info)

        self.query = u''
        self.name = u''

        # パラメータに値がバインドされる前のSQL文字列。
        self.__original_query = ''
        # パラメータがバインド済みかどうかを判断するフラグ。
        self.__value_bind_flag = False

    def set_connection_info(self, connection_info: 'ConnectionInfo') -> None:
        u"""
        サーバへの接続情報を保持するオブジェクトをセットする。

        :param connection_info:
        :return:
        """
        self.__gateway.set_connection_info(connection_info)

    def read(self) -> None:
        u"""RedashサーバとAPI疎通し、プロパティをこのインスタンスにセットする。"""
        response = self.__gateway.get_query(self.id)
        self.set_properties(response.json())

    def update(self) -> None:
        u"""
        RedashサーバとAPI疎通し、このインスタンスに紐づくクエリのプロパティを更新する。

        :return:
        """
        update_properties = self.__extract_update_props_as_dict()
        self.__gateway.update_query(self.id, update_properties)

    def execute(self) -> 'Job':
        u"""
        RedashサーバとAPI疎通し、クエリを再実行する。

        :return: クエリの実行状態を保持するJobクラス。
        """
        response = self.__gateway.execute_query(self.id)
        return Job(
            job_id=response.json()[u'job'][u'id'],
            query_id=self.id,
            connection_info=self.__gateway.get_connection_info(),
            query_name=self.name)

    def fork(self) -> 'Query':
        u"""
        RedashサーバとAPI疎通し、Redash上にこのクエリのコピーを作成する。

        :return: コピーしたQueryインスタンス。
        """
        response = self.__gateway.fork_query(self.id)

        # 新規にQueryオブジェクトを作成して返す。
        fork_query = Query(
            connection_info=self.__gateway.get_connection_info())
        fork_query.set_properties(response.json())
        return fork_query

    def archive(self) -> None:
        u"""
        RedashサーバとAPI疎通し、このインスタンスに基づくクエリを削除(アーカイブ)する。

        :return:
        """
        self.__gateway.archive_query(self.id)

    def set_properties(self, properties: Dict[str, Any]) -> None:
        u"""
        このインスタンスに、プロパティをまとめてセットする。

        :param properties: プロパティ名と値をまとめた辞書。
        """
        for name, value in properties.items():
            setattr(self, name, value)

    def bind_values(self, key_and_values: Dict) -> None:
        u"""
        このインスタンスのクエリにおける、クエリパラメータ部分に、実際の値をバインドする。

        :param key_and_values: クエリパラメータのキーとバリューをまとめた辞書。
        """
        # 現在のSQLを、一旦以下のプロパティに保存しておく。
        if not self.__value_bind_flag:
            self.__original_query = self.query

        # SQL中の'{{ 変数名 }}'の箇所を、値に置き換える。
        for key, value in key_and_values.items():
            self.query = sub(r'{{ *' + key + ' *}}', value, self.query)

        # フラグをonにする。
        self.__value_bind_flag = True

    def unbind_values(self) -> None:
        u"""このインスタンスのクエリにおける、クエリパラメータ部分をバインドされていない状態に復元する。"""
        if self.__original_query:
            self.query = self.__original_query

        # フラグをoffにする。
        self.__value_bind_flag = False

    def is_bound(self) -> bool:
        u"""
        このインスタンスのクエリが、現在クエリパラメータに値がバインドされた状態かどうかを判定する。

        :return: 値がバインドされていればtrue。
        """
        return self.__value_bind_flag

    def serialize(self, file_path: str, file_format: str) -> None:
        u"""
        このインスタンスを、ファイルにシリアライズする。

        このメソッドは、以下の例外を送出する可能性がある。
        ・ValueError: ファイルフォーマットが不正な場合(現状json以外)。
        ・OSError: 引数で指定したファイルの読み取りに問題があった時。
                   (実際は、FileNotFoundErrorやPermissionErrorといった例外が送出される)。

        :param file_path: ファイルのパス。
        :param file_format: ファイルフォーマット。
        """
        self.__check_file_format_and_raise_exception(file_format)

        # このインスタンスのプロパティを走査し、publicなメンバ変数だけ辞書に詰める。
        tmp_dict = {}
        for key, value in self.__dict__.items():
            if match(r'^_Query.*', key):
                continue
            tmp_dict[key] = value

        # ファイルに書き出す(既に存在するファイルなら上書き)。
        with open(file_path, u'w') as file:
            file.write(dumps(tmp_dict))

    def deserialize(self, file_path: str, file_format: str) -> None:
        u"""
        ファイルの中身を読み込んで、このインスタンスのプロパティとしてセットする。

        このメソッドは、以下の例外を送出する可能性がある。
        ・ValueError: ファイルフォーマットが不正な場合(現状json以外)。
        ・OSError: 引数で指定したファイルの読み取りに問題があった時。
                   (実際は、FileNotFoundErrorやPermissionErrorといった例外が送出される)。

        :param file_path: ファイルのパス。
        :param file_format: ファイルフォーマット。
        """
        self.__check_file_format_and_raise_exception(file_format)

        with open(file_path, u'r') as file:
            properties = load(file)

        # TODO ファイル内のデータの形式チェックをすべきかもしれない。

        self.set_properties(properties)

    def get_name(self) -> str:
        u"""
        このクエリの、Redashサーバ上での名称を返す。

        :return:
        """
        return self.name

    def __extract_update_props_as_dict(self) -> Dict[Any, Any]:
        u"""
        更新対象となるプロパティを抽出する。

        :return: 更新対象となるプロパティ名と値を持つ辞書。
        """
        # 以下のプロパティを更新対象とする。
        props = [
            u'data_source_id',
            u'name',
            u'query',
            u'can_edit',
            u'description',
            u'is_archived',
            u'is_draft'
        ]
        ret = {}
        for name in props:
            value = getattr(self, name, None)
            if value is not None:
                ret[name] = value
        return ret

    def __check_file_format_and_raise_exception(
        self, file_format: str
    ) -> None:
        u"""
        ファイルのフォーマットをチェックし、問題があるならValueErrorを送出する。

        :param file_format:
        :return:
        """
        if file_format != u'json':
            raise ValueError()


class QueryList:
    u"""Redash上のクエリを表すクラス。"""

    def __init__(self, connection_info: 'ConnectionInfo'=None) -> None:
        u"""
        コンストラクタ。

        :param connection_info:
        """
        self.__gateway = Gateway(connection_info)
        self.__queries = []

    def set_connection_info(self, connection_info: 'ConnectionInfo') -> None:
        u"""
        サーバへの接続情報を保持するオブジェクトをセットする。

        :param connection_info:
        :return:
        """
        self.__gateway.set_connection_info(connection_info)

    def search_queries_by(self, text: str) -> List['Query']:
        u"""
        文字列でクエリを検索し、該当するQueryオブジェクトをこのインスタンスにセットする。

        :param text: 検索に使う文字列。
        :return: 検索条件に該当するQueryオブジェクトのリスト。
        """
        response = self.__gateway.search_queries(text)

        # サーバから得られた辞書のリストを、Queryオブジェクトのリストに変換する。
        search_queries = []
        for query_params in response.json():
            query = Query(connection_info=self.__gateway.get_connection_info())
            query.set_properties(query_params)
            search_queries.append(query)
        self.__queries += search_queries

        return search_queries

    def create_query(self, properties: Dict[str, Any]) -> 'Query':
        u"""
        新規にクエリを1件作成する。

        引数に必須のプロパティを渡さない場合、ValueErrorをスローする。
        :param properties:
        """
        # 必須のプロパティチェック。
        if u'data_source_id' not in properties:
            raise ValueError()

        # プロパティにデフォルト値を補う。
        default_props = {
            u'data_source_id': 0,
            u'query': u'',
            u'name': u'New Query',
            u'description': u'',
            u'schedule': u'',
            u'options': {}
        }
        merged_props = default_props.copy()
        merged_props.update(properties)

        # サーバと疎通して、Queryを生成する。
        response = self.__gateway.create_query(merged_props)

        # Queryオブジェクト生成。
        props = response.json()
        query = Query(connection_info=self.__gateway.get_connection_info())
        query.set_properties(props)

        return query

    def read_in_bulk(self) -> None:
        u"""RedashサーバとAPI疎通し、各クエリにプロパティをセットする。"""
        for query in self.__queries:
            query.read()

    def update_in_bulk(self) -> None:
        u"""RedashサーバとAPI疎通し、各クエリのプロパティを更新する。"""
        for query in self.__queries:
            query.update()

    def execute_in_bulk(self) -> List['Job']:
        u"""
        RedashサーバとAPI疎通し、各クエリを実行する。

        :return: ジョブのリスト。
        """
        jobs = []
        for query in self.__queries:
            job = query.execute()
            jobs.append(job)
        return jobs

    def fork_in_bulk(self) -> List['Query']:
        u"""
        RedashサーバとAPI疎通し、各クエリをフォークする。

        :return: フォークしたクエリのリスト。
        """
        fork_queries = []
        for query in self.__queries:
            fork_queries.append(query.fork())
        return fork_queries

    def archive_in_bulk(self) -> None:
        u"""RedashサーバとAPI疎通し、各クエリを削除(アーカイブ)する。"""
        for query in self.__queries:
            query.archive()

    def set_properties_in_bulk(self, properties: Dict[str, Any]) -> None:
        u"""
        各クエリに、引数で渡したプロパティをセットする。

        :param properties: プロパティ名と値をまとめた辞書。
        """
        for query in self.__queries:
            query.set_properties(properties)

    def bind_values_in_bulk(self, key_and_values: Dict) -> None:
        u"""
        各クエリのクエリパラメータ部分に、実際の値をバインドする。

        ※あるクエリが、対象のクエリパラメータを持たない場合は、値はバインドされない。
        :param key_and_values: クエリパラメータのキーとバリューをまとめた辞書。
        """
        for query in self.__queries:
            query.bind_values(key_and_values)

    def unbind_values_in_bulk(self) -> None:
        u"""各クエリのクエリパラメータ部分を、バインドされていない状態に復元する。"""
        for query in self.__queries:
            query.unbind_values()

    def serialize_in_bulk(self, dir_path: str, file_format: str) -> None:
        u"""
        各クエリを、ファイルにシリアライズする。

        :param dir_path: シリアライズするディレクトリのパス。
        :param file_format: ファイルフォーマット。
        """
        for query in self.__queries:
            query.serialize(
                path.join(dir_path, query.get_name() + '.' + file_format),
                file_format)

    def deserialize_in_bulk(
        self,
        dir_path: str,
        file_format: str,
        read_recursively: bool=True
    ) -> None:
        u"""
        指定したディレクトリからファイルをリードし、このインスタンスのクエリに追加する。

        :param dir_path: デシリアライズするディレクトリのパス。
        :param file_format: ファイルフォーマット。
        :param read_recursively: Trueの場合、指定したディレクトリ以下を再帰的に走査する。
        """
        files = list_files_in(dir_path, file_format, read_recursively)
        for file in files:
            query = Query(connection_info=self.__gateway.get_connection_info())
            query.deserialize(file, file_format)
            self.__queries.append(query)

    def set_queries(self, queries: List['Query']) -> None:
        u"""
        このインスタンスに、Queryのリストをセットする。

        :param queries:
        :return:
        """
        self.__queries += queries

    def get_queries(self) -> List['Query']:
        U"""
        このインスタンスが保持するQueryのリストを返す。

        :return:
        """
        return self.__queries

    def count(self) -> int:
        u"""
        このインスタンスが保持するQueryの件数を返す。

        :return:
        """
        return len(self.__queries)

# -*- coding: utf-8 -*-
u"""
以下クラスを提供するモジュール。

* RedashQuery
  └ NullRedashQuery
* RedashQueryList
  └ NullRedashQueryList
"""

from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .redash_job import RedashJob
    from .redash_connection_info import RedashConnectionInfo


class RedashQuery:
    u"""Redash上のクエリを表すクラス。"""

    def __init__(
        self,
        query_id: int=0,
        connection_info: RedashConnectionInfo=None
    ) -> None:
        u"""
        コンストラクタ。

        :param query_id: Redash上でこのクエリを一意に識別するid。
        :param connection_info: 接続情報を保持するオブジェクト。
        """
        pass

    def read(self) -> None:
        u"""RedashサーバとAPI疎通し、プロパティをこのインスタンスにセットする。"""
        pass

    def update(self) -> None:
        u"""RedashサーバとAPI疎通し、このインスタンスに紐づくクエリのプロパティを更新する。"""
        pass

    def execute(self) -> RedashJob:
        u"""
        RedashサーバとAPI疎通し、クエリを再実行する。

        :return RedashJob: クエリの実行状態を保持するジョブクラス。
        """
        pass

    def fork(self) -> RedashQuery: # noqa
        u"""
        RedashサーバとAPI疎通し、Redash上にこのクエリのコピーを作成する。

        :return RedashQuery:
        """
        pass

    def archive(self) -> None:
        u"""RedashサーバとAPI疎通し、このインスタンスに基づくクエリを削除(アーカイブ)する。"""
        pass

    def set_properties(self, properties: Dict) -> None:
        u"""
        このインスタンスに、プロパティをまとめてセットする。

        :param properties: プロパティ名と値をまとめた辞書。
        """
        pass

    def bind_values(self, key_and_values: Dict) -> None:
        u"""
        このインスタンスのクエリにおける、クエリパラメータ部分に、実際の値をバインドする。

        :param key_and_values: クエリパラメータのキーとバリューをまとめた辞書。
        """
        pass

    def unbind_values(self) -> None:
        u"""このインスタンスのクエリにおける、クエリパラメータ部分をバインドされていない状態に復元する。"""
        pass

    def is_bound(self) -> bool:
        u"""
        このインスタンスのクエリが、現在クエリパラメータに値がバインドされた状態かどうかを判定する。

        :return bool: 値がバインドされていればtrue。
        """
        pass

    def serialize(self, file_path: str, file_format: str) -> None:
        u"""
        このインスタンスを、ファイルにシリアライズする。

        :param file_path: ファイルのパス。
        :param file_format: ファイルフォーマット。
        """
        pass

    def deserialize(self, file_path: str, file_format: str) -> None:
        u"""
        ファイルの中身を読み込んで、このインスタンスのプロパティとしてセットする。

        :param file_path: ファイルのパス。
        :param file_format: ファイルフォーマット。
        """
        pass


class NullRedashQuery(RedashQuery):

    def __init__(
        self,
        query_id: int=0,
        connection_info: RedashConnectionInfo=None
    ) -> None:
        pass

    def read(self) -> None:
        pass

    def update(self) -> None:
        pass

    def execute(self) -> RedashJob:
        pass

    def fork(self) -> RedashQuery:
        pass

    def archive(self) -> None:
        pass

    def set_properties(self, properties: Dict) -> None:
        pass

    def bind_values(self, key_and_values: Dict) -> None:
        pass

    def unbind_values(self) -> None:
        pass

    def is_bound(self) -> bool:
        pass

    def serialize(self, file_path: str, file_format: str) -> None:
        pass

    def deserialize(self, file_path: str, file_format: str) -> None:
        pass


class RedashQueryList:
    u"""Redash上のクエリを表すクラス。"""

    def __init__(self, connection_info: RedashConnectionInfo=None) -> None:
        pass

    def search_queries_by(self, text: str) -> List[RedashQuery]:
        pass

    def create_query(self, properties) -> RedashQuery:
        pass

    def read_in_bulk(self) -> None:
        u"""RedashサーバとAPI疎通し、各クエリにプロパティをセットする。"""
        pass

    def update_in_bulk(self) -> None:
        u"""RedashサーバとAPI疎通し、各クエリのプロパティを更新する。"""
        pass

    def execute_in_bulk(self) -> List[RedashJob]:
        u"""
        RedashサーバとAPI疎通し、各クエリを実行する。

        :return: ジョブのリスト。
        """
        pass

    def archive_in_bulk(self) -> None:
        u"""RedashサーバとAPI疎通し、各クエリを削除(アーカイブ)する。"""
        pass

    def bind_values_in_bulk(self, key_and_values: Dict) -> None:
        u"""
        各クエリのクエリパラメータ部分に、実際の値をバインドする。

        ※あるクエリが、対象のクエリパラメータを持たない場合は、値はバインドされない。
        :param key_and_values: クエリパラメータのキーとバリューをまとめた辞書。
        """
        pass

    def unbind_values_in_bulk(self) -> None:
        u"""各クエリのクエリパラメータ部分を、バインドされていない状態に復元する。"""
        pass

    def serialize_in_bulk(self, dir_path: str, file_format: str) -> None:
        u"""
        各クエリを、ファイルにシリアライズする。

        :param dir_path: シリアライズするディレクトリのパス。
        :param file_format: ファイルフォーマット。
        """
        pass

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
        pass


class NullRedashQueryList:
    def __init__(self, connection_info: RedashConnectionInfo=None) -> None:
        pass

    def search_queries_by(self, text: str) -> List[RedashQuery]:
        pass

    def create_query(self, properties) -> RedashQuery:
        pass

    def read_in_bulk(self) -> None:
        pass

    def update_in_bulk(self) -> None:
        pass

    def execute_in_bulk(self) -> List[RedashJob]:
        pass

    def archive_in_bulk(self) -> None:
        pass

    def bind_values_in_bulk(self, key_and_values: Dict) -> None:
        pass

    def unbind_values_in_bulk(self) -> None:
        pass

    def serialize_in_bulk(self, dir_path: str, file_format: str) -> None:
        pass

    def deserialize_in_bulk(
        self,
        dir_path: str,
        file_format: str,
        read_recursively: bool=True
    ) -> None:
        pass

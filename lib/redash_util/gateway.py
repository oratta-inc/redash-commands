# -*- coding: utf-8 -*-
u"""
以下クラスを提供するモジュール。

* Gateway
"""
from json import dumps
from typing import Any, Callable, Dict

from requests import Response, delete, get, post

from .connection_info import ConnectionInfo


class Gateway:
    u"""
    Redashサーバとの実際のHTTP通信を行うクラス。

    概要:
    1. Redashの各APIをラップし、このライブラリ上で使いやすいインターフェースを提供する。
    2. どのメソッドも、requestsライブラリのResponseオブジェクトを戻り値として返す。
    3. HTTP通信で例外が発生した場合、requestsライブラリのRequestException系の例外を送出する。

    補足:
    ・このクラスは外部への公開を想定していないため、__init__.pyにimport処理を記載しないこと。
    ・このクラスは、HTTP通信処理が必要になるクラスの内部において、
      インスタンス生成 & ConnectionInfoオブジェクトを渡される使われ方を想定している。
      しかし、機能要件として一つのRedashサーバとしか疎通することが無さそうであれば、
      このクラスとConnectionInfoクラスをシングルトン化し、外部公開してもよいかもしれない。
      (この場合、テストや修正の容易性を考慮して、サービスロケータパターンを使って、
      取得するGatewayクラスの実体を切り替えられるようにしておくこと。)
    """

    def __init__(self, connection_info: 'ConnectionInfo'=None) -> None:
        u"""
        コンストラクタ。

        :param connection_info:
        """
        self.__con = None
        self.set_connection_info(connection_info)

    def set_connection_info(self, connection_info: 'ConnectionInfo') -> None:
        u"""
        サーバへの接続情報を保持するオブジェクトをセットする。

        :param connection_info:
        :return:
        """
        self.__con = connection_info

    def get_connection_info(self) -> 'ConnectionInfo':
        u"""
        サーバへの接続情報を保持するオブジェクトを返す。

        :param connection_info:
        :return:
        """
        return self.__con

    def get_query(self, query_id: int) -> 'Response':
        u"""
        サーバ上から、指定したidのクエリ一件を取得する。

        :param query_id:
        :return:
        """
        return self.__request(
            get,
            self.__make_url(u'/api/queries/' + str(query_id)),
            headers=self.__make_headers()
        )

    def update_query(
        self, query_id: int, properties: [str, Any]
    ) -> 'Response':
        u"""
        サーバ上で、指定したidのクエリのプロパティを更新する。

        :param query_id:
        :param properties: 更新対象となるプロパティ名と値をセットした辞書。
        :return:
        """
        return self.__request(
            post,
            self.__make_url(u'/api/queries/' + str(query_id)),
            headers=self.__make_headers(contents_type=u'json'),
            data=dumps(properties)
        )

    def execute_query(self, query_id: int) -> 'Response':
        u"""
        サーバ上で、指定したidのクエリを実行する。

        :param query_id:
        :return:
        """
        return self.__request(
            post,
            self.__make_url(u'/api/queries/' + str(query_id) + u'/refresh'),
            headers=self.__make_headers()
        )

    def create_query(self, properties: Dict[str, Any]) -> 'Response':
        u"""
        サーバ上で、引数で指定したプロパティを持つクエリを作成する。

        :param properties: プロパティ名と値をセットした辞書。
        :return:
        """
        return self.__request(
            post,
            properties,
            self.__make_url(u'/api/queries/'),
            headers=self.__make_headers(),
        )

    def fork_query(self, query_id: int) -> 'Response':
        u"""
        サーバ上で、指定したidのクエリをフォークする。

        :param query_id:
        :return:
        """
        return self.__request(
            post,
            self.__make_url(u'/api/queries/' + str(query_id) + u'/fork'),
            headers=self.__make_headers()
        )

    def archive_query(self, query_id: int) -> 'Response':
        u"""
        サーバ上で、指定したidのクエリをアーカイブする。

        :param query_id:
        :return:
        """
        return self.__request(
            delete,
            self.__make_url(u'/api/queries/' + str(query_id)),
            headers=self.__make_headers()
        )

    def search_queries(self, text: str) -> 'Response':
        u"""
        サーバと疎通し、引数で指定した文字列を含むクエリを返す。

        :param query_id:
        :return:
        """
        return self.__request(
            get,
            self.__make_url(u'/api/queries/search'),
            headers=self.__make_headers(),
            params={u'q': text}
        )

    def update_job_status(self, job_id: str) -> 'Response':
        u"""
        サーバと疎通し、引数で指定したidのJobを更新する。

        :param job_id:
        :return:
        """
        return self.__request(
            get,
            self.__make_url(u'/api/jobs/' + job_id),
            headers=self.__make_headers()
        )

    def get_query_result(self, query_result_id: int) -> 'Response':
        u"""
        サーバと疎通し、引数で指定したidのQueryResultを返す。

        :param query_result_id:
        :return:
        """
        return self.__request(
            get,
            self.__make_url(u'/api/query_results/' + str(query_result_id)),
            headers=self.__make_headers()
        )

    def kill_job(self, job_id: str) -> 'Response':
        u"""
        サーバと疎通し、引数で指定したidのジョブの実行を停止する。

        :param job_id:
        :return:
        """
        return self.__request(
            delete,
            self.__make_url(u'/api/jobs/' + job_id),
            headers=self.__make_headers()
        )

    def __make_url(self, url: str) -> str:
        u"""
        サーバと疎通するためのurlを生成する。

        :param url:
        :return:
        """
        return self.__con.get_end_point() + url

    def __make_headers(self, contents_type: str=u'') -> Dict[str, str]:
        u"""
        サーバと疎通するためのヘッダ情報を生成する。

        :param contents_type: コンテンツタイプを表す文字列(省略形)。
                              渡すべき値は、このメソッド内のcontents_type_tableを参照すること。
        :return:
        """
        # 認証用のヘッダは必ず付与する。
        header = {u'Authorization': u'Key ' + self.__con.get_api_key()}

        # contents_typeが指定されていれば、追加で付与する。
        contents_type_table = {u'json': u'application/json'}
        if contents_type in contents_type_table:
            header[u'Content-type'] = contents_type_table[contents_type]

        return header

    def __request(
        self,
        request_method: Callable[..., Response],
        *params: [Any],
        **keyword_params: Dict[str, Any]
    ) -> 'Response':
        u"""
        サーバへリクエストを行う。ステータスコードが200以外の場合は例外を送出する。

        :param request_method: 実際にリクエスト処理を行う関数。
        :param params: 第一引数の関数に渡す引数。
        :param keyword_params: 第一引数に渡す引数(キーワード付きの引数)。
        :return: Responseオブジェクト。
        """
        # 補足: *や**を実引数に付けると、リストや辞書の要素を展開し実引数として渡すことができる。
        response = request_method(*params, **keyword_params)
        response.raise_for_status()
        return response

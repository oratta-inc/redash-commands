# -*- coding: utf-8 -*-
u"""
以下クラスを提供するモジュール。

* QueryResult
"""

from os import linesep

from typing import Any, Dict


class QueryResult:
    u"""Redashでのクエリ実行結果を保持するクラス。"""

    def __init__(self, properties: Dict[str, Any]) -> None:
        u"""
        コンストラクタ。

        :param properties: プロパティ名と値をまとめた辞書。
        """
        for key, value in properties.items():
            setattr(self, key, value)

    def serialize(self, file_path: str, file_format: str) -> None:
        u"""
        このインスタンスを、ファイルにシリアライズする。

        :param file_path: ファイルのパス。
        :param file_format: ファイルフォーマット。
        """
        self.__check_file_format_and_raise_exception(file_format)

        with open(file_path, u'w') as file:
            file.write(self.__make_csv_serialize_data())

    def get_query_name(self) -> str:
        u"""
        このインスタンスに対応するQueryオブジェクトの名前を返す。

        :return:
        """
        return getattr(self, u'query_name', u'')

    def __check_file_format_and_raise_exception(
        self, file_format: str
    ) -> None:
        u"""
        ファイルのフォーマットをチェックし、問題があるならValueErrorを送出する。

        :param file_format:
        :return:
        """
        # 現状、csvのみサポート。
        if file_format != u'csv':
            raise ValueError()

    def __make_csv_serialize_data(self) -> str:
        u"""
        このインスタンスをcsvファイルとして出力するための文字列を作って返す。

        補足:
        ・実運用上の事情を考慮して、このインスタンスが持つdataプロパティの内容のみ抽出している。
        ・各行末尾に付与する改行コードは、各OSに準拠した改行コードを付与する(linesepの使用部分)。

        参考:
        csvファイルの一般的なフォーマットについては、以下リンクを参照した。
        http://itdoc.hitachi.co.jp/manuals/3020/30203698A0/swrj0068.htm
        :return:
        """
        if (u'columns' not in self.data) or (u'rows' not in self.data):
            return u''

        # ヘッダ行を作る。
        headers = u''
        for column_definition in self.data[u'columns']:
            headers += column_definition[u'name'] + u','
        # 末尾のカンマを改行文字に置換しておく。
        headers = headers[:-1] + linesep

        # 各レコードを作る。
        records = u''
        for column_values in self.data[u'rows']:
            for column_definition in self.data[u'columns']:
                column_name = column_definition[u'name']

                # 万一値がない場合は、カンマだけ付与。
                if column_name not in column_values:
                    records += u','
                    continue

                # 値を追加(文字列の場合、前後にダブルクォートを付与)。
                value = column_values[column_name]
                if type(value) is str:
                    value = u'"' + value + u'"'

                records += str(value) + u','

            # 末尾のカンマを改行文字に置換しておく。
            records = records[:-1] + linesep

        return headers + records


class NullQueryResult(QueryResult):
    def __init__(self, properties: Dict[str, Any]) -> None:
        u"""
        コンストラクタ。

        :param properties: プロパティ名と値をまとめた辞書。
        """
        # 引数で渡した辞書は参照せず、
        # 各プロパティにデフォルト値を設定する。
        self.id = 0
        self.data = {u'columns': [], 'rows': []}
        self.data_source_id = 0
        self.query_hash = u''
        self.query = u''
        self.retrieved_at = u''
        self.runtime = 0.0

    def serialize(self, file_path: str, file_format: str) -> None:
        u"""
        Nullオブジェクトなので、何もしない。

        :param file_path: ファイルのパス。
        :param file_format: ファイルフォーマット。
        """
        pass

    def get_query_name(self) -> str:
        u"""
        Nullオブジェクトなので、空文字列を返す。

        :return:
        """
        return u''

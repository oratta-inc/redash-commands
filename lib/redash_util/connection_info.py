# -*- coding: utf-8 -*-
u"""
以下クラスを提供するモジュール。

* ConnectionInfo
"""


class ConnectionInfo:
    u"""Redashサーバとの接続時の情報を凝集・カプセル化するためのクラス。"""

    def __init__(self, end_point: str='', api_key: str='') -> None:
        u"""
        コンストラクタ。

        :param end_point: 接続時のエンドポイント。
        :param api_key: ユーザ単位で発行されるAPIキー。
        """
        self.end_point = end_point
        self.api_key   = api_key

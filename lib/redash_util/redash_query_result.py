# -*- coding: utf-8 -*-
u"""
以下クラスを提供するモジュール。

* RedashQueryResult
  └NullRedashQueryResult
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .redash_job import RedashJob


class RedashQueryResult:
    u"""Redashでのクエリ実行結果を保持するクラス。"""

    def __init__(self, job: RedashJob) -> None:
        u"""
        コンストラクタ。

        :param job: 対応するジョブインスタンス。
        """
        pass

    def serialize(self, file_path: str, file_format: str) -> None:
        u"""
        このインスタンスを、ファイルにシリアライズする。

        :param file_path: ファイルのパス。
        :param file_format: ファイルフォーマット。
        """
        pass


class NullRedashQueryResult(RedashQueryResult):
    def __init__(self, job: RedashJob) -> None:
        pass

    def serialize(self, file_path: str, file_format: str) -> None:
        pass

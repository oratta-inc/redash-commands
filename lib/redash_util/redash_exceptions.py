# -*- coding: utf-8 -*-
u"""
以下クラスを提供するモジュール。

* RedashException
  └ RedashJobException
    └ RedashJobFailureException
"""


class RedashException(OSError):
    u"""Redashでの処理実行時に発生する例外クラス。"""

    pass


class RedashJobException(RedashException):
    u"""Redashのジョブに関する例外クラス。"""

    pass


class RedashJobFailureException(RedashJobException):
    u"""Redashのジョブ失敗時にスローされる例外クラス。"""

    pass

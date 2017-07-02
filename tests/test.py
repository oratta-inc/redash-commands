# -*- coding: utf-8 -*-
u"""
テストを一括実行するためのスクリプト。

coverageなどの外部ツールからまとめてテストを実行する場合、
このスクリプトをテスト対象に指定する。
"""

from unittest import TestLoader, TextTestRunner

if __name__ == u'__main__':
    loader = TestLoader()
    suite = loader.discover(u'.', u'test*.py')
    runner = TextTestRunner()
    runner.run(suite)

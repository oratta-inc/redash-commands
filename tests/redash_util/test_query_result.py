# -*- coding: utf-8 -*-
u"""queryモジュールに対するテストをまとめたモジュール。"""

from os import linesep

from unittest import TestCase

from lib.redash_util import QueryResult

from testfixtures import TempDirectory


class QueryResultTest(TestCase):
    u"""QueryResultクラスに対するテストをまとめたクラス。"""

    def tearDown(self):
        TempDirectory.cleanup_all()

    def test_serialize_to_csv_case(self):
        # ダミーのQueryResultインスタンスを作る。
        query_result = QueryResult({
            u'id': 1,
            u'data_source_id': 1,
            u'query': u'SELECT col1, col2 FROM sample_table;',
            u'data': {
                u'columns': [
                    {
                        u'friendly_name': u'col1',
                        u'name': u'col1',
                        u'type': u'string'
                    },
                    {
                        u'friendly_name': u'col2',
                        u'name': u'col2',
                        u'type': u'integer'
                    },
                ],
                u'rows': [
                    {
                        u'col1': 'value1',
                        u'col2': 1,
                    },
                    {
                        u'col1': 'value2',
                        u'col2': 2,
                    },
                ],
            }})

        # csvファイルにシリアライズする。
        temp_dir = TempDirectory()
        query_result.serialize(temp_dir.path + u'/sample_data.csv', u'csv')

        # 以下のように、dataカラム内の内容だけ、csvファイルとしてシリアライズされている。
        expected_data = u'col1,col2' + linesep \
                        + u'"value1",1' + linesep \
                        + u'"value2",2' + linesep
        file_raw_data = temp_dir.read(
            temp_dir.path + u'/sample_data.csv', encoding=u'utf-8')
        self.assertEqual(file_raw_data, expected_data)

        temp_dir.cleanup()

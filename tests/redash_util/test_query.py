# -*- coding: utf-8 -*-
u"""queryモジュールに対するテストをまとめたモジュール。"""

from json import dumps, loads
from unittest import TestCase
from unittest.mock import patch

from lib.redash_util import ConnectionInfo, Job, Query, QueryList
from lib.test_util import ResponseMock

from requests import RequestException

from testfixtures import TempDirectory


class QueryTest(TestCase):
    u"""Queryクラスに対するテストをまとめたクラス。"""

    def setUp(self):
        self.con = ConnectionInfo(
            end_point=u'https://dummy.endpoint',
            api_key=u'dummy api key'
        )

    def tearDown(self):
        TempDirectory.cleanup_all()

    @patch(
        u'lib.redash_util.gateway.Gateway.get_query',
        return_value=ResponseMock({
            u'id': 1,
            u'data_source_id': 1,
            u'name': u'sample query',
            u'query': u'SELECT * FROM sample_table',
        }, 200)
    )
    def test_read_normal_case(self, mock_method):
        query = self.__create_query(1)
        query.read()

        self.assertEqual(query.id, 1)
        self.assertEqual(query.data_source_id, 1)
        self.assertEqual(query.name, u'sample query')
        self.assertEqual(query.query, u'SELECT * FROM sample_table')

    @patch(
        u'lib.redash_util.gateway.Gateway.update_query',
        return_value=ResponseMock({}, 200)
    )
    def test_update_normal_case(self, mock_method):
        query = self.__create_query(1)
        query.set_properties({u'query': u'SELECT * FROM sample_table'})

        try:
            query.update()
        except RequestException:
            self.assertTrue(False)

        # プログラム上では特に変化が起こらないため、例外が発生しなければOKとする。
        self.assertTrue(True)

    @patch(
        u'lib.redash_util.gateway.Gateway.execute_query',
        return_value=ResponseMock({
            u'job': {
                u'id': '752f5afc-ce7e-4d6a-aded-7e33dc8efa28',
                u'query_result_id': None,
                u'status': 2,
                u'error': '',
                u'updated_at': 0
            }
        }, 200)
    )
    def test_execute_normal_case(self, mock_method):
        query = self.__create_query(1)
        query.set_properties({u'query': u'SELECT * FROM sample_table'})

        try:
            job = query.execute()
        except RequestException:
            self.assertTrue(False)

        # 例外が発生せず、Jobインスタンスが返ればOK。
        self.assertIsInstance(job, Job)

    @patch(
        u'lib.redash_util.gateway.Gateway.fork_query',
        return_value=ResponseMock({
            u'id': 2,
            u'data_source_id': 1,
            u'name': u'sample query',
            u'query': u'SELECT * FROM sample_table;',
        }, 200)
    )
    def test_fork_normal_case(self, mock_method):
        query = self.__create_query(1)

        try:
            forked_query = query.fork()
        except RequestException:
            self.assertTrue(False)

        self.assertIsInstance(forked_query, Query)
        self.assertEqual(forked_query.id, 2)

    @patch(
        u'lib.redash_util.gateway.Gateway.archive_query',
        return_value=ResponseMock(None, 200)
    )
    def test_archive_normal_case(self, mock_method):
        query = self.__create_query(1)

        try:
            query.archive()
        except RequestException:
            self.assertTrue(False)

        # プログラム上では特に変化が起こらないため、例外が発生しなければOKとする。
        self.assertTrue(True)

    def test_bind_values_normal_case(self):
        # パラメータ付きのQueryオブジェクトを生成する。
        # (パラメータ部分が任意個の空白を含んでいる点に注目。)
        sql = u'SELECT {{platform_column}}' \
              u'FROM {{table}}' \
              u'WHERE {{  platform_column }} = "ios";'
        query = self.__create_query(1)
        query.set_properties({u'query': sql})

        # 対象メソッドを実行する。
        # ('table'キーがタイポしている点に注目。)。
        query.bind_values({
            u'platform_column': u'user_agent',
            u'tabl': u'dau'
        })

        # バインド後のSQLが設定される。
        expected_query = u'SELECT user_agent' \
                         u'FROM {{table}}' \
                         u'WHERE user_agent = "ios";'
        self.assertEqual(query.query, expected_query)
        self.assertTrue(query.is_bound())

        # 何度対象メソッドを呼んでもパラメータを持つ箇所はバインドされるし、
        # queryの状態(is_bound)も変わらない。
        query.bind_values({u'other_key': u'other_value'})
        self.assertEqual(query.query, expected_query)
        self.assertTrue(query.is_bound())

    def test_unbind_values_normal_case(self):
        # パラメータ付きのQueryオブジェクトを生成する。
        sql = u'SELECT {{platform_column}}' \
              u'FROM {{table}}' \
              u'WHERE {{  platform_column  }} = "ios";'
        query = self.__create_query(1)
        query.set_properties({u'query': sql})

        # 値がバインドされていない状態で対象メソッドを実行しても、
        # 特に例外などは発生しない(呼び出し側で状態を気にする必要はない)。
        query.unbind_values()
        self.assertFalse(query.is_bound())

        # 何度値をバインドしても、対象メソッドを呼べば元に戻る。
        query.bind_values({u'platform': u'user_agent'})
        query.bind_values({u'table': u'dau'})
        query.unbind_values()
        self.assertEqual(query.query, sql)
        self.assertFalse(query.is_bound())

    def test_serialize_normal_case(self):
        sample_data = self.__create_dict_for_file_io_test()
        temp_dir = TempDirectory()

        query = Query()
        query.set_properties(sample_data)
        query.serialize(temp_dir.path + u'/query.json', u'json')

        file_raw_data = temp_dir.read(
            temp_dir.path + u'/query.json', encoding=u'utf-8')
        self.assertEqual(loads(file_raw_data), sample_data)

        temp_dir.cleanup()

    def test_serialize_os_error_case(self):
        sample_data = self.__create_dict_for_file_io_test()

        query = Query()
        query.set_properties(sample_data)

        with self.assertRaises(OSError):
            query.serialize(u'/not_found_file.json', u'json')

    def test_deserialize_normal_case(self):
        sample_data = self.__create_dict_for_file_io_test()

        temp_dir = TempDirectory()
        temp_dir.write(u'query.json', dumps(sample_data), encoding=u'utf-8')

        query = Query()
        query.deserialize(temp_dir.path + u'/query.json', u'json')

        self.assertEqual(getattr(query, u'id'), sample_data[u'id'])
        self.assertEqual(getattr(query, u'options'), sample_data[u'options'])

        temp_dir.cleanup()

    def test_deserialize_os_error_case(self):
        query = Query()
        with self.assertRaises(OSError):
            query.deserialize(u'/not_found_file.json', u'json')

    def __create_query(self, query_id):
        return Query(query_id=query_id, connection_info=self.con)

    def __create_dict_for_file_io_test(self):
        u"""
        ファイルへのシリアライズ・デシリアライズのテストに使う、ダミーの辞書を生成して返す。

        :return:
        """
        return {
            u'id': 1,
            u'data_source_id': 1,
            u'name': u'クエリ1',
            u'query': u'SELECT 1;',
            # 以下のような深いプロパティを1つ用意して、
            # 正しくシリアライズ・デシリアライズされるか確かめる。
            u'options': {
                u'parameters': [
                    {
                        u'global': False,
                        u'title': u'columns',
                        u'value': u'id, name',
                        u'name': u'columns',
                        u'type': u'text'
                    },
                    {
                        u'global': False,
                        u'title': u'table_name',
                        u'value': u'sample_table',
                        u'name': u'table_name',
                        u'type': u'text'
                    }
                ]
            },
        }


class QueryListTest(TestCase):
    u"""QueryListクラスに対するテストをまとめたクラス。"""

    def setUp(self):
        self.con = ConnectionInfo(
            end_point=u'https://dummy.endpoint',
            api_key=u'dummy api key'
        )

    def tearDown(self):
        TempDirectory.cleanup_all()

    @patch(
        u'lib.redash_util.gateway.Gateway.search_queries',
        return_value=ResponseMock([
            {u'data_source_id': 1, u'id': 1, u'name': u'dau1', },
            {u'data_source_id': 2, u'id': 1, u'name': u'dau2', },
        ], 200)
    )
    def test_search_queries_by_normal_case(self, mock_method):
        query_list = self.__create_empty_list()
        query_list.search_queries_by(u'dau')
        self.assertEqual(query_list.count(), 2)

    @patch(
        u'lib.redash_util.gateway.Gateway.search_queries',
        return_value=ResponseMock([], 200)
    )
    def test_search_queries_by_empty_case(self, mock_method):
        query_list = self.__create_empty_list()
        query_list.search_queries_by(u'dau')
        self.assertEqual(query_list.count(), 0)

    @patch(
        u'lib.redash_util.gateway.Gateway.create_query',
        return_value=ResponseMock({
            u'id': 1,
            u'data_source_id': 1,
            u'name': u'new query',
            u'query': u'SELECT 1;',
            u'description': u'',
            u'schedule': u'',
            u'options': {},
        }, 200)
    )
    def test_create_query_normal_case(self, mock_method):
        query_list = self.__create_empty_list()
        query = query_list.create_query({
            u'name': u'new query',
            u'data_source_id': 1,
            u'query': u'SELECT 1;'
        })

        # サーバに生成されたクエリに対応するQueryインスタンスが返る。
        self.assertIsInstance(query, Query)

        # QueryListクラスには、クエリが追加されない。
        self.assertEqual(query_list.count(), 0)

    def test_create_query_exception_case(self):
        query_list = self.__create_empty_list()
        with self.assertRaises(ValueError):
            # 必須プロパティが欠けた辞書を渡す。
            query_list.create_query({
                u'name': u'new query',
                u'query': u'SELECT 1;'
            })

    @patch(u'lib.redash_util.query.Query.read')
    def test_read_in_bulk_normal_case(self, mock_method):
        query_list = self.__create_list_with_queries()
        query_list.read_in_bulk()
        mock_method.assert_called_with()

    @patch(u'lib.redash_util.query.Query.update')
    def test_update_in_bulk_normal_case(self, mock_method):
        query_list = self.__create_list_with_queries()
        query_list.update_in_bulk()
        mock_method.assert_called_with()

    @patch(u'lib.redash_util.query.Query.execute')
    def test_execute_in_bulk_normal_case(self, mock_method):
        query_list = self.__create_list_with_queries()
        query_list.execute_in_bulk()
        mock_method.assert_called_with()

    @patch(u'lib.redash_util.query.Query.archive')
    def test_archive_in_bulk_normal_case(self, mock_method):
        query_list = self.__create_list_with_queries()
        query_list.archive_in_bulk()
        mock_method.assert_called_with()

    @patch(u'lib.redash_util.query.Query.bind_values')
    def test_bind_values_in_bulk_normal_case(self, mock_method):
        query_list = self.__create_list_with_queries()
        query_list.bind_values_in_bulk({'key': 'value'})
        mock_method.assert_called_with({'key': 'value'})

    @patch(u'lib.redash_util.query.Query.unbind_values')
    def test_unbind_values_in_bulk_normal_case(self, mock_method):
        query_list = self.__create_list_with_queries()
        query_list.unbind_values_in_bulk()
        mock_method.assert_called_with()

    @patch(u'lib.redash_util.query.Query.serialize')
    def test_serialize_in_bulk_normal_case(self, mock_method):
        query_list = self.__create_list_with_queries()
        query_list.serialize_in_bulk(u'/tmp/queries', u'json')
        mock_method.assert_any_call(u'/tmp/queries/クエリ1.json', u'json')
        mock_method.assert_any_call(u'/tmp/queries/クエリ2.json', u'json')

    @patch(
        u'lib.redash_util.query.Query.deserialize',
        return_value=Query()
    )
    def test_deserialize_in_bulk_test_single_dir_case(self, mock_method):
        temp_dir = self.__create_dummy_query_files()
        query_list = self.__create_empty_list()
        query_list.deserialize_in_bulk(
            temp_dir.path + u'/dir1/', u'json', read_recursively=False)

        # 対象ディレクトリのjsonファイルに対して、deserializeが呼ばれることを確認。
        mock_method.assert_any_call(
            temp_dir.path + u'/dir1/query1.json', u'json')
        mock_method.assert_any_call(
            temp_dir.path + u'/dir1/query2.json', u'json')

        self.assertEqual(query_list.count(), 2)

        temp_dir.cleanup()

    @patch(
        u'lib.redash_util.query.Query.deserialize',
        return_value=Query()
    )
    def test_deserialize_in_bulk_test_recursive_dir_case(
        self, mock_method
    ):
        temp_dir = self.__create_dummy_query_files()
        query_list = self.__create_empty_list()
        query_list.deserialize_in_bulk(
            temp_dir.path + u'/dir1', u'json', read_recursively=True)

        # 対象ディレクトリを再帰的に走査して、jsonファイルに対しdeserializeが呼ばれることを確認。
        mock_method.assert_any_call(
            temp_dir.path + u'/dir1/query1.json', u'json')
        mock_method.assert_any_call(
            temp_dir.path + u'/dir1/query2.json', u'json')
        mock_method.assert_any_call(
            temp_dir.path + u'/dir1/dir2/dir3/query4.json', u'json')

        self.assertEqual(query_list.count(), 3)

        temp_dir.cleanup()

    def __create_list_with_queries(self, count=2):
        u"""
        ダミーのQueryインスタンスを設定済みの、QueryListインスタンスを返す。

        :param count: ダミーのクエリを何件生成するか。
        :return: QueryListインスタンス。
        """
        query_list = QueryList(connection_info=self.con)
        queries = []
        for i in range(1, count + 1):
            query = Query()
            query.set_properties({
                u'id': i,
                u'name': u'クエリ' + str(i),
                u'query': u'SELECT ' + str(i) + ';',
            })
            queries.append(query)
        query_list.set_queries(queries)
        return query_list

    def __create_empty_list(self):
        return QueryList(connection_info=self.con)

    def __create_dummy_query_files(self):
        u"""
        deserialize処理のテスト用に、以下のようなダミーのディレクトリを生成する。

        dir1
        ├ query1.json
        ├ query2.json
        └ dir2
          ├ query3.csv
          └ dir3
            └ query4.json
        :return: ダミーのディレクトリ情報を保持するオブジェクト。
        """
        temp_dir = TempDirectory()
        temp_dir.write(
            u'dir1/query1.json',
            dumps({
                u'id': 1,
                u'data_source_id': 1,
                u'name': u'クエリ1',
                u'query': u'SELECT 1;', }),
            encoding=u'utf-8')
        temp_dir.write(
            u'dir1/query2.json',
            dumps({
                u'id': 2,
                u'data_source_id': 1,
                u'name': u'クエリ2',
                u'query': u'SELECT 2;', }),
            encoding=u'utf-8')
        temp_dir.write(
            u'dir1/dir2/query3.csv',
            u'id,data_source_id,name,query\n3,1,"クエリ3","SELECT 4;"',
            encoding=u'utf-8')
        temp_dir.write(
            u'dir1/dir2/dir3/query4.json',
            dumps({
                u'id': 4,
                u'data_source_id': 1,
                u'name': u'クエリ4',
                u'query': u'SELECT 4;', }),
            encoding=u'utf-8')
        return temp_dir

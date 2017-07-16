# -*- coding: utf-8 -*-
u"""commandsパッケージに対するテストをまとめたモジュール。"""

from unittest import TestCase
from unittest.mock import patch

from lib.command import \
    ArchiveQueriesCommand,\
    BaseCommand,\
    ExecuteQueriesCommand,\
    ForkQueriesCommand
from lib.redash_util import Job, NullQueryResult


class BaseCommandTest(TestCase):
    u"""BaseCommandクラスに対するテストをまとめたクラス。"""

    def test_init_full_arguments_case(self):
        u"""
        必要なコマンド引数を全て渡すテスト(正常ケース)。

        :return:
        """
        # コマンドインスタンスを生成する。
        # (内部で、引数のパースが行われれる)。
        command = BaseCommand([
            u'sample_text',
            u'--api-key',
            u'dummy api key',
            u'--end-point',
            u'https://dummy.endpoint',
            u'--log-dir',
            u'/tmp/kpi_data',
        ])

        # executeメソッドをコールしても、何も起こらない(派生クラス側に処理を書く)。
        command.execute()

        # Namespaceオブジェクトを取得。
        ns = command.ns

        # コマンド引数に渡した値がNamespaceオブジェクトに設定されている。
        self.assertEqual(u'sample_text', ns.search_text)
        self.assertEqual(u'dummy api key', ns.api_key)
        self.assertEqual(u'https://dummy.endpoint', ns.end_point)
        self.assertEqual(u'/tmp/kpi_data', ns.log_dir)

    def test_init_full_arguments_with_short_options_case(self):
        u"""
        必要なコマンド引数を全て渡すテスト(省略型のオプション引数を付与するケース)。

        :return:
        """
        command = BaseCommand([
            u'sample_text',
            u'-a',
            u'dummy api key',
            u'-e',
            u'https://dummy.endpoint',
            u'-l',
            u'/tmp/log',
        ])

        # 省略形を渡した場合でも、正しくプロパティが設定されることを確認。
        ns = command.ns
        self.assertEqual(u'sample_text', ns.search_text)
        self.assertEqual(u'dummy api key', ns.api_key)
        self.assertEqual(u'https://dummy.endpoint', ns.end_point)
        self.assertEqual(u'/tmp/log', ns.log_dir)

    def test_init_omit_arguments_case(self):
        u"""
        必要なコマンド引数を省略するケース(正常ケース)。

        TODO:
        --api-keyオプションと--end-pointオプションを
        省略するテストケースが網羅できていない。
        (必ず、config以下の設定ファイルにアクセスする仕様のため。)
        :return:
        """
        # 全ての任意オプションを外してコマンドインスタンスを生成。
        command = BaseCommand([
            u'sample_text',
            u'--api-key',
            u'dummy api key',
            u'--end-point',
            u'https://dummy.endpoint',
        ])
        ns = command.ns

        self.assertEqual(u'sample_text', ns.search_text)
        self.assertEqual(u'dummy api key', ns.api_key)
        self.assertEqual(u'https://dummy.endpoint', ns.end_point)

        # デフォルトのログ出力先は/tmp以下。
        self.assertEqual(u'/tmp', ns.log_dir)

    @patch('lib.command.command.ArgumentParser.error')
    def test_init_unnecessary_option_case(self, error_method):
        u"""
        存在しない無駄オプションを渡し、エラーになるケース。

        :return:
        """
        # ArgumentParserクラスのerrorメソッドは、SystemExitを送出する他、
        # 標準出力にコマンドのUsageを出力してしまう副作用がある。
        # テスト時はこの副作用を取り除くため、errorメソッドをpatchして、擬似的にSystemExitを送出する。
        # (以後のテストケースでも、同様の手法を取る。)
        error_method.side_effect = SystemExit(u'')

        try:
            BaseCommand([
                u'sample_text',
                u'unnecessary_option',
            ])
            self.assertTrue(False)
        except BaseException as e:
            self.assertTrue(True)
            pass

    @patch('lib.command.command.ArgumentParser.error')
    def test_init_insufficient_option_case(self, error_method):
        u"""
        必須オプションが足りず、エラーになるケース。

        :return:
        """
        error_method.side_effect = SystemExit(u'')

        try:
            BaseCommand([])
            self.assertTrue(False)
        except BaseException as e:
            self.assertTrue(True)


class ExecuteQueriesCommandTest(TestCase):
    u"""ExecuteQueriesCommandクラスに対するテストをまとめたクラス。"""

    def test_init_full_arguments_case(self):
        u"""
        必要なコマンド引数を全て渡すテスト(正常ケース)。

        :return:
        """
        command = ExecuteQueriesCommand([
            u'sample_text',
            u'csv',
            u'/tmp/query_data',
            u'--parameters',
            u' start_time : 2017-01-01 00:00:00,'
            u' end_time: 2017-02-01 00:00:00  ',
            u'--api-key',
            u'dummy api key',
            u'--end-point',
            u'https://dummy.endpoint',
            u'--log-dir',
            u'/tmp/kpi_data',
        ])
        ns = command.ns

        # 固定引数には、以下のような値が入る。
        self.assertEqual(u'sample_text', ns.search_text)
        self.assertEqual(u'csv', ns.file_format)
        self.assertEqual(u'/tmp/query_data', ns.output_dir)

        # --parametersオプションを省略した場合、空文字列が返る。
        self.assertEqual({
            u'start_time': u'2017-01-01 00:00:00',
            u'end_time': u'2017-02-01 00:00:00',
        }, ns.parameters)

        # その他のオプションは、基底クラスと同じ挙動をする。
        self.assertEqual(u'dummy api key', ns.api_key)
        self.assertEqual(u'https://dummy.endpoint', ns.end_point)
        self.assertEqual(u'/tmp/kpi_data', ns.log_dir)

    def test_init_omit_arguments_case(self):
        u"""
        --parameterオプションを省略するケース(正常ケース)。

        :return:
        """
        command = ExecuteQueriesCommand([
            u'sample_text',
            u'csv',
            u'/tmp/query_data',
            u'--api-key',
            u'dummy api key',
            u'--end-point',
            u'https://dummy.endpoint',
            u'--log-dir',
            u'/tmp/kpi_data',
        ])
        ns = command.ns

        # --parametersオプションを省略した場合、空文字列が返る。
        self.assertEqual({}, ns.parameters)

    @patch('lib.command.command.ArgumentParser.error')
    def test_init_insufficient_option_case(self, error_method):
        u"""
        必須オプションが足りず、エラーになるケース。

        :return:
        """
        error_method.side_effect = SystemExit(u'')

        try:
            ExecuteQueriesCommand([u'sample_text', u'csv'])
            self.assertTrue(False)
        except BaseException as e:
            self.assertTrue(True)

    @patch(u'lib.redash_util.job.JobManager.get_query_result_list')
    @patch(u'lib.redash_util.job.JobManager.update')
    @patch(u'lib.redash_util.job.JobManager.finished')
    @patch(u'lib.redash_util.job.JobManager.add')
    @patch(u'lib.redash_util.query.QueryList.unbind_values_in_bulk')
    @patch(u'lib.redash_util.query.QueryList.execute_in_bulk')
    @patch(u'lib.redash_util.query.QueryList.update_in_bulk')
    @patch(u'lib.redash_util.query.QueryList.bind_values_in_bulk')
    @patch(u'lib.redash_util.query.QueryList.search_queries_by')
    def test_execute_normal_case(
        self,
        mock_ql_search_queries_by,
        mock_ql_bind_values_in_bulk,
        mock_ql_update_in_bulk,
        mock_ql_execute_in_bulk,
        mock_ql_unbind_values_in_bulk,
        mock_jm_add,
        mock_jm_finished,
        mock_jm_update,
        mock_jm_get_query_result_list,
    ):
        u"""
        executeメソッドのテストケース。

        このテストケースでは、委譲している各クラスの処理が、
        特定の引数で呼ばれていることだけを確認する
        (他クラスのexecuteメソッドも、同様の方法でテストしている)。
        :param mock_ql_search_queries_by:
        :param mock_ql_bind_values_in_bulk:
        :param mock_ql_update_in_bulk:
        :param mock_ql_execute_in_bulk:
        :param mock_ql_unbind_values_in_bulk:
        :param mock_jm_add:
        :param mock_jm_update:
        :param mock_jm_get_query_result_list:
        :return:
        """
        # パッチした一部のメソッドは、特定の値を返すようにしておく。
        jobs = [Job(), Job()]
        mock_ql_execute_in_bulk.return_value = jobs
        mock_jm_finished.return_value = True
        query_results = [NullQueryResult([]), NullQueryResult([])]
        mock_jm_get_query_result_list.return_value = query_results

        # インスタンスを生成して、テスト実施。
        command = ExecuteQueriesCommand([
            u'sample_text',
            u'csv',
            u'/tmp/query_data',
            u'--parameters',
            u'key:value',
            u'--api-key',
            u'dummy api key',
            u'--end-point',
            u'https://dummy.endpoint',
            u'--log-dir',
            u'/tmp/kpi_data',
        ])
        command.execute()

        # QueryResultListクラスの各処理が、以下のように呼ばれる。
        mock_ql_search_queries_by.ssert_called_once_with(u'sample_text')
        mock_ql_bind_values_in_bulk.assert_called_once_with({u'key': u'value'})
        mock_ql_update_in_bulk.assert_called_with()
        mock_ql_execute_in_bulk.ssert_called_once_with()
        mock_ql_unbind_values_in_bulk.ssert_called_once_with()

        # JobManagerクラスの各処理が、以下のように呼ばれる。
        mock_jm_add.assert_called_once_with(jobs)
        mock_jm_finished.assert_called_once_with()
        mock_jm_update.assert_not_called()
        mock_jm_get_query_result_list.assert_called_once_with()


class ArchiveQueriesCommandTest(TestCase):
    u"""ArchiveQueriesCommandクラスに対するテストをまとめたクラス。"""

    def test_init_full_arguments_case(self):
        u"""
        必要なコマンド引数を全て渡すテスト(正常ケース)。

        :return:
        """
        command = ArchiveQueriesCommand([
            u'sample_text',
            u'--api-key',
            u'dummy api key',
            u'--end-point',
            u'https://dummy.endpoint',
            u'--log-dir',
            u'/tmp/kpi_data',
        ])
        ns = command.ns

        # サポートする引数は、親クラスと同じ。
        self.assertEqual(u'sample_text', ns.search_text)
        self.assertEqual(u'dummy api key', ns.api_key)
        self.assertEqual(u'https://dummy.endpoint', ns.end_point)
        self.assertEqual(u'/tmp/kpi_data', ns.log_dir)

    @patch('lib.command.command.ArgumentParser.error')
    def test_init_insufficient_option_case(self, error_method):
        u"""
        必須オプションが足りず、エラーになるケース。

        :return:
        """
        error_method.side_effect = SystemExit(u'')

        try:
            ArchiveQueriesCommand([])
            self.assertTrue(False)
        except BaseException as e:
            self.assertTrue(True)

    @patch(u'lib.redash_util.query.QueryList.archive_in_bulk')
    @patch(u'lib.redash_util.query.QueryList.search_queries_by')
    def test_execute_normal_case(
        self, mock_search_queries_by, mock_archive_in_bulk
    ):
        u"""
        executeメソッドのテストケース。

        :param mock_search_queries_by:
        :param mock_archive_in_bulk:
        :return:
        """
        command = ArchiveQueriesCommand([
            u'sample_text',
            u'--api-key',
            u'dummy api key',
            u'--end-point',
            u'https://dummy.endpoint',
            u'--log-dir',
            u'/tmp/kpi_data',
        ])
        command.execute()

        mock_search_queries_by.assert_called_once_with(u'sample_text')
        mock_archive_in_bulk.assert_called_once_with()


class ForkQueriesCommandTest(TestCase):
    u"""ForkQueriesCommandクラスに対するテストをまとめたクラス。"""

    def test_init_full_arguments_case(self):
        u"""
        必要なコマンド引数を全て渡すテスト(正常ケース)。

        :return:
        """
        command = ForkQueriesCommand([
            u'sample_text',
            u'1',
            u'--api-key',
            u'dummy api key',
            u'--end-point',
            u'https://dummy.endpoint',
            u'--log-dir',
            u'/tmp/kpi_data',
        ])
        ns = command.ns

        # サポートする引数は、親クラスと同じ。
        self.assertEqual(u'sample_text', ns.search_text)
        self.assertEqual(1, ns.target_data_source_id)
        self.assertEqual(u'dummy api key', ns.api_key)
        self.assertEqual(u'https://dummy.endpoint', ns.end_point)
        self.assertEqual(u'/tmp/kpi_data', ns.log_dir)

    @patch('lib.command.command.ArgumentParser.error')
    def test_init_insufficient_option_case(self, error_method):
        u"""
        必須オプションが足りず、エラーになるケース。

        :return:
        """
        error_method.side_effect = SystemExit(u'')

        try:
            ForkQueriesCommand([u'sample_text'])
            self.assertTrue(False)
        except BaseException as e:
            self.assertTrue(True)

    @patch(u'lib.redash_util.query.QueryList.update_in_bulk')
    @patch(u'lib.redash_util.query.QueryList.set_properties_in_bulk')
    @patch(u'lib.redash_util.query.QueryList.fork_in_bulk')
    @patch(u'lib.redash_util.query.QueryList.search_queries_by')
    def test_execute_normal_case(
        self,
        mock_search_queries_by,
        mock_fork_in_bulk,
        mock_set_properties_in_bulk,
        mock_update_in_bulk
    ):
        u"""
        executeメソッドのテストケース。

        :param mock_search_queries_by:
        :param mock_fork_in_bulk:
        :param mock_update_in_bulk:
        :return:
        """
        command = ForkQueriesCommand([
            u'sample_text',
            u'1',
            u'--api-key',
            u'dummy api key',
            u'--end-point',
            u'https://dummy.endpoint',
            u'--log-dir',
            u'/tmp/kpi_data',
        ])
        command.execute()

        mock_search_queries_by.assert_called_once_with(
            u'sample_text')
        mock_fork_in_bulk.assert_called_once_with()
        mock_set_properties_in_bulk.assert_called_once_with(
            {u'data_source_id': 1})
        mock_update_in_bulk.assert_called_once_with()

# -*- coding: utf-8 -*-
u"""queryモジュールに対するテストをまとめたモジュール。"""

from unittest import TestCase
from unittest.mock import patch

from lib.redash_util import \
    Job, JobManager, JobStatus, \
    NullQueryResult, QueryResult

from lib.test_util import ResponseMock

from requests import RequestException


class JobTest(TestCase):
    u"""Jobクラスに対するテストをまとめたクラス。"""

    @patch(
        u'lib.redash_util.gateway.Gateway.update_job_status',
        return_value=ResponseMock({
            u'job': {
                u'id': u'7c4b0355-4152-4909-90c9-747712ba256e',
                u'status': JobStatus.running,
                u'query_result_id': None,
                u'error': u'',
                u'updated_at': 0,
            }
        }, 200)
    )
    def test_update_status_is_running_case(self, mock_method):
        job_id = u'7c4b0355-4152-4909-90c9-747712ba256e'
        job = Job(job_id=job_id, query_id=1)
        job.update()

        # statusがrunningの場合、
        # query_result_idやerrorの値は空である。
        self.assertEqual(getattr(job, u'id'), job_id)
        self.assertEqual(getattr(job, u'status'), JobStatus.running)
        self.assertEqual(getattr(job, u'query_result_id'), None)
        self.assertEqual(getattr(job, u'error'), u'')

    @patch(
        u'lib.redash_util.gateway.Gateway.update_job_status',
        return_value=ResponseMock({
            u'job': {
                u'id': u'7c4b0355-4152-4909-90c9-747712ba256e',
                u'status': JobStatus.success,
                u'query_result_id': 1,
                u'error': u'',
                u'updated_at': 0,
            }
        }, 200)
    )
    def test_update_status_is_success_case(self, mock_method):
        job_id = u'7c4b0355-4152-4909-90c9-747712ba256e'
        job = Job(job_id=job_id, query_id=1)
        job.update()

        # statusがsuccessの場合、
        # query_result_idに結果を保持するオブジェクトのidが格納される。
        self.assertEqual(getattr(job, u'id'), job_id)
        self.assertEqual(getattr(job, u'status'), JobStatus.success)
        self.assertEqual(getattr(job, u'query_result_id'), 1)
        self.assertEqual(getattr(job, u'error'), u'')

    @patch(
        u'lib.redash_util.gateway.Gateway.update_job_status',
        return_value=ResponseMock({
            u'job': {
                u'id': u'7c4b0355-4152-4909-90c9-747712ba256e',
                u'status': JobStatus.failure,
                u'query_result_id': None,
                u'error': u'some error message',
                u'updated_at': 0,
            }
        }, 200)
    )
    def test_update_status_is_failure_case(self, mock_method):
        job_id = u'7c4b0355-4152-4909-90c9-747712ba256e'
        job = Job(job_id=job_id, query_id=1)
        job.update()

        # statusがsuccessの場合、
        # errorにerrorの詳細メッセージが格納される。
        self.assertEqual(getattr(job, u'id'), job_id)
        self.assertEqual(getattr(job, u'status'), JobStatus.failure)
        self.assertEqual(getattr(job, u'query_result_id'), None)
        self.assertEqual(getattr(job, u'error'), u'some error message')

    @patch(
        u'lib.redash_util.gateway.Gateway.get_query_result',
        return_value=ResponseMock({
            u'query_result': {
                u'id': 1,
                u'data_source_id': 1,
                u'query': u'SELECT 1 AS number;',
                u'data': {
                    u'columns': [
                        {
                            u'friendly_name': u'number',
                            u'name': u'number',
                            u'type': u'integer'
                        },
                    ],
                    u'rows': [
                        {
                            u'number': 1,
                        },
                    ],
                },
            }
        }, 200)
    )
    def test_get_result_success_case(self, mock_method):
        job = Job(job_id=u'7c4b0355-4152-4909-90c9-747712ba256e', query_id=1)
        setattr(job, u'status', JobStatus.success)

        # statusがsuccessのjobに対しget_resultをコールすると、
        # 対応するQueryResultオブジェクトが返る。
        query_result = job.get_result()
        self.assertIsInstance(query_result, QueryResult)
        self.assertEqual(getattr(query_result, u'id'), 1)
        self.assertEqual(
            getattr(query_result, u'query'), u'SELECT 1 AS number;')

    def test_get_result_failure_case(self):
        job = Job(job_id=u'7c4b0355-4152-4909-90c9-747712ba256e', query_id=1)
        setattr(job, u'status', JobStatus.running)

        # statusがsuccess以外のjobに対しget_resultをコールすると、
        # ヌルオブジェクトが返る。
        query_result = job.get_result()
        self.assertIsInstance(query_result, NullQueryResult)

    @patch(
        u'lib.redash_util.gateway.Gateway.update_job_status',
        return_value=ResponseMock({
            u'job': {u'status': JobStatus.failure}
        }, 200)
    )
    @patch(
        u'lib.redash_util.gateway.Gateway.kill_job',
        return_value=ResponseMock(None, 200)
    )
    def test_kill_job_normal_case(self, mock_kill_job, mock_update_job_status):
        job = Job(job_id=u'7c4b0355-4152-4909-90c9-747712ba256e', query_id=1)
        setattr(job, u'status', JobStatus.running)

        # killをコールしても、Noneしか返らないため、
        # 例外がスローされないことだけを確かめる。
        try:
            job.kill()
        except RequestException:
            self.assertTrue(False)

        # killコール後にupdateを行うと、jobのstatusがfailureになる。
        job.update()
        self.assertEqual(getattr(job, u'status'), JobStatus.failure)


class JobManagerTest(TestCase):
    u"""JobManagerクラスに対するテストをまとめたクラス。"""

    def setUp(self):
        self.manager = JobManager()
        self.manager.count(JobStatus.success)

    def test_add_normal_case(self):
        self.assertEqual(self.manager.count(JobStatus.running), 0)

        job = self.__create_dummy_job(JobStatus.running)
        self.manager.add([job])
        self.assertEqual(self.manager.count(JobStatus.running), 1)

    @patch(
        u'lib.redash_util.gateway.Gateway.update_job_status',
        return_value=ResponseMock({
            u'job': {u'status': JobStatus.success}
        }, 200)
    )
    def test_update(self, mock_method):
        self.manager.count(JobStatus.success)

        # runningのjobを2件セットする。
        self.manager.add([
            self.__create_dummy_job(JobStatus.running),
            self.__create_dummy_job(JobStatus.running),
        ])

        # updateコール後は、各Jobのstatusが更新される。
        self.assertEqual(self.manager.count(JobStatus.success), 0)
        self.manager.update()
        self.assertEqual(self.manager.count(JobStatus.success), 2)

    def test_finished_return_true_case(self):
        # statusがsuccessとfailureのJobのみの場合、Trueが返る。
        self.manager.add([
            self.__create_dummy_job(JobStatus.success),
            self.__create_dummy_job(JobStatus.failure),
        ])
        self.assertTrue(self.manager.finished())

    def test_finished_return_false_case(self):
        # statusがsuccessとfailure以外のJobがある場合、Falseが返る。
        self.manager.add([
            self.__create_dummy_job(JobStatus.success),
            self.__create_dummy_job(JobStatus.running),
        ])
        self.assertFalse(self.manager.finished())

    @patch(
        u'lib.redash_util.gateway.Gateway.get_query_result',
        return_value=ResponseMock({u'query_result': {u'id': 1}}, 200)
    )
    def test_get_query_result_list(self, mock_method):
        self.manager.add([
            self.__create_dummy_job(JobStatus.success),
            self.__create_dummy_job(JobStatus.failure),
            self.__create_dummy_job(JobStatus.success),
        ])

        # statusがsuccessのJobに対応するQueryResultオブジェクトが返る。
        query_result_list = self.manager.get_query_result_list()
        self.assertEqual(len(query_result_list), 2)
        for query_result in query_result_list:
            self.assertIsInstance(query_result, QueryResult)

    def __create_dummy_job(self, job_status=JobStatus.null):
        job = Job()
        setattr(job, u'status', job_status)
        return job

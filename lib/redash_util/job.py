# -*- coding: utf-8 -*-
u"""
以下クラスを提供するモジュール。

* Job
* JobStatus
* JobManager
"""

from enum import IntEnum
from typing import List, TYPE_CHECKING

from .gateway import Gateway

from .query_result import NullQueryResult, QueryResult


class Job:
    u"""Redash上でクエリを実行した際に発行されるジョブを表すクラス。"""

    def __init__(
        self,
        job_id: str=u'',
        query_id: int=0,
        connection_info: 'ConnectionInfo'=None
    ) -> None:
        u"""
        コンストラクタ。

        :param job_id: このジョブを一意に識別するid(ハッシュ値)。
        :param query_id: このジョブに対応するクエリのid。
        :param connection_info: 接続情報を保持するオブジェクト。
        """
        self.id = job_id
        self.query_id = query_id

        # その他のプロパティに、デフォルト値を設定しておく。
        self.status = JobStatus.pending
        self.query_result_id = None
        self.error = u''
        self.updated_at = 0

        self.__gateway = Gateway(connection_info)

    def set_connection_info(self, connection_info: 'ConnectionInfo') -> None:
        u"""
        サーバへの接続情報を保持するオブジェクトをセットする。

        :param connection_info:
        :return:
        """
        self.__gateway.set_connection_info(connection_info)

    def update(self) -> int:
        u"""
        RedashサーバとAPI疎通し、このジョブの状態を更新する。

        :return: 更新後のジョブの状態を表すint値。
        """
        response = self.__gateway.update_job_status(self.id)

        for key, value in response.json()[u'job'].items():
            setattr(self, key, value)

        return self.status

    def get_result(self) -> 'QueryResult':
        u"""
        このジョブが成功した場合に、クエリの実行結果を保持するオブジェクトを返す。

        :return: ジョブの実行結果を保持するオブジェクト。ジョブ実行中や実行失敗した場合に呼び出すと、ヌルオブジェクトを返す。
        """
        if self.status == JobStatus.success:
            response = self.__gateway.get_query_result(self.query_result_id)
            return QueryResult(response.json()[u'query_result'])
        else:
            return NullQueryResult({})

    def kill(self) -> None:
        u"""
        RedashサーバとAPI疎通し、ジョブの実行を停止する。

        注意点:
        実際にAPIを疎通させてみた所、typeがTreasureDataのクエリは
        Redash上でのJobのみkillされ、バックエンドのシステムのJobはkillされていなかったので要注意。

        参考:
        typeがprestoのクエリについても似たようなバグがあり、修正済みのようだ。
        https://github.com/getredash/redash/issues/1658
        """
        self.__gateway.kill_job(self.id)

    def get_status(self) -> int:
        u"""
        このジョブの現在のステータスを返す。

        :return:
        """
        return self.status


class JobStatus(IntEnum):
    u"""
    Redash上のジョブの状態を表すEnumクラス。

    Redash上では、QueryTaskクラスでジョブステータスの定数値が定義されている。
    このクラスの定数値は、上記定数値と対応させている。
    https://github.com/getredash/redash/blob/66a5e394de727849234043d715b926506cc3464e/redash/tasks/queries.py#L138
    """

    null    = 0,
    pending = 1,
    running = 2,
    success = 3,
    failure = 4


class JobManager:
    u"""Redash上のジョブをまとめて管理するクラス。"""

    def __init__(self, job_list: List['Job']=[]) -> None:
        u"""
        コンストラクタ。

        :param job_list: ジョブ配列。
        """
        self.__job_list = job_list

    def add(self, job_list: List['Job']) -> None:
        u"""
        このインスタンスに、ジョブ配列を追加する。

        :param job_list: ジョブ配列。
        :return:
        """
        self.__job_list = self.__job_list + job_list

    def update(self, async: bool=False) -> None:
        u"""
        このインスタンスに登録されたジョブをまとめて更新する。

        TODO:
        非同期モードを後ほど実装すること。
        :param async: Trueの場合、非同期でジョブの更新処理を行う。
        """
        for job in self.__job_list:
            job.update()

    def count(self, job_status: int) -> int:
        u"""
        引数で指定したステータスのジョブが何件あるかカウントする。

        :param job_status: ジョブのステータスを表すint値。
        :return: 対象のステータスのジョブの件数。
        """
        count = 0
        for job in self.__job_list:
            if job.get_status() == job_status:
                count += 1
        return count

    def finished(self) -> bool:
        u"""
        全てのジョブが終了済みかどうかチェックして返す。

        :return: 全てのジョブが終了済みならTrue。
        """
        for job in self.__job_list:
            if (job.get_status() != JobStatus.success) and \
               (job.get_status() != JobStatus.failure):
                return False
        return True

    def get_query_result_list(self) -> List['QueryResult']:
        u"""
        ステータスが成功のジョブに対応する、ジョブ結果配列を返す。

        :return: ジョブ結果配列。
        """
        query_result_list = []
        for job in self.__job_list:
            query_result = job.get_result()
            if type(query_result) == QueryResult:
                # typeで型チェックしていることに注意(サブクラスの場合は該当しない)。
                query_result_list.append(query_result)
        return query_result_list

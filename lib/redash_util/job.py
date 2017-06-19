# -*- coding: utf-8 -*-
u"""
以下クラスを提供するモジュール。

* Job
  └ NullJob
* JobStatus
* JobManager
  └ NullJobManager
"""

from enum import IntEnum
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .query_result import QueryResult


class Job:
    u"""Redash上でクエリを実行した際に発行されるジョブを表すクラス。"""

    def __init__(self, job_id: str='', query_id: int=0) -> None:
        u"""
        コンストラクタ。

        :param job_id: このジョブを一意に識別するid(ハッシュ値)。
        :param query_id: このジョブに対応するクエリのid。
        """
        pass

    def update(self) -> int:
        u"""
        RedashサーバとAPI疎通し、このジョブの状態を更新する。

        :return: 更新後のジョブの状態を表すint値。
        """
        pass

    def get_result(self) -> QueryResult:
        u"""
        このジョブが成功した場合に、クエリの実行結果を保持するオブジェクトを返す。

        :return: ジョブの実行結果を保持するオブジェクト。ジョブ実行中や実行失敗した場合に呼び出すと、ヌルオブジェクトを返す。
        """
        pass

    def kill(self) -> None:
        u"""RedashサーバとAPI疎通し、ジョブの実行を停止する。"""
        pass


class NullJob(Job):
    def __init__(self, job_id: str='', query_id: int=0) -> None:
        pass

    def update(self) -> int:
        return JobStatus.null

    def get_result(self) -> QueryResult:
        pass

    def kill(self) -> None:
        pass


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

    def __init__(self, job_list: List[Job]=[]) -> None:
        u"""
        コンストラクタ。

        :param job_list: ジョブ配列。
        """
        pass

    def add(self, job_list: List[Job]) -> None:
        u"""
        このインスタンスに、ジョブ配列を追加する。

        :param job_list: ジョブ配列。
        :return:
        """
        pass

    def update(self, async: bool=False) -> None:
        u"""
        このインスタンスに登録されたジョブをまとめて更新する。

        :param async: Trueの場合、非同期でジョブの更新処理を行う。
        """
        pass

    def count(self, job_status: int) -> int:
        u"""
        引数で指定したステータスのジョブが何件あるかカウントする。

        :param job_status: ジョブのステータスを表すint値。
        :return: 対象のステータスのジョブの件数。
        """
        pass

    def finished(self) -> bool:
        u"""
        全てのジョブが終了済みかどうかチェックして返す。

        :return: 全てのジョブが終了済みならTrue。
        """
        pass

    def get_query_result_list(self) -> List[QueryResult]:
        u"""
        ステータスが成功のジョブに対応する、ジョブ結果配列を返す。

        :return: ジョブ結果配列。
        """
        pass


class NullJobManager(JobManager):

    def __init__(self, job_list: List[Job]=[]) -> None:
        pass

    def add(self, job_list: List[Job]) -> None:
        pass

    def update(self, async: bool=False) -> None:
        pass

    def count(self, job_status: int) -> int:
        pass

    def finished(self) -> bool:
        pass

    def get_query_result_list(self) -> List[QueryResult]:
        pass

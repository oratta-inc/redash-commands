# -*- coding: utf-8 -*-
u"""Redash関連のユーティリティクラスをまとめたモジュール。"""

from .connection_info import ConnectionInfo
from .exceptions import \
    RedashException, \
    RedashJobException, \
    RedashJobFailureException
from .job import Job, JobManager, JobStatus
from .query import Query, QueryList
from .query_result import NullQueryResult, QueryResult

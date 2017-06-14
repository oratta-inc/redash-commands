# -*- coding: utf-8 -*-
u"""Redash関連のユーティリティクラスをまとめたモジュール。"""

from .connection_info import ConnectionInfo
from .exceptions import \
    RedashException, \
    RedashJobException, \
    RedashJobFailureException
from .job import Job, JobStatus, NullJob
from .query import NullQuery, NullQueryList, Query, QueryList
from .query_result import NullQueryResult, QueryResult

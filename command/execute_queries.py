# -*- coding: utf-8 -*-
u"""execute_queriesコマンドを実行する。"""

import sys
from os import path

lib_path = path.dirname(path.abspath(__file__)) + u'/..'
if lib_path not in sys.path:
    sys.path.append(lib_path)

from lib.command import ExecuteQueriesCommand

command = ExecuteQueriesCommand(sys.argv[1:])
command.execute()

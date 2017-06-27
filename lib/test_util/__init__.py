# -*- coding: utf-8 -*-
u"""テストに関するユーティリティクラスを提供するライブラリ。"""

from typing import Any, Dict


class ResponseMock:
    u"""requestsライブラリの、Responseモジュールのモッククラス。"""

    def __init__(self, json_data: Dict[str, Any], status_code: int) -> None:
        self.json_data = json_data
        self.status_code = status_code

    def json(self) -> Dict[str, Any]:
        return self.json_data

    # TODO status_codeの値に応じた例外を送出するようにする。
    def raise_for_status(self) -> None:
        pass

# -*- coding: utf-8 -*-
u"""ファイル入出力処理のユーティリティ機能をまとめたモジュール。"""

from os import listdir, path, walk
from typing import Iterator


def list_files_in(
    dir_path: str, file_format: str, read_recursively: bool = True
) -> [str]:
    u"""
    指定ディレクトリ以下の、特定拡張子を持つファイルのパスのリストを返す。

    :param dir_path: 走査するディレクトリのパス。
    :param file_format: ファイルフォーマット。
    :param read_recursively: Trueの場合、指定したディレクトリ以下を再帰的に走査する。
    :return: ファイルパスのリスト。
    """
    files = list_all_files_in(dir_path, read_recursively)

    if file_format[0] != u'.':
        file_format = u'.' + file_format

    ret_files = []
    for file in files:
        tmp, ext = path.splitext(file)
        if not ext == file_format:
            continue
        ret_files.append(file)
    return ret_files


def list_all_files_in(
    dir_path: str, read_recursively: bool = True
) -> [str]:
    u"""
    指定ディレクトリ以下の、全てのファイル、ディレクトリ、シンボリックリンクのパスのリストを返す。

    :param dir_path: 走査するディレクトリのパス。
    :param read_recursively: Trueの場合、指定したディレクトリ以下を再帰的に走査する。
    :return: 全てのファイル、ディレクトリ、シンボリックリンクのパスのリスト。
    """
    files = []
    if read_recursively:
        for file in walk_dir(dir_path):
            files.append(file)
        return files
    else:
        for file in listdir(dir_path):
            files.append(path.join(dir_path, file))
    return files


def walk_dir(dir_path: str) -> Iterator[str]:
    u"""
    呼び出し毎に指定ディレクトリ以下を走査し、個々のファイル、ディレクトリ、シンボリックリンクのパスを返す。

    :param dir_path: 走査するディレクトリのパス。
    :return: 個々のファイル、ディレクトリ、シンボリックリンクのパスのリスト。
    """
    for root, dirs, files in walk(dir_path):
        yield root
        for file in files:
            yield path.join(root, file)

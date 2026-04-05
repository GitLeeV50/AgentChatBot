# File reading and MD5 validation

import os
import hashlib
from infrastructure.logging.manager import logger
from infrastructure.exceptions.handler import FileIOError
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader


def get_file_md5_hex(filepath: str):  # 获取文件的md5的十六进制字符串

    if not os.path.exists(filepath):
        raise FileIOError(f"文件不存在: {filepath}", context={"path": filepath})

    if not os.path.isfile(filepath):
        raise FileIOError(f"路径不是文件: {filepath}", context={"path": filepath})

    md5_obj = hashlib.md5()

    chunk_size = 4096  # 4KB分片，避免文件过大爆内存
    try:
        with open(filepath, "rb") as f:  # 必须二进制读取
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
            md5_hex = md5_obj.hexdigest()
            return md5_hex
    except Exception as e:
        raise FileIOError(f"计算文件 MD5 失败: {str(e)}", context={"path": filepath})


def listdir_with_allowed_type(path: str, allowed_types: tuple[str]):  # 返回文件夹内的文件列表（允许的文件后缀）
    if not os.path.isdir(path):
        raise FileIOError(f"不是文件夹: {path}", context={"path": path})

    files = []
    for f in os.listdir(path):
        if f.endswith(allowed_types):
            files.append(os.path.join(path, f))

    return tuple(files)


def pdf_loader(filepath: str, passwd=None) -> list[Document]:
    try:
        return PyPDFLoader(filepath, passwd).load()
    except Exception as e:
        raise FileIOError(f"PDF 加载失败: {str(e)}", context={"path": filepath})


def txt_loader(filepath: str) -> list[Document]:
    try:
        return TextLoader(filepath, encoding="utf-8").load()
    except Exception as e:
        raise FileIOError(f"TXT 加载失败: {str(e)}", context={"path": filepath})

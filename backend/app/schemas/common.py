"""通用Schema定义

包含基础响应格式和分页结构
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Pagination(BaseModel):
    """分页信息

    Attributes:
        page: 当前页码（从1开始）
        size: 每页数量
        total: 总记录数
        pages: 总页数
    """

    page: int
    size: int
    total: int
    pages: int


class ResponseBase(BaseModel, Generic[T]):
    """API统一响应格式

    Attributes:
        code: 状态码，0表示成功
        message: 响应消息
        data: 响应数据
    """

    code: int = 0
    message: str = "success"
    data: T | None = None


class ListResponse(ResponseBase[T]):
    """列表响应格式

    包含分页信息的列表响应
    """

    pagination: Pagination | None = None

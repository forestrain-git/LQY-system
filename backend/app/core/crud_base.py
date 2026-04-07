"""
通用CRUD基础类 / Generic CRUD Base Class

提供数据库操作的通用接口，所有模块的CRUD操作都应继承此类
Provides generic database operation interfaces, all module CRUD should inherit from this

使用示例 / Usage Example:
    class DeviceCRUD(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
        pass

    device_crud = DeviceCRUD(Device)
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from datetime import datetime

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

# 定义类型变量 / Define type variables
ModelType = TypeVar("ModelType", bound=SQLModel)      # SQLModel类型
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)  # 创建Schema
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)  # 更新Schema


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    通用CRUD基础类 / Generic CRUD Base Class

    封装了常见的数据库操作：创建、查询、更新、删除
    Encapsulates common database operations: Create, Read, Update, Delete

    泛型参数 / Generic Parameters:
        ModelType: SQLModel数据模型
        CreateSchemaType: Pydantic创建模型
        UpdateSchemaType: Pydantic更新模型
    """

    def __init__(self, model: Type[ModelType]):
        """
        初始化CRUD对象 / Initialize CRUD object

        Args:
            model: SQLModel模型类 / SQLModel class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        根据ID获取单条记录 / Get single record by ID

        Args:
            db: 数据库会话 / Database session
            id: 记录ID / Record ID

        Returns:
            模型实例或None / Model instance or None
        """
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_or_404(self, db: AsyncSession, id: Any) -> ModelType:
        """
        根据ID获取记录，不存在则抛出404 / Get by ID or raise 404

        Args:
            db: 数据库会话 / Database session
            id: 记录ID / Record ID

        Returns:
            模型实例 / Model instance

        Raises:
            HTTPException: 404 Not Found
        """
        obj = await self.get(db, id)
        if not obj:
            raise HTTPException(
                status_code=404,
                detail=f"{self.model.__name__} with id={id} not found"
            )
        return obj

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        获取多条记录 / Get multiple records

        Args:
            db: 数据库会话 / Database session
            skip: 跳过记录数 / Records to skip
            limit: 返回最大记录数 / Max records to return
            filters: 过滤条件字典 / Filter conditions dict

        Returns:
            记录列表 / List of records
        """
        query = select(self.model)

        # 应用过滤条件 / Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType
    ) -> ModelType:
        """
        创建新记录 / Create new record

        Args:
            db: 数据库会话 / Database session
            obj_in: 创建模型实例 / Create schema instance

        Returns:
            创建的模型实例 / Created model instance
        """
        # 转换Pydantic模型为dict / Convert Pydantic model to dict
        obj_data = jsonable_encoder(obj_in)

        # 创建模型实例 / Create model instance
        db_obj = self.model(**obj_data)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    async def create_multi(
        self,
        db: AsyncSession,
        *,
        objs_in: List[CreateSchemaType]
    ) -> List[ModelType]:
        """
        批量创建记录 / Create multiple records

        Args:
            db: 数据库会话 / Database session
            objs_in: 创建模型列表 / List of create schemas

        Returns:
            创建的模型列表 / List of created models
        """
        db_objs = []
        for obj_in in objs_in:
            obj_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_data)
            db_objs.append(db_obj)

        db.add_all(db_objs)
        await db.commit()

        # 刷新每个对象 / Refresh each object
        for db_obj in db_objs:
            await db.refresh(db_obj)

        return db_objs

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        更新记录 / Update record

        Args:
            db: 数据库会话 / Database session
            db_obj: 数据库中的现有对象 / Existing object in DB
            obj_in: 更新模型或字典 / Update schema or dict

        Returns:
            更新后的模型 / Updated model
        """
        # 转换为字典 / Convert to dict
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        # 更新字段 / Update fields
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        # 自动更新更新时间 / Auto update updated_at if exists
        if hasattr(db_obj, 'updated_at'):
            db_obj.updated_at = datetime.now()

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    async def update_by_id(
        self,
        db: AsyncSession,
        *,
        id: Any,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        根据ID更新记录 / Update record by ID

        Args:
            db: 数据库会话 / Database session
            id: 记录ID / Record ID
            obj_in: 更新数据 / Update data

        Returns:
            更新后的模型 / Updated model

        Raises:
            HTTPException: 404 if not found
        """
        db_obj = await self.get_or_404(db, id)
        return await self.update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, id: Any) -> ModelType:
        """
        删除记录 / Delete record

        Args:
            db: 数据库会话 / Database session
            id: 记录ID / Record ID

        Returns:
            被删除的模型 / Deleted model

        Raises:
            HTTPException: 404 if not found
        """
        obj = await self.get_or_404(db, id)
        await db.delete(obj)
        await db.commit()
        return obj

    async def soft_delete(
        self,
        db: AsyncSession,
        *,
        id: Any,
        status_field: str = "status",
        deleted_status: str = "deleted"
    ) -> ModelType:
        """
        软删除记录 / Soft delete record

        将状态字段设置为删除状态，而非物理删除
        Sets status field to deleted instead of physical deletion

        Args:
            db: 数据库会话 / Database session
            id: 记录ID / Record ID
            status_field: 状态字段名 / Status field name
            deleted_status: 删除状态值 / Deleted status value

        Returns:
            被软删除的模型 / Soft deleted model
        """
        obj = await self.get_or_404(db, id)

        if hasattr(obj, status_field):
            setattr(obj, status_field, deleted_status)
            if hasattr(obj, 'deleted_at'):
                obj.deleted_at = datetime.now()

            db.add(obj)
            await db.commit()
            await db.refresh(obj)

        return obj

    async def count(
        self,
        db: AsyncSession,
        *,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        统计记录数 / Count records

        Args:
            db: 数据库会话 / Database session
            filters: 过滤条件 / Filter conditions

        Returns:
            记录数量 / Record count
        """
        from sqlalchemy import func

        query = select(func.count(self.model.id))

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)

        result = await db.execute(query)
        return result.scalar()

    async def exists(self, db: AsyncSession, id: Any) -> bool:
        """
        检查记录是否存在 / Check if record exists

        Args:
            db: 数据库会话 / Database session
            id: 记录ID / Record ID

        Returns:
            是否存在 / Whether exists
        """
        from sqlalchemy import exists

        query = select(exists().where(self.model.id == id))
        result = await db.execute(query)
        return result.scalar()

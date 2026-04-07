"""
AI助手数据模型 / AI Assistant Data Models

Author: AI Sprint
Date: 2026-04-07
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, String, Integer, Text
from sqlmodel import Field, Relationship, SQLModel


class ConversationRole(str, Enum):
    """对话角色 / Conversation Role"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Conversation(SQLModel, table=True):
    """
    对话会话模型 / Conversation Model

    存储用户与AI的完整对话历史
    Stores complete conversation history between user and AI
    """

    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)

    # 会话信息 / Conversation Info
    title: str = Field(
        ...,
        max_length=200,
        sa_column=Column(String(200), nullable=False),
        description="会话标题 / Conversation title",
    )

    # 关联用户 / Associated User
    user_id: int | None = Field(
        default=None,
        description="用户ID / User ID",
    )

    # 元数据 / Metadata
    model: str = Field(
        default="kimi",
        max_length=50,
        sa_column=Column(String(50)),
        description="使用的模型 / Model used",
    )
    context: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="上下文信息(JSON) / Context info (JSON)",
    )

    # 统计 / Statistics
    message_count: int = Field(
        default=0,
        description="消息数量 / Message count",
    )
    total_tokens: int = Field(
        default=0,
        description="总token数 / Total tokens",
    )

    # 时间戳 / Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="创建时间 / Creation time",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="更新时间 / Update time",
    )
    last_message_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="最后消息时间 / Last message time",
    )

    # 关联关系 / Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    def __repr__(self) -> str:
        return f"<Conversation: {self.title}>"


class Message(SQLModel, table=True):
    """
    消息模型 / Message Model

    存储单条对话消息
    Stores a single conversation message
    """

    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)

    # 关联会话 / Associated Conversation
    conversation_id: int = Field(
        ...,
        foreign_key="conversations.id",
        nullable=False,
        description="会话ID / Conversation ID",
    )

    # 消息内容 / Message Content
    role: ConversationRole = Field(
        ...,
        sa_column=Column(String(20), nullable=False),
        description="角色 / Role",
    )
    content: str = Field(
        ...,
        sa_column=Column(Text, nullable=False),
        description="消息内容 / Message content",
    )

    # 元数据 / Metadata
    tokens: int | None = Field(
        default=None,
        description="Token数量 / Token count",
    )
    model: str | None = Field(
        default=None,
        max_length=50,
        sa_column=Column(String(50)),
        description="生成模型 / Generation model",
    )

    # 工具调用 / Tool Calls
    tool_calls: str | None = Field(
        default=None,
        sa_column=Column(Text),
        description="工具调用(JSON) / Tool calls (JSON)",
    )

    # 时间戳 / Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="创建时间 / Creation time",
    )

    # 关联关系 / Relationships
    conversation: Conversation = Relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message: {self.role.value}>"


# ============== Pydantic Schemas ==============

class ConversationCreate(SQLModel):
    """会话创建Schema"""
    title: str
    user_id: int | None = None


class ConversationRead(SQLModel):
    """会话读取Schema"""
    id: int
    title: str
    user_id: int | None
    model: str
    message_count: int
    total_tokens: int
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime | None

    class Config:
        from_attributes = True


class MessageCreate(SQLModel):
    """消息创建Schema"""
    content: str
    role: ConversationRole = ConversationRole.USER


class MessageRead(SQLModel):
    """消息读取Schema"""
    id: int
    conversation_id: int
    role: ConversationRole
    content: str
    tokens: int | None
    model: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(SQLModel):
    """聊天请求Schema"""
    message: str
    conversation_id: int | None = None
    stream: bool = False


class ChatResponse(SQLModel):
    """聊天响应Schema"""
    message: str
    conversation_id: int
    tokens_used: int
    model: str

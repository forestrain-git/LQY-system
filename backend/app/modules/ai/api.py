"""
AI助手API路由 / AI Assistant API Routes

Author: AI Sprint
Date: 2026-04-07
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.modules.ai.models import (
    Conversation, ConversationCreate, ConversationRead,
    Message, MessageRead, ChatRequest, ChatResponse
)
from app.modules.ai.service import get_ai_service, AIAssistantService

router = APIRouter(prefix="/ai", tags=["ai"])


# ============== 会话管理 / Conversation Management ==============

@router.get("/conversations", response_model=List[ConversationRead])
async def list_conversations(
    user_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    limit: int = 20
):
    """获取会话列表 / Get conversation list"""
    ai_service = get_ai_service()
    conversations = await ai_service.list_conversations(session, user_id, limit)
    return conversations


@router.post("/conversations", response_model=ConversationRead)
async def create_conversation(
    conv_data: ConversationCreate,
    session: AsyncSession = Depends(get_session)
):
    """创建新会话 / Create new conversation"""
    ai_service = get_ai_service()
    conversation = await ai_service.create_conversation(
        session, conv_data.title, conv_data.user_id
    )
    return conversation


@router.get("/conversations/{conversation_id}", response_model=ConversationRead)
async def get_conversation(
    conversation_id: int,
    session: AsyncSession = Depends(get_session)
):
    """获取会话详情 / Get conversation details"""
    ai_service = get_ai_service()
    conversation = await ai_service.get_conversation(session, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    session: AsyncSession = Depends(get_session)
):
    """删除会话 / Delete conversation"""
    ai_service = get_ai_service()
    success = await ai_service.delete_conversation(session, conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted"}


# ============== 消息管理 / Message Management ==============

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageRead])
async def get_messages(
    conversation_id: int,
    session: AsyncSession = Depends(get_session),
    limit: int = 50
):
    """获取会话消息 / Get conversation messages"""
    ai_service = get_ai_service()

    # 验证会话存在
    conversation = await ai_service.get_conversation(session, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await ai_service.get_messages(session, conversation_id, limit)
    return messages


# ============== 聊天 / Chat ==============

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    发送聊天消息 / Send chat message

    Args:
        request: 包含消息和可选会话ID的请求 / Request with message and optional conversation ID
    """
    ai_service = get_ai_service()

    try:
        response = await ai_service.chat(
            session=session,
            message=request.message,
            conversation_id=request.conversation_id
        )
        return ChatResponse(**response)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    流式聊天 / Streaming chat

    返回SSE事件流 / Returns SSE event stream
    """
    ai_service = get_ai_service()

    async def event_generator():
        try:
            async for chunk in ai_service.chat_stream(
                session=session,
                message=request.message,
                conversation_id=request.conversation_id
            ):
                yield chunk
        except Exception as e:
            yield f"data: {{'error': '{str(e)}'}}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# ============== 快捷功能 / Quick Actions ==============

@router.post("/quick/analyze")
async def quick_analyze(
    data_type: str,  # "dispatch", "equipment", "workorders"
    session: AsyncSession = Depends(get_session)
):
    """
    快速数据分析 / Quick data analysis

    让AI分析指定类型的数据并给出建议
    Let AI analyze specified data type and give suggestions
    """
    ai_service = get_ai_service()

    prompts = {
        "dispatch": "分析当前的车辆调度情况，包括队列长度、泊位利用率和等待时间。提供优化建议。",
        "equipment": "分析设备运行状态，识别需要维护或存在故障风险的设备。提供维护建议。",
        "workorders": "分析当前工单状态，识别高优先级任务和潜在的瓶颈。提供资源分配建议。"
    }

    prompt = prompts.get(data_type, "请提供系统整体运行状况分析。")

    try:
        response = await ai_service.chat(
            session=session,
            message=prompt
        )
        return {
            "analysis": response["message"],
            "data_type": data_type,
            "conversation_id": response["conversation_id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/quick/suggest")
async def get_suggestions(
    context: str,
    session: AsyncSession = Depends(get_session)
):
    """
    获取AI建议 / Get AI suggestions

    基于提供的上下文获取AI建议
    Get AI suggestions based on provided context
    """
    ai_service = get_ai_service()

    prompt = f"基于以下情况，请提供专业的处理建议:\n\n{context}"

    try:
        response = await ai_service.chat(
            session=session,
            message=prompt
        )
        return {
            "suggestions": response["message"],
            "conversation_id": response["conversation_id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestion failed: {str(e)}")

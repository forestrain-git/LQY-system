"""
AI助手服务 / AI Assistant Service

集成Kimi API提供服务
Integrates Kimi API for service

Author: AI Sprint
Date: 2026-04-07
"""

import json
import os
from datetime import datetime
from typing import AsyncGenerator, List, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.modules.ai.models import Conversation, Message, ConversationRole


class KimiAIConfig:
    """Kimi API配置 / Kimi API Configuration"""
    API_BASE = "https://api.moonshot.cn/v1"
    MODEL = "moonshot-v1-8k"  # 或其他可用模型
    MAX_TOKENS = 2048
    TEMPERATURE = 0.7


class AIAssistantService:
    """
    AI助手服务 / AI Assistant Service

    提供与Kimi API的交互和对话管理
    Provides interaction with Kimi API and conversation management
    """

    def __init__(self):
        self.api_key = os.getenv("KIMI_API_KEY", "")
        self.system_prompt = """你是龙泉驿环卫智能体的AI助手，专门协助管理垃圾转运站。

你的职责包括:
1. 回答关于设备管理、车辆调度、工单处理的问题
2. 分析运营数据并提供优化建议
3. 协助故障排查和应急处理
4. 提供环卫行业相关法规和标准咨询

请用专业但易懂的语言回答，必要时使用表格或列表来组织信息。
如果问题超出你的知识范围，请诚实告知并建议咨询相关人员。
"""

    async def create_conversation(
        self,
        session: AsyncSession,
        title: str,
        user_id: Optional[int] = None
    ) -> Conversation:
        """创建新会话 / Create new conversation"""
        conversation = Conversation(
            title=title,
            user_id=user_id,
            model=KimiAIConfig.MODEL
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        return conversation

    async def get_conversation(
        self,
        session: AsyncSession,
        conversation_id: int
    ) -> Optional[Conversation]:
        """获取会话 / Get conversation"""
        return await session.get(Conversation, conversation_id)

    async def list_conversations(
        self,
        session: AsyncSession,
        user_id: Optional[int] = None,
        limit: int = 20
    ) -> List[Conversation]:
        """获取会话列表 / Get conversation list"""
        query = select(Conversation)
        if user_id:
            query = query.where(Conversation.user_id == user_id)
        query = query.order_by(Conversation.updated_at.desc()).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    async def get_messages(
        self,
        session: AsyncSession,
        conversation_id: int,
        limit: int = 50
    ) -> List[Message]:
        """获取消息历史 / Get message history"""
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()

    def _build_messages(
        self,
        history: List[Message],
        new_message: str
    ) -> List[dict]:
        """构建消息列表 / Build message list"""
        messages = [{"role": "system", "content": self.system_prompt}]

        for msg in history:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })

        messages.append({"role": "user", "content": new_message})
        return messages

    async def chat(
        self,
        session: AsyncSession,
        message: str,
        conversation_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> dict:
        """
        发送消息并获取回复 / Send message and get response

        Args:
            session: 数据库会话 / Database session
            message: 用户消息 / User message
            conversation_id: 现有会话ID / Existing conversation ID
            user_id: 用户ID / User ID

        Returns:
            包含回复和会话信息的字典 / Dict with response and conversation info
        """
        # 获取或创建会话 / Get or create conversation
        if conversation_id:
            conversation = await self.get_conversation(session, conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
        else:
            # 自动生成标题 / Auto-generate title
            title = message[:30] + "..." if len(message) > 30 else message
            conversation = await self.create_conversation(session, title, user_id)

        # 获取历史消息 / Get history
        history = await self.get_messages(session, conversation.id)

        # 保存用户消息 / Save user message
        user_msg = Message(
            conversation_id=conversation.id,
            role=ConversationRole.USER,
            content=message
        )
        session.add(user_msg)

        # 调用Kimi API / Call Kimi API
        messages = self._build_messages(history, message)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{KimiAIConfig.API_BASE}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": KimiAIConfig.MODEL,
                        "messages": messages,
                        "max_tokens": KimiAIConfig.MAX_TOKENS,
                        "temperature": KimiAIConfig.TEMPERATURE
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()

                # 提取AI回复 / Extract AI response
                ai_content = data["choices"][0]["message"]["content"]
                tokens_used = data.get("usage", {}).get("total_tokens", 0)

            except Exception as e:
                # API调用失败时的回退 / Fallback when API fails
                ai_content = f"抱歉，AI服务暂时不可用。错误: {str(e)}"
                tokens_used = 0

        # 保存AI回复 / Save AI response
        ai_msg = Message(
            conversation_id=conversation.id,
            role=ConversationRole.ASSISTANT,
            content=ai_content,
            model=KimiAIConfig.MODEL,
            tokens=tokens_used
        )
        session.add(ai_msg)

        # 更新会话统计 / Update conversation stats
        conversation.message_count = len(history) + 2
        conversation.total_tokens += tokens_used
        conversation.last_message_at = datetime.now()
        conversation.updated_at = datetime.now()
        session.add(conversation)

        await session.commit()
        await session.refresh(ai_msg)

        return {
            "message": ai_content,
            "conversation_id": conversation.id,
            "tokens_used": tokens_used,
            "model": KimiAIConfig.MODEL
        }

    async def chat_stream(
        self,
        session: AsyncSession,
        message: str,
        conversation_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天 / Streaming chat

        返回SSE格式的流数据 / Returns SSE formatted stream
        """
        # 获取或创建会话
        if conversation_id:
            conversation = await self.get_conversation(session, conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
        else:
            title = message[:30] + "..." if len(message) > 30 else message
            conversation = await self.create_conversation(session, title, user_id)

        # 获取历史消息
        history = await self.get_messages(session, conversation.id)

        # 保存用户消息
        user_msg = Message(
            conversation_id=conversation.id,
            role=ConversationRole.USER,
            content=message
        )
        session.add(user_msg)
        await session.commit()

        # 构建消息
        messages = self._build_messages(history, message)

        # 调用流式API
        full_response = ""

        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    f"{KimiAIConfig.API_BASE}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": KimiAIConfig.MODEL,
                        "messages": messages,
                        "max_tokens": KimiAIConfig.MAX_TOKENS,
                        "temperature": KimiAIConfig.TEMPERATURE,
                        "stream": True
                    },
                    timeout=60.0
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                delta = chunk["choices"][0]["delta"].get("content", "")
                                if delta:
                                    full_response += delta
                                    yield f"data: {json.dumps({'content': delta, 'done': False})}\n\n"
                            except:
                                pass

            except Exception as e:
                error_msg = f"流式响应出错: {str(e)}"
                full_response = error_msg
                yield f"data: {json.dumps({'content': error_msg, 'done': False})}\n\n"

        # 保存完整回复
        ai_msg = Message(
            conversation_id=conversation.id,
            role=ConversationRole.ASSISTANT,
            content=full_response,
            model=KimiAIConfig.MODEL
        )
        session.add(ai_msg)

        # 更新会话
        conversation.message_count += 2
        conversation.last_message_at = datetime.now()
        conversation.updated_at = datetime.now()
        session.add(conversation)
        await session.commit()

        yield f"data: {json.dumps({'conversation_id': conversation.id, 'done': True})}\n\n"

    async def delete_conversation(
        self,
        session: AsyncSession,
        conversation_id: int
    ) -> bool:
        """删除会话 / Delete conversation"""
        conversation = await self.get_conversation(session, conversation_id)
        if conversation:
            await session.delete(conversation)
            await session.commit()
            return True
        return False


# 全局服务实例
_ai_service: Optional[AIAssistantService] = None


def get_ai_service() -> AIAssistantService:
    """获取AI服务单例 / Get AI service singleton"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIAssistantService()
    return _ai_service

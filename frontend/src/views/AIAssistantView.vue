<!--
  AI助手页面 / AI Assistant Page

  提供与AI的智能对话界面
  Provides intelligent chat interface with AI

  Author: AI Sprint
  Date: 2026-04-07
-->
<template>
  <div class="ai-assistant">
    <!-- 侧边栏：会话列表 / Sidebar: Conversation List -->
    <aside class="ai-sidebar">
      <div class="ai-sidebar__header">
        <button class="new-chat-btn" @click="createNewConversation">
          <Plus class="new-chat-btn__icon" />
          新建对话
        </button>
      </div>

      <div class="conversations-list">
        <div
          v-for="conv in conversations"
          :key="conv.id"
          class="conversation-item"
          :class="{ 'is-active': currentConversation?.id === conv.id }"
          @click="selectConversation(conv)"
        >
          <MessageSquare class="conversation-item__icon" />
          <div class="conversation-item__info">
            <div class="conversation-item__title">{{ conv.title }}</div>
            <div class="conversation-item__meta">
              {{ formatDate(conv.last_message_at || conv.created_at) }}
            </div>
          </div>
          <button
            class="conversation-item__delete"
            @click.stop="deleteConversation(conv.id)"
          >
            <Trash2 />
          </button>
        </div>
      </div>
    </aside>

    <!-- 主聊天区 / Main Chat Area -->
    <div class="ai-chat">
      <!-- 欢迎界面 / Welcome Screen -->
      <div v-if="!currentConversation" class="welcome-screen">
        <div class="welcome-content"
          <Bot class="welcome-icon" />
          <h1 class="welcome-title">龙泉驿环卫智能助手</h1>
          <p class="welcome-desc">
            我可以帮你处理设备管理、车辆调度、工单处理等问题
          </p>

          <div class="quick-actions"
            <div class="quick-actions__title">快速开始</div>
            <div class="quick-actions__grid">
              <button
                v-for="action in quickActions"
                :key="action.text"
                class="quick-action-btn"
                @click="sendQuickMessage(action.text)"
              >
                <component :is="action.icon" class="quick-action-btn__icon" />
                {{ action.text }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 消息列表 / Message List -->
      <div v-else class="messages-container" ref="messagesContainer">
        <div
          v-for="message in messages"
          :key="message.id"
          class="message"
          :class="`message--${message.role}`"
        >
          <div class="message__avatar"
003e
            <Bot v-if="message.role === 'assistant'" />
            <User v-else />
          </div>
          <div class="message__content">
            <div class="message__text" v-html="formatMessage(message.content)"></div>
            <div class="message__meta">
              {{ formatTime(message.created_at) }}
              <span v-if="message.tokens" class="message__tokens">
                · {{ message.tokens }} tokens
              </span>
            </div>
          </div>
        </div>

        <!-- 加载状态 / Loading State -->
        <div v-if="isLoading" class="message message--assistant">
          <div class="message__avatar">
            <Bot />
          </div>
          <div class="message__content">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区 / Input Area -->
      <div class="input-area">
        <div class="input-wrapper"
          <textarea
            v-model="inputMessage"
            class="input-field"
            placeholder="输入消息..."
            rows="1"
            @keydown.enter.prevent="sendMessage"
            @input="autoResize"
            ref="inputField"
          />
          <button
            class="send-btn"
            :disabled="!inputMessage.trim() || isLoading"
            @click="sendMessage"
          >
            <Send class="send-btn__icon" />
          </button>
        </div>
        <div class="input-hint">
          按 Enter 发送，Shift + Enter 换行
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import {
  Plus, MessageSquare, Trash2, Bot, User, Send,
  Truck, Wrench, ClipboardList, TrendingUp
} from 'lucide-vue-next'

// 会话数据 / Conversation data
const conversations = ref([
  { id: 1, title: '如何优化车辆调度？', created_at: new Date().toISOString(), last_message_at: new Date().toISOString() },
  { id: 2, title: '设备维护计划建议', created_at: new Date(Date.now() - 86400000).toISOString(), last_message_at: new Date(Date.now() - 3600000).toISOString() },
])

const currentConversation = ref<typeof conversations.value[0] | null>(null)
const messages = ref<Array<{
  id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
  tokens?: number
}>>([])

const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLDivElement>()
const inputField = ref<HTMLTextAreaElement>()

// 快速操作 / Quick actions
const quickActions = [
  { icon: Truck, text: '分析今日调度情况' },
  { icon: Wrench, text: '设备维护建议' },
  { icon: ClipboardList, text: '工单处理优化' },
  { icon: TrendingUp, text: '运营数据分析' },
]

// 创建新会话 / Create new conversation
const createNewConversation = () => {
  currentConversation.value = null
  messages.value = []
  inputMessage.value = ''
}

// 选择会话 / Select conversation
const selectConversation = (conv: typeof conversations.value[0]) => {
  currentConversation.value = conv
  // TODO: 加载消息历史
  messages.value = []
}

// 删除会话 / Delete conversation
const deleteConversation = (id: number) => {
  conversations.value = conversations.value.filter(c => c.id !== id)
  if (currentConversation.value?.id === id) {
    currentConversation.value = null
    messages.value = []
  }
}

// 发送消息 / Send message
const sendMessage = async () => {
  const content = inputMessage.value.trim()
  if (!content || isLoading.value) return

  // 添加用户消息
  const userMsg = {
    id: Date.now(),
    role: 'user' as const,
    content,
    created_at: new Date().toISOString()
  }
  messages.value.push(userMsg)
  inputMessage.value = ''
  resetTextarea()

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  // 模拟AI回复
  isLoading.value = true
  setTimeout(() => {
    const aiMsg = {
      id: Date.now() + 1,
      role: 'assistant' as const,
      content: '这是AI助手的回复示例。在实际应用中，这里会调用后端API获取Kimi的回复。',
      created_at: new Date().toISOString(),
      tokens: 42
    }
    messages.value.push(aiMsg)
    isLoading.value = false

    nextTick().then(scrollToBottom)
  }, 1500)
}

// 发送快速消息 / Send quick message
const sendQuickMessage = (text: string) => {
  inputMessage.value = text
  sendMessage()
}

// 自动调整文本框高度 / Auto resize textarea
const autoResize = () => {
  const el = inputField.value
  if (el) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 200) + 'px'
  }
}

const resetTextarea = () => {
  const el = inputField.value
  if (el) {
    el.style.height = 'auto'
  }
}

// 滚动到底部 / Scroll to bottom
const scrollToBottom = () => {
  const container = messagesContainer.value
  if (container) {
    container.scrollTop = container.scrollHeight
  }
}

// 格式化消息 / Format message
const formatMessage = (content: string) => {
  // 简单 Markdown 支持
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

// 格式化日期 / Format date
const formatDate = (date: string) => {
  const d = new Date(date)
  const now = new Date()
  const diff = now.getTime() - d.getTime()

  if (diff < 86400000) {
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

// 格式化时间 / Format time
const formatTime = (date: string) => {
  return new Date(date).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  // TODO: 加载会话列表
})
</script>

<style scoped>
.ai-assistant {
  display: flex;
  height: calc(100vh - 64px);
  background-color: var(--color-bg-secondary);
}

/* 侧边栏 / Sidebar */
.ai-sidebar {
  width: 260px;
  background-color: var(--color-bg-elevated);
  border-right: 1px solid var(--color-border-primary);
  display: flex;
  flex-direction: column;
}

.ai-sidebar__header {
  padding: var(--space-4);
  border-bottom: 1px solid var(--color-border-secondary);
}

.new-chat-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
  background-color: var(--color-bg-tertiary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.new-chat-btn:hover {
  background-color: var(--color-bg-secondary);
  border-color: var(--color-border-primary);
}

.new-chat-btn__icon {
  width: 16px;
  height: 16px;
}

.conversations-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-2);
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
}

.conversation-item:hover {
  background-color: var(--color-bg-tertiary);
}

.conversation-item.is-active {
  background-color: var(--color-primary-50);
}

.conversation-item__icon {
  width: 16px;
  height: 16px;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.conversation-item__info {
  flex: 1;
  min-width: 0;
}

.conversation-item__title {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-item__meta {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-top: 2px;
}

.conversation-item__delete {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  background: none;
  border: none;
  border-radius: var(--radius-md);
  opacity: 0;
  transition: all var(--transition-fast);
  cursor: pointer;
}

.conversation-item:hover .conversation-item__delete {
  opacity: 1;
}

.conversation-item__delete:hover {
  background-color: var(--color-accent-danger);
  color: white;
}

/* 聊天区域 / Chat Area */
.ai-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 欢迎界面 / Welcome Screen */
.welcome-screen {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
}

.welcome-content {
  text-align: center;
  max-width: 600px;
}

.welcome-icon {
  width: 64px;
  height: 64px;
  color: var(--color-primary-500);
  margin-bottom: var(--space-4);
}

.welcome-title {
  font-size: var(--text-3xl);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.welcome-desc {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-8);
}

.quick-actions__title {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-tertiary);
  margin-bottom: var(--space-3);
}

.quick-actions__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  background-color: var(--color-bg-elevated);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.quick-action-btn:hover {
  background-color: var(--color-bg-tertiary);
  border-color: var(--color-primary-500);
}

.quick-action-btn__icon {
  width: 16px;
  height: 16px;
  color: var(--color-text-secondary);
}

/* 消息列表 / Messages */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}

.message {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.message__avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.message--user .message__avatar {
  background-color: var(--color-primary-100);
  color: var(--color-primary-600);
}

.message--assistant .message__avatar {
  background-color: var(--color-bg-tertiary);
  color: var(--color-primary-500);
}

.message__content {
  flex: 1;
  max-width: 80%;
}

.message__text {
  font-size: var(--text-base);
  line-height: 1.6;
  color: var(--color-text-primary);
  background-color: var(--color-bg-elevated);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
}

.message--user .message__text {
  background-color: var(--color-primary-50);
}

.message__meta {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-top: var(--space-1);
}

.message__tokens {
  margin-left: var(--space-1);
}

/* 输入框代码样式 */
.message__text code {
  background-color: var(--color-bg-tertiary);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}

/* 输入区 / Input Area */
.input-area {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--color-border-primary);
  background-color: var(--color-bg-elevated);
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: var(--space-3);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
}

.input-field {
  flex: 1;
  background: none;
  border: none;
  color: var(--color-text-primary);
  font-size: var(--text-base);
  line-height: 1.5;
  resize: none;
  max-height: 200px;
  min-height: 24px;
}

.input-field:focus {
  outline: none;
}

.input-field::placeholder {
  color: var(--color-text-tertiary);
}

.send-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  background-color: var(--color-primary-600);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background-color: var(--color-primary-700);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn__icon {
  width: 16px;
  height: 16px;
}

.input-hint {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  text-align: center;
  margin-top: var(--space-2);
}

/* 打字动画 / Typing Animation */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: var(--space-4);
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: var(--color-text-tertiary);
  border-radius: var(--radius-full);
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-10px); }
}

@media (max-width: 768px) {
  .ai-sidebar {
    display: none;
  }
}
</style>

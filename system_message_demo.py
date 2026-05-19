from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 1) 固定的系统提示：身份、边界、输出风格（尽量稳定且精简）
SYSTEM_PROMPT = (
    "你是一个资深Python助教。"
    "回答要简洁、准确，优先给出可执行示例；"
    "如果信息不足，先提1个澄清问题。"
)

llm = ChatOllama(
    model="gemma4:26b",
    temperature=0.2
)

# 2) 会话历史只保存“用户+助手”轮次；SystemMessage 每轮构建时注入
chat_history = []

def build_messages(user_input: str, history, max_turns: int = 4):
    # 只保留最近 max_turns 轮（每轮2条消息：Human + AI）
    recent = history[-(max_turns * 2):]

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    messages.extend(recent)
    messages.append(HumanMessage(content=user_input))
    return messages

def chat(user_input: str):
    global chat_history
    messages = build_messages(user_input, chat_history, max_turns=4)

    response = llm.invoke(messages)

    # 3) 仅把当轮 Human + AI 追加到历史
    chat_history.append(HumanMessage(content=user_input))
    chat_history.append(AIMessage(content=response.content))

    return response.content

if __name__ == "__main__":
    # 多轮演示
    q1 = "我想学装饰器，先给一个最小例子"
    a1 = chat(q1)
    print("User:", q1)
    print("Assistant:", a1, "\n")

    q2 = "把这个例子改成带参数的装饰器"
    a2 = chat(q2)
    print("User:", q2)
    print("Assistant:", a2, "\n")

    q3 = "再给一个常见踩坑点和修复方式"
    a3 = chat(q3)
    print("User:", q3)
    print("Assistant:", a3)
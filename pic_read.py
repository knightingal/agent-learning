import base64
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# 1. 辅助函数：将本地图片转换为 Base64 编码
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# 2. 初始化本地的多模态大模型
# 确保你本地 Ollama 已经 pull 了对应的模型
llm = ChatOllama(
    model="qwen2.5vl:7b",
    temperature=0
)

# 3. 准备你的本地图片路径
image_path = "./ScreenshotFrom2026-05-1621-21-59.png"
image_base64 = encode_image_to_base64(image_path)

# 4. 构建 LangChain 标准的多模态消息结构
# image_url 接受符合数据 URI 规范的 base64 字符串
messages = [
    HumanMessage(
        content=[
            {
                "type": "text",
                "text": "识别这张图片中的文字。"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            }
        ]
    )
]

# 5. 调用模型并获取结果
# print("正在等待本地模型识别图片...\n")
# response = llm.invoke(messages)
print("--- 模型正在流式回答 ---")
for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)

# print("--- 模型识别结果 ---")
# print(response.content)
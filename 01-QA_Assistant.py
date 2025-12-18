import gradio as gr
from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ChatBot:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("Zhipu_API_KEY"),
            base_url="https://open.bigmodel.cn/api/paas/v4/"
        )
        self.conversation = [
            {"role": "system", "content": "你是一个有用的AI助手"}
        ]

    def chat(self, user_input: str) -> str:
        # 添加用户消息
        self.conversation.append({"role": "user", "content": user_input})

        # 调用API
        response = self.client.chat.completions.create(
            model="glm-4-air-250414",
            messages=self.conversation,
            temperature=0.7
        )

        # 获取AI回复
        ai_response = response.choices[0].message.content

        # 添加到对话历史
        self.conversation.append({"role": "assistant", "content": ai_response})

        return ai_response

    def clear_history(self):
        """清除对话历史，保留系统提示"""
        self.conversation = self.conversation[:1]

# 创建全局聊天机器人实例
bot = ChatBot()

def respond(message, history):
    """
    处理用户输入并返回AI回复
    """
    try:
        response = bot.chat(message)
        # 将新消息添加到历史记录中
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        return history
    except Exception as e:
        error_msg = f"抱歉，我遇到了一个错误: {str(e)}"
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": error_msg})
        return history

def clear_chat_history():
    """
    清除聊天历史
    """
    bot.clear_history()
    return []

with gr.Blocks(title="答疑助手") as demo:
    gr.Markdown("# 🤖星灿答疑助手")
    gr.Markdown("您的专属AI学习助手，可以回答各种问题")
    
    # 聊天界面
    chatbot = gr.Chatbot(
        label="聊天室",
        height=500,
        type="messages"
    )
    
    # 输入组件
    with gr.Row():
        msg = gr.Textbox(
            label="输入您的问题",
            placeholder="例如：什么是人工智能？",
            container=False,
            scale=9
        )
        clear_btn = gr.Button("清除历史", scale=1)
    
    # 提交按钮
    submit_btn = gr.Button("发送", variant="primary")
    
    # 绑定事件
    # 当用户按下回车或点击发送按钮时提交
    msg.submit(respond, [msg, chatbot], [chatbot]).then(
        lambda: "", None, msg, queue=False
    )
    submit_btn.click(respond, [msg, chatbot], [chatbot]).then(
        lambda: "", None, msg, queue=False
    )
    
    # 清除历史按钮
    clear_btn.click(clear_chat_history, None, chatbot, queue=False)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7861)
import gradio as gr
import base64
from PIL import Image
import io
import os
from dotenv import load_dotenv
from openai import OpenAI
from utils.t2i import encode_image_to_base64

# 加载环境变量
load_dotenv()

# 初始化客户端
client = OpenAI(api_key=os.getenv("Zhipu_API_KEY"), base_url="https://open.bigmodel.cn/api/paas/v4/")

def image_understanding(image, prompt):
    """使用GLM-4V模型进行图像理解"""
    if image is None:
        return "请上传一张图片"

    if not prompt:
        prompt = "请描述这张图片的内容"

    # 将图像编码为base64
    image_base64 = encode_image_to_base64(image)

    try:
        # 调用GLM-4V模型进行图像理解
        response = client.chat.completions.create(
            model="glm-4v",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.7
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"处理图像时出错: {str(e)}"

# 创建Gradio界面
with gr.Blocks(title="星灿图文理解助手") as demo:
    gr.Markdown("# 🌟星灿图文理解助手")
    gr.Markdown("基于GLM-4V模型的智能图像理解工具，可分析图片内容并回答相关问题")
    
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="filepath", label="上传图片")
            prompt_input = gr.Textbox(
                label="输入问题",
                placeholder="例如：请描述这张图片的内容，图片中有什么？",
                value="请描述这张图片的内容",
                visible=False
            )
            submit_btn = gr.Button("开始分析", variant="primary")
        
        with gr.Column():
            result_output = gr.Textbox(label="分析结果", interactive=False, lines=10)

    # 示例图片
    gr.Examples(
        examples=[["docs/img/img.png", "请描述这张图片的内容"]],
        inputs=[image_input, prompt_input],
        outputs=result_output,
        fn=image_understanding,
        cache_examples=True
    )
    
    # 绑定事件
    submit_btn.click(
        fn=image_understanding,
        inputs=[image_input, prompt_input],
        outputs=result_output
    )
    
    # 支持回车提交
    prompt_input.submit(
        fn=image_understanding,
        inputs=[image_input, prompt_input],
        outputs=result_output
    )

if __name__ == "__main__":
    demo.launch()
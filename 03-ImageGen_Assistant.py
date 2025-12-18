import gradio as gr
import os
from dotenv import load_dotenv
import requests
import base64
from io import BytesIO
from PIL import Image

# 加载环境变量
load_dotenv()

from zai import ZhipuAiClient
client = ZhipuAiClient(api_key=os.getenv("Zhipu_API_KEY"))

def generate_image(prompt, model="cogView-4-250304"):
    """
    根据提示生成图像
    
    Args:
        prompt (str): 图像描述
        model (str): 使用的模型名称
    
    Returns:
        tuple: (图像, 状态信息)
    """
    if not prompt:
        return None, "请输入图像描述"

    try:
        # 使用zai包生成图像
        response = client.images.generations(
            model=model,
            prompt=prompt,
            size="1024x1024",
        )
        image_url = response.data[0].url

        # 下载图像
        image_response = requests.get(image_url)
        image = Image.open(BytesIO(image_response.content))
        return image, "图像生成成功"
    except Exception as e:
        return None, f"生成图像时出错: {str(e)}"

# 创建Gradio界面
with gr.Blocks(title="星灿图像生成助手") as demo:
    gr.Markdown("# 🌟星灿图像生成助手")
    gr.Markdown("基于智谱AI的CogView模型，输入文字描述即可生成精美图像")
    
    with gr.Row():
        with gr.Column():
            prompt_input = gr.Textbox(
                label="图像描述",
                placeholder="请输入您想要生成的图像描述，例如：一只可爱的小猫咪，坐在阳光明媚的窗台上，背景是蓝天白云",
                lines=3
            )
            model_choice = gr.Dropdown(
                choices=["cogView-4-250304"],
                value="cogView-4-250304",
                label="选择模型"
            )
            generate_button = gr.Button("✨ 生成图像")
            gr.Markdown("### 示例提示词")
            gr.Examples(
                examples=[
                    "一只可爱的小猫咪，坐在阳光明媚的窗台上，背景是蓝天白云",
                    "一幅油画风格的山水画，山峰高耸入云，瀑布飞流直下",
                    "赛博朋克风格的城市夜景，霓虹灯闪烁，飞行汽车穿梭其中",
                    "梦幻的海底世界，五彩斑斓的珊瑚礁，各种热带鱼游来游去"
                ],
                inputs=prompt_input
            )
        
        with gr.Column():
            image_output = gr.Image(label="生成的图像", type="pil")
            error_output = gr.Textbox(label="状态信息", interactive=False)
    
    generate_button.click(
        fn=generate_image,
        inputs=[prompt_input, model_choice],
        outputs=[image_output, error_output]
    )

if __name__ == "__main__":
    demo.launch()
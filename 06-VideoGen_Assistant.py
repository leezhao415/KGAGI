import os
import gradio as gr
import dashscope
from dashscope import VideoSynthesis
from http import HTTPStatus
from dotenv import load_dotenv
import requests
import time

# 加载环境变量
load_dotenv()

# 初始化DashScope客户端
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

def generate_video(prompt, size="1920*1080", model="wan2.2-t2v-plus"):
    """
    根据文本提示生成视频
    
    Args:
        prompt (str): 视频内容描述
        size (str): 视频分辨率，默认为1920*1080
        model (str): 使用的模型，默认为wan2.2-t2v-plus
    
    Returns:
        str: 视频URL或错误信息
    """
    if not prompt.strip():
        return None, "请输入视频内容描述"
    
    try:
        # 调用DashScope视频生成API
        rsp = VideoSynthesis.call(
            model=model,
            prompt=prompt,
            size=size
        )
        
        if rsp.status_code == HTTPStatus.OK:
            video_url = rsp.output.video_url
            # 下载视频文件
            video_filename = f"generated_video_{int(time.time())}.mp4"
            response = requests.get(video_url)
            
            if response.status_code == 200:
                with open(video_filename, "wb") as f:
                    f.write(response.content)
                return video_filename, "视频生成成功！"
            else:
                return None, f"视频下载失败，状态码: {response.status_code}"
        else:
            return None, f"视频生成失败: {rsp.message}"
            
    except Exception as e:
        return None, f"视频生成过程中发生错误: {str(e)}"

# Gradio界面
with gr.Blocks(title="星灿视频生成助手") as demo:
    gr.Markdown("# 🌟星灿视频生成助手")
    gr.Markdown("基于WanX的智能视频生成工具")
    
    with gr.Row():
        with gr.Column():
            prompt_input = gr.Textbox(
                label="视频内容描述",
                placeholder="请输入要生成的视频内容描述，例如：一只小猫在月光下奔跑...",
                lines=5
            )
            
            with gr.Row():
                size_dropdown = gr.Dropdown(
                    choices=["1920*1080", "1280*720", "1024*1024", "720*1280", "1080*1920"],
                    value="1920*1080",
                    label="视频分辨率"
                )
                model_dropdown = gr.Dropdown(
                    choices=["wan2.2-t2v-plus"],
                    value="wan2.2-t2v-plus",
                    label="生成模型"
                )
            
            generate_button = gr.Button("生成视频", variant="primary")
            status_output = gr.Textbox(label="状态信息", interactive=False)
        
        with gr.Column():
            video_output = gr.Video(label="生成视频")

    generate_button.click(
        generate_video,
        inputs=[prompt_input, size_dropdown, model_dropdown],
        outputs=[video_output, status_output]
    )

if __name__ == "__main__":
    demo.launch()
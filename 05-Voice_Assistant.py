import os
import gradio as gr
import dashscope
import requests
from dashscope.api_entities.dashscope_response import SpeechSynthesisResponse
import pygame
import tempfile
from dotenv import load_dotenv
from tqdm import tqdm

# 加载环境变量
load_dotenv()

# 初始化DashScope客户端
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# 可用的音色选项
VOICE_OPTIONS = {
    "知性女声(Cherry)": "Cherry",
    "甜美女声(Serena)": "Serena",
    "阳光青年男声(Ethan)": "Ethan",
    "优雅女声(Chelsie)": "Chelsie"
}


def download_audio_with_progress(url, save_path='output.wav'):
    """
   带进度条的音频文件下载
   """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # 获取文件总大小
        total_size = int(response.headers.get('content-length', 0))

        # 创建保存目录
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)

        # 下载并显示进度
        with open(save_path, 'wb') as file, tqdm(
                desc=save_path,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:
                    size = file.write(chunk)
                    progress_bar.update(size)

        print(f"✅ 音频下载完成: {save_path}")
        return save_path

    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None


def text_to_speech(text, voice_choice, speed=1.0, pitch=1.0):
    """
    将文本转换为语音
    
    Args:
        text: 要转换的文本
        voice_choice: 选择的音色
        speed: 语速 (0.5-2.0)
        pitch: 音调 (0.5-1.5)
    
    Returns:
        生成的音频文件路径
    """
    if not text.strip():
        return None, "请输入要转换的文本"

    # 获取音色代码
    voice_code = VOICE_OPTIONS[voice_choice]

    try:
        # 调用DashScope TTS API
        response = dashscope.audio.qwen_tts.SpeechSynthesizer.call(
            model='qwen-tts',
            text=text,
            voice=voice_code,
            rate=speed,
            pitch=pitch
        )
        audio_url = response.output.audio["url"]

        if not audio_url:
            print("错误：在响应中未找到音频URL")
            return False

        # 下载音频文件
        print("正在下载音频文件...")
        save_path = download_audio_with_progress(audio_url)

        if response.status_code == 200:
            # 保存音频文件
            return save_path, "语音合成成功"
        else:
            print(f"下载失败，状态码: {response.status_code}")
            return None

    except Exception as e:
        return None, f"语音合成过程中发生错误: {str(e)}"


# 创建Gradio界面
with gr.Blocks(title="星灿语音助手") as demo:
    gr.Markdown("# 🌟星灿语音助手")
    gr.Markdown("将文字转换为自然语音，支持多种音色选择")

    with gr.Row():
        with gr.Column():
            text_input = gr.TextArea(
                label="输入文本",
                placeholder="请输入要转换为语音的文本...",
                lines=5
            )

            with gr.Row():
                voice_choice = gr.Dropdown(
                    choices=list(VOICE_OPTIONS.keys()),
                    value="知性女声(Cherry)",
                    label="音色选择"
                )

                speed = gr.Slider(
                    minimum=0.5,
                    maximum=2.0,
                    value=1.0,
                    step=0.1,
                    label="语速"
                )

                pitch = gr.Slider(
                    minimum=0.5,
                    maximum=1.5,
                    value=1.0,
                    step=0.1,
                    label="音调"
                )

            convert_btn = gr.Button("生成语音", variant="primary")

        with gr.Column():
            audio_output = gr.Audio(
                label="生成的语音",
                type="filepath"
            )
            status_output = gr.Textbox(
                label="状态信息"
            )

    # 设置事件处理
    convert_btn.click(
        fn=text_to_speech,
        inputs=[text_input, voice_choice, speed, pitch],
        outputs=[audio_output, status_output]
    )

    gr.Markdown("---")
    gr.Markdown("### 使用说明")
    gr.Markdown("""
    1. 在文本框中输入要转换为语音的文字
    2. 选择喜欢的音色和语速、音调参数
    3. 点击"生成语音"按钮
    4. 等待语音生成完成后可直接播放
    """)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)

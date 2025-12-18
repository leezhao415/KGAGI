import os
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 初始化DashScope客户端
client = OpenAI(base_url=os.getenv("DASHSCOPE_base_url"),api_key=os.getenv("DASHSCOPE_API_KEY"))

def generate_code(prompt):
    """
    使用qwen2.5-coder-32b-instruct模型生成代码
    
    Args:
        prompt (str): 用户输入的代码需求描述
        
    Returns:
        str: 生成的代码
    """
    try:
        completion = client.completions.create(
            model="qwen2.5-coder-32b-instruct",
            prompt=f"{prompt}",
            max_tokens=1024,
            temperature=0.7
        )
        return completion.choices[0].text
    except Exception as e:
        return f"生成代码时出错: {str(e)}"

# 创建Gradio界面
with gr.Blocks(title="星灿代码生成助手") as demo:
    gr.Markdown("# 🌟星灿代码生成助手")
    gr.Markdown("基于通义千问Qwen2.5-Coder模型，根据自然语言描述生成高质量Python代码")
    
    with gr.Row():
        with gr.Column():
            prompt_input = gr.Textbox(
                label="代码需求描述",
                placeholder="例如：写一个python的快速排序函数，def quick_sort(arr):",
                lines=5
            )
            generate_button = gr.Button("🚀 生成代码", variant="primary")
            gr.Markdown("### 示例需求")
            gr.Examples(
                examples=[
                    "写一个python的快速排序函数，def quick_sort(arr):",
                    "用Python写一个二分查找算法",
                    "写一个Python函数来反转字符串",
                    "用Python实现一个简单的登录验证功能"
                ],
                inputs=prompt_input
            )
            
        with gr.Column():
            code_output = gr.Code(label="生成的代码", language="python", lines=20)

    # 绑定事件
    generate_button.click(
        fn=generate_code,
        inputs=prompt_input,
        outputs=code_output
    )
    
    # 支持回车提交
    prompt_input.submit(
        fn=generate_code,
        inputs=prompt_input,
        outputs=code_output
    )

if __name__ == "__main__":
    demo.launch()
import os
import time

import requests

from tqdm import tqdm

def download_audio_with_progress(url, save_path=f'result/T2A/output{int(time.time())}.wav'):
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

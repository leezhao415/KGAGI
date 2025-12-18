import base64
from PIL import Image
import io


def encode_image_to_base64(image):
    """将上传的图像编码为base64字符串"""
    if image is None:
        return None

    # 打开图像并转换为RGB模式（如果需要）
    img = Image.open(image)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # 将图像保存到内存中的字节流
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")

    # 编码为base64
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str
import json
from pyecharts.datasets import COORDINATES

def generate_coords_json(output_filename="china_city_coords.json"):
    """
    从 pyecharts.datasets.COORDINATES 提取所有城市坐标，
    并将其保存为一个 JSON 文件。
    """
    # pyecharts 的 COORDINATES 是一个类字典对象，我们将其转换为标准字典
    # 键是城市名 (str)，值是 [经度, 纬度] (list)
    city_coords_dict = dict(COORDINATES.items())

    print(f"正在生成坐标文件，共包含 {len(city_coords_dict)} 个城市...")

    # 将字典写入 JSON 文件
    with open(output_filename, 'w', encoding='utf-8') as f:
        # ensure_ascii=False 确保中文字符能被正确写入，而不是被转义成 \uXXXX
        # indent=2 让生成的 JSON 文件格式化，更易于阅读（可选，用于生产环境可设为 None 减小体积）
        json.dump(city_coords_dict, f, ensure_ascii=False, indent=2)

    print(f"✅ 成功生成坐标文件: {output_filename}")
    print("现在你可以将这个文件上传，并在你的 Cloudflare Worker 中使用它的 URL。")

if __name__ == '__main__':
    generate_coords_json()
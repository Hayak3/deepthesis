import fitz  # PyMuPDF
import json
import os
import argparse # 导入argparse模块

def extract_regions_as_images(pdf_path, json_file_path, output_folder="extracted_images", dpi=200):
    """
    从 PDF 中根据 JSON 文件描述提取指定区域为图片。

    参数:
    pdf_path (str): PDF 文件的路径。
    json_file_path (str): 包含图片/表格描述的 JSON 文件的路径。
    output_folder (str): 保存提取图片的文件夹名称。
    dpi (int): 输出图片的DPI (dots per inch)，值越高图片越清晰，文件也越大。
    """
    # 检查输入文件是否存在
    if not os.path.exists(pdf_path):
        print(f"错误: PDF 文件 '{pdf_path}' 不存在。")
        return []
    if not os.path.exists(json_file_path):
        print(f"错误: JSON 文件 '{json_file_path}' 不存在。")
        return []

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON 文件 '{json_file_path}' 解析错误: {e}")
        return []
    except IOError as e:
        print(f"读取 JSON 文件 '{json_file_path}' 失败: {e}")
        return []

    if not os.path.exists(output_folder):
        try:
            os.makedirs(output_folder)
            print(f"创建输出文件夹: {output_folder}")
        except OSError as e:
            print(f"创建输出文件夹 '{output_folder}' 失败: {e}")
            return []
    
    doc = None
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"打开 PDF 文件 '{pdf_path}' 失败: {e}")
        return []

    extracted_files = []

    for item in data:
        page_num_1_indexed = item.get("page")
        region_boundary = item.get("regionBoundary")
        fig_type = item.get("figType", "Region")
        name = item.get("name", "Unknown")
        caption = item.get("caption", "")
        if fig_type != "Figure":
            continue
        if page_num_1_indexed is None or region_boundary is None:
            print(f"条目缺少页码或区域边界: {item.get('caption', 'N/A')}")
            continue

        page_num_0_indexed = page_num_1_indexed

        if not (0 <= page_num_0_indexed < len(doc)):
            print(f"页码 {page_num_1_indexed} 超出范围 (共 {len(doc)} 页). 跳过: {caption}")
            continue

        try:
            page = doc.load_page(page_num_0_indexed)
            clip_rect = fitz.Rect(
                region_boundary["x1"],
                region_boundary["y1"],
                region_boundary["x2"],
                region_boundary["y2"]
            )
            pix = page.get_pixmap(clip=clip_rect, dpi=dpi)
            
            # 构建更安全的文件名，避免特殊字符问题
            # safe_name = "".join(c if c.isalnum() else "_" for c in str(name))
            # safe_fig_type = "".join(c if c.isalnum() else "_" for c in str(fig_type))
            # caption = caption[:200]
            output_filename = f"{name}.png"
            output_path = os.path.join(output_folder, output_filename)

            pix.save(output_path)
            extracted_files.append(output_path)
            print(f"已提取并保存: {output_path} (来自页面 {page_num_1_indexed})")

        except Exception as e:
            print(f"提取 '{caption}' (页面 {page_num_1_indexed}) 时出错: {e}")

    if doc:
        doc.close()
    print(f"\n提取完成. 共提取 {len(extracted_files)} 个图片/表格。")
    return extracted_files

# --- 主程序入口 ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="从PDF中根据JSON数据提取图片区域。")
    
    parser.add_argument("pdf_file_path", 
                        help="要处理的PDF文件的路径。")
    
    parser.add_argument("output_dir", 
                        help="提取出的图片要保存的文件夹路径。")

    parser.add_argument("--json_file", "-j",
                        default="outputa.json",
                        help="包含图片坐标和页码的JSON文件路径 (默认为: outputa.json)。")
    
    parser.add_argument("--dpi", "-d",
                        type=int,
                        default=300,
                        help="提取图片的DPI，影响清晰度 (默认为: 300)。")

    args = parser.parse_args()

    # 调用函数进行提取
    extract_regions_as_images(args.pdf_file_path, args.json_file, args.output_dir, dpi=args.dpi)

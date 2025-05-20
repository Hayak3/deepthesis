import os
from pathlib import Path
import subprocess
import argparse

def run_pipeline(pdf_path, output_dir, api_key=None):
    """
    运行完整的 PDF 翻译流程：
    1. 提取 PDF 元数据（生成 outputxxx.json）
    2. 提取图片
    3. 生成翻译后的 PDF
    """
    # 步骤 1: 运行 java -jar pdf.jar 生成 outputxxx.json
    print("步骤 1: 提取 PDF 元数据...")
    subprocess.run(["java", "-jar", "pdf.jar", pdf_path,"-d",""], check=True)
    filename = Path(pdf_path).stem
    json_file = filename+".json"

    # 步骤 2: 运行 get_figure.py 提取图片
    print("步骤 2: 提取图片...")
    subprocess.run(["python", "get_figure.py", pdf_path, output_dir, "--json_file", json_file], check=True)

    # 步骤 3: 运行 generate.py 生成翻译后的 PDF
    print("步骤 3: 生成翻译后的 PDF...")
    if api_key:
        os.environ["API_KEY"] = api_key
    output_pdf = os.path.join(output_dir, os.path.basename(pdf_path).replace(".pdf", "_cn.pdf"))
    subprocess.run(["python", "generate.py", "-i", pdf_path, "-o", output_pdf], check=True)

    print(f"流程完成！翻译后的 PDF 已保存到: {output_pdf}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF 翻译流程整合脚本")
    parser.add_argument("-i", "--input", required=True, help="输入 PDF 文件路径")
    parser.add_argument("-o", "--output", required=True, help="输出目录路径")
    parser.add_argument("--api_key", help="Gemini/Google API 密钥（可选）")
    args = parser.parse_args()

    run_pipeline(args.input, args.output, args.api_key) 
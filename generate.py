import subprocess
from google import genai
from google.genai import types
import pathlib
import os
from google.genai.types import HttpOptions
import re
import argparse

from compile_tex import compile_latex_to_pdf


def extract_document_content_re(latex_string):
    """
    使用正则表达式提取 \begin{document} 和 \end{document} 之间的内容（包含这两个标记）。
    """
    start_marker = r"```latex"
    end_marker = r"\end{document}"

    escaped_start = re.escape(start_marker)
    escaped_end = re.escape(end_marker)

    pattern = f"({escaped_start}.*?{escaped_end})"

    match = re.search(pattern, latex_string, re.DOTALL)
    if match:
        return match.group(0)[8:]
    else:
        return ""


# get from env
TIMEOUT = os.getenv("TIMEOUT")
api_key = os.getenv("API_KEY")
GEMINI_TIMEOUT = int(TIMEOUT) if TIMEOUT else 10 * 60 * 1000  # 10 minutes

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate LaTeX from PDF.")
    parser.add_argument("-o", "--output", type=str,
                        help="Output LaTeX file name.", default="output.tex")
    parser.add_argument("-i", "--input", type=str,
                        help="Input PDF file name.", default="input.pdf")
    args = parser.parse_args()
    filepath = pathlib.Path(args.input)
    if not filepath.exists():
        print(f"File {filepath} does not exist.")
        exit(1)

    prompt = open("prompt.md", "r", encoding="utf-8").read()

    client = genai.Client(api_key=api_key,
                          http_options=HttpOptions(timeout=GEMINI_TIMEOUT))
    images = pathlib.Path(args.output).parent
    full_response_text = []
    s = subprocess.check_output(f"ls {images}", shell=True).decode("utf-8")
    stream = client.models.generate_content_stream(
        model="models/gemini-2.5-flash-preview-04-17",

        config=types.GenerateContentConfig(
            system_instruction=prompt,
            max_output_tokens=65535,
            temperature=0.1,
        ),
        contents=[
            types.Part.from_bytes(
                data=filepath.read_bytes(),
                mime_type='application/pdf',
            ),
            f"图片目录下ls结果为:{s}"
        ]
    )

    for chunk in stream:
        full_response_text.append(chunk.text)
        print(chunk.text, end="", flush=True)

    final_text_content = "".join(full_response_text)

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    final_text_content = extract_document_content_re(final_text_content)
    with open(os.path.join(current_script_dir, "output.tex"), "w", encoding="utf-8") as f:
        f.write(final_text_content)
    generated_pdf_path = compile_latex_to_pdf(
        tex_content=final_text_content,
        output_pdf_filename=args.output,
        latex_compiler="xelatex",  # Or "xelatex", "lualatex"
        project_root=current_script_dir,
        resource_dirs_to_copy=[images]  # Pass the name of the directory
    )

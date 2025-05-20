# DeepThesis

## 项目简介

本项目旨在实现**英文PDF学术论文自动翻译为中文PDF**，并最大程度还原原始排版。

---

## 主要特性

- **专业学术翻译**：术语精准，保留公式、文献引用格式
- **排版还原**：章节、图片、表格、公式、参考文献等自动适配
- **一键生成**：输入PDF，输出可编译LaTeX和中文PDF
- **图片自动提取**：支持从PDF中批量提取图片并自动插入LaTeX

---

## 依赖环境

- TexLive
- Java
- Python
- uv

---

## 使用方法

### 1. 环境准备(Archlinux)
- ```bash sudo pacman -S uv texlive jdk8-openjdk```
- 安装Python依赖：
  ```bash
  uv sync
  ```

### 2. 运行

如需提取PDF中的图片（如论文插图、表格等），可运行：

```bash
uv run main.py -i <INPUT_PATH> -o <OUTPUT_PATH> --api_key <API_KEY>
```

---

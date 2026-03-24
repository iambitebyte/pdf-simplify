# PDF Simplify

使用 LLM 智能提取 PDF 文档核心内容，生成结构化摘要和简化版本的 Python 工具。

## 功能特性

- **智能解析 PDF 文档**：使用 pymupdf 提取文本和结构
- **PDF 转换为 Markdown**：自动识别标题和段落
- **按标题智能分块**：累加段落到目标大小（10000 字符）
- **LLM 智能简化**：将大段文本简化为核心内容（10000 → 1000 字）
- **自动生成标题**：为简化后的内容生成简洁标题
- **保持文档结构**：保留原有章节、段落层次
- **宽松错误处理**：LLM 失败时自动使用规则简化
- **支持多种输出格式**：Markdown、JSON、HTML、PDF
- **可配置的简化粒度**：自定义目标长度和压缩率
- **批量处理**：支持处理多个 PDF 文件

## 安装

### 使用 uv（推荐）

```bash
# 克隆项目
git clone https://github.com/yourusername/pdf-simplify.git
cd pdf-simplify

# 使用 uv 创建虚拟环境并安装依赖
uv sync
```

### 使用 pip

```bash
pip install -r requirements.txt
```

## 快速开始

### 简化 PDF 文档

```bash
# 简化 PDF 文件（生成 Markdown）
uv run pdf-simplify simplify path/to/your/document.pdf

# 指定输出文件
uv run pdf-simplify simplify document.pdf -o simplified.md

# 使用不同的 LLM 模型
uv run pdf-simplify simplify document.pdf --model gpt-4

# 使用配置文件
uv run pdf-simplify simplify document.pdf --config config.toml
```

### 摘要 PDF 文档

```bash
# 摘要单个 PDF 文件
uv run pdf-simplify summarize path/to/your/document.pdf

# 指定摘要级别
uv run pdf-simplify summarize document.pdf --level detailed

# 输出到文件
uv run pdf-simplify summarize document.pdf --output summary.md

# 批量处理
uv run pdf-simplify summarize *.pdf --output-dir summaries/
```

### API 使用

```python
from pdf_simplify import PDFSimplifier, PDFSummarizer

# 初始化简化器
simplifier = PDFSimplifier(
    model="gpt-4",  # 或其他 LLM
    api_key="your-api-key"
)

# 简化 PDF 文档（生成 Markdown）
simplifier.simplify("document.pdf", "simplified.md")

# 初始化摘要器
summarizer = PDFSummarizer(
    model="gpt-4",
    api_key="your-api-key"
)

# 摘要 PDF 文档
summary = summarizer.summarize("document.pdf")

# 获取摘要内容
print(summary.markdown())
```

## 项目结构

```
pdf-simplify/
├── src/
│   └── pdf_simplify/
│       ├── __init__.py
│       ├── cli.py               # 命令行入口
│       ├── core/                # 核心功能模块
│       │   ├── parser.py        # PDF 纯文本解析器
│       │   ├── markdown_parser.py    # PDF 到 Markdown 解析器（新增）
│       │   ├── chunker.py       # 文本分块器
│       │   ├── simplifier.py    # LLM 简化器（新增）
│       │   ├── summarizer.py    # LLM 摘要生成器
│       │   └── formatter.py     # 输出格式化器
│       ├── models/              # 数据模型
│       │   └── summary.py       # 摘要数据模型
│       └── utils/               # 工具函数
│           └── config.py        # 配置管理
├── tests/                       # 测试文件
├── configs/                     # 配置文件
├── examples/                    # 示例代码
├── docs/                        # 文档
├── pyproject.toml              # 项目配置
└── README.md                   # 本文件
```

## 配置

创建 `config.toml` 文件：

```toml
[llm]
provider = "openai"  # 或 anthropic, azure, local
model = "gpt-4"
temperature = 0.3
max_tokens = 4000

[summary]
level = "detailed"  # detailed, concise, minimal
chunk_size = 4000
chunk_overlap = 200

[output]
format = "markdown"  # markdown, json, html
include_outline = true
include_key_concepts = true
```

或使用 `.env` 文件：

```bash
# LLM 配置
PDF_SIMPLIFY_LLM_MODEL=gpt-4
PDF_SIMPLIFY_API_KEY=your-api-key
PDF_SIMPLIFY_BASE_URL=https://api.openai.com/v1
PDF_SIMPLIFY_PROVIDER=openai
```

## 工作原理

### PDF 简化流程

1. **PDF → Markdown 转换**：使用 pymupdf 解析 PDF，识别标题和段落
2. **标题识别**：基于字体大小自动识别文档结构
3. **智能分块**：按标题内容累加段落到目标大小（10000 字符）
4. **LLM 简化**：
    - 将每个文本块（10000 字）简化为核心内容（1000 字）
    - 自动为简化内容生成新标题
5. **宽松错误处理**：LLM 失败时使用规则简化，确保始终有输出
6. **Markdown 生成**：输出保持标题结构的简化内容

### PDF 摘要流程

1. **PDF 解析**：使用 pdfplumber 解析 PDF 文档，提取文本内容
2. **结构识别**：识别文档的章节、段落层次结构
3. **智能分块**：将文档分成适合 LLM 处理的块，保持语义完整性
4. **分层摘要**：
    - 对每个章节生成摘要
    - 对章节摘要进行二次汇总
    - 生成整体文档摘要
5. **结构化输出**：将结果组织成易读的结构化格式

## 依赖项

- Python >= 3.10
- pymupdf（PDF 解析和 Markdown 转换）
- pdfplumber（PDF 纯文本提取）
- openai/anthropic（LLM API）
- 其他依赖见 pyproject.toml

## 开发

```bash
# 运行测试
uv run pytest

# 代码格式化
uv run black src/
uv run ruff check src/

# 类型检查
uv run mypy src/
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。

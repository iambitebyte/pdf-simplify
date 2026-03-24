"""PDF document simplifier."""

from pathlib import Path
from typing import List, Optional, Dict, Tuple
from pdf_simplify.core.markdown_parser import MarkdownPDFParser
from pdf_simplify.utils.config import Config


class PDFSimplifier:
    """Simplify PDF documents by reducing text length while preserving core logic."""

    CHUNK_TARGET_SIZE = 10000
    CHUNK_MIN_SIZE = 500
    SIMPLIFIED_TARGET_MIN = 1000
    SIMPLIFIED_TARGET_MAX = 1000

    def __init__(
        self,
        config: Optional[Config] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        provider: str = "openai",
    ):
        """Initialize PDF simplifier.

        Args:
            config: Configuration object
            model: LLM model name
            api_key: API key for LLM service
            provider: LLM provider (openai, anthropic, etc.)
        """
        self.config = config or Config()
        self.model = model or self.config.llm_model
        self.api_key = api_key or self.config.api_key
        self.provider = provider
        self.client = None

    def _init_llm_client(self):
        """Initialize LLM client based on provider."""
        if self.provider == "openai":
            from openai import OpenAI

            client_kwargs = {"api_key": self.api_key}
            if self.config.base_url:
                client_kwargs["base_url"] = self.config.base_url
            self.client = OpenAI(**client_kwargs)
        elif self.provider == "anthropic":
            import anthropic

            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _call_llm(self, prompt: str) -> str:
        """Call LLM API.

        Args:
            prompt: Input prompt

        Returns:
            LLM response
        """
        print(f"将 {len(prompt)} 个字符拿去做简化")
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=2000,
                )
                if not response.choices:
                    raise ValueError("No choices in response")
                message = response.choices[0].message
                content = message.content
                if content is None:
                    reasoning = getattr(message, "reasoning_content", None)
                    if reasoning:
                        content = reasoning
                    else:
                        raise ValueError("LLM returned None content")

                content = self._extract_final_content(content)

                return content

            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text

            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            print(f"LLM API Error: {e}")
            raise

    def _extract_final_content(self, content: str) -> str:
        """Extract final content from LLM response, filtering out thinking process.

        Args:
            content: LLM response content

        Returns:
            Extracted final content
        """
        lines = content.split("\n")
        final_content = []

        skip_thinking = True
        found_content = False
        in_content_block = False
        content_markers = ["修订草案：", "修订版：", "最终版本：", "修订草案：", "简化内容："]

        for i, line in enumerate(lines):
            stripped = line.strip()

            if skip_thinking:
                if stripped and not any(
                    stripped.startswith(prefix)
                    for prefix in [
                        "Thinking",
                        "thinking",
                        "1.",
                        "2.",
                        "3.",
                        "4.",
                        "5.",
                        "6.",
                        "7.",
                        "8.",
                        "9.",
                        "•",
                        "-",
                        "*",
                        "_",
                        "**",
                        "标题：",
                    ]
                ):
                    skip_thinking = False
                    found_content = True
                continue

            if found_content:
                if any(marker in stripped for marker in content_markers):
                    in_content_block = True
                    if "标题：" in stripped:
                        title = stripped.replace("标题：", "").replace("标题：", "").strip()
                        if len(title) < 100:
                            final_content.append(f"标题：{title}")
                    continue

                if in_content_block:
                    if (
                        stripped
                        and not stripped.startswith("*")
                        and not stripped.startswith("    *")
                        and not stripped.startswith("修订")
                    ):
                        final_content.append(stripped)
                    elif stripped.startswith("修订"):
                        in_content_block = False

        if final_content:
            return "\n".join(final_content).strip()

        return content.strip()

    def _generate_heading(self, text: str) -> str:
        """Generate heading for simplified text.

        Args:
            text: Simplified text

        Returns:
            Generated heading
        """
        prompt = f"""请为以下内容生成一个简洁的标题（不超过 20 字）。

内容：
{text}

标题："""

        try:
            heading = self._call_llm(prompt).strip()
            heading = self._extract_final_content(heading)
            if len(heading) > 50:
                heading = heading[:50]
            return heading
        except Exception as e:
            print(f"生成标题失败，使用默认标题: {e}")
            return "摘要"

    def _create_chunks_by_heading(self, content: Dict[str, List[str]]) -> List[Tuple[str, str]]:
        """Create chunks by accumulating paragraphs under each heading.

        Args:
            content: Dictionary with headings and paragraphs

        Returns:
            List of (heading, combined_text) tuples
        """
        chunks = []

        for heading, paragraphs in content.items():
            if not paragraphs:
                continue

            current_chunk_text = ""
            current_chunk_size = 0

            for para in paragraphs:
                para_size = len(para)

                if current_chunk_size == 0:
                    current_chunk_text = para
                    current_chunk_size = para_size
                elif current_chunk_size + para_size <= self.CHUNK_TARGET_SIZE:
                    current_chunk_text += "\n\n" + para
                    current_chunk_size += para_size
                else:
                    if current_chunk_size >= self.CHUNK_MIN_SIZE:
                        chunks.append((heading, current_chunk_text))
                    current_chunk_text = para
                    current_chunk_size = para_size

            if current_chunk_size >= self.CHUNK_MIN_SIZE:
                chunks.append((heading, current_chunk_text))
            elif current_chunk_size > 0:
                if (
                    chunks
                    and chunks[-1][1]
                    and len(chunks[-1][1]) + current_chunk_size <= self.CHUNK_TARGET_SIZE
                ):
                    prev_heading, prev_text = chunks[-1]
                    chunks[-1] = (prev_heading, prev_text + "\n\n" + current_chunk_text)
                else:
                    chunks.append((heading, current_chunk_text))

        return chunks

    def simplify_chunk(self, heading: str, text: str) -> Tuple[str, str]:
        """Simplify a text chunk using LLM.

        Args:
            heading: Heading of the chunk
            text: Original text

        Returns:
            Tuple of (heading, simplified_text)
        """
        if len(text) < self.CHUNK_MIN_SIZE:
            print(f"文本块长度 {len(text)} 小于最小阈值 {self.CHUNK_MIN_SIZE}，直接保留")
            return heading, text

        target_length = (self.SIMPLIFIED_TARGET_MIN + self.SIMPLIFIED_TARGET_MAX) // 2

        prompt = f"""请将以下内容大幅简化，只保留最核心的信息和关键点。

严格要求：
1. 必须压缩到 {self.SIMPLIFIED_TARGET_MIN} 字以内（绝对不能超过）
2. 只保留最核心的观点和结论，删除所有细节和冗余
3. 使用最简洁的语言表达
4. 只输出简化后的内容，不要包含任何推理过程

标题：{heading}

原文（{len(text)} 字）：
{text}

简化内容（严格控制在 {self.SIMPLIFIED_TARGET_MIN} 字以内）："""

        try:
            simplified = self._call_llm(prompt).strip()

            if not simplified:
                print("简化结果为空，保留原文")
                return heading, text

            new_heading = self._generate_heading(simplified)
            print(f"生成新标题：{new_heading}")

            print(
                f"简化后长度：{len(simplified)} 字符（原文：{len(text)} 字符，压缩率：{100 * len(simplified) / len(text):.1f}%）"
            )

            return new_heading, simplified

        except Exception as e:
            print(f"简化失败，保留原文: {e}")
            return heading, text

        target_length = (self.SIMPLIFIED_TARGET_MIN + self.SIMPLIFIED_TARGET_MAX) // 2

        prompt = f"""请将以下内容大幅简化，只保留最核心的信息和关键点。

严格要求：
1. 必须压缩到 {self.SIMPLIFIED_TARGET_MIN} 字以内（绝对不能超过）
2. 只保留最核心的观点和结论，删除所有细节和冗余
3. 使用最简洁的语言表达
4. 只输出简化后的内容，不要包含任何推理过程

标题：{heading}

原文（{len(text)} 字）：
{text}

简化内容（严格控制在 {self.SIMPLIFIED_TARGET_MIN} 字以内）："""

        try:
            simplified = self._call_llm(prompt).strip()

            if not simplified:
                print("简化结果为空，保留原文")
                return heading, text

            if len(simplified) < self.SIMPLIFIED_TARGET_MIN * 0.3:
                print(f"简化结果过短（{len(simplified)} 字符），保留原文")
                return heading, text

            max_allowed = len(text) * 0.5
            if len(simplified) > max_allowed:
                print(f"简化结果过长（{len(simplified)} 字符，超过原文的50%），保留原文")
                return heading, text

            new_heading = self._generate_heading(simplified)
            print(f"生成新标题：{new_heading}")

            print(
                f"简化后长度：{len(simplified)} 字符（压缩率：{100 * len(simplified) / len(text):.1f}%）"
            )

            return new_heading, simplified

        except Exception as e:
            print(f"简化失败，保留原文: {e}")
            return heading, text

    def simplify_to_content(self, pdf_path: str) -> str:
        """Simplify PDF document and return simplified Markdown content.

        Args:
            pdf_path: Path to input PDF

        Returns:
            Simplified Markdown content
        """
        print(f"处理 PDF: {pdf_path}")

        parser = MarkdownPDFParser(pdf_path)
        content = parser.parse()

        total_chars = sum(len(para) for paras in content.values() for para in paras)
        print(f"提取到 {len(content)} 个标题，共 {total_chars} 个字符")

        chunks = self._create_chunks_by_heading(content)
        print(f"创建了 {len(chunks)} 个文本块")

        self._init_llm_client()

        simplified_chunks = []
        for i, (heading, text) in enumerate(chunks, 1):
            print(f"\n处理文本块 {i}/{len(chunks)}")
            print(f"标题：{heading}")
            print(f"原文长度：{len(text)} 字符")

            simplified_heading, simplified_text = self.simplify_chunk(heading, text)

            simplified_chunks.append((simplified_heading, simplified_text))
            print(f"简化后长度：{len(simplified_text)} 字符")
            print(f"压缩率：{100 * len(simplified_text) / len(text):.1f}%")

        print("\n生成简化后的 Markdown")
        markdown_content = self._generate_markdown_content(simplified_chunks)
        print("完成!")
        return markdown_content

    def simplify(self, pdf_path: str, output_path: str) -> None:
        """Simplify PDF document and generate simplified Markdown.

        Args:
            pdf_path: Path to input PDF
            output_path: Path to output simplified Markdown
        """
        markdown_content = self.simplify_to_content(pdf_path)
        print(f"\n生成简化后的 Markdown: {output_path}")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(markdown_content, encoding="utf-8")

    def _generate_markdown_content(self, chunks: List[Tuple[str, str]]) -> str:
        """Generate Markdown content from simplified chunks.

        Args:
            chunks: List of (heading, simplified_text) tuples

        Returns:
            Markdown content string
        """
        md_lines = []

        for heading, text in chunks:
            if text:
                md_lines.append(f"# {heading}\n")
                md_lines.append(f"{text}\n\n")

        return "".join(md_lines)

    def _generate_markdown(self, chunks: List[Tuple[str, str]], output_path: str) -> None:
        """Generate Markdown from simplified chunks.

        Args:
            chunks: List of (heading, simplified_text) tuples
            output_path: Path to output Markdown file
        """
        markdown_content = self._generate_markdown_content(chunks)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(markdown_content, encoding="utf-8")

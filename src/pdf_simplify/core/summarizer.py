"""PDF Summary using LLM."""

from pathlib import Path
from typing import Optional, Dict, Any
from pdf_simplify.core.parser import PDFParser
from pdf_simplify.core.chunker import TextChunker
from pdf_simplify.core.formatter import OutputFormatter
from pdf_simplify.models.summary import Summary
from pdf_simplify.utils.config import Config


class PDFSummarizer:
    """Summarize PDF documents using LLM."""

    def __init__(
        self,
        config: Optional[Config] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        provider: str = "openai",
    ):
        """Initialize PDF summarizer.

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

        self.parser: Optional[PDFParser] = None
        self.chunker = TextChunker(
            chunk_size=self.config.chunk_size, chunk_overlap=self.config.chunk_overlap
        )

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

    def summarize(self, pdf_path: str) -> Summary:
        """Summarize PDF document.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Summary object
        """
        pdf_path_str = str(pdf_path)
        self.parser = PDFParser(pdf_path_str)

        self._init_llm_client()

        pages = self.parser.parse()
        full_text = self.parser.get_full_text()

        document_title = Path(pdf_path_str).stem

        overall_summary = self._generate_overall_summary(full_text, document_title)
        key_concepts = self._extract_key_concepts(full_text)
        main_themes = self._extract_main_themes(full_text)

        summary = Summary(
            document_title=document_title,
            document_path=pdf_path_str,
            overall_summary=overall_summary,
            key_concepts=key_concepts,
            main_themes=main_themes,
            target_audience="General readers",
            reading_time_saved="80%",
        )

        return summary

    def _generate_overall_summary(self, text: str, title: str) -> str:
        """Generate overall summary using LLM.

        Args:
            text: Full document text
            title: Document title

        Returns:
            Summary text
        """
        prompt = f"""请为标题为"{title}"的文档提供一份综合摘要。

摘要应该：
- 捕捉主要观点和论证
- 突出关键见解
- 篇幅约为500-800字
- 以清晰、引人入胜的风格撰写
- 使用中文输出
- 仅输出摘要内容，不要包含推理过程

文档内容：
{text[:10000]}... (为了简洁而截断)

摘要："""

        return self._call_llm(prompt)

    def _extract_key_concepts(self, text: str) -> list:
        """Extract key concepts using LLM.

        Args:
            text: Document text

        Returns:
            List of key concepts
        """
        prompt = f"""从以下文档中提取10个最重要的概念。
对于每个概念，提供简短描述及其重要性等级（高/中/低）。

格式为JSON对象列表，键为：concept（概念）、description（描述）、importance（重要性）
仅输出JSON，不要包含其他文本或推理过程。
使用中文输出。

文档片段：
{text[:5000]}

关键概念："""

        response = self._call_llm(prompt)

        import json

        try:
            concepts = json.loads(response)
            return concepts[:10]
        except json.JSONDecodeError:
            return []

    def _extract_main_themes(self, text: str) -> list:
        """Extract main themes using LLM.

        Args:
            text: Document text

        Returns:
            List of main themes
        """
        prompt = f"""识别以下文档的5-8个主要主题。
为每个主题提供一个简短的句子。
仅输出主题，不要包含其他文本或推理过程。
使用中文输出。

文档片段：
{text[:5000]}

主要主题："""

        response = self._call_llm(prompt)

        themes = [line.strip("- ").strip() for line in response.split("\n") if line.strip()]
        return themes[:8]

    def _call_llm(self, prompt: str) -> str:
        """Call LLM API.

        Args:
            prompt: Input prompt

        Returns:
            LLM response
        """
        print(f"将 {len(prompt)} 个字符拿去做摘要")
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

                lines = content.split("\n")
                actual_content = []
                skip = True
                for line in lines:
                    stripped = line.strip()
                    if skip:
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
                            ]
                        ):
                            skip = False
                    if not skip:
                        actual_content.append(line)
                content = "\n".join(actual_content).strip()

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

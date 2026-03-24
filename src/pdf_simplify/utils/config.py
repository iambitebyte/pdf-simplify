"""Configuration management."""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    """Application configuration."""

    llm_model: str = "gpt-4"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    provider: str = "openai"
    temperature: float = 0.3
    max_tokens: int = 4000

    summary_level: str = "detailed"
    chunk_size: int = 4000
    chunk_overlap: int = 200

    output_format: str = "markdown"
    include_outline: bool = True
    include_key_concepts: bool = True

    class Config:
        env_file = ".env"
        env_prefix = "PDF_SIMPLIFY_"
        extra = "ignore"

    @classmethod
    def from_file(cls, config_path: str) -> "Config":
        """Load configuration from TOML file.

        Args:
            config_path: Path to TOML config file

        Returns:
            Config object
        """
        import toml

        config_dict = toml.load(config_path)

        llm_config = config_dict.get("llm", {})
        summary_config = config_dict.get("summary", {})
        output_config = config_dict.get("output", {})

        config_data = {
            "llm_model": llm_config.get("model", "gpt-4"),
            "api_key": llm_config.get("api_key") or os.getenv("PDF_SIMPLIFY_API_KEY"),
            "base_url": llm_config.get("base_url") or os.getenv("PDF_SIMPLIFY_BASE_URL"),
            "provider": llm_config.get("provider", "openai"),
            "temperature": llm_config.get("temperature", 0.3),
            "max_tokens": llm_config.get("max_tokens", 4000),
            "summary_level": summary_config.get("level", "detailed"),
            "chunk_size": summary_config.get("chunk_size", 4000),
            "chunk_overlap": summary_config.get("chunk_overlap", 200),
            "output_format": output_config.get("format", "markdown"),
            "include_outline": output_config.get("include_outline", True),
            "include_key_concepts": output_config.get("include_key_concepts", True),
        }

        return cls(**config_data)

    def save_to_file(self, config_path: str) -> None:
        """Save configuration to TOML file.

        Args:
            config_path: Path to save config file
        """
        import toml

        config_dict = {
            "llm": {
                "provider": self.provider,
                "model": self.llm_model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            "summary": {
                "level": self.summary_level,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
            },
            "output": {
                "format": self.output_format,
                "include_outline": self.include_outline,
                "include_key_concepts": self.include_key_concepts,
            },
        }

        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        Path(config_path).write_text(toml.dumps(config_dict), encoding="utf-8")

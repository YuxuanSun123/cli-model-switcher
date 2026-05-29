#!/usr/bin/env python3
"""Manage active CLI AI model profiles and shared memory."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

APP_DIR = Path(os.environ.get("AI_CLI_SWITCHER_HOME", Path.home() / ".ai-cli-switcher"))
STATE_PATH = APP_DIR / "state.json"
LEGACY_MEMORY_PATH = APP_DIR / "memory.md"
MEMORY_DIR = APP_DIR / "memory"
GLOBAL_MEMORY_PATH = MEMORY_DIR / "global.md"
SESSION_MEMORY_PATH = MEMORY_DIR / "session.md"
CONTEXT_MEMORY_PATH = MEMORY_DIR / "context.md"
PROJECT_CONFIG_NAME = ".ai-cli-switcher.json"
PROJECT_MEMORY_NAME = ".ai-cli-memory.md"
SCRIPT_PATH = Path(__file__).resolve()

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("OpenAI key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("Anthropic key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("generic assignment", re.compile(r"(?i)\b(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[^'\"\s]{12,}")),
]


DEFAULT_PROFILES: dict[str, dict[str, Any]] = {
    "codex": {
        "provider": "codex",
        "command": "codex",
        "model": "gpt-5",
        "env": {"OPENAI_API_KEY": "${OPENAI_API_KEY}"},
        "memory_path": str(CONTEXT_MEMORY_PATH),
        "pages": {"home": "https://help.openai.com/en/articles/11096431"},
    },
    "claude": {
        "provider": "claude",
        "command": "claude",
        "model": "sonnet",
        "env": {"ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"},
        "memory_path": str(CONTEXT_MEMORY_PATH),
        "pages": {"home": "https://claude.ai/"},
    },
    "opencode": {
        "provider": "opencode",
        "command": "opencode",
        "model": "default",
        "env": {},
        "memory_path": str(CONTEXT_MEMORY_PATH),
        "pages": {"home": "https://opencode.ai/"},
    },
}

API_PRESETS: dict[str, dict[str, Any]] = {
    "anthropic": {
        "label": "Anthropic Claude",
        "kind": "anthropic",
        "model": "claude-sonnet-4-5",
        "env": {
            "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}",
            "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
        },
        "pages": {"api": "https://docs.anthropic.com/en/api/overview"},
        "notes": ["Native Anthropic Messages API variables."],
    },
    "azure-openai": {
        "label": "Azure OpenAI",
        "kind": "azure-openai",
        "model": "deployment-name",
        "env": {
            "AZURE_OPENAI_API_KEY": "${AZURE_OPENAI_API_KEY}",
            "AZURE_OPENAI_ENDPOINT": "${AZURE_OPENAI_ENDPOINT}",
            "OPENAI_API_VERSION": "${OPENAI_API_VERSION}",
        },
        "pages": {"api": "https://learn.microsoft.com/azure/ai-services/openai/"},
        "notes": ["Use your Azure deployment name as the model."],
    },
    "cerebras": {
        "label": "Cerebras",
        "kind": "openai-compatible",
        "model": "gpt-oss-120b",
        "env": {
            "OPENAI_API_KEY": "${CEREBRAS_API_KEY}",
            "OPENAI_BASE_URL": "https://api.cerebras.ai/v1",
            "OPENAI_API_BASE": "https://api.cerebras.ai/v1",
            "CEREBRAS_API_KEY": "${CEREBRAS_API_KEY}",
        },
        "pages": {"api": "https://inference-docs.cerebras.ai/resources/openai"},
        "notes": ["OpenAI-compatible endpoint."],
    },
    "custom-openai": {
        "label": "Custom OpenAI-compatible",
        "kind": "openai-compatible",
        "model": "default",
        "env": {
            "OPENAI_API_KEY": "${OPENAI_API_KEY}",
            "OPENAI_BASE_URL": "${OPENAI_BASE_URL}",
            "OPENAI_API_BASE": "${OPENAI_BASE_URL}",
        },
        "pages": {},
        "notes": ["Set --base-url and --api-key-env for a private gateway or proxy."],
    },
    "dashscope": {
        "label": "Alibaba Cloud Model Studio / DashScope",
        "kind": "openai-compatible",
        "model": "qwen-plus",
        "env": {
            "OPENAI_API_KEY": "${DASHSCOPE_API_KEY}",
            "OPENAI_BASE_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "OPENAI_API_BASE": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "DASHSCOPE_API_KEY": "${DASHSCOPE_API_KEY}",
        },
        "pages": {"api": "https://www.alibabacloud.com/help/doc-detail/2579562.html"},
        "notes": ["Use --base-url for intl or US regional endpoints."],
    },
    "deepseek": {
        "label": "DeepSeek",
        "kind": "openai-compatible",
        "model": "deepseek-chat",
        "env": {
            "OPENAI_API_KEY": "${DEEPSEEK_API_KEY}",
            "OPENAI_BASE_URL": "https://api.deepseek.com",
            "OPENAI_API_BASE": "https://api.deepseek.com",
            "DEEPSEEK_API_KEY": "${DEEPSEEK_API_KEY}",
        },
        "pages": {"api": "https://api-docs.deepseek.com/"},
        "notes": ["OpenAI-compatible endpoint."],
    },
    "fireworks": {
        "label": "Fireworks AI",
        "kind": "openai-compatible",
        "model": "accounts/fireworks/models/llama-v3p1-8b-instruct",
        "env": {
            "OPENAI_API_KEY": "${FIREWORKS_API_KEY}",
            "OPENAI_BASE_URL": "https://api.fireworks.ai/inference/v1",
            "OPENAI_API_BASE": "https://api.fireworks.ai/inference/v1",
            "FIREWORKS_API_KEY": "${FIREWORKS_API_KEY}",
        },
        "pages": {"api": "https://docs.fireworks.ai/tools-sdks/openai-compatibility"},
        "notes": ["OpenAI-compatible endpoint."],
    },
    "gemini": {
        "label": "Google Gemini",
        "kind": "openai-compatible",
        "model": "gemini-2.5-pro",
        "env": {
            "OPENAI_API_KEY": "${GEMINI_API_KEY}",
            "OPENAI_BASE_URL": "https://generativelanguage.googleapis.com/v1beta/openai",
            "OPENAI_API_BASE": "https://generativelanguage.googleapis.com/v1beta/openai",
            "GEMINI_API_KEY": "${GEMINI_API_KEY}",
            "GOOGLE_API_KEY": "${GEMINI_API_KEY}",
        },
        "pages": {"api": "https://ai.google.dev/gemini-api/docs/openai"},
        "notes": ["OpenAI compatibility layer for Gemini."],
    },
    "groq": {
        "label": "Groq",
        "kind": "openai-compatible",
        "model": "llama-3.3-70b-versatile",
        "env": {
            "OPENAI_API_KEY": "${GROQ_API_KEY}",
            "OPENAI_BASE_URL": "https://api.groq.com/openai/v1",
            "OPENAI_API_BASE": "https://api.groq.com/openai/v1",
            "GROQ_API_KEY": "${GROQ_API_KEY}",
        },
        "pages": {"api": "https://console.groq.com/docs/"},
        "notes": ["OpenAI-compatible endpoint."],
    },
    "lmstudio": {
        "label": "LM Studio",
        "kind": "openai-compatible-local",
        "model": "local-model",
        "env": {
            "OPENAI_API_KEY": "lm-studio",
            "OPENAI_BASE_URL": "http://localhost:1234/v1",
            "OPENAI_API_BASE": "http://localhost:1234/v1",
        },
        "pages": {"api": "https://lmstudio.ai/docs/api"},
        "notes": ["Start the LM Studio local server before using this preset."],
    },
    "mistral": {
        "label": "Mistral AI",
        "kind": "openai-compatible",
        "model": "mistral-large-latest",
        "env": {
            "OPENAI_API_KEY": "${MISTRAL_API_KEY}",
            "OPENAI_BASE_URL": "https://api.mistral.ai/v1",
            "OPENAI_API_BASE": "https://api.mistral.ai/v1",
            "MISTRAL_API_KEY": "${MISTRAL_API_KEY}",
        },
        "pages": {"api": "https://docs.mistral.ai/api"},
        "notes": ["OpenAI-compatible chat completions endpoint."],
    },
    "moonshot": {
        "label": "Moonshot / Kimi",
        "kind": "openai-compatible",
        "model": "kimi-k2-latest",
        "env": {
            "OPENAI_API_KEY": "${MOONSHOT_API_KEY}",
            "OPENAI_BASE_URL": "https://api.moonshot.ai/v1",
            "OPENAI_API_BASE": "https://api.moonshot.ai/v1",
            "MOONSHOT_API_KEY": "${MOONSHOT_API_KEY}",
        },
        "pages": {"api": "https://platform.kimi.ai/docs/api/overview"},
        "notes": ["Use --base-url https://api.moonshot.cn/v1 when your key belongs to the China endpoint."],
    },
    "novita": {
        "label": "Novita AI",
        "kind": "openai-compatible",
        "model": "default",
        "env": {
            "OPENAI_API_KEY": "${NOVITA_API_KEY}",
            "OPENAI_BASE_URL": "https://api.novita.ai/openai/v1",
            "OPENAI_API_BASE": "https://api.novita.ai/openai/v1",
            "NOVITA_API_KEY": "${NOVITA_API_KEY}",
        },
        "pages": {"api": "https://novita.ai/docs/api-reference/api-reference-overview"},
        "notes": ["OpenAI-compatible endpoint."],
    },
    "ollama": {
        "label": "Ollama",
        "kind": "openai-compatible-local",
        "model": "llama3.1",
        "env": {
            "OPENAI_API_KEY": "ollama",
            "OPENAI_BASE_URL": "http://localhost:11434/v1",
            "OPENAI_API_BASE": "http://localhost:11434/v1",
            "OLLAMA_HOST": "http://localhost:11434",
        },
        "pages": {"api": "https://docs.ollama.com/openai"},
        "notes": ["Start Ollama and pull the model before using this preset."],
    },
    "openai": {
        "label": "OpenAI",
        "kind": "openai-compatible",
        "model": "gpt-5",
        "env": {
            "OPENAI_API_KEY": "${OPENAI_API_KEY}",
            "OPENAI_BASE_URL": "https://api.openai.com/v1",
            "OPENAI_API_BASE": "https://api.openai.com/v1",
        },
        "pages": {"api": "https://platform.openai.com/docs/api-reference"},
        "notes": ["Official OpenAI API endpoint."],
    },
    "openrouter": {
        "label": "OpenRouter",
        "kind": "openai-compatible",
        "model": "openrouter/auto",
        "env": {
            "OPENAI_API_KEY": "${OPENROUTER_API_KEY}",
            "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
            "OPENAI_API_BASE": "https://openrouter.ai/api/v1",
            "OPENROUTER_API_KEY": "${OPENROUTER_API_KEY}",
        },
        "pages": {"api": "https://openrouter.ai/docs/api-reference/overview"},
        "notes": ["Routes many providers through one OpenAI-compatible endpoint."],
    },
    "perplexity": {
        "label": "Perplexity",
        "kind": "openai-compatible",
        "model": "sonar-pro",
        "env": {
            "OPENAI_API_KEY": "${PERPLEXITY_API_KEY}",
            "OPENAI_BASE_URL": "https://api.perplexity.ai/v1",
            "OPENAI_API_BASE": "https://api.perplexity.ai/v1",
            "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}",
        },
        "pages": {"api": "https://perplexity.mintlify.app/docs/agent-api/openai-compatibility"},
        "notes": ["OpenAI-compatible Responses API surface."],
    },
    "siliconflow": {
        "label": "SiliconFlow",
        "kind": "openai-compatible",
        "model": "deepseek-ai/DeepSeek-V3.2",
        "env": {
            "OPENAI_API_KEY": "${SILICONFLOW_API_KEY}",
            "OPENAI_BASE_URL": "https://api.siliconflow.cn/v1",
            "OPENAI_API_BASE": "https://api.siliconflow.cn/v1",
            "SILICONFLOW_API_KEY": "${SILICONFLOW_API_KEY}",
        },
        "pages": {"api": "https://docs.siliconflow.cn/en/api-reference/chat-completions/chat-completions"},
        "notes": ["OpenAI-compatible endpoint."],
    },
    "together": {
        "label": "Together AI",
        "kind": "openai-compatible",
        "model": "openai/gpt-oss-20b",
        "env": {
            "OPENAI_API_KEY": "${TOGETHER_API_KEY}",
            "OPENAI_BASE_URL": "https://api.together.ai/v1",
            "OPENAI_API_BASE": "https://api.together.ai/v1",
            "TOGETHER_API_KEY": "${TOGETHER_API_KEY}",
        },
        "pages": {"api": "https://docs.together.ai/docs/inference/openai-compatibility"},
        "notes": ["OpenAI-compatible endpoint."],
    },
    "volcengine": {
        "label": "Volcengine Ark",
        "kind": "openai-compatible",
        "model": "endpoint-id",
        "env": {
            "OPENAI_API_KEY": "${ARK_API_KEY}",
            "OPENAI_BASE_URL": "https://ark.cn-beijing.volces.com/api/v3",
            "OPENAI_API_BASE": "https://ark.cn-beijing.volces.com/api/v3",
            "ARK_API_KEY": "${ARK_API_KEY}",
        },
        "pages": {"api": "https://www.volcengine.com/docs/82379/1399008"},
        "notes": ["Use your Ark endpoint ID as the model."],
    },
    "xai": {
        "label": "xAI",
        "kind": "openai-compatible",
        "model": "grok-4.3",
        "env": {
            "OPENAI_API_KEY": "${XAI_API_KEY}",
            "OPENAI_BASE_URL": "https://api.x.ai/v1",
            "OPENAI_API_BASE": "https://api.x.ai/v1",
            "XAI_API_KEY": "${XAI_API_KEY}",
        },
        "pages": {"api": "https://docs.x.ai/"},
        "notes": ["OpenAI-compatible endpoint."],
    },
    "zhipu": {
        "label": "Zhipu / GLM",
        "kind": "openai-compatible",
        "model": "glm-4.7",
        "env": {
            "OPENAI_API_KEY": "${ZHIPU_API_KEY}",
            "OPENAI_BASE_URL": "https://open.bigmodel.cn/api/paas/v4",
            "OPENAI_API_BASE": "https://open.bigmodel.cn/api/paas/v4",
            "ZHIPU_API_KEY": "${ZHIPU_API_KEY}",
        },
        "pages": {"api": "https://docs.bigmodel.cn/api-reference"},
        "notes": ["OpenAI-compatible chat completions endpoint."],
    },
}

API_PRESET_ALIASES: dict[str, str] = {
    "aliyun": "dashscope",
    "ark": "volcengine",
    "azure": "azure-openai",
    "claude": "anthropic",
    "custom": "custom-openai",
    "doubao": "volcengine",
    "gemini-openai": "gemini",
    "glm": "zhipu",
    "grok": "xai",
    "kimi": "moonshot",
    "lm-studio": "lmstudio",
    "openai-compatible": "custom-openai",
    "qwen": "dashscope",
}

BASE_URL_ENV_KEYS = {
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_API_URL",
    "AZURE_OPENAI_ENDPOINT",
    "GEMINI_BASE_URL",
    "OPENAI_API_BASE",
    "OPENAI_API_BASE_URL",
    "OPENAI_BASE_URL",
}

API_KEY_ENV_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

MODEL_REGISTRY: dict[str, dict[str, dict[str, Any]]] = {
    "anthropic": {
        "claude-sonnet-4-5": {"context": 200000, "vision": True, "tools": True, "reasoning": True, "coding": True, "deployment": "cloud"},
        "claude-opus-4-1": {"context": 200000, "vision": True, "tools": True, "reasoning": True, "coding": True, "deployment": "cloud"},
    },
    "deepseek": {
        "deepseek-chat": {"context": 64000, "vision": False, "tools": True, "reasoning": False, "coding": True, "deployment": "cloud"},
        "deepseek-reasoner": {"context": 64000, "vision": False, "tools": True, "reasoning": True, "coding": True, "deployment": "cloud"},
    },
    "gemini": {
        "gemini-2.5-pro": {"context": 1000000, "vision": True, "tools": True, "reasoning": True, "coding": True, "deployment": "cloud"},
        "gemini-2.5-flash": {"context": 1000000, "vision": True, "tools": True, "reasoning": True, "coding": True, "deployment": "cloud"},
    },
    "groq": {
        "llama-3.3-70b-versatile": {"context": 128000, "vision": False, "tools": True, "reasoning": False, "coding": True, "deployment": "cloud"},
    },
    "ollama": {
        "llama3.1": {"context": 128000, "vision": False, "tools": True, "reasoning": False, "coding": True, "deployment": "local"},
        "qwen2.5-coder": {"context": 128000, "vision": False, "tools": True, "reasoning": False, "coding": True, "deployment": "local"},
    },
    "openai": {
        "gpt-5": {"context": 400000, "vision": True, "tools": True, "reasoning": True, "coding": True, "deployment": "cloud"},
        "gpt-5-mini": {"context": 400000, "vision": True, "tools": True, "reasoning": True, "coding": True, "deployment": "cloud"},
    },
    "openrouter": {
        "openrouter/auto": {"context": "provider-dependent", "vision": "provider-dependent", "tools": "provider-dependent", "reasoning": "provider-dependent", "coding": True, "deployment": "cloud"},
        "anthropic/claude-sonnet-4.5": {"context": 200000, "vision": True, "tools": True, "reasoning": True, "coding": True, "deployment": "cloud"},
        "openai/gpt-5": {"context": 400000, "vision": True, "tools": True, "reasoning": True, "coding": True, "deployment": "cloud"},
        "google/gemini-2.5-pro": {"context": 1000000, "vision": True, "tools": True, "reasoning": True, "coding": True, "deployment": "cloud"},
        "deepseek/deepseek-chat": {"context": 64000, "vision": False, "tools": True, "reasoning": False, "coding": True, "deployment": "cloud"},
    },
    "xai": {
        "grok-4.3": {"context": 256000, "vision": True, "tools": True, "reasoning": True, "coding": True, "deployment": "cloud"},
    },
}

DEFAULT_MODEL_ALIASES: dict[str, dict[str, Any]] = {
    "fast": {"provider": "openrouter", "model": "openrouter/auto", "capabilities": {"coding": True, "deployment": "cloud"}},
    "cheap": {"provider": "deepseek", "model": "deepseek-chat", "capabilities": MODEL_REGISTRY["deepseek"]["deepseek-chat"]},
    "code": {"provider": "openrouter", "model": "anthropic/claude-sonnet-4.5", "capabilities": MODEL_REGISTRY["openrouter"]["anthropic/claude-sonnet-4.5"]},
    "local": {"provider": "ollama", "model": "llama3.1", "capabilities": MODEL_REGISTRY["ollama"]["llama3.1"]},
}

FULL_SETUP_PROFILES: dict[str, dict[str, Any]] = {
    "codex": {"provider": "codex", "command": "codex", "api": "openai", "model": "gpt-5"},
    "claude": {"provider": "claude", "command": "claude", "api": "anthropic", "model": "claude-sonnet-4-5"},
    "gemini": {"provider": "gemini", "command": "gemini", "api": "gemini", "model": "gemini-2.5-pro"},
    "opencode-openrouter": {"provider": "opencode", "command": "opencode", "api": "openrouter", "model": "openrouter/auto"},
    "opencode-deepseek": {"provider": "opencode", "command": "opencode", "api": "deepseek", "model": "deepseek-chat"},
    "local-ollama": {"provider": "opencode", "command": "opencode", "api": "ollama", "model": "llama3.1"},
}

STRATEGY_PRESETS: dict[str, dict[str, Any]] = {
    "code-fast": {
        "profile": "opencode-openrouter",
        "provider": "opencode",
        "command": "opencode",
        "api": "openrouter",
        "model": "openrouter/auto",
        "description": "Fast coding profile through OpenRouter auto routing.",
    },
    "code-best": {
        "profile": "opencode-openrouter-best",
        "provider": "opencode",
        "command": "opencode",
        "api": "openrouter",
        "model": "anthropic/claude-sonnet-4.5",
        "description": "Highest-quality coding profile through OpenRouter.",
    },
    "local-private": {
        "profile": "local-ollama",
        "provider": "opencode",
        "command": "opencode",
        "api": "ollama",
        "model": "llama3.1",
        "description": "Local private profile through Ollama.",
    },
    "cheap-long-context": {
        "profile": "opencode-deepseek",
        "provider": "opencode",
        "command": "opencode",
        "api": "deepseek",
        "model": "deepseek-chat",
        "description": "Low-cost coding profile with a long-context cloud model.",
    },
}

RECIPE_CATALOG: dict[str, dict[str, Any]] = {
    "codex-openai": {
        "description": "Codex CLI through the native OpenAI API.",
        "profile": "codex",
        "spec": {"provider": "codex", "command": "codex", "api": "openai", "model": "gpt-5"},
        "aliases": ["cx"],
    },
    "claude-native": {
        "description": "Claude Code through the native Anthropic API.",
        "profile": "claude",
        "spec": {"provider": "claude", "command": "claude", "api": "anthropic", "model": "claude-sonnet-4-5"},
        "aliases": ["cl"],
    },
    "gemini-cli": {
        "description": "Gemini CLI through Google Gemini's OpenAI-compatible endpoint.",
        "profile": "gemini",
        "spec": {"provider": "gemini", "command": "gemini", "api": "gemini", "model": "gemini-2.5-pro"},
        "aliases": ["gm"],
    },
    "opencode-openrouter": {
        "description": "OpenCode through OpenRouter auto routing.",
        "profile": "opencode-openrouter",
        "spec": {"provider": "opencode", "command": "opencode", "api": "openrouter", "model": "openrouter/auto"},
        "aliases": ["router", "ocr"],
        "strategies": ["code-fast"],
    },
    "opencode-openrouter-best": {
        "description": "OpenCode through OpenRouter with a stronger coding model pinned.",
        "profile": "opencode-openrouter-best",
        "spec": {"provider": "opencode", "command": "opencode", "api": "openrouter", "model": "anthropic/claude-sonnet-4.5"},
        "aliases": ["best"],
        "strategies": ["code-best"],
    },
    "opencode-deepseek": {
        "description": "OpenCode through DeepSeek's OpenAI-compatible endpoint.",
        "profile": "opencode-deepseek",
        "spec": {"provider": "opencode", "command": "opencode", "api": "deepseek", "model": "deepseek-chat"},
        "aliases": ["ds", "cheap"],
        "strategies": ["cheap-long-context"],
    },
    "local-ollama": {
        "description": "OpenCode pointed at a local Ollama OpenAI-compatible server.",
        "profile": "local-ollama",
        "spec": {"provider": "opencode", "command": "opencode", "api": "ollama", "model": "llama3.1"},
        "aliases": ["local"],
        "strategies": ["local-private"],
    },
    "local-lmstudio": {
        "description": "OpenCode pointed at a local LM Studio OpenAI-compatible server.",
        "profile": "local-lmstudio",
        "spec": {"provider": "opencode", "command": "opencode", "api": "lmstudio", "model": "local-model"},
        "aliases": ["lmstudio"],
    },
    "custom-gateway": {
        "description": "OpenCode through a custom OpenAI-compatible gateway or proxy.",
        "profile": "custom-gateway",
        "spec": {"provider": "opencode", "command": "opencode", "api": "custom-openai", "model": "default"},
        "aliases": ["gateway", "gw"],
    },
}

RECIPE_ALIASES: dict[str, str] = {
    "anthropic": "claude-native",
    "claude": "claude-native",
    "codex": "codex-openai",
    "custom": "custom-gateway",
    "deepseek": "opencode-deepseek",
    "gateway": "custom-gateway",
    "gemini": "gemini-cli",
    "lmstudio": "local-lmstudio",
    "ollama": "local-ollama",
    "openai": "codex-openai",
    "openrouter": "opencode-openrouter",
    "opencode": "opencode-openrouter",
}

MEMORY_ENTRY_RE = re.compile(
    r"^- (?P<stamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2})(?: \[(?P<tags>[^\]]+)\])?: (?P<text>.*)$"
)


def clone_default_profiles() -> dict[str, dict[str, Any]]:
    return json.loads(json.dumps(DEFAULT_PROFILES))


def resolve_api_preset_name(name: str) -> str:
    key = name.strip().lower()
    key = API_PRESET_ALIASES.get(key, key)
    if key not in API_PRESETS:
        available = ", ".join(sorted(API_PRESETS))
        raise SystemExit(f"Unknown API preset {name!r}. Available: {available}")
    return key


def clone_api_preset(name: str) -> tuple[str, dict[str, Any]]:
    key = resolve_api_preset_name(name)
    return key, json.loads(json.dumps(API_PRESETS[key]))


def env_ref(name: str) -> str:
    name = name.strip()
    if not API_KEY_ENV_RE.match(name):
        raise SystemExit(f"Invalid environment variable name {name!r}")
    return f"${{{name}}}"


def looks_like_base_url_key(key: str) -> bool:
    upper = key.upper()
    return upper in BASE_URL_ENV_KEYS or upper.endswith("_BASE_URL") or upper.endswith("_API_BASE") or upper.endswith("_ENDPOINT")


def looks_like_api_key_key(key: str) -> bool:
    upper = key.upper()
    return upper.endswith("_API_KEY") or upper in {"API_KEY", "AUTH_TOKEN"}


def apply_api_preset_to_profile(
    profile: dict[str, Any],
    preset_name: str,
    model: str | None = None,
    base_url: str | None = None,
    api_key_env: str | None = None,
) -> str:
    preset_key, preset = clone_api_preset(preset_name)
    env = dict(preset.get("env", {}))
    if preset.get("kind", "").startswith("openai-compatible") and "OPENAI_BASE_URL" in env:
        env.setdefault("OPENAI_API_BASE_URL", env["OPENAI_BASE_URL"])

    if base_url:
        base_url = base_url.strip()
        if not re.match(r"^(https?://|\$\{[A-Za-z_][A-Za-z0-9_]*\}$)", base_url):
            raise SystemExit("--base-url must start with http://, https://, or be an ${ENV_VAR} reference.")
        url_keys = [key for key in env if looks_like_base_url_key(str(key))]
        if not url_keys:
            url_keys = ["OPENAI_BASE_URL", "OPENAI_API_BASE"]
        for key in url_keys:
            env[key] = base_url

    if api_key_env:
        api_key_reference = env_ref(api_key_env)
        auth_keys = [key for key in env if looks_like_api_key_key(str(key))]
        if not auth_keys:
            auth_keys = ["OPENAI_API_KEY"]
        for key in auth_keys:
            env[key] = api_key_reference

    profile["api_provider"] = preset_key
    profile["api_kind"] = preset.get("kind", "openai-compatible")
    profile["model"] = model or preset.get("model", profile.get("model", "default"))
    profile.setdefault("env", {}).update(env)
    profile.setdefault("pages", {}).update(preset.get("pages", {}))
    return preset_key


def clone_model_aliases() -> dict[str, dict[str, Any]]:
    return json.loads(json.dumps(DEFAULT_MODEL_ALIASES))


def normalize_provider_name(name: str | None) -> str | None:
    if not name:
        return None
    try:
        return resolve_api_preset_name(name)
    except SystemExit:
        return name.strip().lower()


def clone_profile_spec(name: str, spec: dict[str, Any]) -> dict[str, Any]:
    profile = {
        "provider": spec.get("provider", name),
        "command": spec.get("command", name),
        "model": spec.get("model", "default"),
        "env": {},
        "memory_path": spec.get("memory", str(CONTEXT_MEMORY_PATH)),
        "pages": {},
    }
    api_name = spec.get("api")
    if api_name:
        apply_api_preset_to_profile(profile, str(api_name), str(spec.get("model", "")) or None)
    if isinstance(spec.get("env"), dict):
        profile.setdefault("env", {}).update(spec["env"])
    if isinstance(spec.get("pages"), dict):
        profile.setdefault("pages", {}).update(spec["pages"])
    return profile


def upsert_profile_from_spec(state: dict[str, Any], name: str, spec: dict[str, Any]) -> bool:
    profiles = state.setdefault("profiles", {})
    profile = profiles.get(name)
    created = profile is None
    new_profile = clone_profile_spec(name, spec)
    if created:
        profiles[name] = new_profile
        return True
    for key in ["provider", "command", "model", "memory_path", "api_provider", "api_kind"]:
        if new_profile.get(key):
            profile[key] = new_profile[key]
    profile.setdefault("env", {}).update(new_profile.get("env", {}))
    profile.setdefault("pages", {}).update(new_profile.get("pages", {}))
    return False


def ensure_strategy_profile(state: dict[str, Any], strategy_name: str) -> str | None:
    strategy = STRATEGY_PRESETS.get(strategy_name)
    if not strategy:
        return None
    profile_name = str(strategy["profile"])
    upsert_profile_from_spec(state, profile_name, strategy)
    aliases = state.setdefault("aliases", {})
    if strategy_name not in state.get("profiles", {}):
        aliases[strategy_name] = profile_name
    return profile_name


def install_strategy_aliases(state: dict[str, Any]) -> list[str]:
    installed: list[str] = []
    for strategy_name in sorted(STRATEGY_PRESETS):
        profile_name = ensure_strategy_profile(state, strategy_name)
        if profile_name:
            installed.append(f"{strategy_name} -> {profile_name}")
    return installed


def resolve_recipe_name(name: str) -> str:
    key = name.strip().lower()
    key = RECIPE_ALIASES.get(key, key)
    if key not in RECIPE_CATALOG:
        available = ", ".join(sorted(RECIPE_CATALOG))
        raise SystemExit(f"Unknown recipe {name!r}. Available: {available}")
    return key


def recipe_names_from_values(values: list[str] | None) -> list[str]:
    names: list[str] = []
    for value in values or []:
        for item in re.split(r"[, ]+", value.strip()):
            if not item:
                continue
            name = resolve_recipe_name(item)
            if name not in names:
                names.append(name)
    return names


def clone_recipe(name: str) -> tuple[str, dict[str, Any]]:
    key = resolve_recipe_name(name)
    return key, json.loads(json.dumps(RECIPE_CATALOG[key]))


def recipe_profile_name(name: str) -> str:
    _, recipe = clone_recipe(name)
    return str(recipe["profile"])


def install_recipe_into_state(state: dict[str, Any], name: str, force: bool = False) -> tuple[str, list[dict[str, str]]]:
    recipe_name, recipe = clone_recipe(name)
    profile_name = str(recipe["profile"])
    events: list[dict[str, str]] = []
    created = upsert_profile_from_spec(state, profile_name, recipe["spec"])
    add_repair_event(events, "created" if created else "updated", "profile", profile_name)

    profiles = state.setdefault("profiles", {})
    aliases = state.setdefault("aliases", {})
    for alias in recipe.get("aliases", []):
        alias = str(alias)
        if alias in profiles and alias != profile_name:
            add_repair_event(events, "skipped", "alias", f"{alias} conflicts with a profile")
            continue
        if alias in aliases and aliases.get(alias) != profile_name and not force:
            add_repair_event(events, "skipped", "alias", f"{alias} already points to {aliases.get(alias)}")
            continue
        aliases[alias] = profile_name
        add_repair_event(events, "saved", "alias", f"{alias} -> {profile_name}")

    for strategy_name in recipe.get("strategies", []):
        strategy_profile = ensure_strategy_profile(state, str(strategy_name))
        if strategy_profile:
            add_repair_event(events, "saved", "strategy", f"{strategy_name} -> {strategy_profile}")
    return profile_name, events


def load_state_for_dry_run() -> dict[str, Any]:
    if STATE_PATH.exists():
        return normalize_state(read_json(STATE_PATH))
    return normalize_state({"active": "codex", "profiles": clone_default_profiles()})


def default_wizard_recipes(detected: dict[str, str | None]) -> list[str]:
    recipes: list[str] = []
    if detected.get("codex"):
        recipes.append("codex-openai")
    if detected.get("claude"):
        recipes.append("claude-native")
    if detected.get("gemini"):
        recipes.append("gemini-cli")
    if detected.get("opencode"):
        recipes.extend(["opencode-openrouter", "opencode-deepseek"])
        if detected.get("ollama"):
            recipes.append("local-ollama")
    if detected.get("ollama") and "local-ollama" not in recipes:
        recipes.append("local-ollama")
    if recipes:
        return recipes
    return ["codex-openai", "claude-native", "opencode-openrouter"]


def prompt_text(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"{prompt}{suffix}: ").strip()
    except EOFError:
        return default
    return value or default


def prompt_yes_no(prompt: str, default: bool = True) -> bool:
    label = "Y/n" if default else "y/N"
    value = prompt_text(f"{prompt} ({label})", "").strip().lower()
    if not value:
        return default
    return value in {"y", "yes", "1", "true", "on"}


def resolve_active_target(state: dict[str, Any], target: str) -> str:
    if target in RECIPE_CATALOG or target in RECIPE_ALIASES:
        target = recipe_profile_name(target)
    resolved = resolve_profile_name(state, target)
    if resolved not in state.get("profiles", {}):
        available = ", ".join(sorted(state.get("profiles", {})))
        raise SystemExit(f"Unknown active target {target!r}. Available: {available}")
    return resolved


def detect_cli_tools() -> dict[str, str | None]:
    candidates = {
        "codex": "codex",
        "claude": "claude",
        "opencode": "opencode",
        "gemini": "gemini",
        "ollama": "ollama",
    }
    return {name: shutil.which(command) for name, command in candidates.items()}


def resolve_model_reference(
    state: dict[str, Any],
    name: str,
    provider: str | None = None,
) -> tuple[str | None, str, dict[str, Any], str | None]:
    model_aliases = state.setdefault("model_aliases", {})
    normalized_provider = normalize_provider_name(provider)
    if name in model_aliases:
        alias = model_aliases[name]
        alias_provider = normalize_provider_name(str(alias.get("provider", ""))) or normalized_provider
        model = str(alias.get("model", name))
        capabilities = dict(alias.get("capabilities", {}))
        if not capabilities and alias_provider:
            capabilities = dict(MODEL_REGISTRY.get(alias_provider, {}).get(model, {}))
        return alias_provider, model, capabilities, name

    if normalized_provider:
        capabilities = dict(MODEL_REGISTRY.get(normalized_provider, {}).get(name, {}))
        return normalized_provider, name, capabilities, None

    matches: list[tuple[str, dict[str, Any]]] = []
    for provider_name, models in MODEL_REGISTRY.items():
        if name in models:
            matches.append((provider_name, models[name]))
    if len(matches) == 1:
        return matches[0][0], name, dict(matches[0][1]), None
    return None, name, {}, None


def parse_capability_pair(pair: str) -> tuple[str, Any]:
    key, value = parse_env_pair(pair)
    lowered = value.strip().lower()
    if lowered in {"true", "yes", "1"}:
        return key, True
    if lowered in {"false", "no", "0"}:
        return key, False
    try:
        return key, int(value)
    except ValueError:
        return key, value


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Expected a JSON object in {path}")
    return data


def ensure_memory_files(project_root: Path | None = None) -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    if not GLOBAL_MEMORY_PATH.exists():
        if LEGACY_MEMORY_PATH.exists():
            legacy = LEGACY_MEMORY_PATH.read_text(encoding="utf-8").strip()
            GLOBAL_MEMORY_PATH.write_text(legacy + "\n", encoding="utf-8")
        else:
            GLOBAL_MEMORY_PATH.write_text("# Global CLI AI Memory\n\n", encoding="utf-8")
    if not SESSION_MEMORY_PATH.exists():
        SESSION_MEMORY_PATH.write_text("# Session CLI AI Memory\n\n", encoding="utf-8")
    if project_root:
        project_memory = project_root / PROJECT_MEMORY_NAME
        if not project_memory.exists():
            project_memory.write_text("# Project CLI AI Memory\n\n", encoding="utf-8")
    refresh_context_memory(project_root)


def refresh_context_memory(project_root: Path | None = None) -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    parts: list[tuple[str, Path]] = [("Global", GLOBAL_MEMORY_PATH)]
    if project_root:
        parts.append(("Project", project_root / PROJECT_MEMORY_NAME))
    parts.append(("Session", SESSION_MEMORY_PATH))
    content = ["# Combined CLI AI Context", ""]
    for label, path in parts:
        if path.exists():
            text = path.read_text(encoding="utf-8").strip()
            content.extend([f"## {label}", text, ""])
    CONTEXT_MEMORY_PATH.write_text("\n".join(content).rstrip() + "\n", encoding="utf-8")


def ensure_state() -> dict[str, Any]:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    ensure_memory_files(find_project_root())
    if not STATE_PATH.exists():
        state = {"active": "codex", "profiles": clone_default_profiles()}
        save_state(state)
        return state
    return read_json(STATE_PATH)


def save_state(state: dict[str, Any]) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_state(state: dict[str, Any]) -> dict[str, Any]:
    state.setdefault("active", "codex")
    state.setdefault("aliases", {})
    state.setdefault("sessions", {})
    model_aliases = state.setdefault("model_aliases", {})
    for alias, payload in clone_model_aliases().items():
        model_aliases.setdefault(alias, payload)
    profiles = state.setdefault("profiles", {})
    if not profiles:
        profiles.update(clone_default_profiles())
    for name, profile in profiles.items():
        defaults = DEFAULT_PROFILES.get(name, {})
        profile.setdefault("provider", defaults.get("provider", name))
        profile.setdefault("command", defaults.get("command", name))
        profile.setdefault("model", defaults.get("model", "default"))
        profile.setdefault("env", {})
        profile.setdefault("pages", {})
        if isinstance(defaults.get("pages"), dict):
            for label, url in defaults["pages"].items():
                profile["pages"].setdefault(label, url)
        if not profile.get("memory_path") or profile.get("memory_path") == str(LEGACY_MEMORY_PATH):
            profile["memory_path"] = str(CONTEXT_MEMORY_PATH)
    return state


def resolve_profile_name(state: dict[str, Any], name: str) -> str:
    aliases = state.get("aliases", {})
    seen: set[str] = set()
    current = name
    while current in aliases:
        if current in seen:
            raise SystemExit(f"Alias cycle detected at {current!r}")
        seen.add(current)
        current = aliases[current]
    return current


def find_project_config(start: Path | None = None) -> Path | None:
    current = (start or Path.cwd()).resolve()
    for path in [current, *current.parents]:
        config_path = path / PROJECT_CONFIG_NAME
        if config_path.exists():
            return config_path
    return None


def find_project_root(start: Path | None = None) -> Path | None:
    config = find_project_config(start)
    return config.parent if config else None


def load_project_config(start: Path | None = None) -> tuple[dict[str, Any], Path | None]:
    config_path = find_project_config(start)
    if not config_path:
        return {}, None
    return read_json(config_path), config_path


def load_project_config_at(root: Path) -> dict[str, Any]:
    path = root / PROJECT_CONFIG_NAME
    if not path.exists():
        return {}
    return read_json(path)


def save_project_config(config: dict[str, Any], root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / PROJECT_CONFIG_NAME
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def effective_state(start: Path | None = None) -> tuple[dict[str, Any], Path | None]:
    state = normalize_state(ensure_state())
    project_config, config_path = load_project_config(start)
    if project_config:
        merged = json.loads(json.dumps(state))
        merged.setdefault("profiles", {}).update(project_config.get("profiles", {}))
        merged.setdefault("aliases", {}).update(project_config.get("aliases", {}))
        if project_config.get("active"):
            merged["active"] = project_config["active"]
        merged["_project_config"] = str(config_path)
        return normalize_state(merged), config_path
    return state, None


def active_profile(state: dict[str, Any]) -> dict[str, Any]:
    active = state.get("active")
    if isinstance(active, str):
        active = resolve_profile_name(state, active)
    profiles = state.get("profiles", {})
    if active not in profiles:
        raise SystemExit(f"Active profile {active!r} is missing from {STATE_PATH}")
    return profiles[active]


def profile_from_args(args: argparse.Namespace) -> dict[str, Any]:
    env = dict(parse_env_pair(item) for item in args.env)
    validate_env_secrets(env, args.allow_secret_env)
    return {
        "provider": args.provider or args.name,
        "command": args.command or args.name,
        "model": args.model,
        "env": env,
        "memory_path": args.memory or str(CONTEXT_MEMORY_PATH),
        "pages": dict(parse_page_pair(item) for item in args.page),
    }


def update_profile_from_args(profile: dict[str, Any], args: argparse.Namespace) -> None:
    if args.provider:
        profile["provider"] = args.provider
    if args.command:
        profile["command"] = args.command
    if args.model:
        profile["model"] = args.model
    if args.memory:
        profile["memory_path"] = args.memory
    for item in args.env:
        key, value = parse_env_pair(item)
        validate_env_secrets({key: value}, args.allow_secret_env)
        profile.setdefault("env", {})[key] = value
    for key in args.unset_env:
        profile.setdefault("env", {}).pop(key, None)
    for item in args.page:
        key, value = parse_page_pair(item)
        profile.setdefault("pages", {})[key] = value
    for key in args.unset_page:
        profile.setdefault("pages", {}).pop(key, None)


def parse_env_pair(pair: str) -> tuple[str, str]:
    if "=" not in pair:
        raise SystemExit(f"Expected KEY=VALUE, got {pair!r}")
    key, value = pair.split("=", 1)
    key = key.strip()
    if not key:
        raise SystemExit(f"Environment key cannot be empty in {pair!r}")
    return key, value


def parse_page_pair(pair: str) -> tuple[str, str]:
    if "=" not in pair:
        raise SystemExit(f"Expected LABEL=URL, got {pair!r}")
    label, url = pair.split("=", 1)
    label = label.strip()
    url = url.strip()
    if not label or not url:
        raise SystemExit(f"Page label and URL cannot be empty in {pair!r}")
    if not re.match(r"^https?://", url, re.IGNORECASE):
        raise SystemExit(f"Page URL must start with http:// or https://, got {url!r}")
    return label, url


def profile_summary(name: str, profile: dict[str, Any]) -> str:
    api_provider = profile.get("api_provider")
    api_suffix = f" via {api_provider}" if api_provider else ""
    return f"{name}: {profile.get('command')} ({profile.get('model')}){api_suffix}"


def memory_target(scope: str) -> Path:
    project_root = find_project_root()
    if scope == "global":
        return GLOBAL_MEMORY_PATH
    if scope == "session":
        return SESSION_MEMORY_PATH
    if scope == "project":
        if not project_root:
            raise SystemExit(f"No {PROJECT_CONFIG_NAME} found. Run project-init first.")
        return project_root / PROJECT_MEMORY_NAME
    raise SystemExit(f"Unknown memory scope {scope!r}")


def detect_secret(text: str) -> str | None:
    for label, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            return label
    return None


def env_reference_name(value: Any) -> str | None:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        name = value[2:-1].strip()
        return name or None
    return None


def validate_env_secrets(env: dict[str, str], allow_secret: bool) -> None:
    if allow_secret:
        return
    for key, value in env.items():
        if value.startswith("${") and value.endswith("}"):
            continue
        secret = detect_secret(f"{key}={value}") or detect_secret(value)
        if secret:
            raise SystemExit(
                f"Refusing to store possible secret in env {key!r} ({secret}). "
                "Use a shell environment variable reference like KEY=${KEY}, or pass --allow-secret-env."
            )


def validate_state_secrets(state: dict[str, Any], allow_secret: bool) -> None:
    if allow_secret:
        return
    for profile_name, profile in state.get("profiles", {}).items():
        env = profile.get("env", {})
        if isinstance(env, dict):
            try:
                validate_env_secrets({str(k): str(v) for k, v in env.items()}, False)
            except SystemExit as exc:
                raise SystemExit(f"Profile {profile_name!r}: {exc}") from exc


def timestamp_slug() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def backup_file(path: Path) -> Path:
    backup = path.with_name(f"{path.name}.bak-{timestamp_slug()}")
    shutil.copy2(path, backup)
    return backup


def add_repair_event(events: list[dict[str, str]], status: str, name: str, detail: str) -> None:
    events.append({"status": status, "name": name, "detail": detail})


def safe_read_json_for_repair(path: Path, label: str, fix: bool, events: list[dict[str, str]]) -> dict[str, Any] | None:
    if not path.exists():
        add_repair_event(events, "warn", label, f"missing: {path}")
        return None
    try:
        return read_json(path)
    except SystemExit as exc:
        if not fix:
            add_repair_event(events, "fail", label, str(exc))
            return None
        backup = backup_file(path)
        add_repair_event(events, "fixed", label, f"invalid JSON backed up to {backup}")
        return None


def clean_aliases(state: dict[str, Any]) -> tuple[list[str], bool]:
    profiles = state.setdefault("profiles", {})
    aliases = state.setdefault("aliases", {})
    changed = False
    removed: list[str] = []
    for alias in list(aliases):
        target = aliases.get(alias)
        if alias in profiles:
            removed.append(f"{alias} conflicts with a profile")
            del aliases[alias]
            changed = True
            continue
        try:
            resolved = resolve_profile_name(state, alias)
        except SystemExit:
            removed.append(f"{alias} has an alias cycle")
            del aliases[alias]
            changed = True
            continue
        if resolved not in profiles:
            removed.append(f"{alias} targets missing profile {target!r}")
            del aliases[alias]
            changed = True
    return removed, changed


def ensure_valid_active(state: dict[str, Any]) -> tuple[str | None, bool]:
    profiles = state.setdefault("profiles", {})
    active = str(state.get("active", ""))
    try:
        resolved = resolve_profile_name(state, active) if active else ""
    except SystemExit:
        resolved = ""
    if resolved in profiles:
        return None, False
    replacement = "codex" if "codex" in profiles else next(iter(profiles), None)
    if replacement:
        state["active"] = replacement
        return f"active profile reset to {replacement}", True
    state.setdefault("profiles", {}).update(clone_default_profiles())
    state["active"] = "codex"
    return "missing profiles recreated and active profile reset to codex", True


def repair_state_object(state: dict[str, Any]) -> tuple[dict[str, Any], list[str], bool]:
    before = json.dumps(state, sort_keys=True, ensure_ascii=False)
    state = normalize_state(state)
    notes: list[str] = []
    removed_aliases, alias_changed = clean_aliases(state)
    notes.extend([f"removed alias: {item}" for item in removed_aliases])
    active_note, active_changed = ensure_valid_active(state)
    if active_note:
        notes.append(active_note)
    after = json.dumps(state, sort_keys=True, ensure_ascii=False)
    return state, notes, before != after or alias_changed or active_changed


def repair_global_state(fix: bool, events: list[dict[str, str]]) -> dict[str, Any]:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    raw = safe_read_json_for_repair(STATE_PATH, "state file", fix, events)
    if raw is None:
        state = {"active": "codex", "profiles": clone_default_profiles(), "aliases": {}, "model_aliases": clone_model_aliases()}
        if fix:
            save_state(normalize_state(state))
            add_repair_event(events, "fixed", "state file", f"created default state at {STATE_PATH}")
        return normalize_state(state)
    state, notes, changed = repair_state_object(raw)
    for note in notes:
        add_repair_event(events, "fixed" if fix else "warn", "state repair", note)
    if changed and fix:
        save_state(state)
        add_repair_event(events, "fixed", "state file", "normalized and saved state")
    elif changed:
        add_repair_event(events, "warn", "state file", "normalization changes available; run doctor --fix")
    else:
        add_repair_event(events, "ok", "state file", str(STATE_PATH))
    return state


def repair_project_config(fix: bool, state: dict[str, Any], events: list[dict[str, str]]) -> Path | None:
    config_path = find_project_config()
    if not config_path:
        return None
    raw = safe_read_json_for_repair(config_path, "project config", fix, events)
    if raw is None:
        if fix:
            config = {"active": state.get("active", "codex"), "profiles": {}, "aliases": {}}
            save_project_config(config, config_path.parent)
            ensure_memory_files(config_path.parent)
            add_repair_event(events, "fixed", "project config", f"created default project config at {config_path}")
        return config_path
    before = json.dumps(raw, sort_keys=True, ensure_ascii=False)
    raw.setdefault("profiles", {})
    raw.setdefault("aliases", {})
    removed, alias_changed = clean_aliases(raw)
    for item in removed:
        add_repair_event(events, "fixed" if fix else "warn", "project alias", f"removed alias: {item}")
    if raw.get("active"):
        effective_profiles = dict(state.get("profiles", {}))
        effective_profiles.update(raw.get("profiles", {}))
        active = str(raw.get("active"))
        try:
            resolved = resolve_profile_name({"aliases": {**state.get("aliases", {}), **raw.get("aliases", {})}}, active)
        except SystemExit:
            resolved = ""
        if resolved not in effective_profiles:
            raw["active"] = state.get("active", "codex")
            add_repair_event(events, "fixed" if fix else "warn", "project active", f"reset to {raw['active']}")
    after = json.dumps(raw, sort_keys=True, ensure_ascii=False)
    if (before != after or alias_changed) and fix:
        save_project_config(raw, config_path.parent)
        add_repair_event(events, "fixed", "project config", "normalized and saved project config")
    ensure_memory_files(config_path.parent)
    add_repair_event(events, "ok", "project memory", str(config_path.parent / PROJECT_MEMORY_NAME))
    return config_path


def check_wrapper_staleness(fix: bool, events: list[dict[str, str]]) -> None:
    required_ps = [
        "function ai-api",
        "function ai-model",
        "function ai-strategy",
        "function ai-recipe",
        "function ai-adapter",
        "function ai-session",
        "function ai-handoff",
        "function ai-memory",
        "function ai-secret",
    ]
    ps_profile = Path(os.environ.get("PROFILE", Path.home() / "Documents/PowerShell/Microsoft.PowerShell_profile.ps1"))
    if ps_profile.exists():
        text = ps_profile.read_text(encoding="utf-8", errors="replace")
        if "# >>> ai-cli-switcher >>>" in text:
            missing = [item for item in required_ps if item not in text]
            if missing and fix:
                cmd_install_powershell(argparse.Namespace(profile=str(ps_profile), dry_run=False))
                add_repair_event(events, "fixed", "PowerShell wrapper", f"reinstalled missing helpers: {', '.join(missing)}")
            elif missing:
                add_repair_event(events, "warn", "PowerShell wrapper", f"missing helpers: {', '.join(missing)}")
            else:
                add_repair_event(events, "ok", "PowerShell wrapper", str(ps_profile))
    cmd_dir = Path.home() / "bin" / "ai-cli-switcher"
    if cmd_dir.exists():
        required_cmd = [
            "ai-api.cmd",
            "ai-model.cmd",
            "ai-strategy.cmd",
            "ai-recipe.cmd",
            "ai-adapter.cmd",
            "ai-session.cmd",
            "ai-handoff.cmd",
            "ai-memory.cmd",
            "ai-secret.cmd",
        ]
        missing_cmd = [name for name in required_cmd if not (cmd_dir / name).exists()]
        if missing_cmd and fix:
            cmd_install_cmd(argparse.Namespace(dir=str(cmd_dir), dry_run=False))
            add_repair_event(events, "fixed", "cmd wrapper", f"reinstalled missing wrappers: {', '.join(missing_cmd)}")
        elif missing_cmd:
            add_repair_event(events, "warn", "cmd wrapper", f"missing wrappers: {', '.join(missing_cmd)}")
        else:
            add_repair_event(events, "ok", "cmd wrapper", str(cmd_dir))


def portable_path(path_value: Any) -> Any:
    if not isinstance(path_value, str):
        return path_value
    try:
        path = Path(path_value).expanduser().resolve()
    except OSError:
        return path_value
    try:
        rel = path.relative_to(APP_DIR.resolve())
        return "${AI_CLI_SWITCHER_HOME}/" + rel.as_posix()
    except ValueError:
        pass
    if path == CONTEXT_MEMORY_PATH.resolve():
        return "${AI_CLI_SWITCHER_HOME}/memory/context.md"
    if path.name == PROJECT_MEMORY_NAME:
        return "${PROJECT_ROOT}/" + PROJECT_MEMORY_NAME
    return path_value


def expand_portable_path(path_value: Any) -> Any:
    if not isinstance(path_value, str):
        return path_value
    if path_value.startswith("${AI_CLI_SWITCHER_HOME}/"):
        rel = path_value.split("/", 1)[1]
        return str(APP_DIR / Path(rel))
    if path_value == "${PROJECT_ROOT}/" + PROJECT_MEMORY_NAME:
        return PROJECT_MEMORY_NAME
    return path_value


def make_portable_state(state: dict[str, Any]) -> dict[str, Any]:
    portable = json.loads(json.dumps(normalize_state(state)))
    for profile in portable.get("profiles", {}).values():
        if isinstance(profile, dict) and "memory_path" in profile:
            profile["memory_path"] = portable_path(profile["memory_path"])
    return portable


def expand_portable_state(state: dict[str, Any]) -> dict[str, Any]:
    expanded = json.loads(json.dumps(state))
    for profile in expanded.get("profiles", {}).values():
        if isinstance(profile, dict) and "memory_path" in profile:
            profile["memory_path"] = expand_portable_path(profile["memory_path"])
    return expanded


def unique_import_name(existing: dict[str, Any], name: str) -> str:
    candidate = f"{name}-imported"
    index = 2
    while candidate in existing:
        candidate = f"{name}-imported{index}"
        index += 1
    return candidate


def merge_named_mapping(
    existing: dict[str, Any],
    incoming: dict[str, Any],
    policy: str,
) -> tuple[dict[str, str], list[str]]:
    name_map: dict[str, str] = {}
    notes: list[str] = []
    for name, value in incoming.items():
        target = name
        if name in existing:
            if policy == "keep":
                name_map[name] = name
                notes.append(f"kept existing {name}")
                continue
            if policy == "rename":
                target = unique_import_name(existing, name)
                notes.append(f"renamed {name} -> {target}")
            else:
                notes.append(f"overwrote {name}")
        existing[target] = value
        name_map[name] = target
    return name_map, notes


def add_secret_finding(findings: list[dict[str, str]], scope: str, path: Path, location: str, label: str) -> None:
    findings.append({"scope": scope, "path": str(path), "location": location, "secret_type": label})


def audit_env_map(findings: list[dict[str, str]], scope: str, path: Path, prefix: str, env: dict[str, Any]) -> None:
    for key, value in env.items():
        text = str(value)
        if env_reference_name(text):
            continue
        secret = detect_secret(f"{key}={text}") or detect_secret(text)
        if secret:
            add_secret_finding(findings, scope, path, f"{prefix}.env.{key}", secret)


def audit_state_object(findings: list[dict[str, str]], scope: str, path: Path, state: dict[str, Any]) -> None:
    for profile_name, profile in state.get("profiles", {}).items():
        env = profile.get("env", {}) if isinstance(profile, dict) else {}
        if isinstance(env, dict):
            audit_env_map(findings, scope, path, f"profiles.{profile_name}", env)


def audit_text_file(findings: list[dict[str, str]], scope: str, path: Path) -> None:
    if not path.exists():
        return
    for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        secret = detect_secret(line)
        if secret:
            add_secret_finding(findings, scope, path, f"line {lineno}", secret)


def shell_quote(value: str, shell: str) -> str:
    if shell in {"powershell", "nu"}:
        return "'" + value.replace("'", "''") + "'"
    if shell == "cmd":
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def emit_env_assignment(key: str, value: str, shell: str) -> str:
    if shell == "powershell":
        return f"$env:{key} = {shell_quote(value, shell)}"
    if shell == "cmd":
        return f'set "{key}={value}"'
    if shell == "fish":
        return f"set -gx {key} {shell_quote(value, shell)}"
    if shell == "nu":
        return f"$env.{key} = {shell_quote(value, shell)}"
    return f"export {key}={shell_quote(value, shell)}"


def emit_env_reference(key: str, ref: str, shell: str) -> str:
    if shell == "powershell":
        return f"if ($env:{ref}) {{ $env:{key} = $env:{ref} }}"
    if shell == "cmd":
        return f'set "{key}=%{ref}%"'
    if shell == "fish":
        return f"if set -q {ref}; set -gx {key} ${ref}; end"
    if shell == "nu":
        return f"if ({shell_quote(ref, shell)} in $env) {{ $env.{key} = $env.{ref} }}"
    return f'[ -n "${{{ref}:-}}" ] && export {key}="${{{ref}}}"'


def profile_env_values(profile: dict[str, Any]) -> dict[str, str]:
    values = {
        "AI_CLI_PROVIDER": profile["provider"],
        "AI_CLI_MODEL": profile.get("model", ""),
        "AI_CLI_COMMAND": profile.get("command", ""),
        "AI_CLI_MEMORY": profile.get("memory_path", str(CONTEXT_MEMORY_PATH)),
    }
    if profile.get("api_provider"):
        values["AI_CLI_API_PROVIDER"] = profile["api_provider"]
    if profile.get("api_kind"):
        values["AI_CLI_API_KIND"] = profile["api_kind"]
    return {str(key): str(value) for key, value in values.items()}


def project_root_for_env(start: Path | None = None) -> Path | None:
    return find_project_root(start) if start else find_project_root()


def emit_env(profile: dict[str, Any], shell: str, project_root: Path | None = None) -> str:
    ensure_memory_files(project_root if project_root is not None else project_root_for_env())
    values = profile_env_values(profile)
    lines: list[str] = []
    for key, value in values.items():
        lines.append(emit_env_assignment(key, value, shell))
    for key, value in profile.get("env", {}).items():
        ref = env_reference_name(value)
        if ref:
            lines.append(emit_env_reference(str(key), ref, shell))
            continue
        lines.append(emit_env_assignment(str(key), str(value), shell))
    return "\n".join(lines)


def profile_process_env(profile: dict[str, Any], project_root: Path | None = None) -> dict[str, str]:
    ensure_memory_files(project_root if project_root is not None else project_root_for_env())
    env = os.environ.copy()
    env.update(profile_env_values(profile))
    for key, value in profile.get("env", {}).items():
        ref = env_reference_name(value)
        if ref:
            if os.environ.get(ref) is not None:
                env[str(key)] = os.environ[ref]
            continue
        env[str(key)] = str(value)
    return env


def command_invocation(command: str, args: list[str], shell: str) -> str:
    if not command:
        raise SystemExit("Profile has no command configured.")
    if shell == "powershell":
        parts = [f"& {shell_quote(command, shell)}"]
        parts.extend(shell_quote(item, shell) for item in args)
        return " ".join(parts)
    parts = [f"exec {shell_quote(command, 'bash')}"]
    parts.extend(shell_quote(item, "bash") for item in args)
    return " ".join(parts)


def profile_launch_script(profile: dict[str, Any], shell: str, args: list[str], cwd: Path | None = None) -> str:
    cwd = (cwd or Path.cwd()).resolve()
    project_root = project_root_for_env(cwd)
    command = str(profile.get("command", ""))
    if shell == "powershell":
        lines = [f"Set-Location -LiteralPath {shell_quote(str(cwd), shell)}", emit_env(profile, shell, project_root), command_invocation(command, args, shell)]
        return "\n".join(line for line in lines if line)
    lines = [f"cd {shell_quote(str(cwd), 'bash')}", emit_env(profile, "bash", project_root), command_invocation(command, args, "bash")]
    return "\n".join(line for line in lines if line)


def profile_launch_command(profile: dict[str, Any], shell: str, args: list[str], cwd: Path | None = None) -> str:
    script = profile_launch_script(profile, shell, args, cwd)
    if shell == "powershell":
        return f"powershell -NoExit -ExecutionPolicy Bypass -Command {shell_quote(script, shell)}"
    return f"bash -lc {shell_quote(script, 'bash')}"


def cmd_init(_: argparse.Namespace) -> None:
    state = normalize_state(ensure_state())
    save_state(state)
    print(f"Initialized {STATE_PATH}")
    print(f"Global memory: {GLOBAL_MEMORY_PATH}")
    print(f"Combined context: {CONTEXT_MEMORY_PATH}")


def cmd_list(_: argparse.Namespace) -> None:
    state, config_path = effective_state()
    active = resolve_profile_name(state, str(state.get("active")))
    if config_path:
        print(f"Project config: {config_path}")
    for name, profile in state.get("profiles", {}).items():
        marker = "*" if name == active else " "
        found = "ok" if shutil.which(str(profile.get("command"))) else "missing"
        print(f"{marker} {profile_summary(name, profile)} [{found}]")
    aliases = state.get("aliases", {})
    if aliases:
        print("Aliases:")
        for alias, target in aliases.items():
            print(f"  {alias} -> {target}")


def cmd_use(args: argparse.Namespace) -> None:
    state = normalize_state(ensure_state())
    effective, _ = effective_state()
    if args.project:
        profiles = effective.get("profiles", {})
        name = resolve_profile_name(effective, args.name)
        if name not in profiles:
            strategy_profile = ensure_strategy_profile(state, args.name)
            if strategy_profile:
                save_state(state)
                effective, _ = effective_state()
                profiles = effective.get("profiles", {})
                name = strategy_profile
        if name not in profiles:
            available = ", ".join(sorted(profiles))
            raise SystemExit(f"Unknown profile {args.name!r}. Available: {available}")
        root = Path.cwd().resolve()
        config, config_path = load_project_config(root)
        if config_path:
            root = config_path.parent
        config["active"] = name
        save_project_config(config, root)
        ensure_memory_files(root)
        print(f"Project CLI AI profile: {name} ({root / PROJECT_CONFIG_NAME})")
        if args.open_page:
            open_profile_page(effective, name, args.open_page)
        return
    profiles = state.get("profiles", {})
    name = resolve_profile_name(state, args.name)
    if name not in profiles:
        strategy_profile = ensure_strategy_profile(state, args.name)
        if strategy_profile:
            name = strategy_profile
            profiles = state.get("profiles", {})
    if name not in profiles:
        available = ", ".join(sorted(profiles))
        raise SystemExit(f"Unknown global profile {args.name!r}. Available: {available}")
    state["active"] = name
    save_state(state)
    profile = profiles[name]
    print(f"Active CLI AI profile: {name} -> {profile.get('command')} ({profile.get('model')})")
    if args.open_page:
        open_profile_page(state, name, args.open_page)


def cmd_current(args: argparse.Namespace) -> None:
    state, config_path = effective_state()
    profile = active_profile(state)
    if args.shell:
        print(emit_env(profile, args.shell))
        return
    print(json.dumps({"active": state["active"], "project_config": str(config_path) if config_path else None, "profile": profile}, indent=2, ensure_ascii=False))


def cmd_status(args: argparse.Namespace) -> None:
    state, config_path = effective_state()
    active = resolve_profile_name(state, str(state.get("active")))
    profile = active_profile(state)
    command = str(profile.get("command", ""))
    command_path = shutil.which(command)
    payload = {
        "active": active,
        "provider": profile.get("provider"),
        "api_provider": profile.get("api_provider"),
        "api_kind": profile.get("api_kind"),
        "model": profile.get("model"),
        "command": command,
        "command_found": bool(command_path),
        "command_path": command_path,
        "memory": profile.get("memory_path", str(CONTEXT_MEMORY_PATH)),
        "project_config": str(config_path) if config_path else None,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    scope = "project" if config_path else "global"
    found = "ok" if command_path else "missing"
    print(f"{payload['active']} [{scope}] -> {payload['command']} ({payload['model']}) [{found}]")
    if payload["api_provider"]:
        print(f"api: {payload['api_provider']} ({payload['api_kind']})")
    print(f"memory: {payload['memory']}")


def cmd_add(args: argparse.Namespace) -> None:
    state = normalize_state(ensure_state())
    project_config: dict[str, Any] | None = None
    if args.project:
        project_config, config_path = load_project_config()
        if not config_path:
            raise SystemExit(f"No {PROJECT_CONFIG_NAME} found. Run project-init first.")
        profiles = project_config.setdefault("profiles", {})
        save = lambda: save_project_config(project_config, config_path.parent)
    else:
        profiles = state["profiles"]
        save = lambda: save_state(state)
    if args.name in profiles and not args.force:
        raise SystemExit(f"Profile {args.name!r} already exists. Use --force to replace it.")
    profiles[args.name] = profile_from_args(args)
    save()
    print(f"Saved {profile_summary(args.name, profiles[args.name])}")


def cmd_profile(args: argparse.Namespace) -> None:
    state = normalize_state(ensure_state())
    if args.project:
        config, config_path = load_project_config()
        root = config_path.parent if config_path else Path.cwd().resolve()
        if not config:
            config = {"active": state.get("active", "codex"), "profiles": {}, "aliases": {}}
        profiles = config.setdefault("profiles", {})
        aliases = config.setdefault("aliases", {})
        save = lambda: save_project_config(config, root)
    else:
        profiles = state.setdefault("profiles", {})
        aliases = state.setdefault("aliases", {})
        save = lambda: save_state(state)

    profile = profiles.get(args.name)
    created = profile is None
    if created:
        profile = {
            "provider": args.provider or args.name,
            "command": args.command or args.name,
            "model": args.model or "default",
            "env": {},
            "memory_path": args.memory or str(CONTEXT_MEMORY_PATH),
            "pages": {},
        }
        profiles[args.name] = profile

    if args.api:
        apply_api_preset_to_profile(profile, args.api, args.model, args.base_url, args.api_key_env)

    update_profile_from_args(profile, argparse.Namespace(
        provider=args.provider,
        command=args.command,
        model=args.model,
        memory=args.memory,
        env=args.env,
        unset_env=[],
        page=args.page,
        unset_page=[],
        allow_secret_env=args.allow_secret_env,
    ))

    if args.alias:
        if args.alias in profiles:
            raise SystemExit(f"Alias {args.alias!r} conflicts with an existing profile.")
        aliases[args.alias] = args.name
    if args.use:
        if args.project:
            config["active"] = args.name
            ensure_memory_files(root)
        else:
            state["active"] = args.name
    if args.project:
        ensure_memory_files(root)
    save()
    action = "Created" if created else "Updated"
    suffix = " and activated" if args.use else ""
    print(f"{action} {profile_summary(args.name, profile)}{suffix}")
    if args.alias:
        print(f"Alias saved: {args.alias} -> {args.name}")


def cmd_set(args: argparse.Namespace) -> None:
    state = normalize_state(ensure_state())
    if args.project:
        project_config, config_path = load_project_config()
        if not config_path:
            raise SystemExit(f"No {PROJECT_CONFIG_NAME} found. Run project-init first.")
        profiles = project_config.setdefault("profiles", {})
        save = lambda: save_project_config(project_config, config_path.parent)
    else:
        profiles = state["profiles"]
        save = lambda: save_state(state)
    if args.name not in profiles:
        raise SystemExit(f"Unknown profile {args.name!r}. Use add first.")
    profile = profiles[args.name]
    if args.api:
        apply_api_preset_to_profile(profile, args.api, args.model, args.base_url, args.api_key_env)
    update_profile_from_args(profile, args)
    save()
    print(f"Updated {profile_summary(args.name, profile)}")


def cmd_remove(args: argparse.Namespace) -> None:
    state = normalize_state(ensure_state())
    if args.project:
        project_config, config_path = load_project_config()
        if not config_path:
            raise SystemExit(f"No {PROJECT_CONFIG_NAME} found. Run project-init first.")
        profiles = project_config.setdefault("profiles", {})
        active = resolve_profile_name({"aliases": project_config.get("aliases", {})}, str(project_config.get("active", "")))
        save = lambda: save_project_config(project_config, config_path.parent)
    else:
        profiles = state["profiles"]
        active = resolve_profile_name(state, str(state.get("active", "")))
        save = lambda: save_state(state)
    if args.name not in profiles:
        raise SystemExit(f"Unknown profile {args.name!r}")
    if active == args.name:
        raise SystemExit("Cannot remove the active profile. Switch to another profile first.")
    del profiles[args.name]
    save()
    print(f"Removed profile {args.name}")


def cmd_select(args: argparse.Namespace) -> None:
    state, config_path = effective_state()
    profiles = list(state.get("profiles", {}).items())
    if not profiles:
        raise SystemExit("No profiles configured.")
    active = resolve_profile_name(state, str(state.get("active")))
    for index, (name, profile) in enumerate(profiles, start=1):
        marker = "*" if name == active else " "
        print(f"{index}. {marker} {profile_summary(name, profile)}")
    choice = input("Select profile number: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(profiles)):
        raise SystemExit("Invalid selection.")
    selected = profiles[int(choice) - 1][0]
    if args.project:
        root = config_path.parent if config_path else Path.cwd().resolve()
        config, _ = load_project_config(root)
        config["active"] = selected
        save_project_config(config, root)
        ensure_memory_files(root)
        print(f"Project CLI AI profile: {selected} ({root / PROJECT_CONFIG_NAME})")
        if args.open_page:
            open_profile_page(state, selected, args.open_page)
        return
    global_state = normalize_state(ensure_state())
    if selected not in global_state.get("profiles", {}):
        raise SystemExit(f"Profile {selected!r} only exists in project config. Use select --project.")
    global_state["active"] = selected
    save_state(global_state)
    print(f"Active CLI AI profile: {selected}")
    if args.open_page:
        open_profile_page(global_state, selected, args.open_page)


def launch_path_or_url(target: str | Path) -> None:
    value = str(target)
    if os.name == "nt":
        os.startfile(value)  # type: ignore[attr-defined]
        return
    opener = shutil.which("xdg-open") or shutil.which("open")
    if not opener:
        raise SystemExit("No opener found. Print the path/URL and open it manually.")
    subprocess.Popen([opener, value])


def open_profile_page(state: dict[str, Any], profile_name: str, page_name: str | bool = "home", print_only: bool = False) -> None:
    profile_name = resolve_profile_name(state, profile_name)
    profile = state.get("profiles", {}).get(profile_name)
    if not profile:
        raise SystemExit(f"Unknown profile {profile_name!r}")
    pages = profile.get("pages", {})
    label = "home" if page_name is True else str(page_name or "home")
    if label not in pages:
        available = ", ".join(sorted(pages)) or "none"
        raise SystemExit(f"Profile {profile_name!r} has no page {label!r}. Available: {available}")
    url = str(pages[label])
    if print_only:
        print(url)
        return
    launch_path_or_url(url)
    print(f"Opened {profile_name}:{label} -> {url}")


def cmd_page(args: argparse.Namespace) -> None:
    state, _ = effective_state()
    if args.action == "list":
        for profile_name, profile in state.get("profiles", {}).items():
            pages = profile.get("pages", {})
            if not pages:
                continue
            for label, url in pages.items():
                print(f"{profile_name}:{label} -> {url}")
        return
    if args.action == "open":
        profile_name = args.profile or str(state.get("active"))
        open_profile_page(state, profile_name, args.label, args.print)
        return
    if args.action in {"set", "remove"}:
        target_state = normalize_state(ensure_state())
        profile_name = args.profile
        if not profile_name:
            raise SystemExit(f"page {args.action} requires PROFILE.")
        profile_name = resolve_profile_name(target_state, profile_name)
        profile = target_state.get("profiles", {}).get(profile_name)
        if not profile:
            raise SystemExit(f"Unknown global profile {profile_name!r}")
        if args.action == "set":
            if not args.url:
                raise SystemExit("page set requires URL.")
            label, url = parse_page_pair(f"{args.label}={args.url}")
            profile.setdefault("pages", {})[label] = url
            save_state(target_state)
            print(f"Saved page {profile_name}:{label} -> {url}")
            return
        label = args.label or "home"
        profile.setdefault("pages", {}).pop(label, None)
        save_state(target_state)
        print(f"Removed page {profile_name}:{label}")


def cmd_alias(args: argparse.Namespace) -> None:
    state = normalize_state(ensure_state())
    aliases = state.setdefault("aliases", {})
    if args.action == "list":
        if not aliases:
            print("No aliases configured.")
            return
        for alias, target in aliases.items():
            print(f"{alias} -> {target}")
        return
    if args.action == "set":
        if not args.name or not args.target:
            raise SystemExit("alias set requires NAME and TARGET.")
        target = resolve_profile_name(state, args.target)
        if target not in state.get("profiles", {}):
            available = ", ".join(sorted(state.get("profiles", {})))
            raise SystemExit(f"Unknown target profile {args.target!r}. Available: {available}")
        if args.name in state.get("profiles", {}):
            raise SystemExit(f"Alias {args.name!r} conflicts with an existing profile.")
        if args.name == target:
            raise SystemExit("Alias cannot point to itself.")
        aliases[args.name] = target
        save_state(state)
        print(f"Alias saved: {args.name} -> {target}")
        return
    if args.action == "remove":
        if not args.name:
            raise SystemExit("alias remove requires NAME.")
        aliases.pop(args.name, None)
        save_state(state)
        print(f"Alias removed: {args.name}")


def cmd_paths(args: argparse.Namespace) -> None:
    project_root = find_project_root()
    ensure_memory_files(project_root)
    paths = {
        "home": str(APP_DIR),
        "state": str(STATE_PATH),
        "global_memory": str(GLOBAL_MEMORY_PATH),
        "session_memory": str(SESSION_MEMORY_PATH),
        "context_memory": str(CONTEXT_MEMORY_PATH),
        "project_config": str(project_root / PROJECT_CONFIG_NAME) if project_root else None,
        "project_memory": str(project_root / PROJECT_MEMORY_NAME) if project_root else None,
    }
    if args.json:
        print(json.dumps(paths, indent=2, ensure_ascii=False))
        return
    for key, value in paths.items():
        if value:
            print(f"{key}: {value}")


def cmd_export(args: argparse.Namespace) -> None:
    state = normalize_state(ensure_state())
    export_state = make_portable_state(state) if args.portable else state
    if args.portable:
        validate_state_secrets(export_state, args.allow_secret_env)
    payload = {
        "version": 2 if args.portable else 1,
        "portable": bool(args.portable),
        "exported_at": datetime.now().isoformat(timespec="seconds"),
        "state": export_state,
    }
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        path = Path(args.output).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"Exported config to {path}")
        return
    print(text, end="")


def cmd_import(args: argparse.Namespace) -> None:
    path = Path(args.input).expanduser()
    payload = read_json(path)
    raw_state = payload.get("state", payload)
    if not isinstance(raw_state, dict):
        raise SystemExit(f"Expected imported state to be a JSON object in {path}")
    if payload.get("portable"):
        raw_state = expand_portable_state(raw_state)
    imported = normalize_state(raw_state)
    validate_state_secrets(imported, args.allow_secret_env)
    if args.replace:
        save_state(imported)
        print(f"Replaced config from {path}")
        return
    state = normalize_state(ensure_state())
    profile_map, profile_notes = merge_named_mapping(state.setdefault("profiles", {}), imported.get("profiles", {}), args.merge_policy)
    remapped_aliases: dict[str, Any] = {}
    for alias, target in imported.get("aliases", {}).items():
        remapped_aliases[alias] = profile_map.get(str(target), target)
    _, alias_notes = merge_named_mapping(state.setdefault("aliases", {}), remapped_aliases, args.merge_policy)
    _, model_alias_notes = merge_named_mapping(state.setdefault("model_aliases", {}), imported.get("model_aliases", {}), args.merge_policy)
    if args.active:
        imported_active = str(imported.get("active", state.get("active")))
        state["active"] = profile_map.get(imported_active, imported_active)
    state, _, _ = repair_state_object(normalize_state(state))
    save_state(state)
    print(f"Merged config from {path} using {args.merge_policy} policy")
    for note in [*profile_notes, *alias_notes, *model_alias_notes]:
        print(f"- {note}")


def cmd_secret(args: argparse.Namespace) -> None:
    if args.action != "audit":
        raise SystemExit(f"Unknown secret action {args.action!r}")
    findings: list[dict[str, str]] = []
    if args.scope in {"all", "state"}:
        raw = safe_read_json_for_repair(STATE_PATH, "state file", False, [])
        if raw:
            audit_state_object(findings, "state", STATE_PATH, normalize_state(raw))
        elif STATE_PATH.exists():
            audit_text_file(findings, "state", STATE_PATH)
    if args.scope in {"all", "project"}:
        config_path = find_project_config()
        if config_path:
            raw_project = safe_read_json_for_repair(config_path, "project config", False, [])
            if raw_project:
                audit_state_object(findings, "project", config_path, raw_project)
            else:
                audit_text_file(findings, "project", config_path)
    if args.scope in {"all", "memory"}:
        ensure_memory_files(find_project_root())
        for scope, path in memory_paths_for_scope("all"):
            audit_text_file(findings, f"memory:{scope}", path)
        archive_dir = MEMORY_DIR / "archive"
        if archive_dir.exists():
            for path in archive_dir.glob("*.md"):
                audit_text_file(findings, "memory:archive", path)
    if args.json:
        print(json.dumps({"findings": findings, "count": len(findings)}, indent=2, ensure_ascii=False))
    else:
        if not findings:
            print("No obvious secrets found.")
        else:
            for item in findings:
                print(f"[warn] {item['scope']} {item['path']} {item['location']}: {item['secret_type']}")
            print("Review these locations and replace direct secrets with ${ENV_VAR} references or remove them.")
    if findings and args.fail:
        raise SystemExit(1)


def resolve_named_profile(name: str | None = None) -> tuple[dict[str, Any], str, dict[str, Any], Path | None]:
    state, config_path = effective_state()
    target = name or str(state.get("active"))
    resolved = resolve_profile_name(state, target)
    profile = state.get("profiles", {}).get(resolved)
    if not profile:
        available = ", ".join(sorted(state.get("profiles", {})))
        raise SystemExit(f"Unknown profile {target!r}. Available: {available}")
    return state, resolved, profile, config_path


def resolve_profile_env_value(profile: dict[str, Any], key: str) -> tuple[str | None, str | None]:
    value = profile.get("env", {}).get(key)
    ref = env_reference_name(value)
    if ref:
        return os.environ.get(ref), ref
    if value is None:
        return None, None
    return str(value), None


def first_profile_env(
    profile: dict[str, Any],
    predicate: Any,
    preferred: list[str] | None = None,
) -> tuple[str | None, str | None, str | None]:
    env = profile.get("env", {})
    keys = list(preferred or []) + [str(key) for key in env if str(key) not in set(preferred or [])]
    for key in keys:
        if key in env and predicate(key):
            value, ref = resolve_profile_env_value(profile, key)
            return key, value, ref
    return None, None, None


def profile_base_url(profile: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    preferred = [
        "OPENAI_BASE_URL",
        "OPENAI_API_BASE_URL",
        "OPENAI_API_BASE",
        "ANTHROPIC_BASE_URL",
        "ANTHROPIC_API_URL",
        "AZURE_OPENAI_ENDPOINT",
    ]
    return first_profile_env(profile, looks_like_base_url_key, preferred)


def profile_api_key(profile: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    preferred = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "AZURE_OPENAI_API_KEY"]
    return first_profile_env(profile, looks_like_api_key_key, preferred)


def is_local_url(url: str | None) -> bool:
    if not url:
        return False
    parsed = urllib.parse.urlparse(url)
    return parsed.hostname in {"localhost", "127.0.0.1", "::1"}


def http_get_text(url: str, headers: dict[str, str], timeout: float) -> tuple[int | None, str, str | None]:
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace"), None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, body, None
    except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
        return None, "", str(exc)


def add_check(checks: list[dict[str, Any]], status: str, name: str, detail: str) -> None:
    checks.append({"status": status, "name": name, "detail": detail})


def cmd_api_test(args: argparse.Namespace) -> None:
    _, profile_name, profile, config_path = resolve_named_profile(args.profile)
    checks: list[dict[str, Any]] = []
    command = str(profile.get("command", ""))
    command_path = shutil.which(command)
    add_check(checks, "ok" if command_path else "warn", "cli command", command_path or f"{command!r} not found on PATH")

    api_provider = str(profile.get("api_provider") or "")
    api_kind = str(profile.get("api_kind") or "")
    if api_provider:
        add_check(checks, "ok", "api preset", f"{api_provider} ({api_kind})")
    else:
        add_check(checks, "warn", "api preset", "profile has no api_provider; only CLI/memory checks are available")

    base_key, base_url, base_ref = profile_base_url(profile)
    parsed = urllib.parse.urlparse(base_url or "")
    if base_url and parsed.scheme in {"http", "https"} and parsed.netloc:
        source = f" from ${base_ref}" if base_ref else f" from {base_key}"
        add_check(checks, "ok", "base URL", f"{base_url}{source}")
    elif base_key:
        add_check(checks, "fail", "base URL", f"{base_key} is unset or invalid")
    elif api_provider and api_kind != "azure-openai":
        add_check(checks, "fail", "base URL", "no API base URL variable found in profile")

    key_name, api_key, key_ref = profile_api_key(profile)
    dummy_key = api_key in {"ollama", "lm-studio"}
    if key_name and (api_key or dummy_key):
        source = f"${key_ref}" if key_ref else key_name
        add_check(checks, "ok", "API key", f"{source} is available")
    elif key_name and key_ref:
        add_check(checks, "fail", "API key", f"${key_ref} is missing in the current shell")
    elif api_provider and api_kind not in {"openai-compatible-local"}:
        add_check(checks, "fail", "API key", "no usable API key variable found")

    if api_kind == "azure-openai":
        version = profile.get("env", {}).get("OPENAI_API_VERSION") or profile.get("env", {}).get("AZURE_OPENAI_API_VERSION")
        version_ref = env_reference_name(version)
        version_value = os.environ.get(version_ref) if version_ref else version
        add_check(checks, "ok" if version_value else "warn", "Azure API version", "set" if version_value else "OPENAI_API_VERSION is not set")

    should_probe = not args.skip_network and bool(base_url) and parsed.scheme in {"http", "https"} and parsed.netloc
    if should_probe and (api_kind.startswith("openai-compatible") or api_provider in {"openai", "openrouter", "deepseek", "ollama", "lmstudio"}):
        headers = {"Accept": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        models_url = base_url.rstrip("/") + "/models"
        status, body, error = http_get_text(models_url, headers, args.timeout)
        if status == 200:
            add_check(checks, "ok", "models endpoint", f"GET {models_url} returned 200")
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                payload = {}
            model_ids = {str(item.get("id")) for item in payload.get("data", []) if isinstance(item, dict)}
            model = str(profile.get("model", ""))
            if model and model not in {"default", "deployment-name", "endpoint-id", "local-model"} and model_ids:
                add_check(checks, "ok" if model in model_ids else "warn", "model id", f"{model} {'found' if model in model_ids else 'not listed by /models'}")
        elif status in {401, 403}:
            add_check(checks, "fail", "authentication", f"GET {models_url} returned {status}; check API key and account access")
        elif status is not None:
            severity = "fail" if is_local_url(base_url) else "warn"
            add_check(checks, severity, "models endpoint", f"GET {models_url} returned {status}")
        else:
            severity = "fail" if is_local_url(base_url) else "warn"
            add_check(checks, severity, "network", f"could not reach {models_url}: {error}")
    elif args.skip_network:
        add_check(checks, "skip", "network", "network probe skipped by --skip-network")

    payload = {
        "profile": profile_name,
        "project_config": str(config_path) if config_path else None,
        "api_provider": api_provider or None,
        "api_kind": api_kind or None,
        "checks": checks,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"API test: {profile_name}")
        for check in checks:
            print(f"[{check['status']}] {check['name']}: {check['detail']}")
    if any(check["status"] == "fail" for check in checks):
        raise SystemExit(1)


def cmd_api(args: argparse.Namespace) -> None:
    if args.action == "list":
        if args.json:
            print(json.dumps(API_PRESETS, indent=2, ensure_ascii=False))
            return
        for name in sorted(API_PRESETS):
            preset = API_PRESETS[name]
            print(f"{name}: {preset.get('label')} [{preset.get('kind')}] default={preset.get('model')}")
        if API_PRESET_ALIASES:
            aliases = ", ".join(f"{alias}->{target}" for alias, target in sorted(API_PRESET_ALIASES.items()))
            print(f"Aliases: {aliases}")
        return

    if args.action == "show":
        name, preset = clone_api_preset(args.name)
        payload = {"name": name, **preset}
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return
        print(f"{name}: {preset.get('label')}")
        print(f"kind: {preset.get('kind')}")
        print(f"default_model: {preset.get('model')}")
        env = preset.get("env", {})
        if env:
            print("env:")
            for key, value in env.items():
                print(f"  {key}={value}")
        pages = preset.get("pages", {})
        if pages:
            print("pages:")
            for key, value in pages.items():
                print(f"  {key}: {value}")
        notes = preset.get("notes", [])
        for note in notes:
            print(f"note: {note}")
        return

    if args.action == "test":
        cmd_api_test(args)
        return

    if args.action != "apply":
        raise SystemExit(f"Unknown api action {args.action!r}")

    state = normalize_state(ensure_state())
    if args.project:
        config, config_path = load_project_config()
        root = config_path.parent if config_path else Path.cwd().resolve()
        if not config:
            config = {"active": state.get("active", "codex"), "profiles": {}, "aliases": {}}
        profiles = config.setdefault("profiles", {})
        aliases = config.setdefault("aliases", {})
        save = lambda: save_project_config(config, root)
    else:
        profiles = state.setdefault("profiles", {})
        aliases = state.setdefault("aliases", {})
        save = lambda: save_state(state)

    profile = profiles.get(args.profile)
    created = profile is None
    if created:
        profile = {
            "provider": args.provider or args.profile,
            "command": args.command or args.profile,
            "model": "default",
            "env": {},
            "memory_path": args.memory or str(CONTEXT_MEMORY_PATH),
            "pages": {},
        }
        profiles[args.profile] = profile

    if args.provider:
        profile["provider"] = args.provider
    if args.command:
        profile["command"] = args.command
    if args.memory:
        profile["memory_path"] = args.memory

    preset_name = apply_api_preset_to_profile(profile, args.preset, args.model, args.base_url, args.api_key_env)
    for item in args.env:
        key, value = parse_env_pair(item)
        validate_env_secrets({key: value}, args.allow_secret_env)
        profile.setdefault("env", {})[key] = value
    for item in args.page:
        key, value = parse_page_pair(item)
        profile.setdefault("pages", {})[key] = value
    if args.alias:
        if args.alias in profiles:
            raise SystemExit(f"Alias {args.alias!r} conflicts with an existing profile.")
        aliases[args.alias] = args.profile
    if args.use:
        if args.project:
            config["active"] = args.profile
            ensure_memory_files(root)
        else:
            state["active"] = args.profile
    if args.project:
        ensure_memory_files(root)
    save()
    action = "Created" if created else "Updated"
    suffix = " and activated" if args.use else ""
    print(f"{action} {profile_summary(args.profile, profile)} with API preset {preset_name}{suffix}")
    if args.alias:
        print(f"Alias saved: {args.alias} -> {args.profile}")


def adapter_payload(adapter: str, profile_name: str, profile: dict[str, Any], shell: str) -> dict[str, Any]:
    env_script = emit_env(profile, shell)
    base_key, base_url, _ = profile_base_url(profile)
    key_name, _, key_ref = profile_api_key(profile)
    api_key_hint = f"${key_ref}" if key_ref else (key_name or "configured outside this profile")
    common = {
        "adapter": adapter,
        "profile": profile_name,
        "command": profile.get("command"),
        "model": profile.get("model"),
        "api_provider": profile.get("api_provider"),
        "api_kind": profile.get("api_kind"),
        "memory": profile.get("memory_path", str(CONTEXT_MEMORY_PATH)),
        "env": env_script,
    }
    snippets: list[str] = []
    if adapter == "codex":
        snippets.append(
            "\n".join(
                [
                    "# Codex-compatible environment",
                    env_script,
                    f"# API base: {base_url or 'default OpenAI endpoint'}",
                    f"# API key: {api_key_hint}",
                    "# Run: codex",
                ]
            )
        )
    elif adapter == "claude":
        snippets.append(
            "\n".join(
                [
                    "# Claude Code-compatible environment",
                    env_script,
                    "# Claude Code uses ANTHROPIC_API_KEY and can use ANTHROPIC_BASE_URL for compatible gateways.",
                    "# Run: claude",
                ]
            )
        )
    elif adapter == "gemini":
        snippets.append(
            "\n".join(
                [
                    "# Gemini CLI-compatible environment",
                    env_script,
                    "# Gemini tools usually read GEMINI_API_KEY or GOOGLE_API_KEY.",
                    "# Run: gemini",
                ]
            )
        )
    elif adapter == "opencode":
        snippets.append(
            json.dumps(
                {
                    "provider": profile.get("api_provider") or profile.get("provider"),
                    "model": profile.get("model"),
                    "baseURL": f"${base_key}" if base_key else base_url,
                    "apiKey": api_key_hint,
                    "memory": "$AI_CLI_MEMORY",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        snippets.append("# Apply env with ai-use, then run: opencode")
    else:
        raise SystemExit(f"Unknown adapter {adapter!r}. Use adapter list.")
    common["snippets"] = snippets
    return common


def cmd_adapter(args: argparse.Namespace) -> None:
    adapters = ["codex", "claude", "gemini", "opencode"]
    if args.adapter == "list":
        for name in adapters:
            print(name)
        return
    if args.adapter not in adapters:
        raise SystemExit(f"Unknown adapter {args.adapter!r}. Available: {', '.join(adapters)}")
    _, profile_name, profile, _ = resolve_named_profile(args.profile)
    payload = adapter_payload(args.adapter, profile_name, profile, args.shell)
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    print(f"{args.adapter} adapter for profile {profile_name}")
    for snippet in payload["snippets"]:
        print(snippet.rstrip())
        print()


def model_registry_payload(state: dict[str, Any], provider: str | None = None) -> dict[str, Any]:
    normalized_provider = normalize_provider_name(provider)
    providers = {}
    for provider_name, models in MODEL_REGISTRY.items():
        if normalized_provider and provider_name != normalized_provider:
            continue
        providers[provider_name] = models
    return {"providers": providers, "aliases": state.get("model_aliases", {})}


def cmd_model(args: argparse.Namespace) -> None:
    state = normalize_state(ensure_state())
    if args.action == "list":
        payload = model_registry_payload(state, args.provider)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return
        for provider_name, models in payload["providers"].items():
            print(f"{provider_name}:")
            for model_id, capabilities in models.items():
                context = capabilities.get("context", "unknown")
                traits = ", ".join(key for key in ["coding", "vision", "tools", "reasoning"] if capabilities.get(key) is True)
                print(f"  {model_id} context={context} {traits}".rstrip())
        aliases = payload.get("aliases", {})
        if aliases and not args.provider:
            print("Aliases:")
            for alias, item in aliases.items():
                print(f"  {alias} -> {item.get('provider')}:{item.get('model')}")
        return

    if args.action == "show":
        provider, model, capabilities, alias = resolve_model_reference(state, args.name, args.provider)
        payload = {"alias": alias, "provider": provider, "model": model, "capabilities": capabilities}
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return
        label = f"{alias} -> " if alias else ""
        print(f"{label}{provider or 'custom'}:{model}")
        for key, value in capabilities.items():
            print(f"{key}: {value}")
        return

    if args.action == "pin":
        provider, model, capabilities, alias = resolve_model_reference(state, args.model, args.provider)
        target_state = state
        if args.project:
            project_config, config_path = load_project_config()
            if not config_path:
                raise SystemExit(f"No {PROJECT_CONFIG_NAME} found. Run project-init first.")
            profiles = project_config.setdefault("profiles", {})
            save = lambda: save_project_config(project_config, config_path.parent)
        else:
            profiles = target_state.setdefault("profiles", {})
            save = lambda: save_state(target_state)
        profile_name = resolve_profile_name(target_state, args.profile)
        if profile_name not in profiles:
            raise SystemExit(f"Unknown profile {args.profile!r}. Use profile or api apply first.")
        profile = profiles[profile_name]
        if provider and provider in API_PRESETS:
            apply_api_preset_to_profile(profile, provider, model)
        else:
            profile["model"] = model
        if capabilities:
            profile["model_capabilities"] = capabilities
        if alias:
            profile["model_alias"] = alias
        save()
        provider_text = f" via {provider}" if provider else ""
        print(f"Pinned {profile_name} to {model}{provider_text}")
        return

    if args.action == "alias":
        aliases = state.setdefault("model_aliases", {})
        if args.alias_action == "list":
            for alias, item in aliases.items():
                print(f"{alias} -> {item.get('provider')}:{item.get('model')}")
            return
        if args.alias_action == "set":
            if not args.name or not args.provider or not args.model:
                raise SystemExit("model alias set requires NAME PROVIDER MODEL.")
            provider = normalize_provider_name(args.provider)
            capabilities = dict(MODEL_REGISTRY.get(provider or "", {}).get(args.model, {}))
            for item in args.cap:
                key, value = parse_capability_pair(item)
                capabilities[key] = value
            aliases[args.name] = {"provider": provider, "model": args.model, "capabilities": capabilities}
            save_state(state)
            print(f"Model alias saved: {args.name} -> {provider}:{args.model}")
            return
        if args.alias_action == "remove":
            if not args.name:
                raise SystemExit("model alias remove requires NAME.")
            aliases.pop(args.name, None)
            save_state(state)
            print(f"Model alias removed: {args.name}")
            return
    raise SystemExit(f"Unknown model action {args.action!r}")


def cmd_strategy(args: argparse.Namespace) -> None:
    state = normalize_state(ensure_state())
    if args.action == "list":
        if args.json:
            print(json.dumps(STRATEGY_PRESETS, indent=2, ensure_ascii=False))
            return
        for name, strategy in STRATEGY_PRESETS.items():
            print(f"{name}: {strategy['description']} -> {strategy['profile']} ({strategy['model']})")
        return
    if args.action == "install":
        installed = install_strategy_aliases(state)
        save_state(state)
        for item in installed:
            print(f"Strategy alias: {item}")
        return
    if args.action == "use":
        if not args.name:
            raise SystemExit("strategy use requires NAME.")
        profile_name = ensure_strategy_profile(state, args.name)
        if not profile_name:
            available = ", ".join(sorted(STRATEGY_PRESETS))
            raise SystemExit(f"Unknown strategy {args.name!r}. Available: {available}")
        state["active"] = profile_name
        save_state(state)
        profile = state["profiles"][profile_name]
        print(f"Active strategy: {args.name} -> {profile_name} ({profile.get('model')})")
        return
    raise SystemExit(f"Unknown strategy action {args.action!r}")


def cmd_open(args: argparse.Namespace) -> None:
    ensure_memory_files(find_project_root())
    targets = {
        "home": APP_DIR,
        "state": STATE_PATH,
        "global": GLOBAL_MEMORY_PATH,
        "session": SESSION_MEMORY_PATH,
        "context": CONTEXT_MEMORY_PATH,
        "project": memory_target("project") if find_project_root() else None,
    }
    target = targets.get(args.target)
    if not target:
        raise SystemExit(f"No target available for {args.target!r}.")
    path = Path(target)
    if args.print:
        print(path)
        return
    launch_path_or_url(path)
    print(f"Opened {path}")


def cmd_run(args: argparse.Namespace) -> None:
    state, _ = effective_state()
    profile = active_profile(state)
    command = [str(profile.get("command"))] + args.args
    env = profile_process_env(profile, project_root_for_env())
    raise SystemExit(subprocess.call(command, env=env))


def session_safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip().lower()).strip("-")
    return cleaned or "agent"


def session_backend_id(name: str) -> str:
    return "ai-" + session_safe_name(name)


def default_session_backend() -> str:
    if shutil.which("tmux"):
        return "tmux"
    if os.name == "nt" and shutil.which("wt"):
        return "wt"
    if os.name == "nt":
        return "powershell"
    return "print"


def resolve_session_backend(requested: str) -> str:
    return default_session_backend() if requested == "auto" else requested


def tmux_has_session(session_id: str) -> bool:
    if not shutil.which("tmux"):
        return False
    result = subprocess.run(["tmux", "has-session", "-t", session_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0


def tmux_attach_or_switch(session_id: str) -> None:
    if os.environ.get("TMUX"):
        subprocess.run(["tmux", "switch-client", "-t", session_id], check=True)
        return
    subprocess.run(["tmux", "attach-session", "-t", session_id], check=True)


def start_tmux_session(session_id: str, script: str, attach: bool, reuse: bool) -> str:
    if not shutil.which("tmux"):
        raise SystemExit("tmux is not installed or not on PATH.")
    if tmux_has_session(session_id):
        if not reuse:
            raise SystemExit(f"tmux session {session_id!r} already exists. Use --reuse or stop it first.")
    else:
        subprocess.run(["tmux", "new-session", "-d", "-s", session_id, script], check=True)
    if attach:
        tmux_attach_or_switch(session_id)
    return f"tmux:{session_id}"


def start_windows_terminal_session(title: str, script: str) -> str:
    wt = shutil.which("wt")
    if not wt:
        raise SystemExit("Windows Terminal wt.exe is not installed or not on PATH.")
    subprocess.Popen([wt, "new-tab", "--title", title, "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", script])
    return f"wt:{title}"


def start_powershell_session(title: str, script: str) -> str:
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        raise SystemExit("No PowerShell executable found.")
    creationflags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
    subprocess.Popen([powershell, "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", script], creationflags=creationflags)
    return f"powershell:{title}"


def session_status(record: dict[str, Any]) -> str:
    backend = str(record.get("backend", ""))
    if backend == "tmux":
        return "running" if tmux_has_session(str(record.get("backend_id", ""))) else "missing"
    if backend in {"wt", "powershell"}:
        return "external"
    return "command"


def session_target_candidates(state: dict[str, Any], target: str) -> set[str]:
    candidates = {target}
    try:
        candidates.add(resolve_profile_name(state, target))
    except SystemExit:
        pass
    if target in RECIPE_CATALOG or target in RECIPE_ALIASES:
        candidates.add(recipe_profile_name(target))
    if target in STRATEGY_PRESETS:
        candidates.add(str(STRATEGY_PRESETS[target]["profile"]))
    candidates.update(session_safe_name(item) for item in list(candidates))
    candidates.update(session_backend_id(item) for item in list(candidates))
    return candidates


def session_record_for_target(state: dict[str, Any], target: str) -> tuple[str, dict[str, Any] | None]:
    sessions = state.setdefault("sessions", {})
    candidates = session_target_candidates(state, target)
    if target in sessions:
        return target, sessions[target]
    for name, record in sessions.items():
        if name in candidates or str(record.get("profile", "")) in candidates or str(record.get("backend_id", "")) in candidates:
            return name, record
    return target, None


def resolve_profile_for_session(target: str) -> tuple[dict[str, Any], str, dict[str, Any], Path | None]:
    state = normalize_state(ensure_state())
    if target in RECIPE_CATALOG or target in RECIPE_ALIASES:
        profile_name, _ = install_recipe_into_state(state, target, False)
        save_state(state)
        return resolve_named_profile(profile_name)
    try:
        return resolve_named_profile(target)
    except SystemExit:
        strategy_profile = ensure_strategy_profile(state, target)
        if strategy_profile:
            save_state(state)
            return resolve_named_profile(strategy_profile)
        raise


def cmd_session(args: argparse.Namespace) -> None:
    state = normalize_state(ensure_state())
    sessions = state.setdefault("sessions", {})

    if args.action == "list":
        payload = []
        for name, record in sorted(sessions.items()):
            item = dict(record)
            item["name"] = name
            item["status"] = session_status(record)
            payload.append(item)
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return
        if not payload:
            print("No managed AI sessions recorded.")
            return
        for item in payload:
            print(f"{item['name']}: {item.get('profile')} [{item.get('backend')}] {item.get('status')} ({item.get('backend_id')})")
        return

    if args.action == "start":
        if not args.target:
            raise SystemExit("session start requires a profile, alias, strategy, or recipe.")
        _, profile_name, profile, _ = resolve_profile_for_session(args.target)
        state = normalize_state(ensure_state())
        sessions = state.setdefault("sessions", {})
        backend = resolve_session_backend(args.backend)
        session_name = session_safe_name(args.session_name or profile_name)
        backend_id = session_backend_id(session_name)
        cwd = Path(args.cwd).expanduser().resolve() if args.cwd else Path.cwd().resolve()
        extra_args = list(args.arg or [])
        title = f"ai:{session_name}"
        shell = "powershell" if backend in {"wt", "powershell"} or os.name == "nt" else "bash"
        script = profile_launch_script(profile, shell, extra_args, cwd)

        if backend == "tmux":
            detail = start_tmux_session(backend_id, script, args.attach, args.reuse)
        elif backend == "wt":
            detail = start_windows_terminal_session(title, script)
        elif backend == "powershell":
            detail = start_powershell_session(title, script)
        elif backend == "print":
            print(profile_launch_command(profile, shell, extra_args, cwd))
            detail = "printed launch command"
        else:
            raise SystemExit(f"Unknown session backend {backend!r}")

        sessions[session_name] = {
            "profile": profile_name,
            "backend": backend,
            "backend_id": backend_id,
            "title": title,
            "cwd": str(cwd),
            "command": profile.get("command"),
            "model": profile.get("model"),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        save_state(state)
        print(f"Session {session_name}: {detail}")
        return

    if args.action in {"switch", "attach"}:
        if not args.target:
            raise SystemExit(f"session {args.action} requires a session name or profile.")
        name, record = session_record_for_target(state, args.target)
        if not record:
            raise SystemExit(f"Unknown session {args.target!r}. Use ai-session list or ai-session start.")
        if record.get("backend") != "tmux":
            print(f"Session {name} uses {record.get('backend')}; direct terminal switching is only available for tmux.")
            print(f"Start another window/tab with: ai-session start {record.get('profile')} --backend {record.get('backend')} --reuse")
            return
        backend_id = str(record.get("backend_id", ""))
        if not tmux_has_session(backend_id):
            raise SystemExit(f"tmux session {backend_id!r} is not running.")
        tmux_attach_or_switch(backend_id)
        return

    if args.action == "stop":
        if not args.target:
            raise SystemExit("session stop requires a session name or profile.")
        name, record = session_record_for_target(state, args.target)
        if not record:
            raise SystemExit(f"Unknown session {args.target!r}.")
        if record.get("backend") == "tmux" and tmux_has_session(str(record.get("backend_id", ""))):
            subprocess.run(["tmux", "kill-session", "-t", str(record.get("backend_id"))], check=True)
            print(f"Stopped tmux session {record.get('backend_id')}")
        else:
            print(f"Forgot session record {name}. Stop external windows manually if they are still running.")
        sessions.pop(name, None)
        save_state(state)
        return

    raise SystemExit(f"Unknown session action {args.action!r}")


def cmd_handoff(args: argparse.Namespace) -> None:
    target = args.profile
    text = " ".join(args.text).strip()
    if not text:
        raise SystemExit("handoff requires a note.")
    tags = list(args.tag or []) + ["handoff", session_safe_name(target)]
    cmd_remember(argparse.Namespace(scope=args.scope, tag=tags, duplicate=args.duplicate, force=args.force, text=[text]))
    if args.no_start:
        return
    cmd_session(
        argparse.Namespace(
            action="start",
            target=target,
            backend=args.backend,
            session_name=args.session_name,
            cwd=args.cwd,
            attach=args.attach,
            reuse=True,
            arg=[],
            json=False,
        )
    )


def powershell_functions() -> str:
    script = str(SCRIPT_PATH).replace("'", "''")
    return f"""
# >>> ai-cli-switcher >>>
function Invoke-AiCliSwitcher {{
  if ($env:AI_CLI_SWITCHER_PYTHON) {{
    & $env:AI_CLI_SWITCHER_PYTHON '{script}' @args
  }} elseif (Get-Command py -ErrorAction SilentlyContinue) {{
    py -3.12 '{script}' @args
  }} elseif (Get-Command python -ErrorAction SilentlyContinue) {{
    python '{script}' @args
  }} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {{
    python3 '{script}' @args
  }} else {{
    throw 'No Python launcher found. Set AI_CLI_SWITCHER_PYTHON to a Python executable.'
  }}
}}

function ai-use {{
  param([Parameter(Mandatory=$true)][string]$Name)
  Invoke-AiCliSwitcher use $Name @args | Write-Host
  Invoke-Expression (Invoke-AiCliSwitcher current --shell powershell)
}}

function ai-current {{
  Invoke-AiCliSwitcher current
}}

function ai-status {{
  Invoke-AiCliSwitcher status
}}

function ai-paths {{
  Invoke-AiCliSwitcher paths
}}

function ai-list {{
  Invoke-AiCliSwitcher list
}}

function ai-profile {{
  Invoke-AiCliSwitcher profile @args
}}

function ai-api {{
  Invoke-AiCliSwitcher api @args
}}

function ai-model {{
  Invoke-AiCliSwitcher model @args
}}

function ai-strategy {{
  Invoke-AiCliSwitcher strategy @args
}}

function ai-recipe {{
  Invoke-AiCliSwitcher recipe @args
}}

function ai-adapter {{
  Invoke-AiCliSwitcher adapter @args
}}

function ai-session {{
  Invoke-AiCliSwitcher session @args
}}

function ai-handoff {{
  Invoke-AiCliSwitcher handoff @args
}}

function ai-select {{
  Invoke-AiCliSwitcher select @args
  Invoke-Expression (Invoke-AiCliSwitcher current --shell powershell)
}}

  function ai-doctor {{
    Invoke-AiCliSwitcher doctor @args
  }}
  
  function ai-remember {{
    Invoke-AiCliSwitcher remember @args
  }}
  
  function ai-recall {{
    Invoke-AiCliSwitcher recall @args
  }}
  
  function ai-memory {{
    Invoke-AiCliSwitcher memory @args
  }}

  function ai-secret {{
    Invoke-AiCliSwitcher secret @args
  }}
  
  function ai-open-memory {{
    Invoke-AiCliSwitcher open context @args
  }}

function ai-run {{
  Invoke-AiCliSwitcher run @args
}}
# <<< ai-cli-switcher <<<
""".strip()


def cmd_batch_files() -> dict[str, str]:
    script = str(SCRIPT_PATH)
    bootstrap = f"""set "AI_SWITCHER_SCRIPT={script}"
if defined AI_CLI_SWITCHER_PYTHON (
  set "AI_SWITCHER_PY=%AI_CLI_SWITCHER_PYTHON%"
) else (
  set "AI_SWITCHER_PY="
  where py >nul 2>nul && set "AI_SWITCHER_PY=py -3.12"
  if not defined AI_SWITCHER_PY where python >nul 2>nul && set "AI_SWITCHER_PY=python"
  if not defined AI_SWITCHER_PY where python3 >nul 2>nul && set "AI_SWITCHER_PY=python3"
)
if not defined AI_SWITCHER_PY (
  echo No Python launcher found. Set AI_CLI_SWITCHER_PYTHON to a Python executable.
  exit /b 1
)"""
    py_cmd = '%AI_SWITCHER_PY% "%AI_SWITCHER_SCRIPT%"'
    apply_env = f'for /f "usebackq delims=" %%i in (`{py_cmd} current --shell cmd`) do call %%i'
    return {
        "ai-use.cmd": f"""@echo off
{bootstrap}
if "%~1"=="" (
  echo Usage: ai-use PROFILE [--project] [--open-page [PAGE]]
  exit /b 2
)
{py_cmd} use %*
if errorlevel 1 exit /b %errorlevel%
{apply_env}
""",
        "ai-select.cmd": f"""@echo off
{bootstrap}
{py_cmd} select %*
if errorlevel 1 exit /b %errorlevel%
{apply_env}
""",
        "ai-current.cmd": f"""@echo off
{bootstrap}
{py_cmd} current %*
""",
        "ai-status.cmd": f"""@echo off
{bootstrap}
{py_cmd} status %*
""",
        "ai-list.cmd": f"""@echo off
{bootstrap}
{py_cmd} list %*
""",
        "ai-profile.cmd": f"""@echo off
{bootstrap}
{py_cmd} profile %*
""",
        "ai-api.cmd": f"""@echo off
{bootstrap}
{py_cmd} api %*
""",
        "ai-model.cmd": f"""@echo off
{bootstrap}
{py_cmd} model %*
""",
        "ai-strategy.cmd": f"""@echo off
{bootstrap}
{py_cmd} strategy %*
""",
        "ai-recipe.cmd": f"""@echo off
{bootstrap}
{py_cmd} recipe %*
""",
        "ai-adapter.cmd": f"""@echo off
{bootstrap}
{py_cmd} adapter %*
""",
        "ai-session.cmd": f"""@echo off
{bootstrap}
{py_cmd} session %*
""",
        "ai-handoff.cmd": f"""@echo off
{bootstrap}
{py_cmd} handoff %*
""",
        "ai-paths.cmd": f"""@echo off
{bootstrap}
{py_cmd} paths %*
""",
        "ai-doctor.cmd": f"""@echo off
{bootstrap}
{py_cmd} doctor %*
""",
        "ai-secret.cmd": f"""@echo off
{bootstrap}
{py_cmd} secret %*
""",
        "ai-remember.cmd": f"""@echo off
{bootstrap}
{py_cmd} remember %*
""",
        "ai-recall.cmd": f"""@echo off
{bootstrap}
{py_cmd} recall %*
""",
        "ai-memory.cmd": f"""@echo off
{bootstrap}
{py_cmd} memory %*
""",
        "ai-page.cmd": f"""@echo off
{bootstrap}
{py_cmd} page %*
""",
        "ai-open-memory.cmd": f"""@echo off
{bootstrap}
{py_cmd} open context %*
""",
        "ai-run.cmd": f"""@echo off
{bootstrap}
{py_cmd} run %*
""",
    }


def posix_shell_functions() -> str:
    script = shell_quote(str(SCRIPT_PATH), "bash")
    return f"""# >>> ai-cli-switcher >>>
AI_CLI_SWITCHER_SCRIPT={script}

_ai_cli_switcher() {{
  if [ -n "${{AI_CLI_SWITCHER_PYTHON:-}}" ]; then
    "$AI_CLI_SWITCHER_PYTHON" "$AI_CLI_SWITCHER_SCRIPT" "$@"
  elif command -v python3 >/dev/null 2>&1; then
    python3 "$AI_CLI_SWITCHER_SCRIPT" "$@"
  elif command -v python >/dev/null 2>&1; then
    python "$AI_CLI_SWITCHER_SCRIPT" "$@"
  elif command -v py >/dev/null 2>&1; then
    py -3.12 "$AI_CLI_SWITCHER_SCRIPT" "$@"
  else
    echo "No Python launcher found. Set AI_CLI_SWITCHER_PYTHON to a Python executable." >&2
    return 1
  fi
}}

ai-use() {{
  _ai_cli_switcher use "$@" || return $?
  eval "$(_ai_cli_switcher current --shell bash)"
}}

ai-select() {{
  _ai_cli_switcher select "$@" || return $?
  eval "$(_ai_cli_switcher current --shell bash)"
}}

ai-current() {{ _ai_cli_switcher current "$@"; }}
ai-status() {{ _ai_cli_switcher status "$@"; }}
ai-paths() {{ _ai_cli_switcher paths "$@"; }}
ai-list() {{ _ai_cli_switcher list "$@"; }}
ai-profile() {{ _ai_cli_switcher profile "$@"; }}
ai-api() {{ _ai_cli_switcher api "$@"; }}
ai-model() {{ _ai_cli_switcher model "$@"; }}
ai-strategy() {{ _ai_cli_switcher strategy "$@"; }}
ai-recipe() {{ _ai_cli_switcher recipe "$@"; }}
ai-adapter() {{ _ai_cli_switcher adapter "$@"; }}
ai-session() {{ _ai_cli_switcher session "$@"; }}
ai-handoff() {{ _ai_cli_switcher handoff "$@"; }}
ai-doctor() {{ _ai_cli_switcher doctor "$@"; }}
ai-secret() {{ _ai_cli_switcher secret "$@"; }}
ai-remember() {{ _ai_cli_switcher remember "$@"; }}
ai-recall() {{ _ai_cli_switcher recall "$@"; }}
ai-memory() {{ _ai_cli_switcher memory "$@"; }}
ai-page() {{ _ai_cli_switcher page "$@"; }}
ai-open-memory() {{ _ai_cli_switcher open context "$@"; }}
ai-run() {{ _ai_cli_switcher run "$@"; }}
# <<< ai-cli-switcher <<<
"""


def fish_shell_functions() -> str:
    script = shell_quote(str(SCRIPT_PATH), "fish")
    return f"""# >>> ai-cli-switcher >>>
set -gx AI_CLI_SWITCHER_SCRIPT {script}

function _ai_cli_switcher
  if set -q AI_CLI_SWITCHER_PYTHON
    "$AI_CLI_SWITCHER_PYTHON" "$AI_CLI_SWITCHER_SCRIPT" $argv
  else if command -q python3
    python3 "$AI_CLI_SWITCHER_SCRIPT" $argv
  else if command -q python
    python "$AI_CLI_SWITCHER_SCRIPT" $argv
  else if command -q py
    py -3.12 "$AI_CLI_SWITCHER_SCRIPT" $argv
  else
    echo "No Python launcher found. Set AI_CLI_SWITCHER_PYTHON to a Python executable." >&2
    return 1
  end
end

function ai-use
  _ai_cli_switcher use $argv; or return $status
  _ai_cli_switcher current --shell fish | source
end

function ai-select
  _ai_cli_switcher select $argv; or return $status
  _ai_cli_switcher current --shell fish | source
end

function ai-current; _ai_cli_switcher current $argv; end
function ai-status; _ai_cli_switcher status $argv; end
function ai-paths; _ai_cli_switcher paths $argv; end
function ai-list; _ai_cli_switcher list $argv; end
function ai-profile; _ai_cli_switcher profile $argv; end
function ai-api; _ai_cli_switcher api $argv; end
function ai-model; _ai_cli_switcher model $argv; end
function ai-strategy; _ai_cli_switcher strategy $argv; end
function ai-recipe; _ai_cli_switcher recipe $argv; end
function ai-adapter; _ai_cli_switcher adapter $argv; end
function ai-session; _ai_cli_switcher session $argv; end
function ai-handoff; _ai_cli_switcher handoff $argv; end
function ai-doctor; _ai_cli_switcher doctor $argv; end
function ai-secret; _ai_cli_switcher secret $argv; end
function ai-remember; _ai_cli_switcher remember $argv; end
function ai-recall; _ai_cli_switcher recall $argv; end
function ai-memory; _ai_cli_switcher memory $argv; end
function ai-page; _ai_cli_switcher page $argv; end
function ai-open-memory; _ai_cli_switcher open context $argv; end
function ai-run; _ai_cli_switcher run $argv; end
# <<< ai-cli-switcher <<<
"""


def cmd_install_powershell(args: argparse.Namespace) -> None:
    profile_path = Path(args.profile or os.environ.get("PROFILE", Path.home() / "Documents/PowerShell/Microsoft.PowerShell_profile.ps1"))
    marker_start = "# >>> ai-cli-switcher >>>"
    marker_end = "# <<< ai-cli-switcher <<<"
    block = powershell_functions()
    existing = profile_path.read_text(encoding="utf-8") if profile_path.exists() else ""
    if marker_start in existing and marker_end in existing:
        before, rest = existing.split(marker_start, 1)
        _, after = rest.split(marker_end, 1)
        updated = before.rstrip() + "\n\n" + block + "\n" + after.lstrip()
    else:
        updated = existing.rstrip() + "\n\n" + block + "\n"
    if args.dry_run:
        print(updated)
        return
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.write_text(updated, encoding="utf-8")
    print(f"Installed PowerShell helpers into {profile_path}")


def cmd_install_cmd(args: argparse.Namespace) -> None:
    install_dir = Path(args.dir or Path.home() / "bin" / "ai-cli-switcher").expanduser()
    files = cmd_batch_files()
    if args.dry_run:
        for name, content in files.items():
            print(f"--- {install_dir / name} ---")
            print(content.rstrip())
        return
    install_dir.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (install_dir / name).write_text(content.replace("\n", "\r\n"), encoding="utf-8")
    path_entries = [entry.strip('"') for entry in os.environ.get("PATH", "").split(os.pathsep)]
    in_path = any(Path(entry).expanduser().resolve() == install_dir.resolve() for entry in path_entries if entry)
    print(f"Installed cmd.exe helpers into {install_dir}")
    if not in_path:
        print(f"Add this directory to PATH for native cmd.exe use: {install_dir}")


def cmd_install_shell(args: argparse.Namespace) -> None:
    output = Path(args.output or Path.home() / ".config" / "ai-cli-switcher" / "ai-cli-switcher.sh").expanduser()
    content = posix_shell_functions()
    if args.dry_run:
        print(content.rstrip())
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    output.chmod(0o755)
    print(f"Installed Bash/Zsh helpers into {output}")
    print(f"Source it from your shell profile: source {output}")


def cmd_install_fish(args: argparse.Namespace) -> None:
    output = Path(args.output or Path.home() / ".config" / "fish" / "conf.d" / "ai-cli-switcher.fish").expanduser()
    content = fish_shell_functions()
    if args.dry_run:
        print(content.rstrip())
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"Installed fish helpers into {output}")


def detect_unix_shell() -> str:
    shell = os.environ.get("SHELL", "")
    name = Path(shell).name
    if name in {"bash", "zsh", "fish"}:
        return name
    return "zsh" if sys_platform_name() == "darwin" else "bash"


def sys_platform_name() -> str:
    import platform

    return platform.system().lower()


def default_unix_profile(shell: str) -> Path:
    home = Path.home()
    if shell == "zsh":
        return home / ".zshrc"
    if shell == "bash":
        if sys_platform_name() == "darwin":
            return home / ".bash_profile"
        return home / ".bashrc"
    if shell == "fish":
        return home / ".config" / "fish" / "conf.d" / "ai-cli-switcher.fish"
    raise SystemExit(f"Unsupported shell {shell!r}. Use install-shell or install-fish directly.")


def upsert_source_line(profile_path: Path, source_path: Path, dry_run: bool) -> None:
    line = f"source {shell_quote(str(source_path), 'bash')}"
    marker_start = "# >>> ai-cli-switcher >>>"
    marker_end = "# <<< ai-cli-switcher <<<"
    block = f"{marker_start}\n{line}\n{marker_end}\n"
    existing = profile_path.read_text(encoding="utf-8") if profile_path.exists() else ""
    if marker_start in existing and marker_end in existing:
        before, rest = existing.split(marker_start, 1)
        _, after = rest.split(marker_end, 1)
        updated = before.rstrip() + "\n\n" + block + after.lstrip()
    else:
        updated = existing.rstrip() + "\n\n" + block
    if dry_run:
        print(f"--- {profile_path} ---")
        print(updated.rstrip())
        return
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.write_text(updated, encoding="utf-8")


def cmd_install_unix(args: argparse.Namespace) -> None:
    shell = args.shell if args.shell != "auto" else detect_unix_shell()
    if shell == "fish":
        output = Path(args.output or default_unix_profile("fish")).expanduser()
        content = fish_shell_functions()
        if args.dry_run:
            print(f"--- {output} ---")
            print(content.rstrip())
            return
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
        print(f"Installed fish helpers into {output}")
        return

    helper = Path(args.output or Path.home() / ".config" / "ai-cli-switcher" / "ai-cli-switcher.sh").expanduser()
    profile = Path(args.profile or default_unix_profile(shell)).expanduser()
    helper_content = posix_shell_functions()
    if args.dry_run:
        print(f"--- {helper} ---")
        print(helper_content.rstrip())
        upsert_source_line(profile, helper, True)
        return
    helper.parent.mkdir(parents=True, exist_ok=True)
    helper.write_text(helper_content, encoding="utf-8")
    helper.chmod(0o755)
    upsert_source_line(profile, helper, False)
    print(f"Installed {shell} helpers into {helper}")
    print(f"Updated shell profile: {profile}")
    print(f"Reload with: source {profile}")


def cmd_recipe(args: argparse.Namespace) -> None:
    if args.action == "list":
        if args.json:
            print(json.dumps(RECIPE_CATALOG, indent=2, ensure_ascii=False))
            return
        for name in sorted(RECIPE_CATALOG):
            recipe = RECIPE_CATALOG[name]
            print(f"{name}: {recipe.get('description')} -> {recipe.get('profile')}")
        if RECIPE_ALIASES:
            aliases = ", ".join(f"{alias}->{target}" for alias, target in sorted(RECIPE_ALIASES.items()))
            print(f"Aliases: {aliases}")
        return

    if args.action == "show":
        if not args.names:
            raise SystemExit("recipe show requires a recipe name.")
        name, recipe = clone_recipe(args.names[0])
        payload = {"name": name, **recipe}
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return
        print(f"{name}: {recipe.get('description')}")
        print(f"profile: {recipe.get('profile')}")
        print(f"spec: {json.dumps(recipe.get('spec', {}), ensure_ascii=False)}")
        aliases = recipe.get("aliases", [])
        if aliases:
            print(f"aliases: {', '.join(str(item) for item in aliases)}")
        strategies = recipe.get("strategies", [])
        if strategies:
            print(f"strategies: {', '.join(str(item) for item in strategies)}")
        return

    if args.action != "install":
        raise SystemExit(f"Unknown recipe action {args.action!r}")

    names = sorted(RECIPE_CATALOG) if args.all else recipe_names_from_values(args.names)
    if not names:
        raise SystemExit("recipe install requires at least one recipe name, or --all.")
    state = load_state_for_dry_run() if args.dry_run else normalize_state(ensure_state())
    installed_profiles: list[str] = []
    events: list[dict[str, str]] = []
    for name in names:
        profile_name, recipe_events = install_recipe_into_state(state, name, args.force)
        installed_profiles.append(profile_name)
        for event in recipe_events:
            events.append({"recipe": name, **event})

    active_target = args.active or (installed_profiles[-1] if args.use else "")
    if active_target:
        state["active"] = resolve_active_target(state, active_target)
        events.append({"recipe": "active", "status": "saved", "name": "active", "detail": str(state["active"])})

    if not args.dry_run:
        save_state(state)

    payload = {"dry_run": bool(args.dry_run), "recipes": names, "active": state.get("active"), "events": events}
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    verb = "Would install" if args.dry_run else "Installed"
    print(f"{verb} recipes: {', '.join(names)}")
    for event in events:
        print(f"[{event['status']}] {event['recipe']} {event['name']}: {event['detail']}")
    print(f"Active profile: {state.get('active')}")


def selected_setup_shell(requested: str) -> str:
    if requested == "auto":
        return "powershell" if os.name == "nt" else "unix"
    return requested


def install_shell_helpers_for_setup(args: argparse.Namespace, shell: str) -> None:
    if getattr(args, "no_install", False):
        print("Skipped shell helper installation because --no-install was passed.")
        return
    if shell == "powershell":
        cmd_install_powershell(argparse.Namespace(profile=args.profile, dry_run=args.dry_run))
    elif shell == "cmd":
        cmd_install_cmd(argparse.Namespace(dir=args.dir, dry_run=args.dry_run))
    elif shell == "unix":
        cmd_install_unix(argparse.Namespace(shell="auto", output=args.output, profile=args.profile, dry_run=args.dry_run))
    elif shell in {"bash", "zsh", "fish"}:
        cmd_install_unix(argparse.Namespace(shell=shell, output=args.output, profile=args.profile, dry_run=args.dry_run))
    else:
        raise SystemExit(f"Unsupported setup shell {shell!r}")

    with_cmd = getattr(args, "with_cmd", False) or (getattr(args, "full", False) and os.name == "nt" and shell != "cmd")
    if with_cmd and shell != "cmd":
        cmd_install_cmd(argparse.Namespace(dir=args.dir, dry_run=args.dry_run))


def preferred_active_recipe(recipes: list[str]) -> str:
    priority = [
        "opencode-openrouter",
        "opencode-openrouter-best",
        "codex-openai",
        "claude-native",
        "gemini-cli",
        "opencode-deepseek",
        "local-ollama",
        "local-lmstudio",
        "custom-gateway",
    ]
    for name in priority:
        if name in recipes:
            return recipe_profile_name(name)
    return recipe_profile_name(recipes[0]) if recipes else "codex"


def cmd_setup_wizard(args: argparse.Namespace) -> None:
    detected = detect_cli_tools()
    default_recipes = default_wizard_recipes(detected)
    recipes = recipe_names_from_values(args.recipes)
    interactive = sys.stdin.isatty() and not args.yes
    if not recipes:
        if interactive:
            print("Detected CLI tools:")
            for name, path in detected.items():
                marker = "found" if path else "missing"
                print(f"  {name}: {marker}{f' ({path})' if path else ''}")
            print("Available recipes:")
            for name in sorted(RECIPE_CATALOG):
                print(f"  {name}: {RECIPE_CATALOG[name]['description']}")
            default_text = ",".join(default_recipes)
            recipes = recipe_names_from_values([prompt_text("Recipes to install", default_text)])
        elif args.yes:
            recipes = default_recipes
        else:
            raise SystemExit("setup --wizard needs an interactive terminal, or pass --yes and optionally --recipes.")

    if not recipes:
        raise SystemExit("No recipes selected.")

    state = load_state_for_dry_run() if args.dry_run else normalize_state(ensure_state())
    events: list[dict[str, str]] = []
    for recipe_name in recipes:
        _, recipe_events = install_recipe_into_state(state, recipe_name, args.force)
        for event in recipe_events:
            events.append({"recipe": recipe_name, **event})

    if not args.no_strategy:
        for item in install_strategy_aliases(state):
            events.append({"recipe": "strategy", "status": "saved", "name": "alias", "detail": item})

    active_default = preferred_active_recipe(recipes)
    active_target = args.active or active_default
    if interactive:
        active_target = prompt_text("Active profile or recipe", active_target)
    state["active"] = resolve_active_target(state, active_target)

    if not args.dry_run:
        save_state(state)

    print(f"{'Would initialize' if args.dry_run else 'Initialized'} wizard setup under {APP_DIR}")
    print("Detected CLI tools:")
    for name, path in detected.items():
        marker = "found" if path else "missing"
        print(f"  {name}: {marker}{f' ({path})' if path else ''}")
    print(f"Recipes: {', '.join(recipes)}")
    for event in events:
        print(f"[{event['status']}] {event['recipe']} {event['name']}: {event['detail']}")
    print(f"Active profile: {state['active']}")

    install_helpers = not args.no_install
    if interactive:
        install_helpers = prompt_yes_no("Install shell helpers now", install_helpers)
    setup_args = argparse.Namespace(
        profile=args.profile,
        dir=args.dir,
        output=args.output,
        dry_run=args.dry_run,
        no_install=not install_helpers,
        with_cmd=args.with_cmd,
        full=False,
    )
    shell = selected_setup_shell(args.shell)
    install_shell_helpers_for_setup(setup_args, shell)

    if not args.dry_run and not args.skip_doctor:
        print("Doctor:")
        cmd_doctor(argparse.Namespace(fix=True, json=False))
    if not args.dry_run and not args.skip_secret_audit:
        print("Secret audit:")
        cmd_secret(argparse.Namespace(action="audit", scope="all", json=False, fail=False))

    print("Next commands:")
    print("  ai-list")
    print(f"  ai-use {state['active']}")
    print("  ai-doctor --fix")
    print("  ai-secret audit --scope all")


def cmd_setup_full(args: argparse.Namespace) -> None:
    detected = detect_cli_tools()
    state = normalize_state({"active": "codex", "profiles": clone_default_profiles()}) if args.dry_run else normalize_state(ensure_state())
    created: list[str] = []
    updated: list[str] = []
    for name, spec in FULL_SETUP_PROFILES.items():
        was_created = upsert_profile_from_spec(state, name, spec)
        (created if was_created else updated).append(name)
    strategies = install_strategy_aliases(state)
    if not args.dry_run:
        save_state(state)
        print(f"Initialized {STATE_PATH}")
    else:
        print(f"Would initialize state under {APP_DIR}")

    print("Detected CLI tools:")
    for name, path in detected.items():
        marker = "found" if path else "missing"
        print(f"  {name}: {marker}{f' ({path})' if path else ''}")
    if created:
        print(f"Created profiles: {', '.join(created)}")
    if updated:
        print(f"Updated profiles: {', '.join(updated)}")
    if strategies:
        print("Strategy aliases:")
        for item in strategies:
            print(f"  {item}")

    shell = selected_setup_shell(args.shell)
    install_shell_helpers_for_setup(args, shell)
    print("Next commands:")
    print("  ai-list")
    print("  ai-use code-fast")
    print("  ai-api test code-fast")
    print("  ai-model list --provider openrouter")
    print("  ai-recall")


def cmd_setup(args: argparse.Namespace) -> None:
    if getattr(args, "wizard", False):
        cmd_setup_wizard(args)
        return
    if getattr(args, "full", False):
        cmd_setup_full(args)
        return
    if args.dry_run:
        print(f"Would initialize state under {APP_DIR}")
    else:
        state = normalize_state(ensure_state())
        save_state(state)
        print(f"Initialized {STATE_PATH}")

    shell = selected_setup_shell(args.shell)
    install_shell_helpers_for_setup(args, shell)
    if not args.dry_run:
        print("Run ai-status after reloading your shell to confirm the active profile.")


def cmd_project_init(args: argparse.Namespace) -> None:
    root = Path(args.path or Path.cwd()).resolve()
    state = normalize_state(ensure_state())
    effective, _ = effective_state(root)
    profiles = effective.get("profiles", {})
    active = resolve_profile_name(effective, args.active) if args.active else None
    if active and active not in profiles:
        available = ", ".join(sorted(profiles))
        raise SystemExit(f"Unknown profile {args.active!r}. Available: {available}")
    config = load_project_config_at(root)
    config.setdefault("profiles", {})
    config.setdefault("aliases", {})
    config["active"] = active or config.get("active") or state.get("active", "codex")
    path = save_project_config(config, root)
    ensure_memory_files(root)
    print(f"Initialized project config: {path}")
    print(f"Project memory: {root / PROJECT_MEMORY_NAME}")


def normalize_tags(tags: list[str]) -> list[str]:
    normalized: list[str] = []
    for item in tags:
        for tag in re.split(r"[, ]+", item.strip()):
            if not tag:
                continue
            clean = re.sub(r"[^A-Za-z0-9_.-]", "-", tag.lower()).strip("-")
            if clean and clean not in normalized:
                normalized.append(clean)
    return normalized


def parse_memory_entry(line: str) -> dict[str, Any] | None:
    match = MEMORY_ENTRY_RE.match(line.strip())
    if not match:
        return None
    tags = normalize_tags([match.group("tags") or ""])
    return {"stamp": match.group("stamp"), "tags": tags, "text": match.group("text"), "line": line}


def format_memory_entry(stamp: str, text: str, tags: list[str]) -> str:
    tag_text = f" [{','.join(tags)}]" if tags else ""
    return f"- {stamp}{tag_text}: {text}"


def memory_paths_for_scope(scope: str) -> list[tuple[str, Path]]:
    project_root = find_project_root()
    if scope == "all":
        items: list[tuple[str, Path]] = [("global", GLOBAL_MEMORY_PATH)]
        if project_root:
            items.append(("project", project_root / PROJECT_MEMORY_NAME))
        items.append(("session", SESSION_MEMORY_PATH))
        return items
    return [(scope, memory_target(scope))]


def memory_archive_path(scope: str) -> Path:
    archive_dir = MEMORY_DIR / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return archive_dir / f"{stamp}-{scope}.md"


def filter_memory_text(text: str, tags: list[str]) -> str:
    if not tags:
        return text.rstrip()
    output: list[str] = []
    for line in text.splitlines():
        entry = parse_memory_entry(line)
        if entry and set(tags).issubset(set(entry["tags"])):
            output.append(line)
    return "\n".join(output).rstrip()


def dedupe_memory_file(path: Path) -> tuple[int, int]:
    if not path.exists():
        return 0, 0
    lines = path.read_text(encoding="utf-8").splitlines()
    seen: set[str] = set()
    kept: list[str] = []
    removed = 0
    for line in lines:
        entry = parse_memory_entry(line)
        if not entry:
            kept.append(line)
            continue
        key = re.sub(r"\s+", " ", entry["text"].strip().lower())
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        kept.append(line)
    path.write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8")
    return len(seen), removed


def archive_memory_file(path: Path, scope: str, keep_last: int = 0) -> Path | None:
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    header = [line for line in lines if not parse_memory_entry(line)]
    entries = [line for line in lines if parse_memory_entry(line)]
    if not entries:
        return None
    archive_entries = entries[:-keep_last] if keep_last else entries
    keep_entries = entries[-keep_last:] if keep_last else []
    if not archive_entries:
        return None
    archive_path = memory_archive_path(scope)
    archive_path.write_text("\n".join([f"# Archived {scope} memory", "", *archive_entries]).rstrip() + "\n", encoding="utf-8")
    if keep_entries:
        new_lines = [*(header or [f"# {scope.title()} CLI AI Memory", ""]), *keep_entries]
    else:
        new_lines = [f"# {scope.title()} CLI AI Memory", ""]
    path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")
    return archive_path


def cmd_remember(args: argparse.Namespace) -> None:
    ensure_state()
    text = " ".join(args.text).strip()
    if not text:
        raise SystemExit("Nothing to remember.")
    secret = detect_secret(text)
    if secret and not args.force:
        raise SystemExit(f"Refusing to save possible secret ({secret}). Re-run with --force only if this is intentional.")
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    target = memory_target(args.scope)
    tags = normalize_tags(args.tag)
    ensure_memory_files(find_project_root())
    if target.exists() and not args.duplicate:
        existing = target.read_text(encoding="utf-8")
        for line in existing.splitlines():
            entry = parse_memory_entry(line)
            if entry and entry["text"].strip() == text:
                print(f"Memory entry already exists in {target}. Use --duplicate to save another copy.")
                return
    with target.open("a", encoding="utf-8") as handle:
        handle.write(format_memory_entry(stamp, text, tags) + "\n")
    refresh_context_memory(find_project_root())
    print(f"Saved {args.scope} memory entry to {target}")


def cmd_forget_session(_: argparse.Namespace) -> None:
    ensure_memory_files(find_project_root())
    SESSION_MEMORY_PATH.write_text("# Session CLI AI Memory\n\n", encoding="utf-8")
    refresh_context_memory(find_project_root())
    print(f"Cleared session memory: {SESSION_MEMORY_PATH}")


def cmd_recall(args: argparse.Namespace) -> None:
    ensure_memory_files(find_project_root())
    tags = normalize_tags(args.tag)
    if args.scope == "all":
        print(filter_memory_text(CONTEXT_MEMORY_PATH.read_text(encoding="utf-8"), tags))
        return
    print(filter_memory_text(memory_target(args.scope).read_text(encoding="utf-8"), tags))


def cmd_memory(args: argparse.Namespace) -> None:
    ensure_memory_files(find_project_root())
    if args.action == "tags":
        counts: dict[str, int] = {}
        for _, path in memory_paths_for_scope(args.scope):
            if not path.exists():
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                entry = parse_memory_entry(line)
                if not entry:
                    continue
                for tag in entry["tags"]:
                    counts[tag] = counts.get(tag, 0) + 1
        if args.json:
            print(json.dumps(counts, indent=2, ensure_ascii=False))
            return
        if not counts:
            print("No tagged memory entries found.")
            return
        for tag, count in sorted(counts.items()):
            print(f"{tag}: {count}")
        return
    if args.action == "dedupe":
        for scope, path in memory_paths_for_scope(args.scope):
            _, removed = dedupe_memory_file(path)
            print(f"{scope}: removed {removed} duplicate entries")
        refresh_context_memory(find_project_root())
        return
    if args.action == "archive":
        for scope, path in memory_paths_for_scope(args.scope):
            archive_path = archive_memory_file(path, scope, 0)
            print(f"{scope}: archived to {archive_path}" if archive_path else f"{scope}: nothing to archive")
        refresh_context_memory(find_project_root())
        return
    if args.action == "compact":
        for scope, path in memory_paths_for_scope(args.scope):
            archive_path = archive_memory_file(path, scope, args.keep)
            print(f"{scope}: archived older entries to {archive_path}" if archive_path else f"{scope}: nothing to compact")
        refresh_context_memory(find_project_root())
        return
    raise SystemExit(f"Unknown memory action {args.action!r}")


def cmd_doctor(args: argparse.Namespace) -> None:
    events: list[dict[str, str]] = []
    state = repair_global_state(args.fix, events)
    project_config_path = repair_project_config(args.fix, state, events)
    project_root = project_config_path.parent if project_config_path else find_project_root()
    ensure_memory_files(project_root)
    check_wrapper_staleness(args.fix, events)

    if any(item["status"] == "fail" for item in events):
        payload = {"fix": bool(args.fix), "events": events, "active": state.get("active"), "profile": None, "project_config": str(project_config_path) if project_config_path else None}
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            for item in events:
                print(f"[{item['status']}] {item['name']}: {item['detail']}")
            print("Run doctor --fix to repair fixable issues.")
        raise SystemExit(1)

    effective, config_path = effective_state()
    profile = active_profile(effective)
    python_detail = os.environ.get("AI_CLI_SWITCHER_PYTHON") or shutil.which("py") or shutil.which("python3") or shutil.which("python")
    add_repair_event(events, "ok" if python_detail else "warn", "python launcher", python_detail or "not found")
    add_repair_event(events, "ok", "script", str(SCRIPT_PATH))
    add_repair_event(events, "ok" if GLOBAL_MEMORY_PATH.exists() else "warn", "global memory", str(GLOBAL_MEMORY_PATH))
    add_repair_event(events, "ok" if CONTEXT_MEMORY_PATH.exists() else "warn", "combined context", str(CONTEXT_MEMORY_PATH))
    if config_path:
        add_repair_event(events, "ok", "project config", str(config_path))
        add_repair_event(events, "ok" if (config_path.parent / PROJECT_MEMORY_NAME).exists() else "warn", "project memory", str(config_path.parent / PROJECT_MEMORY_NAME))
    command = str(profile.get("command", ""))
    add_repair_event(events, "ok" if shutil.which(command) else "warn", f"active command {command!r}", shutil.which(command) or "not found on PATH")
    seen_env_refs: set[str] = set()
    for key, value in profile.get("env", {}).items():
        ref = env_reference_name(value)
        if ref:
            if ref in seen_env_refs:
                continue
            seen_env_refs.add(ref)
            add_repair_event(events, "ok" if os.environ.get(ref) else "warn", f"env {ref}", "set" if os.environ.get(ref) else "missing")
        else:
            add_repair_event(events, "ok", f"env {key}", "managed by profile")

    payload = {
        "fix": bool(args.fix),
        "events": events,
        "active": effective.get("active"),
        "profile": profile,
        "project_config": str(config_path) if config_path else None,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    for item in events:
        marker = item["status"]
        print(f"[{marker}] {item['name']}: {item['detail']}")
    print(f"Active profile: {effective.get('active')} -> {profile.get('command')} ({profile.get('model')})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(required=True)

    init_parser = sub.add_parser("init", help="Create default state and shared memory.")
    init_parser.set_defaults(func=cmd_init)

    list_parser = sub.add_parser("list", help="List profiles.")
    list_parser.set_defaults(func=cmd_list)

    status_parser = sub.add_parser("status", help="Show a concise active profile summary.")
    status_parser.add_argument("--json", action="store_true")
    status_parser.set_defaults(func=cmd_status)

    alias_parser = sub.add_parser("alias", help="List, set, or remove profile aliases.")
    alias_parser.add_argument("action", choices=["list", "set", "remove"])
    alias_parser.add_argument("name", nargs="?")
    alias_parser.add_argument("target", nargs="?")
    alias_parser.set_defaults(func=cmd_alias)

    paths_parser = sub.add_parser("paths", help="Show switcher config and memory paths.")
    paths_parser.add_argument("--json", action="store_true")
    paths_parser.set_defaults(func=cmd_paths)

    export_parser = sub.add_parser("export", help="Export global switcher config as JSON.")
    export_parser.add_argument("--output", "-o")
    export_parser.add_argument("--portable", action="store_true", help="Export without machine-specific absolute memory paths.")
    export_parser.add_argument("--allow-secret-env", action="store_true", help="Allow exported env values that look like secrets.")
    export_parser.set_defaults(func=cmd_export)

    import_parser = sub.add_parser("import", help="Import global switcher config from JSON.")
    import_parser.add_argument("input")
    import_parser.add_argument("--replace", action="store_true", help="Replace the entire global config.")
    import_parser.add_argument("--active", action="store_true", help="Also import the active profile setting when merging.")
    import_parser.add_argument("--merge-policy", choices=["overwrite", "keep", "rename"], default="overwrite", help="How to handle conflicting profiles, aliases, and model aliases.")
    import_parser.add_argument("--allow-secret-env", action="store_true", help="Allow imported env values that look like secrets.")
    import_parser.set_defaults(func=cmd_import)

    secret_parser = sub.add_parser("secret", help="Audit switcher files for direct-looking secrets.")
    secret_parser.add_argument("action", choices=["audit"])
    secret_parser.add_argument("--scope", choices=["all", "state", "project", "memory"], default="all")
    secret_parser.add_argument("--json", action="store_true")
    secret_parser.add_argument("--fail", action="store_true", help="Exit non-zero when findings are present.")
    secret_parser.set_defaults(func=cmd_secret)

    api_parser = sub.add_parser("api", help="List, inspect, or apply model API presets.")
    api_sub = api_parser.add_subparsers(dest="action", required=True)
    api_list_parser = api_sub.add_parser("list", help="List built-in API presets.")
    api_list_parser.add_argument("--json", action="store_true")
    api_list_parser.set_defaults(func=cmd_api)
    api_show_parser = api_sub.add_parser("show", help="Show one API preset.")
    api_show_parser.add_argument("name")
    api_show_parser.add_argument("--json", action="store_true")
    api_show_parser.set_defaults(func=cmd_api)
    api_test_parser = api_sub.add_parser("test", help="Test a profile's API settings and optional connectivity.")
    api_test_parser.add_argument("profile", nargs="?", help="Profile or alias to test. Defaults to the active profile.")
    api_test_parser.add_argument("--timeout", type=float, default=5.0)
    api_test_parser.add_argument("--skip-network", action="store_true", help="Only validate local profile/env configuration.")
    api_test_parser.add_argument("--json", action="store_true")
    api_test_parser.set_defaults(func=cmd_api)
    api_apply_parser = api_sub.add_parser("apply", help="Apply an API preset to a profile.")
    api_apply_parser.add_argument("profile")
    api_apply_parser.add_argument("preset")
    api_apply_parser.add_argument("--provider")
    api_apply_parser.add_argument("--command")
    api_apply_parser.add_argument("--model")
    api_apply_parser.add_argument("--memory")
    api_apply_parser.add_argument("--base-url")
    api_apply_parser.add_argument("--api-key-env", metavar="ENV")
    api_apply_parser.add_argument("--env", action="append", default=[], metavar="KEY=VALUE")
    api_apply_parser.add_argument("--page", action="append", default=[], metavar="LABEL=URL")
    api_apply_parser.add_argument("--alias")
    api_apply_parser.add_argument("--use", action="store_true", help="Activate the profile after saving.")
    api_apply_parser.add_argument("--project", action="store_true", help="Save the profile in the current project config.")
    api_apply_parser.add_argument("--allow-secret-env", action="store_true", help="Allow storing env values that look like secrets.")
    api_apply_parser.set_defaults(func=cmd_api)

    adapter_parser = sub.add_parser("adapter", help="Generate CLI-specific config snippets for a profile.")
    adapter_parser.add_argument("adapter", choices=["list", "codex", "claude", "gemini", "opencode"])
    adapter_parser.add_argument("profile", nargs="?")
    adapter_parser.add_argument("--shell", choices=["powershell", "cmd", "bash", "zsh", "fish", "nu"], default="bash")
    adapter_parser.add_argument("--json", action="store_true")
    adapter_parser.set_defaults(func=cmd_adapter)

    model_parser = sub.add_parser("model", help="List, show, pin, or alias model registry entries.")
    model_sub = model_parser.add_subparsers(dest="action", required=True)
    model_list_parser = model_sub.add_parser("list", help="List known models and aliases.")
    model_list_parser.add_argument("--provider")
    model_list_parser.add_argument("--json", action="store_true")
    model_list_parser.set_defaults(func=cmd_model)
    model_show_parser = model_sub.add_parser("show", help="Show a model or alias.")
    model_show_parser.add_argument("name")
    model_show_parser.add_argument("--provider")
    model_show_parser.add_argument("--json", action="store_true")
    model_show_parser.set_defaults(func=cmd_model)
    model_pin_parser = model_sub.add_parser("pin", help="Pin a profile to a model or model alias.")
    model_pin_parser.add_argument("profile")
    model_pin_parser.add_argument("model")
    model_pin_parser.add_argument("--provider")
    model_pin_parser.add_argument("--project", action="store_true")
    model_pin_parser.set_defaults(func=cmd_model)
    model_alias_parser = model_sub.add_parser("alias", help="List, set, or remove model aliases.")
    model_alias_parser.add_argument("alias_action", choices=["list", "set", "remove"])
    model_alias_parser.add_argument("name", nargs="?")
    model_alias_parser.add_argument("provider", nargs="?")
    model_alias_parser.add_argument("model", nargs="?")
    model_alias_parser.add_argument("--cap", action="append", default=[], metavar="KEY=VALUE")
    model_alias_parser.set_defaults(func=cmd_model)

    strategy_parser = sub.add_parser("strategy", help="List, install, or activate task-based model strategies.")
    strategy_parser.add_argument("action", choices=["list", "install", "use"])
    strategy_parser.add_argument("name", nargs="?")
    strategy_parser.add_argument("--json", action="store_true")
    strategy_parser.set_defaults(func=cmd_strategy)

    recipe_parser = sub.add_parser("recipe", help="List, show, or install one-step profile recipes.")
    recipe_parser.add_argument("action", choices=["list", "show", "install"])
    recipe_parser.add_argument("names", nargs="*", help="Recipe names or aliases.")
    recipe_parser.add_argument("--all", action="store_true", help="Install every built-in recipe.")
    recipe_parser.add_argument("--use", action="store_true", help="Activate the last installed recipe profile.")
    recipe_parser.add_argument("--active", help="Activate a specific profile, alias, or recipe after installing.")
    recipe_parser.add_argument("--force", action="store_true", help="Overwrite conflicting recipe aliases.")
    recipe_parser.add_argument("--dry-run", action="store_true")
    recipe_parser.add_argument("--json", action="store_true")
    recipe_parser.set_defaults(func=cmd_recipe)

    session_parser = sub.add_parser("session", help="Start, list, switch, attach, or stop managed AI CLI sessions.")
    session_sub = session_parser.add_subparsers(dest="action", required=True)
    session_list_parser = session_sub.add_parser("list", help="List managed AI CLI sessions.")
    session_list_parser.add_argument("--json", action="store_true")
    session_list_parser.set_defaults(func=cmd_session)
    session_start_parser = session_sub.add_parser("start", help="Start a profile, alias, strategy, or recipe in a managed session.")
    session_start_parser.add_argument("target", help="Profile, alias, strategy, or recipe.")
    session_start_parser.add_argument("--backend", choices=["auto", "tmux", "wt", "powershell", "print"], default="auto")
    session_start_parser.add_argument("--name", dest="session_name", help="Session record name. Defaults to the resolved profile.")
    session_start_parser.add_argument("--cwd", help="Working directory for the launched agent session.")
    session_start_parser.add_argument("--attach", action="store_true", help="Attach or switch to tmux session after starting.")
    session_start_parser.add_argument("--reuse", action="store_true", help="Reuse an existing tmux session with the same name.")
    session_start_parser.add_argument("--arg", action="append", default=[], help="Extra argument passed to the launched CLI. Repeat as needed; use --arg=--flag for option-like values.")
    session_start_parser.set_defaults(func=cmd_session)
    for action_name in ["switch", "attach", "stop"]:
        action_parser = session_sub.add_parser(action_name, help=f"{action_name.capitalize()} a managed AI CLI session.")
        action_parser.add_argument("target", help="Session name, profile, or backend id.")
        action_parser.set_defaults(func=cmd_session)

    handoff_parser = sub.add_parser("handoff", help="Write a handoff note to shared memory and open a target AI session.")
    handoff_parser.add_argument("profile", help="Target profile, alias, strategy, or recipe.")
    handoff_parser.add_argument("text", nargs="+", help="Handoff note to store in session memory.")
    handoff_parser.add_argument("--scope", choices=["global", "project", "session"], default="session")
    handoff_parser.add_argument("--tag", action="append", default=[], help="Extra tag for the handoff memory entry.")
    handoff_parser.add_argument("--backend", choices=["auto", "tmux", "wt", "powershell", "print"], default="auto")
    handoff_parser.add_argument("--name", dest="session_name", help="Session record name for the target agent.")
    handoff_parser.add_argument("--cwd", help="Working directory for the launched agent session.")
    handoff_parser.add_argument("--attach", action="store_true", help="Attach or switch to tmux after starting.")
    handoff_parser.add_argument("--no-start", action="store_true", help="Only write memory; do not start a session.")
    handoff_parser.add_argument("--duplicate", action="store_true")
    handoff_parser.add_argument("--force", action="store_true", help="Save even if the handoff note looks like a secret.")
    handoff_parser.set_defaults(func=cmd_handoff)

    add_parser = sub.add_parser("add", help="Add a profile.")
    add_parser.add_argument("name")
    add_parser.add_argument("--provider")
    add_parser.add_argument("--command")
    add_parser.add_argument("--model", default="default")
    add_parser.add_argument("--memory")
    add_parser.add_argument("--env", action="append", default=[], metavar="KEY=VALUE")
    add_parser.add_argument("--page", action="append", default=[], metavar="LABEL=URL")
    add_parser.add_argument("--force", action="store_true")
    add_parser.add_argument("--project", action="store_true", help="Add the profile to the current project config.")
    add_parser.add_argument("--allow-secret-env", action="store_true", help="Allow storing env values that look like secrets.")
    add_parser.set_defaults(func=cmd_add)

    profile_parser = sub.add_parser("profile", help="Create or update a profile in one step.")
    profile_parser.add_argument("name")
    profile_parser.add_argument("--provider")
    profile_parser.add_argument("--command")
    profile_parser.add_argument("--model")
    profile_parser.add_argument("--memory")
    profile_parser.add_argument("--api", metavar="PRESET", help="Apply a built-in API preset.")
    profile_parser.add_argument("--base-url", help="Override the preset API base URL.")
    profile_parser.add_argument("--api-key-env", metavar="ENV", help="Use this environment variable as the API key source.")
    profile_parser.add_argument("--env", action="append", default=[], metavar="KEY=VALUE")
    profile_parser.add_argument("--page", action="append", default=[], metavar="LABEL=URL")
    profile_parser.add_argument("--alias")
    profile_parser.add_argument("--use", action="store_true", help="Activate the profile after saving.")
    profile_parser.add_argument("--project", action="store_true", help="Save the profile in the current project config.")
    profile_parser.add_argument("--allow-secret-env", action="store_true", help="Allow storing env values that look like secrets.")
    profile_parser.set_defaults(func=cmd_profile)

    set_parser = sub.add_parser("set", help="Update a profile.")
    set_parser.add_argument("name")
    set_parser.add_argument("--provider")
    set_parser.add_argument("--command")
    set_parser.add_argument("--model")
    set_parser.add_argument("--memory")
    set_parser.add_argument("--api", metavar="PRESET", help="Apply a built-in API preset.")
    set_parser.add_argument("--base-url", help="Override the preset API base URL.")
    set_parser.add_argument("--api-key-env", metavar="ENV", help="Use this environment variable as the API key source.")
    set_parser.add_argument("--env", action="append", default=[], metavar="KEY=VALUE")
    set_parser.add_argument("--unset-env", action="append", default=[], metavar="KEY")
    set_parser.add_argument("--page", action="append", default=[], metavar="LABEL=URL")
    set_parser.add_argument("--unset-page", action="append", default=[], metavar="LABEL")
    set_parser.add_argument("--project", action="store_true", help="Update the profile in the current project config.")
    set_parser.add_argument("--allow-secret-env", action="store_true", help="Allow storing env values that look like secrets.")
    set_parser.set_defaults(func=cmd_set)

    remove_parser = sub.add_parser("remove", help="Remove a profile.")
    remove_parser.add_argument("name")
    remove_parser.add_argument("--project", action="store_true", help="Remove the profile from the current project config.")
    remove_parser.set_defaults(func=cmd_remove)

    use_parser = sub.add_parser("use", help="Set the active profile.")
    use_parser.add_argument("name")
    use_parser.add_argument("--project", action="store_true", help="Set profile for the current project only.")
    use_parser.add_argument("--open-page", nargs="?", const="home", help="Open the selected profile page after switching.")
    use_parser.set_defaults(func=cmd_use)

    select_parser = sub.add_parser("select", help="Pick a profile from an interactive numbered menu.")
    select_parser.add_argument("--project", action="store_true", help="Save the selected profile to the current project config.")
    select_parser.add_argument("--open-page", nargs="?", const="home", help="Open the selected profile page after switching.")
    select_parser.set_defaults(func=cmd_select)

    page_parser = sub.add_parser("page", help="List, open, set, or remove profile pages.")
    page_parser.add_argument("action", choices=["list", "open", "set", "remove"])
    page_parser.add_argument("profile", nargs="?")
    page_parser.add_argument("label", nargs="?", default="home")
    page_parser.add_argument("url", nargs="?")
    page_parser.add_argument("--print", action="store_true")
    page_parser.set_defaults(func=cmd_page)

    current_parser = sub.add_parser("current", help="Show current profile or emit shell env commands.")
    current_parser.add_argument("--shell", choices=["powershell", "cmd", "bash", "zsh", "fish", "nu"])
    current_parser.set_defaults(func=cmd_current)

    remember_parser = sub.add_parser("remember", help="Append a shared memory entry.")
    remember_parser.add_argument("--scope", choices=["global", "project", "session"], default="global")
    remember_parser.add_argument("--tag", action="append", default=[], help="Tag the memory entry. Can be repeated or comma-separated.")
    remember_parser.add_argument("--duplicate", action="store_true", help="Allow saving duplicate memory text.")
    remember_parser.add_argument("--force", action="store_true", help="Save even if the text looks like a secret.")
    remember_parser.add_argument("text", nargs="+")
    remember_parser.set_defaults(func=cmd_remember)

    recall_parser = sub.add_parser("recall", help="Print shared memory.")
    recall_parser.add_argument("--scope", choices=["all", "global", "project", "session"], default="all")
    recall_parser.add_argument("--tag", action="append", default=[], help="Only print entries matching this tag. Can be repeated.")
    recall_parser.set_defaults(func=cmd_recall)

    memory_parser = sub.add_parser("memory", help="Manage tagged memory, dedupe, archive, or compact memory files.")
    memory_parser.add_argument("action", choices=["tags", "dedupe", "archive", "compact"])
    memory_parser.add_argument("--scope", choices=["all", "global", "project", "session"], default="all")
    memory_parser.add_argument("--keep", type=int, default=50, help="Entries to keep when compacting.")
    memory_parser.add_argument("--json", action="store_true")
    memory_parser.set_defaults(func=cmd_memory)

    open_parser = sub.add_parser("open", help="Open or print a config or memory file path.")
    open_parser.add_argument("target", choices=["home", "state", "global", "session", "context", "project"])
    open_parser.add_argument("--print", action="store_true")
    open_parser.set_defaults(func=cmd_open)

    forget_session_parser = sub.add_parser("forget-session", help="Clear temporary session memory.")
    forget_session_parser.set_defaults(func=cmd_forget_session)

    project_init_parser = sub.add_parser("project-init", help="Create project-local config and memory files.")
    project_init_parser.add_argument("--active")
    project_init_parser.add_argument("--path")
    project_init_parser.set_defaults(func=cmd_project_init)

    doctor_parser = sub.add_parser("doctor", help="Check profiles, commands, env vars, and memory files.")
    doctor_parser.add_argument("--fix", action="store_true", help="Repair missing files, invalid active profile, bad aliases, and stale wrappers where possible.")
    doctor_parser.add_argument("--json", action="store_true")
    doctor_parser.set_defaults(func=cmd_doctor)

    run_parser = sub.add_parser("run", add_help=False, help="Run the active CLI command with profile environment.")
    run_parser.add_argument("args", nargs=argparse.REMAINDER)
    run_parser.set_defaults(func=cmd_run)

    install_ps_parser = sub.add_parser("install-powershell", help="Install ai-* helper functions into PowerShell profile.")
    install_ps_parser.add_argument("--profile")
    install_ps_parser.add_argument("--dry-run", action="store_true")
    install_ps_parser.set_defaults(func=cmd_install_powershell)

    install_cmd_parser = sub.add_parser("install-cmd", help="Install native cmd.exe .cmd helper scripts.")
    install_cmd_parser.add_argument("--dir")
    install_cmd_parser.add_argument("--dry-run", action="store_true")
    install_cmd_parser.set_defaults(func=cmd_install_cmd)

    install_shell_parser = sub.add_parser("install-shell", help="Install Bash/Zsh helper functions.")
    install_shell_parser.add_argument("--output", "-o")
    install_shell_parser.add_argument("--dry-run", action="store_true")
    install_shell_parser.set_defaults(func=cmd_install_shell)

    install_fish_parser = sub.add_parser("install-fish", help="Install fish shell helper functions.")
    install_fish_parser.add_argument("--output", "-o")
    install_fish_parser.add_argument("--dry-run", action="store_true")
    install_fish_parser.set_defaults(func=cmd_install_fish)

    install_unix_parser = sub.add_parser("install-unix", help="Install Linux/macOS helpers for bash, zsh, or fish.")
    install_unix_parser.add_argument("--shell", choices=["auto", "bash", "zsh", "fish"], default="auto")
    install_unix_parser.add_argument("--output", "-o")
    install_unix_parser.add_argument("--profile")
    install_unix_parser.add_argument("--dry-run", action="store_true")
    install_unix_parser.set_defaults(func=cmd_install_unix)

    setup_parser = sub.add_parser("setup", help="Initialize and install shell helpers in one step.")
    setup_parser.add_argument("--shell", choices=["auto", "powershell", "cmd", "unix", "bash", "zsh", "fish"], default="auto")
    setup_parser.add_argument("--profile")
    setup_parser.add_argument("--dir")
    setup_parser.add_argument("--output", "-o")
    setup_parser.add_argument("--with-cmd", action="store_true", help="Also install cmd.exe wrappers on Windows.")
    setup_parser.add_argument("--full", action="store_true", help="Create recommended profiles, strategy aliases, and shell helpers.")
    setup_parser.add_argument("--wizard", action="store_true", help="Interactively detect tools, install recipes, choose an active profile, and run checks.")
    setup_parser.add_argument("--yes", "-y", action="store_true", help="Use wizard defaults without prompting.")
    setup_parser.add_argument("--recipes", action="append", default=[], metavar="NAMES", help="Comma- or space-separated wizard recipes.")
    setup_parser.add_argument("--active", help="Wizard active profile, alias, or recipe.")
    setup_parser.add_argument("--force", action="store_true", help="Overwrite conflicting recipe aliases in wizard mode.")
    setup_parser.add_argument("--no-strategy", action="store_true", help="Skip installing task strategy aliases in wizard mode.")
    setup_parser.add_argument("--skip-doctor", action="store_true", help="Skip doctor --fix after wizard setup.")
    setup_parser.add_argument("--skip-secret-audit", action="store_true", help="Skip secret audit after wizard setup.")
    setup_parser.add_argument("--no-install", action="store_true", help="Create config without installing shell helper files.")
    setup_parser.add_argument("--dry-run", action="store_true")
    setup_parser.set_defaults(func=cmd_setup)

    return parser


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        cmd_run(argparse.Namespace(args=sys.argv[2:]))
        return
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

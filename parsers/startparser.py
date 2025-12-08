"""
Simple CLI tool for generating new parser feature modules inside the `parsers` package.

Usage example:
    python startparser.py weather
"""

from __future__ import annotations

import keyword
from pathlib import Path
import re
import sys

# ============================================================
# Paths
# ============================================================

PARSERS_ROOT = Path(__file__).resolve().parent
FEATURES_DIR = PARSERS_ROOT / "features"
TOP_INIT = PARSERS_ROOT / "__init__.py"


# ============================================================
# Utility functions
# ============================================================


def to_snake(name: str) -> str:
    """
    Convert an arbitrary string into snake_case.
    """
    name = name.strip()
    name = name.replace("-", "_").replace(" ", "_")
    name = re.sub(r"[^0-9a-zA-Z_]", "", name)
    name = re.sub(r"_+", "_", name)
    return name.lower()


def to_pascal(name: str) -> str:
    """
    Convert a string into PascalCase.
    """
    name = name.strip().replace("-", " ").replace("_", " ")
    parts = [p for p in re.split(r"\s+", name) if p]
    return "".join(p.capitalize() for p in parts)


def validate_feature_name(name: str) -> str:
    """
    Validate that the feature name is a safe Python identifier (in snake_case).
    """
    snake = to_snake(name)
    if not snake:
        raise ValueError("Feature name becomes empty after normalization.")
    if snake[0].isdigit():
        raise ValueError("Feature name must not begin with a digit.")
    if keyword.iskeyword(snake):
        raise ValueError(f"'{snake}' is a reserved Python keyword.")
    return snake


# ============================================================
# File templates
# ============================================================

DTOS_TEMPLATE = """from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class {FeaturePascal}DTO:
    \"\"\"DTO for the '{feature_name}' parser.

    TODO: Replace fields with real ones.
    \"\"\"
    value: str
"""

EXCEPTIONS_TEMPLATE = """class {FeaturePascal}Error(Exception):
    \"\"\"Base exception for the '{feature_name}' parser.\"\"\"
    pass
"""

ENDPOINTS_TEMPLATE = """from furl import furl

BASE_URL = "https://example.com"  # TODO: Replace with an actual endpoint root


def build_example_url(param: str) -> str:
    \"\"\"Example endpoint builder.

    TODO: Replace with actual endpoint-building logic.
    \"\"\"
    return str(furl(BASE_URL).add(path="/example").add(args={{"q": param}}))
"""

SCRAPERS_TEMPLATE = """from ..base_scraper import BaseScraper
from .dtos import {FeaturePascal}DTO
from .endpoints import build_example_url
from .exceptions import {FeaturePascal}Error


class Example{FeaturePascal}Scraper(BaseScraper[{FeaturePascal}DTO]):
    \"\"\"Example scraper implementation for the '{feature_name}' feature.

    Use `self._client.request(...)` and parse the response accordingly.
    \"\"\"

    def __call__(self, param: str) -> {FeaturePascal}DTO:
        resp = self._client.request(method="get", url=build_example_url(param))
        if resp.status_code != 200:
            raise {FeaturePascal}Error(
                f"Unexpected status code: {{resp.status_code}}"
            )

        # TODO: Parse response and return real DTO values
        return {FeaturePascal}DTO(value=resp.text)
"""

PARSER_TEMPLATE = """from ...infra.client import configs
from ..base_parser import BaseParser
from .scrapers import Example{FeaturePascal}Scraper


class {FeaturePascal}Parser(BaseParser):
    \"\"\"Entry point parser class for the '{feature_name}' feature.\"\"\"

    def __init__(self, config_box: configs.ConfigBox) -> None:
        super().__init__(config_box)
        self.example = Example{FeaturePascal}Scraper(self._client)
"""

FEATURE_INIT_TEMPLATE = """from ...infra.client import configs as cfgs
from . import dtos, exceptions
from .parser import {FeaturePascal}Parser

{feature_name}_parser = {FeaturePascal}Parser(
    cfgs.ConfigBox(
        net=cfgs.NetConfig(),
        cache=cfgs.CacheConfig(
            enabled=True,
            automatic_prune_cache=True,
            prune_interval=10 * 60,
            ttl=30 * 60,
            name="{feature_name}_parser_cache.sqlite",
        ),
        cookie=cfgs.CookieConfig(),
    )
)

__all__ = ["{feature_name}_parser", "exceptions", "dtos"]
"""


# ============================================================
# Generation logic
# ============================================================


def create_feature_structure(feature_name: str) -> None:
    """
    Generate the full folder template for a new parser feature.
    """
    snake = validate_feature_name(feature_name)
    pascal = to_pascal(snake)

    feature_dir = FEATURES_DIR / snake
    if feature_dir.exists():
        raise SystemExit(f"Feature '{snake}' already exists: {feature_dir}")

    feature_dir.mkdir(parents=True, exist_ok=False)

    files = {
        "dtos.py": DTOS_TEMPLATE,
        "exceptions.py": EXCEPTIONS_TEMPLATE,
        "endpoints.py": ENDPOINTS_TEMPLATE,
        "scrapers.py": SCRAPERS_TEMPLATE,
        "parser.py": PARSER_TEMPLATE,
        "__init__.py": FEATURE_INIT_TEMPLATE,
    }

    ctx = {"feature_name": snake, "FeaturePascal": pascal}

    for filename, template in files.items():
        (feature_dir / filename).write_text(template.format(**ctx), encoding="utf-8")

    print(f"[OK] Created feature directory '{snake}' at {feature_dir}")


# ============================================================
# Update top-level parsers/__init__.py
# ============================================================


def update_top_level_init(feature_name: str) -> None:
    """
    Insert import statements and __all__ exports for the new feature.
    """
    snake = to_snake(feature_name)
    init_text = TOP_INIT.read_text(encoding="utf-8")

    import_block = (
        f"from .features.{snake} import (\n"
        f"    dtos as {snake}_dtos,\n"
        f"    exceptions as {snake}_exceptions,\n"
        f"    {snake}_parser,\n"
        f")\n"
    )

    if f"from .features.{snake} import" in init_text:
        print(f"[WARN] Imports for 'features.{snake}' already exist, skipping.")
    else:
        lines = init_text.splitlines()
        # find end of the LAST import block
        last_import_start = None

        for i, line in enumerate(lines):
            if line.strip().startswith("from .features."):
                last_import_start = i

        if last_import_start is None:
            insert_pos = 0
        else:
            i = last_import_start
            while i < len(lines) and ")" not in lines[i]:
                i += 1
            insert_pos = i + 1
        lines.insert(insert_pos, import_block.rstrip("\n"))
        init_text = "\n".join(lines)
        print(f"[OK] Added new import block for '{snake}'")

    # Update __all__
    lines = init_text.splitlines()
    if "__all__" not in init_text:
        # Create __all__ from scratch
        all_block = (
            "\n\n__all__ = [\n"
            f'    "{snake}_parser",\n'
            f'    "{snake}_exceptions",\n'
            f'    "{snake}_dtos",\n'
            "]\n"
        )
        TOP_INIT.write_text(init_text.rstrip() + all_block + "\n", encoding="utf-8")
        print(f"[OK] Created __all__ with '{snake}' items")
        return

    # Append to existing __all__
    start_idx = next(i for i, line in enumerate(lines) if line.strip().startswith("__all__"))
    end_idx = start_idx
    while end_idx < len(lines) and "]" not in lines[end_idx]:
        end_idx += 1

    block = "\n".join(lines[start_idx : end_idx + 1])
    if f'"{snake}_parser"' in block:
        print(f"[WARN] __all__ already contains entries for '{snake}', skipping.")
        TOP_INIT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    new_items = [
        f'    "{snake}_parser",',
        f'    "{snake}_exceptions",',
        f'    "{snake}_dtos",',
    ]

    lines = lines[:end_idx] + new_items + lines[end_idx:]
    TOP_INIT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[OK] Appended '{snake}' entries to __all__")


# ============================================================
# CLI / Entry point
# ============================================================


def main() -> None:
    """
    Minimal CLI: expects exactly one argument - the feature name.
    """
    if len(sys.argv) != 2:
        print("Usage: python startparser.py <feature_name>")
        raise SystemExit(1)

    raw_name = sys.argv[1]
    snake = validate_feature_name(raw_name)

    if not PARSERS_ROOT.exists():
        raise SystemExit(f"'parsers' package not found at: {PARSERS_ROOT}")
    if not FEATURES_DIR.exists():
        raise SystemExit(f"'features' directory not found at: {FEATURES_DIR}")
    if not TOP_INIT.exists():
        raise SystemExit(f"'__init__.py' not found at: {TOP_INIT}")

    create_feature_structure(snake)
    update_top_level_init(snake)


if __name__ == "__main__":
    main()

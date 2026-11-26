"""Offline inventory/eligibility. Metadata describes effects; CMDOP grants authorize calls."""

import json
from pathlib import Path
import re
from typing import Mapping


class CatalogError(ValueError):
    pass


FLAGS = {"exec": "EXAMPLES_EXEC", "agent": "AGENT_PROMPT", "write": "EXAMPLES_WRITE",
         "destructive": "EXAMPLES_DESTRUCTIVE", "network": "EXAMPLES_NETWORK",
         "screen": "EXAMPLES_SCREEN", "control": "EXAMPLES_CONTROL"}


def load(root: Path) -> dict:
    data = json.loads((root / "catalog.json").read_text())
    if data.get("schema") != 1 or not re.fullmatch(r"\d+\.\d+\.\d+", data.get("sdkVersion", "")):
        raise CatalogError("invalid_catalog_header")
    entries = data.get("examples")
    if not isinstance(entries, list) or not entries:
        raise CatalogError("empty_inventory")
    seen = set()
    for row in entries:
        name = row.get("id", "")
        if not re.fullmatch(r"[a-z][a-z0-9-]*", name) or name in seen:
            raise CatalogError("invalid_or_duplicate_id")
        seen.add(name)
        if not isinstance(row.get("title"), str) or not row["title"].strip() or len(row["title"]) > 120:
            raise CatalogError("invalid_title")
        for lang, suffix in (("python", ".py"), ("typescript", ".ts")):
            file = Path(row.get(lang, ""))
            try:
                (root / file).resolve().relative_to(root.resolve())
                (root / file).resolve().relative_to((root / lang).resolve())
            except ValueError:
                raise CatalogError("unsafe_source_path") from None
            if file.is_absolute() or file.suffix != suffix or not (root / file).is_file():
                raise CatalogError("missing_language_source")
        effects = row.get("effects")
        if not isinstance(effects, list) or not effects or len(set(effects)) != len(effects):
            raise CatalogError("invalid_effects")
        if set(effects) - {"read", *FLAGS}:
            raise CatalogError("unknown_effect")
        if type(row.get("default")) is not bool or type(row.get("requiresMachine")) is not bool:
            raise CatalogError("invalid_execution_policy")
        if set(effects) - {"read"} and (row["default"] or not row["requiresMachine"]):
            raise CatalogError("effectful_example_needs_explicit_selection_and_target")
        if row.get("assertion") not in ("smoke", "outcome"):
            raise CatalogError("invalid_assertion_kind")
        if not re.fullmatch(r"/(reference/sdk(?:/examples)?|guides/use-cases)/[a-z0-9-]+", row.get("docsRoute", "")):
            raise CatalogError("invalid_docs_route")
        if row.get("agentId") and "agent" not in effects:
            raise CatalogError("agent_example_missing_effect")
    return data


def select(data: dict, only: str | None, env: Mapping[str, str]) -> list[dict]:
    entries = data["examples"]
    if only is None or only == "":
        chosen = [row for row in entries if row["default"]]
    else:
        names = [name.strip() for name in only.split(",")]
        by_id = {row["id"]: row for row in entries}
        if any(not name or name not in by_id for name in names) or len(set(names)) != len(names):
            raise CatalogError("unknown_empty_or_duplicate_selection")
        chosen = [by_id[name] for name in names]
    if not chosen:
        raise CatalogError("no_examples_selected")
    # Eligibility follows selection, including ONLY. Selecting a name never grants an effect.
    for row in chosen:
        for effect in row["effects"]:
            if effect != "read" and env.get(FLAGS[effect]) != "1":
                raise CatalogError(f"opt_in_required: {row['id']} needs {FLAGS[effect]}=1")
        if row["requiresMachine"] and not env.get("CMDOP_MACHINE", "").strip():
            raise CatalogError("explicit_machine_id_required")
    return chosen


def public_index(data: dict) -> str:
    lines = ["# SDK examples", "", "Generated from `examples/catalog.json`; edit the inventory, not this index.",
             "", "[Setup and execution guide](../docs/examples/run.md).",
             "Source availability does not establish live integration verification.", "",
             "| Example | Python | TypeScript | Access | Local check |", "|---|---|---|---|---|"]
    for row in data["examples"]:
        title = row["title"].replace("|", "\\|").replace("\n", " ")
        route = row["docsRoute"]
        guide = "../docs/" + route.removeprefix("/reference/sdk/") + ".md" if route.startswith("/reference/sdk/") else "https://docs.cmdop.ai" + route
        lines.append(f"| [{title}]({guide}) | [{row['id']}.py]({row['python']}) | [{row['id']}.ts]({row['typescript']}) | "
                     + ", ".join(f"`{effect}`" for effect in row["effects"]) + f" | {row['assertion']} |")
    return "\n".join(lines) + "\n"

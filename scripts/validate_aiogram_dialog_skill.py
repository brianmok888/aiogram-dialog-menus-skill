#!/usr/bin/env python3
"""Validate aiogram-dialog skill docs against known upstream-sensitive checks.

The local checks are dependency-free. If AIOGRAM_DIALOG_SRC points at a local
Tishka17/aiogram_dialog checkout, this also verifies key signatures/enums from
that source tree with the Python stdlib ast module.
"""
from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILURES: list[str] = []


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def check(condition: bool, message: str) -> None:
    if not condition:
        FAILURES.append(message)


def find_class(tree: ast.AST, class_name: str) -> ast.ClassDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    raise AssertionError(f"class {class_name} not found")


def class_init_args(source_path: Path, class_name: str) -> list[str]:
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    cls = find_class(tree, class_name)
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            return [arg.arg for arg in node.args.args + node.args.kwonlyargs]
    dataclass_fields = [
        node.target.id
        for node in cls.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    ]
    if dataclass_fields:
        return ["self", *dataclass_fields]
    raise AssertionError(f"{class_name}.__init__ not found")


def enum_assignments(source_path: Path, class_name: str) -> set[str]:
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    cls = find_class(tree, class_name)
    names: set[str] = set()
    for node in cls.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def local_checks() -> None:
    readme = read("README.md")
    agents = read("AGENTS.md")
    skill = read("SKILL.md")
    combined = "\n".join([readme, agents, skill])

    check("Python 3.9" not in combined and "Python ≥3.9" not in combined,
          "Python prerequisite must be 3.10+, not 3.9+")
    check("github.com/mok888/aiogram-dialog-menus-skill" not in combined
          and "raw.githubusercontent.com/mok888/aiogram-dialog-menus-skill" not in combined,
          "installation URLs must use brianmok888/aiogram-dialog-menus-skill")
    check('pip install "aiogram>=3.14.0" "aiogram-dialog>=2.6.0"' in skill,
          "pip install command should quote version constraints")
    check("https://aiogram-dialog.readthedocs.io/en/stable/" in combined,
          "documentation links should target the stable docs URL")

    check("ShowMode.SEND_AND_EDIT" not in skill,
          "ShowMode.SEND_AND_EDIT is not an upstream enum value")
    check("CalendarScope" not in skill and "scopes=" not in skill,
          "CalendarConfig example must not use CalendarScope/scopes")
    check("min_date=date(" in skill and "max_date=date(" in skill,
          "CalendarConfig example should use datetime.date values")
    example_sections = skill[:skill.find("## Common Mistakes")]
    check(not re.search(r"Const\([\"'][^\"']*\{item", example_sections),
          "dynamic item labels must use Format(...), not Const(...)")

    check('Progress(\n    "progress"' in skill,
          "Progress example must pass the data field name as the first argument")
    check("id=\"progress\"" not in skill,
          "Progress example must not use an id= parameter")

    check('DynamicMedia("media")' in skill,
          "DynamicMedia example should use selector-based API")
    check("getter=media_getter" not in skill and "type=ContentType.PHOTO,\n    getter=" not in skill,
          "DynamicMedia example must not use removed type/getter parameters")
    check('MediaScroll(\n    DynamicMedia("item")' in skill,
          "MediaScroll example must pass a nested Media widget")
    check("item_id_getter=lambda" not in skill[skill.find("#### MediaScroll"):skill.find("## Data Flow")],
          "MediaScroll example must not use item_id_getter")

    check("await dialog_manager.bg" not in skill,
          "DialogManager.bg() is synchronous and must not be awaited")
    check("bg_manager = dialog_manager.bg(" in skill,
          "background manager example should show synchronous DialogManager.bg()")
    check("bg_factory.bg(bot=bot" in skill,
          "background manager example should show factory form requiring bot=")

    check("reply-keyboard request buttons" in skill,
          "RequestContact/Location/Poll should be documented as reply-keyboard buttons")
    check("All API signatures checked" not in agents,
          "AGENTS.md must not overclaim all signatures are currently checked")
    check("Source-verified gotchas" not in readme,
          "README should avoid overclaiming source verification without a validation run")
    check("scripts/validate_aiogram_dialog_skill.py" in readme + agents,
          "README and AGENTS should mention the validation harness")


def upstream_checks(upstream_root: Path) -> None:
    src = upstream_root / "src" / "aiogram_dialog"
    check(src.exists(), f"AIOGRAM_DIALOG_SRC does not look like an upstream checkout: {upstream_root}")
    if not src.exists():
        return

    pyproject = upstream_root / "pyproject.toml"
    check('requires-python = ">=3.10"' in pyproject.read_text(encoding="utf-8"),
          "upstream Python requirement changed; update docs/checks")

    show_modes = enum_assignments(src / "api/entities/modes.py", "ShowMode")
    check(show_modes == {"AUTO", "EDIT", "SEND", "DELETE_AND_SEND", "NO_UPDATE"},
          f"unexpected upstream ShowMode values: {sorted(show_modes)}")

    calendar_args = class_init_args(src / "widgets/kbd/calendar_kbd.py", "CalendarConfig")
    check("scopes" not in calendar_args and {"min_date", "max_date"}.issubset(calendar_args),
          f"unexpected CalendarConfig args: {calendar_args}")

    progress_args = class_init_args(src / "widgets/text/progress.py", "Progress")
    check(progress_args[:2] == ["self", "field"] and "id" not in progress_args,
          f"unexpected Progress args: {progress_args}")

    dynamic_args = class_init_args(src / "widgets/media/dynamic.py", "DynamicMedia")
    check(dynamic_args[:2] == ["self", "selector"] and "getter" not in dynamic_args,
          f"unexpected DynamicMedia args: {dynamic_args}")

    media_scroll_args = class_init_args(src / "widgets/media/scroll.py", "MediaScroll")
    check(media_scroll_args[:4] == ["self", "media", "items", "id"] and "item_id_getter" not in media_scroll_args,
          f"unexpected MediaScroll args: {media_scroll_args}")

    manager_tree = ast.parse((src / "manager/manager.py").read_text(encoding="utf-8"))
    async_bg = [node for node in ast.walk(manager_tree) if isinstance(node, ast.AsyncFunctionDef) and node.name == "bg"]
    sync_bg = [node for node in ast.walk(manager_tree) if isinstance(node, ast.FunctionDef) and node.name == "bg"]
    check(not async_bg and sync_bg, "DialogManager.bg() should be synchronous in upstream source")


def main() -> int:
    local_checks()
    upstream = os.environ.get("AIOGRAM_DIALOG_SRC")
    if upstream:
        upstream_checks(Path(upstream).resolve())
    else:
        print("AIOGRAM_DIALOG_SRC not set; skipped optional upstream source checks")

    if FAILURES:
        print("Validation failed:", file=sys.stderr)
        for failure in FAILURES:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("aiogram-dialog skill validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

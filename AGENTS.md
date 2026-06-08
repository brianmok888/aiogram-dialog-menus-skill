# AIODIALOG-MENUS SKILL KNOWLEDGE BASE

**Maintained:** 2026-06-08
**Type:** AI Coding Agent Skill (OpenCode, Claude, Codex, etc.)

## OVERVIEW
Reference skill for building interactive Telegram bot menus using `aiogram_dialog` (v2.x, latest 2.6.0). Dialog > Windows > Widgets architecture with Python async patterns, link previews, and stack-aware interaction guidance.

## STRUCTURE
```
aiogram-dialog-menus/
├── SKILL.md    # Complete reference (~1250 lines, 35+ widget types)
├── AGENTS.md   # This file — agent navigation guide
├── README.md   # Installation + usage for humans
└── scripts/    # Dependency-free validation checks for source drift
```

## WHERE TO LOOK
| Task | SKILL.md Section | Notes |
|------|-----------------|-------|
| Setup | "Quick Start" | `setup_dialogs(dp)`, handler registration |
| Buttons | "Button" | Basic click handler, `on_click` signature |
| Navigation | "Navigation Widgets" | SwitchTo, Next, Back, Cancel, Start |
| URL buttons | "URL & Special Buttons" | Url, WebApp, LoginURLButton, SwitchInlineQuery* |
| Selection | "Select/Multiselect/Radio/Toggle/Checkbox" | item_id_getter, on_click, on_state_changed |
| Calendar | "Calendar" | Calendar, CalendarConfig, ManagedCalendar |
| Counter | "Counter" | +/- number input, on_text_click, ManagedCounter |
| Lists | "ListGroup" / "ScrollingGroup" | Dynamic button lists, paginated scrolling |
| Pager controls | "Pager Widgets" | NumberedPager, PrevPage, NextPage, CurrentPage |
| Request buttons | "Request Buttons" | RequestContact, RequestLocation, RequestPoll |
| CopyText | "CopyText" | Copy-to-clipboard button |
| Layout | "Layout Widgets" | Row, Column, Group |
| Text content | "Text Widgets" | Const, Format, Multi, Case, Progress, List, Jinja |
| Media | "Media Widgets" | StaticMedia, DynamicMedia, MediaScroll |
| Link previews | "Link Preview Widgets" | LinkPreview configuration and preview disabling |
| Input handling | "Input Widgets" | TextInput, MessageInput |
| Data flow | "Getters" / "dialog_data" / "start_data" | getter returns dict, dialog_data dict access |
| Navigation modes | "Launch Modes" | StartMode, LaunchMode, ShowMode |
| Visibility | "Hiding Widgets with `when`" | data-key, predicate, and magic_filter visibility |
| Group/business chats | "Groups and Business Chats" | GROUP_STACK_ID, AccessSettings, thread/business caveats |
| Background tasks | "Background Manager" | BgManagerFactory, bg(), fg() |
| Widget state | "Managed Widgets" | manager.find(), Managed* variants |
| Error handling | "Error Handling" | UnknownIntent, UnknownState, ExceptionTypeFilter |
| Migration | "Migration from v1 to v2" | Registry→setup_dialogs, Adapter rename |

## CONVENTIONS
- **Stack**: Python ≥3.10, aiogram ≥3.14, aiogram-dialog v2.x (latest 2.6.0)
- **Data access**: `dialog_data["key"]` dict-style (NOT `dialog_data.key` attribute access)
- **Getters**: Must return `dict` — never `None`, never fail silently
- **Navigation**: Use dedicated widgets (SwitchTo/Next/Back/Cancel/Start) over custom `on_click`
- **Widget IDs**: Always set unique `id` for stateful widgets; exceptions: CopyText, RequestContact/Location/Poll (no `id`)
- **Widget ID charset**: ASCII letters, numbers, underscore, and dot only
- **URL params**: `url` param on Url/WebApp/LoginURLButton takes `Text` widget, not plain string — use `Const("...")`
- **Error handling**: Register `UnknownIntent`+`UnknownState` via `dp.errors.register()` with `ExceptionTypeFilter`

## ANTI-PATTERNS (THIS SKILL)
| Pattern | Fix |
|---------|-----|
| `dialog_data.key = value` (attribute) | `dialog_data["key"] = value` (dict) |
| `Url(text, url="string")` (plain string) | `Url(text, url=Const("string"))` (Text widget) |
| `Counter(on_text_change=...)` | `Counter(on_text_click=...)` — correct param name |
| `CopyText(text, id="x", copy_text="y")` | `CopyText(text, copy_text=Const("y"))` — no `id` |
| `RequestContact(text, id="x")` | `RequestContact(text)` — no `id` param |
| `Const("{item}")` for dynamic item labels | `Format("{item}")` |
| `Progress(id="progress")` | `Progress("progress")` — field name, not widget id |
| `await dialog_manager.bg(...)` | `dialog_manager.bg(...)` — synchronous manager method |
| `bg_manager.dialog_data[...]` | `await bg_manager.update(data={...})`, or use `async with bg_manager.fg()` |
| `DynamicMedia(type=..., getter=...)` | `DynamicMedia("media")` — selector-based API |
| `MediaScroll(items=..., item_id_getter=...)` | `MediaScroll(DynamicMedia("item"), items=..., id=...)` |
| `Window(..., disable_web_page_preview=...)` | `LinkPreview(is_disabled=True)` |
| Getter returns `None` | Return `{}` |
| Custom `on_click` for navigation | Use SwitchTo/Next/Back/Cancel/Start |
| `Registry` class | `setup_dialogs(dp)` (removed in 2.0b18) |
| `reset_stack=True` | `mode=StartMode.RESET_STACK` |
| `*Adapter` suffix on managed widgets | Simplified: ManagedCalendar, ManagedCheckbox, etc. |

## UNIQUE STYLES
- **Monolithic skill file**: All content in single SKILL.md (~1250 lines)
- **Example-driven**: Heavy code snippets, minimal prose
- **Complete widget index**: Exhaustive table of 35+ widgets at end of file
- **Source-aligned**: Keep API examples checked against Tishka17/aiogram_dialog source code; run `python3 scripts/validate_aiogram_dialog_skill.py` before release

## COMMANDS
```bash
pip install "aiogram>=3.14.0" "aiogram-dialog>=2.6.0"
python3 scripts/validate_aiogram_dialog_skill.py
```

## NOTES
- External docs: https://aiogram-dialog.readthedocs.io/en/stable/
- GitHub: Tishka17/aiogram_dialog
- `setup_dialogs(dp)` must be called AFTER `dp.include_router(dialog)`
- `StartMode.RESET_STACK` for main menu entry; `NORMAL` for sub-dialogs
- `dialog_data` is `DataDict` (plain dict) — always dict-style access
- `UnknownIntent`/`UnknownState` imported from `aiogram_dialog.api.exceptions`

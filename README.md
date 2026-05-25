# aiogram-dialog-menus

AI coding assistant skill for building interactive Telegram bot menus using `aiogram_dialog` v2.x (latest: 2.6.0). Compatible with OpenCode, Claude, Codex, and other AI coding agents.

## What This Does

Provides expert knowledge for creating:
- Multi-step wizards (registration, booking, configuration)
- Menu systems with nested options
- Polls and surveys with interactive selection
- Admin panels with toggleable settings
- Calendar/date pickers
- Media galleries with scrolling
- Paginated item lists
- Any complex stateful user interaction

## Installation

### OpenCode

Ask your AI agent:

```
Install the aiogram-dialog-menus skill from https://github.com/brianmok888/aiogram-dialog-menus-skill into ~/.config/opencode/skills/
```

### Claude CLI

Add to your global instructions:

```bash
# Create user-level CLAUDE.md if it doesn't exist
mkdir -p ~/.claude

# Append skill content to your global instructions
curl -sL https://raw.githubusercontent.com/brianmok888/aiogram-dialog-menus-skill/main/SKILL.md >> ~/.claude/CLAUDE.md
```

Or for project-specific use, copy `SKILL.md` content to your project's `CLAUDE.md`:
```bash
# Project-level (committed to git)
curl -sL https://raw.githubusercontent.com/brianmok888/aiogram-dialog-menus-skill/main/SKILL.md >> ./CLAUDE.md
```

### Codex CLI

Add to your global instructions:

```bash
# Create Codex home directory if it doesn't exist
mkdir -p ~/.codex

# Append skill content to your global AGENTS.md
curl -sL https://raw.githubusercontent.com/brianmok888/aiogram-dialog-menus-skill/main/SKILL.md >> ~/.codex/AGENTS.md
```

Or for project-specific use:
```bash
# Project-level AGENTS.md (Codex auto-discovers this)
curl -sL https://raw.githubusercontent.com/brianmok888/aiogram-dialog-menus-skill/main/SKILL.md >> ./AGENTS.md
```

### Manual

Clone or download this repo to your agent's skills directory:

```bash
git clone https://github.com/brianmok888/aiogram-dialog-menus-skill
```

## Usage

Once installed, the skill activates automatically when:
- Building Telegram bot menus
- Implementing dialog flows
- Creating interactive bot interfaces
- Working with aiogram_dialog widgets

### Example Prompts

```
"Create a registration wizard for my Telegram bot with 3 steps"
"Build a settings menu with toggles using aiogram_dialog"
"Add a language selector to my bot menu"
"Implement an admin panel with multiselect options"
"Create a calendar date picker for booking"
"Build a paginated product list with scrolling"
```

## Prerequisites

- Python 3.10+
- aiogram ≥3.14
- aiogram-dialog v2.x (latest: 2.6.0)

```bash
pip install "aiogram>=3.14.0" "aiogram-dialog>=2.6.0"
```

## Coverage

| Topic | Description |
|-------|-------------|
| **Core concepts** | Dialog > Windows > Widgets architecture, key components |
| **Setup** | `setup_dialogs()`, handler registration, Dialog/Window/StatesGroup |
| **Buttons** | Button, SwitchTo, Next, Back, Cancel, Start |
| **URL & special** | Url, WebApp, LoginURLButton, SwitchInlineQuery*, CopyText |
| **Request buttons** | RequestContact, RequestLocation, RequestPoll |
| **Selection** | Select, Multiselect, Radio, Toggle, Checkbox |
| **Calendar** | Calendar, CalendarConfig, ManagedCalendar |
| **Counter** | Counter, ManagedCounter (+/- with cycle, min/max) |
| **Lists & scrolling** | ListGroup, ScrollingGroup, StubScroll |
| **Pager controls** | NumberedPager, PrevPage, NextPage, CurrentPage, SwitchPage |
| **Layout** | Row, Column, Group (width-based wrapping) |
| **Text widgets** | Const, Format, Multi, Case, Progress, List, Jinja, ScrollingText |
| **Media** | StaticMedia, DynamicMedia, MediaScroll |
| **Input** | TextInput (type_factory, on_success/on_error), MessageInput |
| **Data flow** | Getters (dict return), dialog_data (dict access), start_data |
| **Launch modes** | StartMode, LaunchMode, ShowMode |
| **Background** | BgManagerFactory, bg(), fg() context manager |
| **Managed widgets** | `manager.find()` → Managed* variants |
| **Error handling** | UnknownIntent/UnknownState via ExceptionTypeFilter |
| **Patterns** | Main Menu, Wizard, Admin Panel, Paginated List |
| **Best practices** | Widget IDs, getter performance, exception handling |
| **Common mistakes** | Source-aligned gotchas and corrections |
| **Migration** | v1 → v2 breaking changes |
| **Widget index** | Complete table of 35+ widgets with purposes and managed variants |

## Validation

Run the dependency-free drift checks before publishing updates:

```bash
python3 scripts/validate_aiogram_dialog_skill.py
```

For source-signature checks against a local upstream checkout:

```bash
AIOGRAM_DIALOG_SRC=/path/to/aiogram_dialog python3 scripts/validate_aiogram_dialog_skill.py
```

## Resources

- [Official Docs](https://aiogram-dialog.readthedocs.io/en/stable/)
- [GitHub](https://github.com/Tishka17/aiogram_dialog)
- [Examples](https://github.com/Tishka17/aiogram_dialog/tree/develop/example)

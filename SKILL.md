---
name: aiogram-dialog-menus
description: Use when building interactive Telegram bot menus using aiogram_dialog library - creating dialogs with windows, buttons, selectors, and state management for Telegram bots
---

# aiogram_dialog Menu Building Skill

Expert knowledge for building interactive Telegram bot menus using the `aiogram_dialog` library (v2.x, latest 2.6.0).

## When to Use This Skill

**Use for:**
- Multi-step wizards (registration, booking, configuration)
- Menu systems with nested options
- Polls and surveys with interactive selection
- Admin panels with toggleable settings
- Calendar/date pickers in bots
- Media display with scrolling
- Any complex stateful user interaction

**Don't use for:**
- Simple one-off replies (use plain `message.answer()`)
- Complex FSM logic that doesn't fit dialog pattern

## Prerequisites

```bash
pip install aiogram>=3.14 aiogram-dialog>=2.0
```

- Python 3.9+
- aiogram 3.14+
- aiogram-dialog 2.x (latest: 2.6.0)

## Core Concepts

### Architecture: Dialog > Windows > Widgets

```
Dialog (manages state + navigation)
  └── Windows (individual screens)
        ├── Text widgets (message content)
        ├── Keyboard widgets (inline buttons)
        ├── Media widgets (photos, videos, documents)
        └── Input widgets (text/message handlers)
```

### Key Components

1. **StatesGroup** - Define dialog states
2. **Dialog** - Container for windows
3. **Window** - Single screen with widgets
4. **Widgets** - Buttons, selectors, inputs, media, text
5. **Getters** - Async functions providing data to windows
6. **Managed Widgets** - Access widget state via `manager.find("widget_id")`

## Quick Start

### 1. Setup

```python
from aiogram import Dispatcher
from aiogram_dialog import DialogManager, setup_dialogs

dp = Dispatcher()
setup_dialogs(dp)  # Required once at startup
```

### 2. Define States

```python
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram.fsm.state import StatesGroup, State

class MainMenu(StatesGroup):
    main = State()
    settings = State()
    profile = State()
```

### 3. Create Window with Button

```python
from aiogram_dialog import StartMode

async def on_settings_click(callback, button, manager: DialogManager):
    await manager.switch_to(MainMenu.settings)

main_window = Window(
    Const("Welcome to the bot!"),
    Button(Const("⚙️ Settings"), id="settings_btn", on_click=on_settings_click),
    state=MainMenu.main,
)
```

### 4. Create Dialog and Register

```python
dialog = Dialog(main_window)
dp.include_router(dialog)
```

### 5. Start Dialog

```python
from aiogram_dialog import StartMode

async def start_handler(message, dialog_manager: DialogManager):
    await dialog_manager.start(MainMenu.main, mode=StartMode.RESET_STACK)
```

## Widget Reference

### Keyboard Widgets

All keyboard widgets are in `aiogram_dialog.widgets.kbd`.

#### Button

```python
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

# Basic button
Button(Const("Click me"), id="btn1", on_click=my_handler)

# Switch to another window (use SwitchTo widget instead)
from aiogram_dialog.widgets.kbd import SwitchTo
SwitchTo(Const("Go to settings"), id="to_settings", state=MainMenu.settings)
```

#### Navigation Widgets (SwitchTo, Next, Back, Cancel, Start)

Dedicated widgets for common navigation patterns. No need to write custom `on_click` handlers.

```python
from aiogram_dialog.widgets.kbd import SwitchTo, Next, Back, Cancel, Start

# Switch to a specific window state
SwitchTo(Const("⚙️ Settings"), id="to_settings", state=MainMenu.settings)

# Go to next/previous window in dialog
Next(Const("Next →"))
Back(Const("← Back"))

# Close the dialog (calls manager.done())
Cancel(Const("❌ Cancel"))

# Start a new dialog (with mode and data)
Start(
    Const("📋 Open Wizard"),
    id="start_wizard",
    state=Wizard.name,
    mode=StartMode.NORMAL,
    data={"prefill": "value"},
)
```

All navigation widgets accept optional `on_click` and `show_mode` parameters.

#### Select (Single Choice)

```python
from aiogram_dialog.widgets.kbd import Select

async def get_items(**kwargs):
    return {"items": ["Option A", "Option B", "Option C"]}

async def on_item_selected(callback, select, manager: DialogManager, item_id: str):
    await callback.answer(f"Selected: {item_id}")

Select(
    Const("{item}"),  # Text template
    id="item_select",
    item_id_getter=lambda x: x,  # Extract ID from item
    items="items",  # Key in getter data
    on_click=on_item_selected,
)
```

#### Multiselect

```python
from aiogram_dialog.widgets.kbd import Multiselect

async def get_options(**kwargs):
    return {
        "options": [
            {"id": "opt1", "name": "Option 1"},
            {"id": "opt2", "name": "Option 2"},
        ]
    }

Multiselect(
    Const("✓ {item[name]}"),  # Checked format
    Const("  {item[name]}"),  # Unchecked format
    id="multi_select",
    item_id_getter=lambda x: x["id"],
    items="options",
)
```

#### Radio

```python
from aiogram_dialog.widgets.kbd import Radio

Radio(
    Const("◉ {item}"),  # Selected
    Const("○ {item}"),  # Unselected
    id="radio_group",
    item_id_getter=lambda x: x,
    items="choices",
)
```

#### Toggle

```python
from aiogram_dialog.widgets.kbd import Toggle

# Simpler than Radio — toggles between elements when clicked
Toggle(
    Const("{item}"),
    id="theme_toggle",
    items=["light", "dark"],
    item_id_getter=lambda x: x,
)
```

#### Checkbox

```python
from aiogram_dialog.widgets.kbd import Checkbox

Checkbox(
    Const("✓ Enabled"),
    Const("○ Disabled"),
    id="feature_toggle",
    default=False,
)
```

#### Calendar

```python
from aiogram_dialog.widgets.kbd import Calendar, CalendarConfig, CalendarScope

# Basic calendar
Calendar(id="calendar", on_click=on_date_selected)

# With configuration
Calendar(
    id="calendar",
    config=CalendarConfig(
        min_date=datetime(2024, 1, 1),
        max_date=datetime(2026, 12, 31),
        scopes=[CalendarScope.DAYS, CalendarScope.MONTHS, CalendarScope.YEARS],
    ),
    on_click=on_date_selected,
)

async def on_date_selected(callback, widget, manager: DialogManager, selected_date: date):
    manager.dialog_data["selected_date"] = selected_date.isoformat()
    await manager.next()

# Access calendar state programmatically
managed = manager.find("calendar")  # Returns ManagedCalendar
```

#### TimeSelect

```python
from datetime import time
from aiogram_dialog.widgets.kbd import TimeSelect

TimeSelect(
    id="time_picker",
    hour_width=6,           # Number of columns for hour grid
    minute_width=6,         # Number of columns for minute grid
    minute_precision=5,     # Minute step (1, 5, 10, 15, 30)
    on_value_changed=on_time_changed,
)

async def on_time_changed(callback, widget, manager: DialogManager, value: time):
    manager.dialog_data["selected_time"] = value.isoformat()

# Access time state programmatically
managed = manager.find("time_picker")  # Returns ManagedTimeSelect
current = managed.get_value()           # Returns time | None
await managed.set_value(time(14, 30))   # Set programmatically
```

#### Counter

```python
from aiogram_dialog.widgets.kbd import Counter

Counter(
    id="quantity",
    plus=Const("+"),       # Optional: custom + button text
    minus=Const("-"),      # Optional: custom - button text
    text=Format("{value}"),  # Optional: center text format
    min_value=1,
    max_value=99,
    increment=1,
    default=1,
    cycle=False,           # Wrap around at min/max
    on_click=on_counter_click,
    on_text_click=on_text_click,
)
```

#### ListGroup

```python
from aiogram_dialog.widgets.kbd import ListGroup

# Render a dynamic list of button groups, one per item
ListGroup(
    Button(Format("{item[name]}"), id="item_btn", on_click=on_item_click),
    id="items_list",
    items="items",          # Key in getter data
    item_id_getter=lambda x: x["id"],
)
```

#### ScrollingGroup

```python
from aiogram_dialog.widgets.kbd import ScrollingGroup

ScrollingGroup(
    Select(
        Const("{item}"),
        id="scroll_select",
        item_id_getter=lambda x: x,
        items="long_list",
    ),
    id="scroll_group",
    width=1,
    height=5,  # Show 5 items at a time
)
```

#### Pager Widgets

Pagination controls for `ScrollingGroup` and other scrollable widgets.

```python
from aiogram_dialog.widgets.kbd import (
    ScrollingGroup, PrevPage, NextPage, FirstPage, LastPage,
    CurrentPage, NumberedPager,
)

# Manual pager buttons
Row(
    FirstPage(scroll="scroll_group", id="first"),
    PrevPage(scroll="scroll_group", id="prev"),
    CurrentPage(scroll="scroll_group", id="current"),
    NextPage(scroll="scroll_group", id="next"),
    LastPage(scroll="scroll_group", id="last"),
)

# Numbered page buttons
NumberedPager(scroll="scroll_group", id="pager")

# Jump to a specific page (e.g., page 2)
from aiogram_dialog.widgets.kbd import SwitchPage

SwitchPage(
    text=Const("Go to Page 2"),
    page=2,
    scroll="scroll_group",
    id="switch_p2",
)
```

#### URL & Special Buttons

```python
from aiogram_dialog.widgets.kbd import (
    Url, WebApp, LoginURLButton,
    SwitchInlineQuery, SwitchInlineQueryCurrentChat,
    SwitchInlineQueryChosenChatButton,
)

# Open URL in browser (url param is a Text widget)
Url(Const("🌐 Website"), url=Const("https://example.com"))

# Open Web App
WebApp(Const("📱 App"), url=Const("https://app.example.com"))

# Login URL for authorization
LoginURLButton(
    Const("🔐 Login"),
    url=Const("https://example.com/auth"),
)

# Switch inline query (query param is a Text widget)
SwitchInlineQuery(Const("🔍 Search"), switch_inline_query=Const("search "))
SwitchInlineQueryCurrentChat(Const("🔎 Here"), switch_inline_query_current_chat=Const("search "))
SwitchInlineQueryChosenChatButton(Const("💬 Choose Chat"), query=Const("search "))
```

#### Request Buttons

These create inline keyboard buttons. No `id` parameter.

```python
from aiogram_dialog.widgets.kbd import RequestContact, RequestLocation, RequestPoll

RequestContact(Const("📱 Share Phone"))
RequestLocation(Const("📍 Share Location"))
RequestPoll(Const("📊 Create Poll"))  # Optional: poll_type="regular" or "quiz"
```

#### CopyText

```python
from aiogram_dialog.widgets.kbd import CopyText

# Note: No `id` parameter — text and copy_text are both Text widgets
CopyText(
    text=Const("📋 Copy Code"),
    copy_text=Const("PROMO-2024"),
)
```

### Layout Widgets

```python
from aiogram_dialog.widgets.kbd import Row, Column, Group

# Horizontal layout
Row(
    Button(Const("A"), id="a"),
    Button(Const("B"), id="b"),
    Button(Const("C"), id="c"),
)

# Vertical layout
Column(
    Button(Const("1"), id="1"),
    Button(Const("2"), id="2"),
)

# Group with width (N buttons per row)
Group(
    Button(Const("1"), id="1"),
    Button(Const("2"), id="2"),
    Button(Const("3"), id="3"),
    Button(Const("4"), id="4"),
    width=2,  # 2 buttons per row
)
```

### Text Widgets

All text widgets are in `aiogram_dialog.widgets.text`. These control the message body content.

#### Const

```python
from aiogram_dialog.widgets.text import Const

Const("Static text content")
```

#### Format

```python
from aiogram_dialog.widgets.text import Format

# String formatting with getter data
Format("Hello, {name}! Balance: {balance}")
```

#### Multi

```python
from aiogram_dialog.widgets.text import Multi

# Concatenate multiple text widgets
Multi(
    Const("📄 Title\n"),
    Format("Name: {name}\n"),
    Format("Balance: {balance}"),
)
```

#### Case

```python
from aiogram_dialog.widgets.text import Case

# Show different text based on a condition
Case(
    {
        "admin": Const("🔐 Admin Panel"),
        "user": Format("👤 Hello, {name}"),
        "guest": Const("👋 Welcome, please /start"),
    },
    selector=lambda data, manager: data.get("role", "guest"),
)
```

#### Progress

```python
from aiogram_dialog.widgets.text import Progress

# Visual progress bar
Progress(
    id="progress",          # or pass a Counter widget
    width=10,               # bar width in characters
    filled="█",
    empty="░",
)
```

#### List

```python
from aiogram_dialog.widgets.text import List

# Render a list of items as text
List(
    Format("• {item}"),
    items="items",  # Key in getter data
    sep="\n",
)

# Scrollable text list with pagination
List(
    Format("{pos}. {item[name]}"),
    items="products",
    id="product_list",   # Required for scrolling
    page_size=10,        # Items per page
)
```

#### Jinja

```python
from aiogram_dialog.widgets.text import Jinja

# Jinja2 templating for complex formatting
Jinja("""
{% for item in items %}
{{ loop.index }}. {{ item.name }} - {{ item.price }}$
{% endfor %}
Total: {{ total }}$
""")
```

#### ScrollingText

```python
from aiogram_dialog.widgets.text import ScrollingText

# Paginate long text content (e.g., terms of service, logs)
ScrollingText(
    text=Format("{long_text}"),
    id="scrolling_text",
    page_size=500,  # Characters per page (0 = auto)
)
```

### Input Widgets

Input widgets are in `aiogram_dialog.widgets.input`.

#### TextInput

```python
from aiogram_dialog.widgets.input import TextInput

async def on_name_success(message, widget, manager: DialogManager, value: str):
    manager.dialog_data["name"] = value
    await manager.next()

async def on_name_error(message, widget, manager: DialogManager, error: ValueError):
    await message.answer(f"Invalid input: {error}")

TextInput(
    id="name_input",
    type_factory=str,       # Conversion function (int, float, etc.)
    on_success=on_name_success,
    on_error=on_name_error,  # Optional: handle conversion errors
)
```

#### MessageInput

```python
from aiogram_dialog.widgets.input import MessageInput

# Catch raw Message objects (for photos, documents, etc.)
async def on_photo(message, widget, manager: DialogManager):
    photo = message.photo[-1]
    manager.dialog_data["photo_id"] = photo.file_id
    await manager.next()

MessageInput(id="photo_input", func=on_photo)
```

### Media Widgets

Media widgets are in `aiogram_dialog.widgets.media`. Attach media content to windows.

#### StaticMedia

```python
from aiogram_dialog.widgets.media import StaticMedia

StaticMedia(
    path=Const("images/logo.png"),  # File path or URL
    type=ContentType.PHOTO,         # PHOTO, VIDEO, DOCUMENT
)
```

#### DynamicMedia

```python
from aiogram_dialog.widgets.media import DynamicMedia

# Media determined by getter data
async def media_getter(dialog_manager: DialogManager, **kwargs):
    return {"media": InputFile("dynamic.png")}

DynamicMedia(
    type=ContentType.PHOTO,
    getter=media_getter,
)
```

#### MediaScroll

```python
from aiogram_dialog.widgets.media import MediaScroll

# Scrollable media gallery
MediaScroll(
    id="gallery",
    items="photos",    # Key in getter data
    item_id_getter=lambda x: x["file_id"],
)
```

## Data Flow

### Getters (Window Data Provider)

```python
async def user_getter(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    user = await get_user(user_id)
    return {
        "username": user.name,
        "balance": user.balance,
        "level": user.level,
    }

profile_window = Window(
    Format("👤 Profile\n\nName: {username}\nBalance: {balance}"),
    getter=user_getter,  # Attach getter
    state=Profile.view,
)
```

### dialog_data (Persistent State Within Dialog)

```python
# Store data across windows in same dialog
manager.dialog_data["step"] = 1
manager.dialog_data["selected"] = []

# Retrieve data
step = manager.dialog_data.get("step", 0)
selected = manager.dialog_data.get("selected", [])
```

### start_data (From Parent Dialog)

```python
async def open_sub_dialog(callback, button, manager: DialogManager):
    await manager.start(
        SubDialog.main,
        data={"parent_id": 123, "mode": "edit"}  # start_data
    )

# In sub-dialog getter
async def sub_getter(dialog_manager: DialogManager, **kwargs):
    parent_id = dialog_manager.start_data.get("parent_id")
    return {"parent_id": parent_id}
```

## Launch Modes

### StartMode (Stack Behavior)

```python
from aiogram_dialog import StartMode

# Normal: push onto existing stack
await manager.start(MyDialog.main, mode=StartMode.NORMAL)

# Reset stack: clear all, start fresh (use for main menu)
await manager.start(MainMenu.main, mode=StartMode.RESET_STACK)

# New stack: create separate independent stack
await manager.start(AdminPanel.main, mode=StartMode.NEW_STACK)
```

### LaunchMode (Dialog-Level Config)

Set on `Dialog` to control how it interacts with the stack.

```python
from aiogram_dialog import Dialog, LaunchMode

Dialog(
    # ... windows ...
    launch_mode=LaunchMode.ROOT,         # Always root, resets stack
    # launch_mode=LaunchMode.EXCLUSIVE,  # Single dialog only
    # launch_mode=LaunchMode.SINGLE_TOP, # No repeat on top of stack
    # launch_mode=LaunchMode.STANDARD,   # No restrictions (default)
)
```

### ShowMode (Message Update Behavior)

```python
from aiogram_dialog import ShowMode

# Control how messages are updated during navigation
await manager.switch_to(MyState.settings, show_mode=ShowMode.EDIT)
await manager.start(MyState.main, show_mode=ShowMode.SEND_AND_EDIT)
```

## Background Manager

Send dialog updates from background tasks (e.g., after async work completes).

```python
from aiogram_dialog import BgManagerFactory

# Setup (setup_dialogs returns the factory)
bg_factory = setup_dialogs(dp)

# In a background task
async def background_task(bg_manager):
    # Update dialog data
    bg_manager.dialog_data["result"] = "done"
    await bg_manager.update()

    # Foreground mode for full dialog manager access (async context manager)
    async with bg_manager.fg() as dialog_manager:
        dialog_manager.dialog_data["key"] = value
        await dialog_manager.update()

# Get bg_manager from dialog manager
bg_manager = await dialog_manager.bg(
    user_id=user_id,
    chat_id=chat_id,
    stack_id=DEFAULT_STACK_ID,       # Optional
    thread_id=None,                  # Optional (for topics)
    business_connection_id=None,     # Optional (for business bots)
)
```

## Error Handling

### Required: Unknown Handlers

```python
from aiogram_dialog import Dialog
from aiogram_dialog.widgets.text import Const

dialog = Dialog(
    Window(Const("Main menu"), state=MainMenu.main),
)
# Note: Unknown callback handling is done via dispatcher error handlers
# (see UnknownIntent & UnknownState below), NOT via Dialog constructor params.
```

### UnknownIntent & UnknownState

Register error handlers at the dispatcher level (recommended pattern from official examples):

```python
from aiogram.filters import ExceptionTypeFilter
from aiogram_dialog import DialogManager, StartMode, ShowMode
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState

async def on_unknown_intent(event, dialog_manager: DialogManager):
    logging.error("Restarting dialog: %s", event.exception)
    await dialog_manager.start(
        MainMenu.main, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND,
    )

async def on_unknown_state(event, dialog_manager: DialogManager):
    logging.error("Restarting dialog: %s", event.exception)
    await dialog_manager.start(
        MainMenu.main, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND,
    )

# Register on dispatcher
dp.errors.register(on_unknown_intent, ExceptionTypeFilter(UnknownIntent))
dp.errors.register(on_unknown_state, ExceptionTypeFilter(UnknownState))
```

Or set handlers directly on the Dialog:

```python
dialog = Dialog(
    # ... windows ...
    on_process_unknown_intent=handle_unknown_intent,
    on_process_unknown_state=handle_unknown_state,
)
```

## Common Patterns

### Main Menu Pattern

```python
from aiogram_dialog.widgets.kbd import Row, Cancel

class MainMenu(StatesGroup):
    main = State()

main_dialog = Dialog(
    Window(
        Const("🏠 Main Menu\n\nChoose an option:"),
        Row(
            SwitchTo(Const("👤 Profile"), id="profile", state=MainMenu.profile),
            SwitchTo(Const("⚙️ Settings"), id="settings", state=MainMenu.settings),
        ),
        Row(
            SwitchTo(Const("📊 Stats"), id="stats", state=MainMenu.stats),
            Cancel(Const("❌ Exit")),
        ),
        state=MainMenu.main,
    )
)

# Always start main menu with RESET_STACK
await dialog_manager.start(MainMenu.main, mode=StartMode.RESET_STACK)
```

### Wizard Pattern

```python
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Next, Back, Cancel
from aiogram_dialog.widgets.text import Format

class Registration(StatesGroup):
    name = State()
    email = State()
    confirm = State()

async def on_name_entered(message, widget, manager: DialogManager, value: str):
    manager.dialog_data["name"] = value
    await manager.next()

async def on_email_entered(message, widget, manager: DialogManager, value: str):
    manager.dialog_data["email"] = value
    await manager.next()

registration_dialog = Dialog(
    Window(
        Const("📝 Step 1: Enter your name"),
        TextInput(id="name_input", on_success=on_name_entered),
        Cancel(Const("❌ Cancel")),
        state=Registration.name,
    ),
    Window(
        Const("📧 Step 2: Enter your email"),
        TextInput(id="email_input", on_success=on_email_entered),
        Row(Back(Const("← Back")), Cancel(Const("❌ Cancel"))),
        state=Registration.email,
    ),
    Window(
        Format("✅ Confirm:\nName: {name}\nEmail: {email}"),
        Row(
            Back(Const("← Back")),
            Button(Const("✅ Confirm"), id="confirm", on_click=finish_registration),
        ),
        getter=lambda **kw: {
            "name": kw["dialog_manager"].dialog_data.get("name", ""),
            "email": kw["dialog_manager"].dialog_data.get("email", ""),
        },
        state=Registration.confirm,
    ),
)
```

### Admin Panel Pattern

```python
from aiogram_dialog.widgets.kbd import Multiselect
from aiogram_dialog.widgets.text import Format

class AdminPanel(StatesGroup):
    main = State()

async def get_admin_stats(**kwargs):
    return {
        "users_count": await db.get_users_count(),
        "messages_count": await db.get_messages_count(),
        "settings": [
            {"id": "maintenance", "name": "Maintenance Mode", "enabled": False},
            {"id": "debug", "name": "Debug Mode", "enabled": True},
        ]
    }

admin_dialog = Dialog(
    Window(
        Format("🔐 Admin Panel\n\nUsers: {users_count}\nMessages: {messages_count}"),
        Multiselect(
            Format("✓ {item[name]}"),
            Format("○ {item[name]}"),
            id="admin_toggles",
            item_id_getter=lambda x: x["id"],
            items="settings",
            on_state_changed=save_admin_settings,
        ),
        getter=get_admin_stats,
        state=AdminPanel.main,
    ),
    launch_mode=LaunchMode.EXCLUSIVE,
)
```

### Paginated List Pattern

```python
from aiogram_dialog.widgets.kbd import (
    ScrollingGroup, Select, NumberedPager, Row,
)

class ItemList(StatesGroup):
    browse = State()

async def items_getter(dialog_manager: DialogManager, **kwargs):
    items = await db.get_items()
    return {"items": items}

browse_window = Window(
    Const("📦 Items:"),
    ScrollingGroup(
        Select(
            Format("{item[name]} — {item[price]}$"),
            id="item_select",
            items="items",
            item_id_getter=lambda x: x["id"],
            on_click=on_item_selected,
        ),
        id="items_scroll",
        width=1,
        height=5,
    ),
    NumberedPager(scroll="items_scroll", id="pager"),
    getter=items_getter,
    state=ItemList.browse,
)
```

## Managed Widgets

Access widget state programmatically using `manager.find()`.

```python
# Checkbox state
checkbox = manager.find("feature_toggle")  # ManagedCheckbox
is_checked = checkbox.is_checked()

# Multiselect selected items
multi = manager.find("multi_select")  # ManagedMultiselect
selected = multi.get_checked()

# Calendar selected date
calendar = manager.find("calendar")  # ManagedCalendar

# Counter value
counter = manager.find("quantity")  # ManagedCounter
value = counter.get_value()

# Radio/Toggle selected
radio = manager.find("radio_group")  # ManagedRadio
selected = radio.get_checked()

# ListGroup
list_group = manager.find("items_list")  # ManagedListGroup
```

## Best Practices

### Widget IDs

```python
# ALWAYS set unique IDs for widgets
Button(Const("Click"), id="unique_button_id")  # ✓

# Widget IDs must be unique within the dialog
# They're used for state tracking and callbacks
```

### Getter Performance

```python
# ✓ Always return dict
async def good_getter(**kwargs):
    return {"items": []}  # ✓

# ✗ Never return None
async def bad_getter(**kwargs):
    return None  # ✗ Causes TypeError
```

### Exception Handling

```python
async def safe_button_click(callback, button, manager: DialogManager):
    try:
        await risky_operation()
    except Exception as e:
        logger.error(f"Button error: {e}")
        await callback.answer("❌ An error occurred", show_alert=True)
        # Don't let exceptions propagate - they crash the bot
```

## Common Mistakes

1. **Forgetting `setup_dialogs(dp)`** — Dialogs won't work
2. **Missing widget `id`** — Widget state not tracked
3. **Getter returning `None`** — TypeError, always return `{}`
4. **Not using `StartMode.RESET_STACK`** for main menus — Stack overflow
5. **Wrong `item_id_getter`** — Selection fails
6. **Exceptions in callbacks** — Crashes bot, always catch
7. **Blocking operations in getter** — Blocks event loop
8. **Using deprecated `Registry` class** — Use `setup_dialogs(dp)` instead
9. **Writing custom `on_click` for navigation** — Use `SwitchTo`, `Next`, `Back`, `Cancel`, `Start` widgets instead
10. **Using plain `Button` for URLs** — Use `Url` widget instead

## Migration from v1 to v2

| v1 | v2 |
|----|----|
| `reset_stack=True` | `mode=StartMode.RESET_STACK` |
| `manager.context` | `manager.current_context()` |
| `manager.current_stack()` | `manager.stack()` |
| `Registry` class | `setup_dialogs(dp)` |
| `Registry.register_start_handler` | Router-based start handlers |
| `*Adapter` suffix on managed widgets | Simplified: `ManagedCalendar`, `ManagedCheckbox`, etc. |

## Resources

- **Official Docs**: https://aiogram-dialog.readthedocs.io
- **GitHub**: https://github.com/Tishka17/aiogram_dialog
- **Examples**: https://github.com/Tishka17/aiogram_dialog/tree/master/example

## Quick Reference

```python
# Start dialog (clear stack)
await manager.start(MyDialog.main, mode=StartMode.RESET_STACK)

# Start dialog (keep stack)
await manager.start(SubDialog.main, mode=StartMode.NORMAL)

# Start dialog (new stack)
await manager.start(SubDialog.main, mode=StartMode.NEW_STACK)

# Switch window
await manager.switch_to(MyDialog.settings)

# Next/previous window
await manager.next()
await manager.back()

# Update current window (refresh data)
await manager.update()

# End dialog (with optional result)
await manager.done()
await manager.done(result={"selected": item})

# Find widget by ID
widget = manager.find("widget_id")

# Update dialog data
manager.dialog_data["key"] = value
```

## Complete Widget Index

### Keyboard Widgets (`aiogram_dialog.widgets.kbd`)

| Widget | Purpose | Managed Variant |
|--------|---------|----------------|
| `Button` | Clickable button | — |
| `SwitchTo` | Navigate to window state | — |
| `Next` | Go to next window | — |
| `Back` | Go to previous window | — |
| `Cancel` | Close dialog | — |
| `Start` | Start another dialog | — |
| `Select` | Single-choice selector | — |
| `Radio` | Radio button group | `ManagedRadio` |
| `Multiselect` | Multi-choice selector | `ManagedMultiselect` |
| `Toggle` | Toggle between items | `ManagedToggle` |
| `Checkbox` | Boolean toggle | `ManagedCheckbox` |
| `Calendar` | Date picker | `ManagedCalendar` |
| `TimeSelect` | Time picker | `ManagedTimeSelect` |
| `Counter` | +/- number input | `ManagedCounter` |
| `ListGroup` | Dynamic button list | `ManagedListGroup` |
| `Url` | Open URL button | — |
| `WebApp` | Open Web App button | — |
| `LoginURLButton` | Login URL button | — |
| `SwitchInlineQuery` | Switch to inline query | — |
| `SwitchInlineQueryCurrentChat` | Inline query in current chat | — |
| `SwitchInlineQueryChosenChatButton` | Inline query with chat picker | — |
| `RequestContact` | Request user's contact | — |
| `RequestLocation` | Request user's location | — |
| `RequestPoll` | Request poll creation | — |
| `CopyText` | Copy text to clipboard | — |
| `Row` | Horizontal layout | — |
| `Column` | Vertical layout | — |
| `Group` | Grid layout with width | — |
| `ScrollingGroup` | Paginated scrollable group | — |
| `PrevPage` / `NextPage` | Pagination buttons | — |
| `FirstPage` / `LastPage` | Jump to first/last page | — |
| `CurrentPage` | Show current page number | — |
| `NumberedPager` | Numbered page buttons | — |
| `SwitchPage` | Custom page navigation | — |

### Text Widgets (`aiogram_dialog.widgets.text`)

| Widget | Purpose |
|--------|---------|
| `Const` | Static text |
| `Format` | Format string with getter data |
| `Multi` | Concatenate multiple text widgets |
| `Case` | Conditional text based on selector |
| `Progress` | Visual progress bar |
| `List` | Render list of items as text |
| `Jinja` | Jinja2 template rendering |
| `ScrollingText` | Scrollable text content |

### Media Widgets (`aiogram_dialog.widgets.media`)

| Widget | Purpose |
|--------|---------|
| `StaticMedia` | Static file/URL media |
| `DynamicMedia` | Getter-based dynamic media |
| `MediaScroll` | Scrollable media gallery |

### Input Widgets (`aiogram_dialog.widgets.input`)

| Widget | Purpose |
|--------|---------|
| `TextInput` | Text input with type conversion |
| `MessageInput` | Raw message handler (photos, docs, etc.) |

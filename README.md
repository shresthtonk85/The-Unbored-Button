# Unbored Button - Code Context & Architecture

> **Context refreshed:** 2026-10-25, based on the current source and local data files.

## Overview
**The Unbored Button** is a mood-lifting, habit-building desktop application built with Python and Tkinter. Designed to break procrastination and boredom loops, the app suggests micro-challenges (typically 1 to 10 minutes) that encourage users to take tiny, manageable actions, refresh mental focus, and celebrate small wins.

The project is structured with a modular architecture split across `config.py`, `data_manager.py`, `views.py`, and `unbored.py`.

## Current Project State
- This is a local desktop application; the project root contains the four Python modules, `boredom_data.json`, the original `logo.png`, and resized/icon assets under `assets/`.
- The app has no test suite or dependency manifest in the project root. Tkinter is the UI toolkit; Pillow is optional and enables high-quality logo resizing, with Tkinter image loading as a fallback.
- The local `boredom_data.json` currently has no completion history. It contains custom activity data and a serialized combined activity list.
- **Known persistence limitation:** built-in catalog edits and deletions are not restored after restart. `save_data()` writes the combined `activities` list, but `load_data()` only reads `history` and `custom_activities`; built-ins are recreated from `config.DEFAULT_ACTIVITIES`. Custom activities and completion history are loaded from JSON.

---

## What the Code Does
- **Playful Pink Theme & Official Mascot**: Features the official "The Unbored Button" mascot logo (an adorable bunny sitting on a pink challenge button with confetti), breathing floating animation, motivational quotes, and a refined color palette.
- **Random Micro-Challenges**: Suggests low-effort activities from a curated catalog or user-defined activities.
- **Dual Filter Pills (Category & Mood)**: Interactive filter pill rows for **Category** (`All`, `Indoor`, `Outdoor`, `Creative`, `Relaxing`) and **Mood** (`All`, `Energetic`, `Calm`, `Focused`, `Playful`, `Cozy`) for nuanced, mood-targeted challenge discovery.
- **Custom Activity Creator**: Clean form to add custom challenges with custom titles, categories, moods, and durations.
- **Catalog Management (Treeview)**: Tabular view of all catalog tasks with Title, Category, Mood, and Duration columns, scaled row height, zebra striping, and dialog-based editing/deletion.
- **Micro-Timer**: Countdown timer with Start, Pause, and Reset controls, parsing duration strings like `"5 minutes"` and `"60 seconds"`.
- **Completion Tracking & Stats Overview**: Tracks completed challenges in a timestamped log and displays a dynamic "Progress & Insights" dashboard header (Total Completed, Top Focus category, and Catalog Size).
- **JSON Persistence**: Preserves completed history and custom activities in `boredom_data.json`; built-in catalog changes are currently not restored after restart.

---

## File Structure & Module Responsibilities

### 1. `config.py` — Centralized Settings & Design Tokens
Stores all UI configuration, design tokens, and default data:
- **High-DPI Awareness**: `enable_high_dpi_awareness()` initializes Windows Per-Monitor V2 DPI context (`-4`), preventing Windows bitmap virtualization and blurry/pixelated scaling.
- **Palette**: Window background (`#FFF0F5`), card surfaces (`#FFFFFF`), hero hot pink (`#FF69B4`), completion accent (`#FFEFF3` / `#C71585`), secondary light pink (`#FFF4F8`), and high-contrast dark plum text (`#2C1820`).
- **Typography**: Scaled font definitions for headers, titles, timer, buttons, pill badges, and metrics.
- **Window Constraints**: Minimum dimensions (`920x700`); the live window geometry is calculated from screen dimensions and bounded between `920x700` and `1120x840`. `DEFAULT_GEOMETRY` remains defined as `1080x820`.
- **Default Catalog**: Built-in collection of 84 micro-challenges (21 in each category: Indoor, Outdoor, Creative, Relaxing) with assigned moods (`Energetic`, `Calm`, `Focused`, `Playful`, `Cozy`).
- **Paths**: JSON data file location (`boredom_data.json`) and asset paths.

### 2. `data_manager.py` — Business Logic & Persistence
Encapsulates all non-GUI state, persistence, and activity processing via `DataManager` (aliased as `BoredomDataManager`):
- **Normalization**: Strips whitespace, standardizes fields, defaults missing moods to `"Calm"` for backwards compatibility, and removes duplicate tasks (`normalize_activity`, `normalize_activity_list`).
- **Dual Filtering & Selection**: Retrieves activities matching Category AND Mood simultaneously (`get_filtered_activities`, `get_all_activities`).
- **Activity CRUD**: Adds, updates, and deletes activities with mood support (`add_custom_activity`, `edit_activity`/`replace_activity`, `remove_activity`).
- **History & Stats**: Records timestamped completions including mood (`add_completed`, `clear_history`) and calculates insights (`get_stats`: total count, top category, top mood, catalog size).
- **Duration Helpers**: Converts human-readable duration strings to seconds (`parse_duration`) and formats integers to `MM:SS` strings (`format_seconds`).
- **JSON I/O**: Loads history and custom activities from `boredom_data.json`; the `activities` key is written as a combined catalog snapshot but is not used to restore the built-in catalog. Load/save failures set `last_error`.

### 3. `views.py` — Tkinter UI & Presentation
Houses the graphical presentation layer, widgets, and animation:
- **`MascotCanvas`**: Custom Tkinter canvas rendering the official "The Unbored Button" mascot logo with dynamic High-DPI scaling (via Pillow Lanczos when available) and gentle floating animation.
- **`Application`**: Main `tk.Tk` window managing widget layout, responsive grid weights, and UI events:
  - **Responsive Layout & High DPI**: Derives its initial size from screen dimensions, detects monitor DPI scale, and scales image assets dynamically from the master source when Pillow is available.
  - **Button Contrast & Theming**: Crisp `#C71585` deep magenta text on secondary buttons (`Soft.TButton`), distinct `#FFEFF3` / `#C71585` border styling for "Mark as Completed" (`Completed.TButton`), and vibrant hot pink for the hero button (`Accent.TButton`).
  - **Styled TTK Comboboxes**: Dropdowns with `#FFF4F8` field backgrounds, `#2C1820` text, `#FFB6C1` borders, and matching option database theming for popdown listboxes.
  - **Challenges Tab**: Interactive Category & Mood Filter Pills with dynamic active indicators, paired with a custom activity form and quick-tip panel.
  - **Manage Tab**: `Pink.Treeview` configured with Title, Category, Mood, and Duration columns, scaled row height, zebra-striping tags (`evenrow`/`oddrow`), and selection highlights (`#FFD1DC` background, `#2C1820` text).
  - **Completed Tab**: "Progress & Insights" summary header with live tiles for total completions, top category, and catalog size, plus a scrollable completion listbox. The data manager also calculates top mood and category/mood counts, though these are not currently shown in the UI.
  - **Edit Activity Dialog**: Modal window (`tk.Toplevel`) for updating task titles, categories, moods, and durations.

### 4. `unbored.py` — Main Entrypoint
- Exposes `Application`, `DataManager`, and `config` for backwards compatibility.
- Launches the application when executed directly.

---

## Main Execution Flow
1. **Startup**: `unbored.py` or `views.py` calls `app = Application(); app.run()`.
2. **Initialization**:
   - `DataManager` loads data from `boredom_data.json` (or initializes defaults).
   - TTK styles (`clam` theme) are applied with custom palettes and combobox overrides.
   - UI grid layout and responsive weights are established.
3. **View Hydration**:
   - Mascot canvas is drawn and animation timer begins.
   - Initial random activity is selected and displayed.
   - Treeview table and history view (with stats overview) are populated.
4. **Interaction**:
   - **"I'm Bored!"**: Picks a fresh random activity matching active filter pills.
   - **Filter Pills**: Category and mood filters combine with AND semantics, updating the hero suggestion and Treeview table.
   - **Timer**: Starts, pauses, or resets countdown for the current challenge duration.
   - **Mark as Completed**: Records timestamped completion in history, updates the Stats Overview cards, and switches to the Completed tab.
   - **Manage / Edit / Delete**: Modifies tasks via dialog or deletes selected entries and saves JSON. Custom activity changes persist; changes to built-in activities currently do not survive a restart (see Current Project State).

---

## How to Run
From the project root:

```bash
python unbored.py
```

Or run the views module directly:

```bash
python views.py
```

---

## Data Schema (`boredom_data.json`)
The file currently serializes `history`, `custom_activities`, and a combined `activities` snapshot. On load, only history and custom activities are consumed; the built-in catalog is sourced from `config.py`.

```json
{
  "history": [
    {
      "title": "Take a short tea or water break",
      "category": "Relaxing",
      "duration": "5 minutes",
      "mood": "Cozy",
      "completed_at": "2026-10-25 14:50:05"
    }
  ],
  "custom_activities": [
    {
      "title": "Draw something in 60 seconds",
      "category": "Creative",
      "duration": "60 seconds",
      "mood": "Playful"
    }
  ],
  "activities": [ ... ]
}
```

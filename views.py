"""UI Views and Tkinter Presentation for The Unbored Button."""
import os
import random
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

import config
from data_manager import DataManager

# Pre-enable high-DPI scaling before any Tkinter windows are constructed
config.enable_high_dpi_awareness()


class MascotCanvas(tk.Canvas):
    """Custom canvas for rendering and gently animating The Unbored Button logo."""

    def __init__(self, parent: tk.Widget, dpi_scale: float = 1.0, **kwargs: Any):
        self.dpi_scale = max(1.0, dpi_scale)
        width = kwargs.pop("width", int(200 * self.dpi_scale))
        height = kwargs.pop("height", int(196 * self.dpi_scale))
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=kwargs.pop("bg", config.COLOR_BG_CARD),
            highlightthickness=0,
            borderwidth=0,
            **kwargs,
        )
        self.phase = 0
        self.animating = False
        self.logo_image: Any = None
        self._load_logo()
        self.draw()

    def _load_logo(self) -> None:
        """Loads and scales the logo image asset at high DPI resolution."""
        target_w = max(50, int(200 * self.dpi_scale))
        target_h = max(50, int(196 * self.dpi_scale))

        if HAS_PIL and os.path.exists(config.LOGO_ORIGINAL_PATH):
            try:
                img = Image.open(config.LOGO_ORIGINAL_PATH)
                resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(resized)
                return
            except Exception:
                pass

        try:
            if os.path.exists(config.LOGO_PATH):
                self.logo_image = tk.PhotoImage(file=config.LOGO_PATH)
            elif os.path.exists(config.LOGO_ORIGINAL_PATH):
                self.logo_image = tk.PhotoImage(file=config.LOGO_ORIGINAL_PATH)
        except Exception:
            self.logo_image = None

    def draw(self) -> None:
        """Renders the logo on the canvas."""
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        default_w = int(200 * self.dpi_scale)
        default_h = int(196 * self.dpi_scale)
        if width <= 10 or height <= 10:
            width, height = default_w, default_h

        cx = width / 2
        cy = height / 2

        if self.logo_image is not None:
            self.create_image(cx, cy, image=self.logo_image, anchor="center")
        else:
            # Fallback graphic badge
            badge_r = int(50 * self.dpi_scale)
            self.create_oval(
                cx - badge_r, cy - badge_r, cx + badge_r, cy + badge_r,
                fill=config.COLOR_BG_SECONDARY, outline=config.COLOR_BORDER_LIGHT, width=2
            )
            self.create_text(cx, cy, text="🐰", font=("Segoe UI Emoji", int(32 * self.dpi_scale)))
            self.create_text(
                cx, cy + int(40 * self.dpi_scale), text="Unbored Button",
                font=("Segoe UI", 10, "bold"), fill=config.COLOR_TITLE_PINK
            )

    def tick_animation(self) -> None:
        """Animates a gentle breathing / floating cycle for the logo."""
        width = self.winfo_width()
        if width <= 1:
            self.after(150, self.tick_animation)
            return

        self.phase = (self.phase + 1) % 20
        y_offset = 4 if self.phase % 2 == 0 else 0
        self.move("all", 0, y_offset - 2)

        self.after(650, self.tick_animation)


class Application(tk.Tk):
    """The Unbored Button desktop application."""

    def __init__(self, data_file: Optional[str] = None):
        # Enable Windows High-DPI awareness before Tk initialization
        config.enable_high_dpi_awareness()
        super().__init__()
        self.title(config.APP_TITLE)

        # Detect physical DPI scale
        try:
            self.dpi = self.winfo_fpixels("1i")
            self.dpi_scale = max(1.0, self.dpi / 96.0)
        except Exception:
            self.dpi = 96.0
            self.dpi_scale = 1.0

        # Responsive high-DPI window size
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        default_w = min(1120, max(config.MIN_WINDOW_WIDTH, int(screen_w * 0.82)))
        default_h = min(840, max(config.MIN_WINDOW_HEIGHT, int(screen_h * 0.82)))
        self.geometry(f"{default_w}x{default_h}")
        self.minsize(config.MIN_WINDOW_WIDTH, config.MIN_WINDOW_HEIGHT)
        self.configure(bg=config.COLOR_BG_MAIN)

        # Data & State
        self.data_manager = DataManager(data_file=data_file)
        self.categories = config.CATEGORIES
        self.moods = config.MOODS
        self.current_activity: Optional[Dict[str, str]] = None
        self.filter_var = tk.StringVar(value="All")
        self.mood_var = tk.StringVar(value="All")
        self.motivation_var = tk.StringVar(value="Tiny breaks are still wins.")

        # Filter pill button dictionaries
        self.filter_pills: Dict[str, ttk.Button] = {}
        self.mood_pills: Dict[str, ttk.Button] = {}

        # Timer State
        self.timer_running = False
        self.timer_seconds = 0
        self.timer_total = 0
        self.timer_after: Optional[str] = None

        # Window Icon
        self.icon_image: Optional[tk.PhotoImage] = None
        try:
            if os.path.exists(config.LOGO_ICON_PATH):
                self.icon_image = tk.PhotoImage(file=config.LOGO_ICON_PATH)
                self.iconphoto(True, self.icon_image)
        except Exception:
            pass

        # Build Styles and UI
        self._setup_styles()
        self._build_ui()

        # Handle errors if any during load
        if self.data_manager.last_error:
            self.update_motivation(self.data_manager.last_error)
        else:
            self.update_motivation("Boredom is a signal to play, not a problem.")

        # Bindings & Initialization
        self.bind("<Configure>", self._on_resize)
        self.refresh_activity()
        self.refresh_activity_table()
        self.update_history_view()
        self.mascot_canvas.tick_animation()

    def _setup_styles(self) -> None:
        """Configures ttk styles with pink palette, high contrast, and custom widgets."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Popdown listbox theming for Comboboxes globally
        self.option_add("*TCombobox*Listbox.background", config.COLOR_TREEVIEW_BG)
        self.option_add("*TCombobox*Listbox.foreground", config.COLOR_TEXT_DARK)
        self.option_add("*TCombobox*Listbox.selectBackground", config.COLOR_SELECTION_BG)
        self.option_add("*TCombobox*Listbox.selectForeground", config.COLOR_SELECTION_FG)
        self.option_add("*TCombobox*Listbox.font", config.FONT_BODY)

        # Frame styles
        style.configure("PinkCard.TFrame", background=config.COLOR_BG_CARD)
        style.configure("PinkPanel.TFrame", background=config.COLOR_BG_PANEL)
        style.configure("StatTile.TFrame", background=config.COLOR_BG_SECONDARY, borderwidth=1, relief="solid")

        # 1. FIX BUTTON TEXT CONTRAST & STYLING
        # Hero button: Bold, vibrant pink with crisp white text
        style.configure(
            "Accent.TButton",
            background=config.COLOR_HERO_BG,
            foreground=config.COLOR_HERO_FG,
            font=config.FONT_BUTTON_HERO,
            borderwidth=1,
            bordercolor=config.COLOR_HERO_HOVER,
            relief="raised",
            padding=(16, 10),
        )
        style.map(
            "Accent.TButton",
            background=[("pressed", config.COLOR_TITLE_PINK), ("active", config.COLOR_HERO_HOVER)],
            foreground=[("pressed", config.COLOR_HERO_FG), ("active", config.COLOR_HERO_FG)],
            bordercolor=[("active", config.COLOR_TITLE_PINK)],
        )

        # Differentiated "Mark as Completed" button: Softer accent style with solid #C71585 border & text
        style.configure(
            "Completed.TButton",
            background=config.COLOR_COMPLETED_BG,
            foreground=config.COLOR_COMPLETED_FG,
            font=config.FONT_BUTTON_COMPLETED,
            borderwidth=2,
            bordercolor=config.COLOR_COMPLETED_BORDER,
            relief="raised",
            padding=(14, 10),
        )
        style.map(
            "Completed.TButton",
            background=[("pressed", config.COLOR_SELECTION_BG), ("active", config.COLOR_COMPLETED_HOVER)],
            foreground=[("pressed", config.COLOR_TEXT_DARK), ("active", config.COLOR_COMPLETED_FG)],
            bordercolor=[("active", config.COLOR_COMPLETED_BORDER)],
        )

        # Secondary buttons: Crisp, high-contrast dark text (#C71585 or #2C1820) over light background
        style.configure(
            "Soft.TButton",
            background=config.COLOR_BG_SECONDARY,
            foreground=config.COLOR_TEXT_MAGENTA,
            font=config.FONT_BUTTON_SECONDARY,
            borderwidth=1,
            bordercolor=config.COLOR_BORDER_MEDIUM,
            relief="raised",
            padding=(12, 6),
        )
        style.map(
            "Soft.TButton",
            background=[("pressed", config.COLOR_SELECTION_BG), ("active", config.COLOR_BG_HOVER)],
            foreground=[("pressed", config.COLOR_TEXT_DARK), ("active", config.COLOR_TEXT_MAGENTA)],
            bordercolor=[("active", config.COLOR_TEXT_MAGENTA)],
        )

        # Delete button style
        style.configure(
            "Delete.TButton",
            background="#FFF0F2",
            foreground=config.COLOR_TITLE_PINK,
            font=config.FONT_BUTTON_SECONDARY,
            borderwidth=1,
            bordercolor="#FFB3C1",
            relief="raised",
            padding=(12, 6),
        )
        style.map(
            "Delete.TButton",
            background=[("pressed", config.COLOR_SELECTION_BG), ("active", "#FFE5EA")],
            foreground=[("pressed", config.COLOR_TEXT_DARK), ("active", config.COLOR_TITLE_PINK)],
            bordercolor=[("active", config.COLOR_TITLE_PINK)],
        )

        # Category Filter Pills
        style.configure(
            "PillInactive.TButton",
            background=config.COLOR_BG_SECONDARY,
            foreground=config.COLOR_TEXT_DARK,
            font=config.FONT_PILL,
            borderwidth=1,
            bordercolor=config.COLOR_BORDER_LIGHT,
            relief="flat",
            padding=(10, 5),
        )
        style.map(
            "PillInactive.TButton",
            background=[("pressed", config.COLOR_SELECTION_BG), ("active", config.COLOR_BG_HOVER)],
            foreground=[("pressed", config.COLOR_TEXT_DARK), ("active", config.COLOR_TEXT_MAGENTA)],
            bordercolor=[("active", config.COLOR_BORDER_FOCUS)],
        )

        style.configure(
            "PillActive.TButton",
            background=config.COLOR_HERO_BG,
            foreground=config.COLOR_HERO_FG,
            font=config.FONT_PILL,
            borderwidth=1,
            bordercolor=config.COLOR_HERO_HOVER,
            relief="raised",
            padding=(10, 5),
        )
        style.map(
            "PillActive.TButton",
            background=[("pressed", config.COLOR_TITLE_PINK), ("active", config.COLOR_HERO_HOVER)],
            foreground=[("pressed", config.COLOR_HERO_FG), ("active", config.COLOR_HERO_FG)],
        )

        # 2. STYLED TTK COMBOBOXES
        style.configure(
            "TCombobox",
            fieldbackground=config.COLOR_BG_SECONDARY,
            background=config.COLOR_BG_PANEL,
            foreground=config.COLOR_TEXT_DARK,
            darkcolor=config.COLOR_BORDER_LIGHT,
            lightcolor=config.COLOR_BORDER_LIGHT,
            arrowcolor=config.COLOR_TEXT_MAGENTA,
            bordercolor=config.COLOR_BORDER_MEDIUM,
            insertcolor=config.COLOR_TEXT_DARK,
            padding=5,
        )
        style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", config.COLOR_BG_SECONDARY),
                ("focus", "#FFFFFF"),
                ("active", config.COLOR_BG_SECONDARY),
            ],
            foreground=[
                ("readonly", config.COLOR_TEXT_DARK),
                ("focus", config.COLOR_TEXT_DARK),
            ],
            selectbackground=[
                ("readonly", config.COLOR_BG_SECONDARY),
                ("focus", config.COLOR_SELECTION_BG),
            ],
            selectforeground=[
                ("readonly", config.COLOR_TEXT_DARK),
                ("focus", config.COLOR_TEXT_DARK),
            ],
            bordercolor=[
                ("focus", config.COLOR_TEXT_MAGENTA),
                ("active", config.COLOR_HERO_BG),
            ],
            arrowcolor=[
                ("active", config.COLOR_TITLE_PINK),
            ],
        )

        # Entry fields
        style.configure(
            "TEntry",
            fieldbackground=config.COLOR_BG_SECONDARY,
            foreground=config.COLOR_TEXT_DARK,
            bordercolor=config.COLOR_BORDER_MEDIUM,
            padding=5,
        )
        style.map(
            "TEntry",
            bordercolor=[("focus", config.COLOR_TEXT_MAGENTA)],
            fieldbackground=[("focus", "#FFFFFF")],
        )

        # 4. TREEVIEW SELECTION & ROW HEIGHT (Scaled for High DPI)
        scaled_row_height = max(28, int(config.TREEVIEW_ROW_HEIGHT * self.dpi_scale))
        style.configure(
            "Pink.Treeview",
            background=config.COLOR_TREEVIEW_BG,
            fieldbackground=config.COLOR_TREEVIEW_BG,
            foreground=config.COLOR_TEXT_DARK,
            rowheight=scaled_row_height,
            font=config.FONT_BODY,
            borderwidth=0,
        )
        style.map(
            "Pink.Treeview",
            background=[("selected", config.COLOR_SELECTION_BG)],
            foreground=[("selected", config.COLOR_SELECTION_FG)],
        )
        style.configure(
            "Pink.Treeview.Heading",
            background=config.COLOR_TREEVIEW_HEADER,
            foreground=config.COLOR_TREEVIEW_HEADER_FG,
            font=config.FONT_CARD_TITLE,
            padding=(8, 6),
        )
        style.map(
            "Pink.Treeview.Heading",
            background=[("active", config.COLOR_HERO_HOVER)],
            foreground=[("active", "#FFFFFF")],
        )

        # Notebook tabs
        style.configure("Pink.TNotebook", background=config.COLOR_BG_PANEL, borderwidth=0)
        style.configure(
            "Pink.TNotebook.Tab",
            background=config.COLOR_BG_SECONDARY,
            foreground=config.COLOR_TEXT_SUBTITLE,
            padding=(14, 8),
            font=config.FONT_BUTTON_SECONDARY,
        )
        style.map(
            "Pink.TNotebook.Tab",
            background=[("selected", config.COLOR_BG_CARD), ("active", config.COLOR_BG_HOVER)],
            foreground=[("selected", config.COLOR_TITLE_PINK), ("active", config.COLOR_TEXT_DARK)],
        )

    def _build_ui(self) -> None:
        """Constructs the responsive user interface layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header bar
        header = ttk.Frame(self, padding=(24, 16, 24, 12), style="PinkCard.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        header_left = ttk.Frame(header, style="PinkCard.TFrame")
        header_left.grid(row=0, column=0, sticky="w")

        # Header logo thumbnail (Crisp High-DPI scaled)
        self.header_logo_img: Any = None
        target_h = max(24, int(36 * self.dpi_scale))
        if HAS_PIL and os.path.exists(config.LOGO_ORIGINAL_PATH):
            try:
                img = Image.open(config.LOGO_ORIGINAL_PATH)
                ratio = img.height / img.width
                resized = img.resize((target_h, int(target_h * ratio)), Image.Resampling.LANCZOS)
                self.header_logo_img = ImageTk.PhotoImage(resized)
                logo_lbl = ttk.Label(header_left, image=self.header_logo_img, background=config.COLOR_BG_CARD)
                logo_lbl.grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="w")
            except Exception:
                pass
        elif os.path.exists(config.LOGO_HEADER_PATH):
            try:
                self.header_logo_img = tk.PhotoImage(file=config.LOGO_HEADER_PATH)
                logo_lbl = ttk.Label(header_left, image=self.header_logo_img, background=config.COLOR_BG_CARD)
                logo_lbl.grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="w")
            except Exception:
                pass

        title_label = ttk.Label(
            header_left,
            text=config.APP_TITLE,
            font=config.FONT_APP_TITLE,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TITLE_PINK,
        )
        title_label.grid(row=0, column=1, sticky="w")

        subtitle_label = ttk.Label(
            header_left,
            text="Pick a tiny challenge and get moving.",
            font=config.FONT_SUBTITLE,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_SUBTITLE,
        )
        subtitle_label.grid(row=1, column=1, sticky="w", pady=(4, 0))

        tagline_badge = ttk.Label(
            header,
            text="✨ Micro-moments of joy",
            font=config.FONT_BODY_BOLD,
            background=config.COLOR_BG_SECONDARY,
            foreground=config.COLOR_TEXT_MAGENTA,
            padding=(12, 6),
        )
        tagline_badge.grid(row=0, column=1, sticky="e")

        # Main content area
        main_content = ttk.Frame(self, padding=(18, 10, 18, 18), style="PinkPanel.TFrame")
        main_content.grid(row=1, column=0, sticky="nsew")
        main_content.grid_columnconfigure(0, weight=5)
        main_content.grid_columnconfigure(1, weight=6)
        main_content.grid_rowconfigure(0, weight=1)

        # --- LEFT PANEL: Hero Activity & Timer ---
        left_panel = ttk.Frame(main_content, padding=(18, 16, 18, 16), style="PinkCard.TFrame")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(3, weight=1)  # Allow details card to expand smoothly

        # Mascot Canvas with High-DPI Logo
        canvas_w = int(200 * self.dpi_scale)
        canvas_h = int(196 * self.dpi_scale)
        self.mascot_canvas = MascotCanvas(left_panel, dpi_scale=self.dpi_scale, width=canvas_w, height=canvas_h)
        self.mascot_canvas.grid(row=0, column=0, sticky="n", pady=(0, 6))

        # Motivational quote
        self.quote_label = ttk.Label(
            left_panel,
            textvariable=self.motivation_var,
            wraplength=340,
            justify="center",
            font=config.FONT_QUOTE,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_MUTED,
        )
        self.quote_label.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Hero Action Button ("I'm Bored!")
        hero_btn_frame = ttk.Frame(left_panel, style="PinkCard.TFrame")
        hero_btn_frame.grid(row=2, column=0, sticky="ew")
        hero_btn_frame.grid_columnconfigure(0, weight=1)

        self.action_button = ttk.Button(
            hero_btn_frame,
            text="✨  I'm Bored!  ✨",
            command=self.refresh_activity,
            style="Accent.TButton",
        )
        self.action_button.pack(fill="x", ipady=8)

        # Challenge Details & Timer Card
        details_frame = ttk.Frame(left_panel, style="PinkCard.TFrame", padding=(16, 16, 16, 16))
        details_frame.grid(row=3, column=0, sticky="nsew", pady=(14, 0))
        details_frame.grid_columnconfigure(0, weight=1)

        self.activity_title = ttk.Label(
            details_frame,
            text="Choose a challenge",
            font=config.FONT_ACTIVITY_TITLE,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_DARK,
            wraplength=330,
            justify="left",
        )
        self.activity_title.grid(row=0, column=0, sticky="w")

        self.activity_meta = ttk.Label(
            details_frame,
            text="Category: — | Duration: —",
            font=config.FONT_BODY,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_SUBTITLE,
        )
        self.activity_meta.grid(row=1, column=0, sticky="w", pady=(6, 10))

        # Timer Sub-Frame
        timer_box = ttk.Frame(details_frame, padding=(12, 10, 12, 10), style="StatTile.TFrame")
        timer_box.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        timer_box.grid_columnconfigure(0, weight=1)
        timer_box.grid_columnconfigure(1, weight=1)
        timer_box.grid_columnconfigure(2, weight=1)

        self.timer_label = ttk.Label(
            timer_box,
            text="00:00",
            font=config.FONT_TIMER,
            background=config.COLOR_BG_SECONDARY,
            foreground=config.COLOR_TITLE_PINK,
            anchor="center",
        )
        self.timer_label.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(2, 8))

        # Secondary Timer Buttons (High Contrast Soft.TButton)
        self.start_timer_btn = ttk.Button(timer_box, text="Start", command=self.start_timer, style="Soft.TButton")
        self.start_timer_btn.grid(row=1, column=0, sticky="ew", padx=(0, 4))

        self.pause_timer_btn = ttk.Button(timer_box, text="Pause", command=self.pause_timer, style="Soft.TButton")
        self.pause_timer_btn.grid(row=1, column=1, sticky="ew", padx=3)

        self.reset_timer_btn = ttk.Button(timer_box, text="Reset", command=self.reset_timer, style="Soft.TButton")
        self.reset_timer_btn.grid(row=1, column=2, sticky="ew", padx=(4, 0))

        # Differentiated "Mark as Completed" button
        action_row = ttk.Frame(details_frame, style="PinkCard.TFrame")
        action_row.grid(row=3, column=0, sticky="ew")
        action_row.grid_columnconfigure(0, weight=1)

        self.complete_button = ttk.Button(
            action_row,
            text="✔  Mark as Completed",
            command=self.mark_completed,
            style="Completed.TButton",
        )
        self.complete_button.pack(fill="x", ipady=4)

        # --- RIGHT PANEL: Notebook Tabs ---
        right_panel = ttk.Frame(main_content, style="PinkPanel.TFrame")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=1)

        self.right_tabs = ttk.Notebook(right_panel, style="Pink.TNotebook")
        self.right_tabs.grid(row=0, column=0, sticky="nsew")

        # Tab 1: Challenges
        challenges_tab = ttk.Frame(self.right_tabs, style="PinkPanel.TFrame", padding=(0, 10, 0, 0))
        # Tab 2: Manage
        manage_tab = ttk.Frame(self.right_tabs, style="PinkPanel.TFrame", padding=(0, 10, 0, 0))
        # Tab 3: Completed
        self.history_tab = ttk.Frame(self.right_tabs, style="PinkPanel.TFrame", padding=(0, 10, 0, 0))

        self.right_tabs.add(challenges_tab, text="Challenges")
        self.right_tabs.add(manage_tab, text="Manage")
        self.right_tabs.add(self.history_tab, text="Completed")

        self._build_challenges_tab(challenges_tab)
        self._build_manage_tab(manage_tab)
        self._build_completed_tab(self.history_tab)

    # 3. ELIMINATE DEAD SPACE: CHALLENGES TAB WITH FILTER PILLS
    def _build_challenges_tab(self, parent: ttk.Frame) -> None:
        """Constructs the Challenges tab with Category & Mood Filter Pills and Custom Activity form."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=1)

        # Filter Card (Dual Category and Mood Pills)
        filter_card = ttk.Frame(parent, style="PinkCard.TFrame", padding=(16, 12, 16, 12))
        filter_card.grid(row=0, column=0, sticky="ew")
        filter_card.grid_columnconfigure(0, weight=1)

        filter_header_frame = ttk.Frame(filter_card, style="PinkCard.TFrame")
        filter_header_frame.grid(row=0, column=0, sticky="ew")
        filter_header_frame.grid_columnconfigure(0, weight=1)
        filter_header_frame.grid_columnconfigure(1, weight=0)

        ttk.Label(
            filter_header_frame,
            text="Filter by Category",
            font=config.FONT_CARD_TITLE,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_DARK,
        ).grid(row=0, column=0, sticky="w")

        self.filter_count_badge = ttk.Label(
            filter_header_frame,
            text="",
            font=config.FONT_BODY_MUTED,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_SUBTITLE,
        )
        self.filter_count_badge.grid(row=0, column=1, sticky="e")

        # Category Pills Frame
        cat_pills_frame = ttk.Frame(filter_card, style="PinkCard.TFrame")
        cat_pills_frame.grid(row=1, column=0, sticky="ew", pady=(6, 8))

        for idx, cat in enumerate(self.categories):
            cat_pills_frame.grid_columnconfigure(idx, weight=1)
            btn = ttk.Button(
                cat_pills_frame,
                text=cat,
                command=lambda c=cat: self.select_category_pill(c),
                style="PillActive.TButton" if cat == "All" else "PillInactive.TButton",
            )
            btn.grid(row=0, column=idx, padx=2, sticky="ew")
            self.filter_pills[cat] = btn

        # Mood Filter Row
        ttk.Label(
            filter_card,
            text="Filter by Mood",
            font=config.FONT_CARD_TITLE,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_DARK,
        ).grid(row=2, column=0, sticky="w", pady=(2, 4))

        mood_pills_frame = ttk.Frame(filter_card, style="PinkCard.TFrame")
        mood_pills_frame.grid(row=3, column=0, sticky="ew", pady=(0, 2))

        for idx, mood in enumerate(self.moods):
            mood_pills_frame.grid_columnconfigure(idx, weight=1)
            btn = ttk.Button(
                mood_pills_frame,
                text=mood,
                command=lambda m=mood: self.select_mood_pill(m),
                style="PillActive.TButton" if mood == "All" else "PillInactive.TButton",
            )
            btn.grid(row=0, column=idx, padx=2, sticky="ew")
            self.mood_pills[mood] = btn

        # Form Card: Create Custom Activity
        custom_card = ttk.Frame(parent, style="PinkCard.TFrame", padding=(18, 14, 18, 14))
        custom_card.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        custom_card.grid_columnconfigure(0, weight=1)

        ttk.Label(
            custom_card,
            text="Create Custom Activity",
            font=config.FONT_CARD_TITLE,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_DARK,
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            custom_card,
            text="Add personalized tasks to overcome boredom anytime.",
            font=config.FONT_BODY_MUTED,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_SUBTITLE,
        ).grid(row=1, column=0, sticky="w", pady=(1, 10))

        # Title input
        ttk.Label(
            custom_card,
            text="Activity Title",
            font=config.FONT_BODY_BOLD,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_LABEL,
        ).grid(row=2, column=0, sticky="w", pady=(0, 3))

        self.custom_title = ttk.Entry(custom_card)
        self.custom_title.grid(row=3, column=0, sticky="ew", pady=(0, 8))

        # Dual row for Category and Mood dropdowns
        cat_mood_row = ttk.Frame(custom_card, style="PinkCard.TFrame")
        cat_mood_row.grid(row=4, column=0, sticky="ew", pady=(0, 8))
        cat_mood_row.grid_columnconfigure(0, weight=1)
        cat_mood_row.grid_columnconfigure(1, weight=1)

        ttk.Label(
            cat_mood_row,
            text="Category",
            font=config.FONT_BODY_BOLD,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_LABEL,
        ).grid(row=0, column=0, sticky="w", padx=(0, 4), pady=(0, 3))

        ttk.Label(
            cat_mood_row,
            text="Mood",
            font=config.FONT_BODY_BOLD,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_LABEL,
        ).grid(row=0, column=1, sticky="w", padx=(4, 0), pady=(0, 3))

        self.custom_category = ttk.Combobox(
            cat_mood_row,
            values=config.ACTIVITY_CATEGORIES,
            state="readonly",
        )
        self.custom_category.grid(row=1, column=0, sticky="ew", padx=(0, 4))
        self.custom_category.set("Indoor")

        self.custom_mood = ttk.Combobox(
            cat_mood_row,
            values=config.ACTIVITY_MOODS,
            state="readonly",
        )
        self.custom_mood.grid(row=1, column=1, sticky="ew", padx=(4, 0))
        self.custom_mood.set("Calm")

        # Duration input
        ttk.Label(
            custom_card,
            text="Duration (e.g. 5 minutes, 60 seconds)",
            font=config.FONT_BODY_BOLD,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_LABEL,
        ).grid(row=5, column=0, sticky="w", pady=(0, 3))

        self.custom_duration = ttk.Entry(custom_card)
        self.custom_duration.grid(row=6, column=0, sticky="ew", pady=(0, 10))

        # Add Activity button (High contrast Soft.TButton)
        ttk.Button(
            custom_card,
            text="➕  Add Activity to Catalog",
            command=self.add_custom_activity,
            style="Soft.TButton",
        ).grid(row=7, column=0, sticky="ew", ipady=4)

        # Pro Tip Footer to gracefully fill remaining vertical space
        tip_frame = ttk.Frame(custom_card, padding=(12, 8, 12, 8), style="StatTile.TFrame")
        tip_frame.grid(row=8, column=0, sticky="ew", pady=(14, 0))
        tip_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(
            tip_frame,
            text="💡 Quick Tip: 2-to-5 minute micro-breaks break procrastination loops and restore mental energy without cognitive friction.",
            font=config.FONT_BODY_MUTED,
            background=config.COLOR_BG_SECONDARY,
            foreground=config.COLOR_TEXT_MUTED,
            wraplength=340,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

    def select_category_pill(self, category: str) -> None:
        """Handles selecting a category filter pill and updates UI accordingly."""
        self.filter_var.set(category)
        for cat, btn in self.filter_pills.items():
            if cat == category:
                btn.configure(style="PillActive.TButton")
            else:
                btn.configure(style="PillInactive.TButton")

        self.apply_filter()

    def select_mood_pill(self, mood: str) -> None:
        """Handles selecting a mood filter pill and updates UI accordingly."""
        self.mood_var.set(mood)
        for m, btn in self.mood_pills.items():
            if m == mood:
                btn.configure(style="PillActive.TButton")
            else:
                btn.configure(style="PillInactive.TButton")

        self.apply_filter()

    # --- TAB 2: MANAGE TAB ---
    def _build_manage_tab(self, parent: ttk.Frame) -> None:
        """Constructs the Manage tab with responsive Treeview table and action buttons."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        activity_card = ttk.Frame(parent, style="PinkCard.TFrame", padding=(16, 16, 16, 14))
        activity_card.grid(row=0, column=0, sticky="nsew")
        activity_card.grid_columnconfigure(0, weight=1)
        activity_card.grid_columnconfigure(1, weight=0)
        activity_card.grid_rowconfigure(1, weight=1)

        header_frame = ttk.Frame(activity_card, style="PinkCard.TFrame")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        header_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(
            header_frame,
            text="Manage Catalog Activities",
            font=config.FONT_CARD_TITLE,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_DARK,
        ).grid(row=0, column=0, sticky="w")

        # 4. TREEVIEW CONFIGURATION (rowheight=scaled, zebra striping, selection highlights)
        self.activity_table = ttk.Treeview(
            activity_card,
            columns=("title", "category", "mood", "duration"),
            show="headings",
            style="Pink.Treeview",
            selectmode="browse",
        )
        self.activity_table.heading("title", text="Title", anchor="w")
        self.activity_table.heading("category", text="Category", anchor="w")
        self.activity_table.heading("mood", text="Mood", anchor="w")
        self.activity_table.heading("duration", text="Duration", anchor="w")

        self.activity_table.column("title", width=160, anchor="w")
        self.activity_table.column("category", width=85, anchor="w")
        self.activity_table.column("mood", width=80, anchor="w")
        self.activity_table.column("duration", width=80, anchor="w")

        # Zebra striping tags
        self.activity_table.tag_configure("evenrow", background=config.COLOR_ZEBRA_EVEN, foreground=config.COLOR_TEXT_DARK)
        self.activity_table.tag_configure("oddrow", background=config.COLOR_ZEBRA_ODD, foreground=config.COLOR_TEXT_DARK)

        table_scroll = ttk.Scrollbar(activity_card, orient="vertical", command=self.activity_table.yview)
        self.activity_table.configure(yscrollcommand=table_scroll.set)

        self.activity_table.grid(row=1, column=0, sticky="nsew")
        table_scroll.grid(row=1, column=1, sticky="ns")

        # Action Buttons Row
        button_row = ttk.Frame(activity_card, style="PinkCard.TFrame")
        button_row.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        button_row.grid_columnconfigure(0, weight=1)
        button_row.grid_columnconfigure(1, weight=1)

        ttk.Button(
            button_row,
            text="✎  Edit Activity",
            command=self.edit_selected_activity,
            style="Soft.TButton",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(
            button_row,
            text="🗑  Delete Selected",
            command=self.delete_selected_activity,
            style="Delete.TButton",
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    # 3. ELIMINATE DEAD SPACE: COMPLETED TAB WITH STATS OVERVIEW HEADER
    def _build_completed_tab(self, parent: ttk.Frame) -> None:
        """Constructs the Completed tab with Stats Overview header and completion history list."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=1)

        # Stats Overview Card
        stats_card = ttk.Frame(parent, style="PinkCard.TFrame", padding=(16, 14, 16, 14))
        stats_card.grid(row=0, column=0, sticky="ew")
        stats_card.grid_columnconfigure(0, weight=1)
        stats_card.grid_columnconfigure(1, weight=1)
        stats_card.grid_columnconfigure(2, weight=1)

        ttk.Label(
            stats_card,
            text="Progress & Insights",
            font=config.FONT_CARD_TITLE,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_DARK,
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        # Stat Tile 1: Total Completed
        tile_completed = ttk.Frame(stats_card, style="StatTile.TFrame", padding=(10, 8, 10, 8))
        tile_completed.grid(row=1, column=0, sticky="nsew", padx=(0, 4))
        tile_completed.grid_columnconfigure(0, weight=1)

        ttk.Label(tile_completed, text="Completed", font=config.FONT_STAT_LABEL, background=config.COLOR_BG_SECONDARY, foreground=config.COLOR_TEXT_SUBTITLE).grid(row=0, column=0, sticky="w")
        self.stat_completed_val = ttk.Label(tile_completed, text="0", font=config.FONT_STAT_NUM, background=config.COLOR_BG_SECONDARY, foreground=config.COLOR_TITLE_PINK)
        self.stat_completed_val.grid(row=1, column=0, sticky="w")
        ttk.Label(tile_completed, text="tiny wins unlocked", font=config.FONT_BODY_MUTED, background=config.COLOR_BG_SECONDARY, foreground=config.COLOR_TEXT_MUTED).grid(row=2, column=0, sticky="w")

        # Stat Tile 2: Top Category
        tile_top_cat = ttk.Frame(stats_card, style="StatTile.TFrame", padding=(10, 8, 10, 8))
        tile_top_cat.grid(row=1, column=1, sticky="nsew", padx=3)
        tile_top_cat.grid_columnconfigure(0, weight=1)

        ttk.Label(tile_top_cat, text="Top Focus", font=config.FONT_STAT_LABEL, background=config.COLOR_BG_SECONDARY, foreground=config.COLOR_TEXT_SUBTITLE).grid(row=0, column=0, sticky="w")
        self.stat_top_cat_val = ttk.Label(tile_top_cat, text="None yet", font=("Segoe UI", 14, "bold"), background=config.COLOR_BG_SECONDARY, foreground=config.COLOR_TEXT_MAGENTA)
        self.stat_top_cat_val.grid(row=1, column=0, sticky="w")
        ttk.Label(tile_top_cat, text="most active category", font=config.FONT_BODY_MUTED, background=config.COLOR_BG_SECONDARY, foreground=config.COLOR_TEXT_MUTED).grid(row=2, column=0, sticky="w")

        # Stat Tile 3: Available Challenges
        tile_catalog = ttk.Frame(stats_card, style="StatTile.TFrame", padding=(10, 8, 10, 8))
        tile_catalog.grid(row=1, column=2, sticky="nsew", padx=(4, 0))
        tile_catalog.grid_columnconfigure(0, weight=1)

        ttk.Label(tile_catalog, text="Catalog Size", font=config.FONT_STAT_LABEL, background=config.COLOR_BG_SECONDARY, foreground=config.COLOR_TEXT_SUBTITLE).grid(row=0, column=0, sticky="w")
        self.stat_catalog_val = ttk.Label(tile_catalog, text="25", font=config.FONT_STAT_NUM, background=config.COLOR_BG_SECONDARY, foreground=config.COLOR_TITLE_PINK)
        self.stat_catalog_val.grid(row=1, column=0, sticky="w")
        ttk.Label(tile_catalog, text="ready challenges", font=config.FONT_BODY_MUTED, background=config.COLOR_BG_SECONDARY, foreground=config.COLOR_TEXT_MUTED).grid(row=2, column=0, sticky="w")

        # History List Card
        history_card = ttk.Frame(parent, style="PinkCard.TFrame", padding=(16, 16, 16, 14))
        history_card.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        history_card.grid_columnconfigure(0, weight=1)
        history_card.grid_columnconfigure(1, weight=0)
        history_card.grid_rowconfigure(1, weight=1)

        header_row = ttk.Frame(history_card, style="PinkCard.TFrame")
        header_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        header_row.grid_columnconfigure(0, weight=1)
        header_row.grid_columnconfigure(1, weight=0)

        ttk.Label(
            header_row,
            text="Completed Challenges Log",
            font=config.FONT_CARD_TITLE,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_DARK,
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            header_row,
            text="Clear History",
            command=self.clear_history,
            style="Soft.TButton",
        ).grid(row=0, column=1, sticky="e")

        # 4. LISTBOX SELECTION HIGHLIGHTS (selectbackground="#FFD1DC", selectforeground="#2C1820")
        self.history_list = tk.Listbox(
            history_card,
            bg=config.COLOR_TREEVIEW_BG,
            fg=config.COLOR_TEXT_DARK,
            selectbackground=config.COLOR_SELECTION_BG,
            selectforeground=config.COLOR_SELECTION_FG,
            bd=0,
            activestyle="none",
            highlightthickness=0,
            font=config.FONT_BODY,
        )
        history_scrollbar = ttk.Scrollbar(history_card, orient="vertical", command=self.history_list.yview)
        self.history_list.configure(yscrollcommand=history_scrollbar.set)

        self.history_list.grid(row=1, column=0, sticky="nsew")
        history_scrollbar.grid(row=1, column=1, sticky="ns")

        self.history_empty_label = ttk.Label(
            history_card,
            text="No completed challenges yet.\nFinish any challenge on the left and it will appear here!",
            justify="center",
            background=config.COLOR_TREEVIEW_BG,
            foreground=config.COLOR_TEXT_SUBTITLE,
            font=config.FONT_BODY,
        )
        self.history_empty_label.grid(row=1, column=0, columnspan=2, sticky="nsew")

    def _on_resize(self, event: Optional[tk.Event] = None) -> None:
        """Handles window resize by redrawing canvas elements."""
        self.mascot_canvas.draw()

    # --- Activity & Filter Actions ---
    def apply_filter(self, event: Optional[tk.Event] = None) -> None:
        """Applies active category and mood filters to view and activity table."""
        self.refresh_activity()
        self.refresh_activity_table()
        self._update_filter_badge()

    def _update_filter_badge(self) -> None:
        """Updates the indicator count on the filter header with category and mood."""
        cat = self.filter_var.get()
        mood = self.mood_var.get()
        options = self.data_manager.get_filtered_activities(category=cat, mood=mood)
        count = len(options)

        parts = []
        if cat != "All":
            parts.append(cat)
        if mood != "All":
            parts.append(mood)

        if not parts:
            label_text = f"Showing all {count} tasks"
        else:
            filter_desc = " · ".join(parts)
            label_text = f"Showing {count} tasks ({filter_desc})"

        self.filter_count_badge.configure(text=label_text)

    def refresh_activity(self) -> None:
        """Selects and displays a random activity matching active Category and Mood."""
        category = self.filter_var.get()
        mood = self.mood_var.get()
        options = self.data_manager.get_filtered_activities(category=category, mood=mood)
        self._update_filter_badge()

        if not options:
            self.current_activity = None
            self.activity_title.configure(text="No matching activities")
            filter_desc = f"{category} + {mood}" if (category != "All" or mood != "All") else "selected filters"
            self.activity_meta.configure(text=f"No challenge found for {filter_desc}. Switch a filter or add one!")
            self.timer_total = 0
            self.timer_seconds = 0
            self.refresh_timer_display()
            self.update_motivation(f"No activities match {filter_desc}. Try switching category or mood.")
            return

        self.current_activity = random.choice(options)
        self.activity_title.configure(text=self.current_activity["title"])
        act_mood = self.current_activity.get("mood", "Calm")
        self.activity_meta.configure(
            text=f"Category: {self.current_activity['category']}   ·   Mood: {act_mood}   ·   Duration: {self.current_activity['duration']}"
        )
        self.timer_total = self.data_manager.parse_duration(self.current_activity["duration"])
        self.timer_seconds = 0
        self.refresh_timer_display()

        if self.timer_running:
            self.pause_timer()
        self.update_motivation("Fresh challenge unlocked. You are one move away from a better mood.")

    def refresh_activity_table(self) -> None:
        """Refreshes the Treeview with clean zebra-striped rows including Mood."""
        for item in self.activity_table.get_children():
            self.activity_table.delete(item)

        category = self.filter_var.get()
        mood = self.mood_var.get()
        rows = self.data_manager.get_filtered_activities(category=category, mood=mood)
        for idx, activity in enumerate(rows):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.activity_table.insert(
                "", "end",
                values=(
                    activity["title"],
                    activity["category"],
                    activity.get("mood", "Calm"),
                    activity["duration"],
                ),
                tags=(tag,),
            )

    # --- Timer Operations ---
    def start_timer(self) -> None:
        """Starts countdown for the current challenge."""
        if self.current_activity is None:
            self.update_motivation("Pick a challenge before starting the timer.")
            return
        if self.timer_running:
            return

        self.timer_running = True
        self.timer_total = self.data_manager.parse_duration(self.current_activity["duration"])
        if self.timer_seconds >= self.timer_total:
            self.timer_seconds = 0
        if self.timer_seconds > 0:
            self.update_motivation("Resuming countdown. Keep going!")
        else:
            self.update_motivation("You’ve got this. One tiny step at a time.")
        self.schedule_timer_tick()

    def pause_timer(self) -> None:
        """Pauses the active countdown."""
        if not self.timer_running:
            return
        self.timer_running = False
        if self.timer_after is not None:
            self.after_cancel(self.timer_after)
            self.timer_after = None
        self.update_motivation("Paused. Take a breath and jump back in when ready.")
        self.refresh_timer_display()

    def reset_timer(self) -> None:
        """Resets the timer back to challenge duration."""
        if self.timer_after is not None:
            self.after_cancel(self.timer_after)
            self.timer_after = None
        self.timer_running = False
        self.timer_seconds = 0
        self.timer_total = self.data_manager.parse_duration(self.current_activity["duration"]) if self.current_activity else 0
        self.refresh_timer_display()
        self.update_motivation("The timer is ready when you are.")

    def schedule_timer_tick(self) -> None:
        """Schedules tick callback in 1 second."""
        self.timer_after = self.after(1000, self.tick_timer)

    def tick_timer(self) -> None:
        """Advances timer and updates display."""
        if not self.timer_running:
            return

        self.timer_seconds += 1
        remaining = self.timer_total - self.timer_seconds
        self.refresh_timer_display()

        if remaining <= 0:
            self.timer_running = False
            self.timer_seconds = self.timer_total
            self.update_motivation("Time’s up! Nice work. Pick the next tiny win.")
            if self.timer_after is not None:
                self.after_cancel(self.timer_after)
                self.timer_after = None
            return

        self.schedule_timer_tick()

    def refresh_timer_display(self) -> None:
        """Updates the timer label with formatted MM:SS string."""
        if self.current_activity is None:
            self.timer_label.configure(text="00:00")
            return

        total = self.data_manager.parse_duration(self.current_activity["duration"])
        if self.timer_total == 0:
            self.timer_total = total
        remaining = max(self.timer_total - self.timer_seconds, 0)
        self.timer_label.configure(text=self.data_manager.format_seconds(remaining))

    # --- Completion & History Operations ---
    def mark_completed(self) -> None:
        """Records the active challenge as completed and updates views."""
        if self.current_activity is None:
            self.update_motivation("There is no active challenge to complete.")
            return

        self.data_manager.add_completed(self.current_activity)
        self.update_history_view()
        self.right_tabs.select(self.history_tab)
        self.pause_timer()
        self.update_motivation("Challenge complete! That counts as momentum.")

    def update_history_view(self) -> None:
        """Refreshes completion list and updates Stats Overview header."""
        self.history_list.delete(0, tk.END)
        for item in self.data_manager.completed_history[:50]:
            label = f"{item.get('title', 'Untitled')}   ·   {item.get('category', '—')}   ·   {item.get('completed_at', 'Unknown')}"
            self.history_list.insert(tk.END, label)

        count = len(self.data_manager.completed_history)
        self.right_tabs.tab(self.history_tab, text=f"Completed ({count})")

        if count > 0:
            self.history_list.tkraise()
        else:
            self.history_empty_label.tkraise()

        # Update Stats Overview Header
        stats = self.data_manager.get_stats()
        self.stat_completed_val.configure(text=str(stats["total_completed"]))
        top_cat_display = stats["top_category"]
        if stats["top_category_count"] > 0:
            top_cat_display = f"{stats['top_category']} ({stats['top_category_count']})"
        self.stat_top_cat_val.configure(text=top_cat_display)
        self.stat_catalog_val.configure(text=str(stats["total_activities"]))

    def clear_history(self) -> None:
        """Clears completed challenges history."""
        self.data_manager.clear_history()
        self.update_history_view()
        self.update_motivation("History cleared. Fresh start, same spark.")

    # --- Custom Activity & Management Operations ---
    def add_custom_activity(self) -> None:
        """Adds a new activity from the custom challenge form with category and mood."""
        title = self.custom_title.get().strip()
        category = self.custom_category.get().strip() or "Indoor"
        mood = self.custom_mood.get().strip() or "Calm"
        duration = self.custom_duration.get().strip() or "5 minutes"

        if not title:
            self.update_motivation("Give your activity a title so it can be added.")
            return

        activity = self.data_manager.add_custom_activity(title, category, duration, mood)
        if not activity:
            self.update_motivation("Invalid activity details. Please try again.")
            return

        self.custom_title.delete(0, tk.END)
        self.custom_duration.delete(0, tk.END)
        self.custom_category.set("Indoor")
        self.custom_mood.set("Calm")
        self.update_motivation(f"Added '{title}' ({mood}) to your custom collection.")
        self.apply_filter()
        self.update_history_view()

    def edit_selected_activity(self) -> None:
        """Opens editor dialog for the selected Treeview item."""
        selection = self.activity_table.selection()
        if not selection:
            self.update_motivation("Select an activity first to edit it.")
            return

        values = self.activity_table.item(selection[0], "values")
        activity = {
            "title": str(values[0]),
            "category": str(values[1]),
            "mood": str(values[2]),
            "duration": str(values[3]),
        }
        self.open_activity_editor(activity)

    def delete_selected_activity(self) -> None:
        """Deletes the selected activity from the catalog."""
        selection = self.activity_table.selection()
        if not selection:
            self.update_motivation("Select an activity to delete.")
            return

        values = self.activity_table.item(selection[0], "values")
        activity = {
            "title": str(values[0]),
            "category": str(values[1]),
            "mood": str(values[2]),
            "duration": str(values[3]),
        }
        if not self.data_manager.remove_activity(activity):
            self.update_motivation("That activity could not be found for deletion.")
            return

        self.refresh_activity_table()
        self.refresh_activity()
        self.update_history_view()
        self.update_motivation(f"Deleted '{activity['title']}' from your activity list.")

    def open_activity_editor(self, activity: Dict[str, str]) -> None:
        """Displays modal dialog for editing an existing activity including category and mood."""
        popup = tk.Toplevel(self)
        popup.title("Edit Activity")
        popup.geometry("440x430")
        popup.minsize(390, 390)
        popup.configure(bg=config.COLOR_BG_MAIN)
        popup.transient(self)
        popup.grab_set()

        frame = ttk.Frame(popup, padding=20, style="PinkCard.TFrame")
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        frame.grid_columnconfigure(0, weight=1)

        ttk.Label(
            frame,
            text="Edit Activity Details",
            font=config.FONT_CARD_TITLE,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_DARK,
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        ttk.Label(
            frame,
            text="Title",
            font=config.FONT_BODY_BOLD,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_LABEL,
        ).grid(row=1, column=0, sticky="w", pady=(0, 4))
        title_entry = ttk.Entry(frame)
        title_entry.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        title_entry.insert(0, activity.get("title", ""))

        ttk.Label(
            frame,
            text="Category",
            font=config.FONT_BODY_BOLD,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_LABEL,
        ).grid(row=3, column=0, sticky="w", pady=(0, 4))
        category_combo = ttk.Combobox(
            frame,
            values=config.ACTIVITY_CATEGORIES,
            state="readonly",
        )
        category_combo.grid(row=4, column=0, sticky="ew", pady=(0, 8))
        category_combo.set(activity.get("category", "Indoor"))

        ttk.Label(
            frame,
            text="Mood",
            font=config.FONT_BODY_BOLD,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_LABEL,
        ).grid(row=5, column=0, sticky="w", pady=(0, 4))
        mood_combo = ttk.Combobox(
            frame,
            values=config.ACTIVITY_MOODS,
            state="readonly",
        )
        mood_combo.grid(row=6, column=0, sticky="ew", pady=(0, 8))
        mood_combo.set(activity.get("mood", "Calm"))

        ttk.Label(
            frame,
            text="Duration",
            font=config.FONT_BODY_BOLD,
            background=config.COLOR_BG_CARD,
            foreground=config.COLOR_TEXT_LABEL,
        ).grid(row=7, column=0, sticky="w", pady=(0, 4))
        duration_entry = ttk.Entry(frame)
        duration_entry.grid(row=8, column=0, sticky="ew", pady=(0, 14))
        duration_entry.insert(0, activity.get("duration", "5 minutes"))

        buttons = ttk.Frame(frame, style="PinkCard.TFrame")
        buttons.grid(row=9, column=0, sticky="ew")
        buttons.grid_columnconfigure(0, weight=1)
        buttons.grid_columnconfigure(1, weight=1)

        def save_edit() -> None:
            updated_title = title_entry.get().strip()
            updated_category = category_combo.get().strip() or "Indoor"
            updated_mood = mood_combo.get().strip() or "Calm"
            updated_duration = duration_entry.get().strip() or "5 minutes"

            if not updated_title:
                self.update_motivation("Activity title cannot be blank.")
                return

            new_activity = {
                "title": updated_title,
                "category": updated_category,
                "mood": updated_mood,
                "duration": updated_duration,
            }
            self.data_manager.edit_activity(activity, new_activity)
            self.refresh_activity_table()
            self.refresh_activity()
            self.update_history_view()
            popup.destroy()
            self.update_motivation(f"Updated '{updated_title}' in your catalog.")

        ttk.Button(buttons, text="Save Changes", command=save_edit, style="Accent.TButton").grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        ttk.Button(buttons, text="Cancel", command=popup.destroy, style="Soft.TButton").grid(
            row=0, column=1, sticky="ew", padx=(6, 0)
        )

        popup.bind("<Escape>", lambda event: popup.destroy())

    # --- Backward-Compatibility Delegation Methods ---
    @property
    def completed_history(self) -> List[Dict[str, Any]]:
        return self.data_manager.completed_history

    @completed_history.setter
    def completed_history(self, value: List[Dict[str, Any]]) -> None:
        self.data_manager.completed_history = value

    @property
    def custom_activities(self) -> List[Dict[str, str]]:
        return self.data_manager.custom_activities

    @custom_activities.setter
    def custom_activities(self, value: List[Dict[str, str]]) -> None:
        self.data_manager.custom_activities = value

    @property
    def default_activities(self) -> List[Dict[str, str]]:
        return self.data_manager.default_activities

    @default_activities.setter
    def default_activities(self, value: List[Dict[str, str]]) -> None:
        self.data_manager.default_activities = value

    def normalize_activity(self, activity: Any) -> Optional[Dict[str, str]]:
        return self.data_manager.normalize_activity(activity)

    def normalize_activity_list(self, activities: Any) -> List[Dict[str, str]]:
        return self.data_manager.normalize_activity_list(activities)

    def get_all_activities(self) -> List[Dict[str, str]]:
        return self.data_manager.get_all_activities()

    def get_filtered_activities(self, category: str = "All", mood: str = "All") -> List[Dict[str, str]]:
        return self.data_manager.get_filtered_activities(category, mood)

    def edit_activity(self, original: Dict[str, str], replacement: Dict[str, str]) -> bool:
        return self.data_manager.edit_activity(original, replacement)

    def replace_activity(self, original: Dict[str, str], replacement: Dict[str, str]) -> bool:
        return self.data_manager.edit_activity(original, replacement)

    def load_data(self) -> bool:
        return self.data_manager.load_data()

    def save_data(self) -> bool:
        return self.data_manager.save_data()

    def parse_duration(self, duration_text: Any) -> int:
        return self.data_manager.parse_duration(duration_text)

    def format_seconds(self, total_seconds: int) -> str:
        return self.data_manager.format_seconds(total_seconds)

    def matches_activity(self, first: Any, second: Any) -> bool:
        return self.data_manager.matches_activity(first, second)

    def replace_activity(self, original: Dict[str, str], replacement: Dict[str, str]) -> bool:
        return self.data_manager.replace_activity(original, replacement)

    def remove_activity(self, activity: Dict[str, str]) -> bool:
        return self.data_manager.remove_activity(activity)

    def update_motivation(self, text: str) -> None:
        """Sets the motivational banner message."""
        self.motivation_var.set(text)

    def run(self) -> None:
        """Enters the main application event loop."""
        self.mainloop()


if __name__ == "__main__":
    app = Application()
    app.run()


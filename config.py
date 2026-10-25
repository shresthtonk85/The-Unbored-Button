"""Configuration and constants for The Unbored Button application."""
import ctypes
import os


def enable_high_dpi_awareness() -> None:
    """Enables per-monitor DPI awareness on Windows to prevent blurry/pixelated scaling."""
    if os.name != "nt":
        return

    try:
        # Windows 10 v1703+ and Windows 11: Per-Monitor V2
        # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        return
    except (AttributeError, OSError):
        pass

    try:
        # Windows 8.1 / Windows 10 early builds
        # PROCESS_PER_MONITOR_DPI_AWARE = 2
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return
    except (AttributeError, OSError):
        pass

    try:
        # Windows Vista / 7
        ctypes.windll.user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass


# --- Window Configuration ---
APP_TITLE = "The Unbored Button"
DEFAULT_GEOMETRY = "1080x820"
MIN_WINDOW_WIDTH = 920
MIN_WINDOW_HEIGHT = 700

# --- Color Palette ---
# Backgrounds
COLOR_BG_MAIN = "#FFF0F5"         # Soft lavender blush window background
COLOR_BG_CARD = "#FFFFFF"         # Pure white card surface
COLOR_BG_PANEL = "#FFEFF3"        # Soft rose panel background
COLOR_BG_SECONDARY = "#FFF4F8"    # Light pink for secondary buttons & combo fields
COLOR_BG_HOVER = "#FFE4EF"        # Hover state for secondary elements
COLOR_BG_ACTIVE = "#FFD1DC"       # Pressed/active state

# Hero & Completion Accents
COLOR_HERO_BG = "#FF69B4"         # Hot pink hero button background
COLOR_HERO_HOVER = "#FF5C8D"      # Hot pink hero hover
COLOR_HERO_FG = "#FFFFFF"         # Crisp white text for hero button
COLOR_COMPLETED_BG = "#FFEFF3"    # Soft accent background for "Mark as Completed"
COLOR_COMPLETED_HOVER = "#FFE0E8" # Hover for "Mark as Completed"
COLOR_COMPLETED_BORDER = "#C71585"# Solid deep magenta border
COLOR_COMPLETED_FG = "#C71585"    # High-contrast deep magenta text

# High-Contrast Text Colors
COLOR_TEXT_DARK = "#2C1820"       # Dark plum - crisp, high-contrast primary text
COLOR_TEXT_MAGENTA = "#C71585"    # Deep magenta - high-contrast accent text
COLOR_TEXT_PRIMARY = "#333333"    # Charcoal text
COLOR_TEXT_MUTED = "#725A6F"      # Muted plum for hints and quotes
COLOR_TEXT_SUBTITLE = "#8B5F7A"   # Medium plum for subtitles
COLOR_TEXT_LABEL = "#5B4966"      # Plum for field labels
COLOR_TITLE_PINK = "#D81B60"      # Vivid raspberry pink for main titles & timer

# Selection & Table Colors
COLOR_SELECTION_BG = "#FFD1DC"    # Soft pink selection highlight for Treeview & Listbox
COLOR_SELECTION_FG = "#2C1820"    # Dark plum text on selection
COLOR_ZEBRA_EVEN = "#FFFFFF"      # White alternating rows
COLOR_ZEBRA_ODD = "#FFF5F8"       # Very light pink alternating rows
COLOR_TREEVIEW_BG = "#FFF9FB"     # Treeview default background
COLOR_TREEVIEW_HEADER = "#FF69B4" # Hot pink header for table
COLOR_TREEVIEW_HEADER_FG = "#FFFFFF"

# Borders & Details
COLOR_BORDER_LIGHT = "#FFD1DC"
COLOR_BORDER_MEDIUM = "#FFB6C1"
COLOR_BORDER_FOCUS = "#C71585"


# --- Asset Paths ---
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo_200.png")
LOGO_HEADER_PATH = os.path.join(ASSETS_DIR, "logo_36.png")
LOGO_ICON_PATH = os.path.join(ASSETS_DIR, "logo_icon.png")
LOGO_ORIGINAL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")

# Mascot Palette
COLOR_MASCOT_OUTLINE = "#111111"
COLOR_MASCOT_BOW = "#FF5C8D"
COLOR_MASCOT_EARS = "#F8C7D8"
COLOR_MASCOT_NOSE = "#FFD700"
COLOR_MASCOT_NOSE_BORDER = "#E0B000"
COLOR_MASCOT_BODY = "#F8D7E6"

# --- Typography ---
FONT_APP_TITLE = ("Segoe UI", 24, "bold")
FONT_SUBTITLE = ("Segoe UI", 11)
FONT_CARD_TITLE = ("Segoe UI", 12, "bold")
FONT_ACTIVITY_TITLE = ("Segoe UI", 18, "bold")
FONT_TIMER = ("Segoe UI", 28, "bold")
FONT_QUOTE = ("Segoe UI", 11, "italic")
FONT_BODY = ("Segoe UI", 10)
FONT_BODY_BOLD = ("Segoe UI", 10, "bold")
FONT_BODY_MUTED = ("Segoe UI", 9)
FONT_BUTTON_HERO = ("Segoe UI", 13, "bold")
FONT_BUTTON_COMPLETED = ("Segoe UI", 11, "bold")
FONT_BUTTON_SECONDARY = ("Segoe UI", 10, "bold")
FONT_PILL = ("Segoe UI", 9, "bold")
FONT_STAT_NUM = ("Segoe UI", 20, "bold")
FONT_STAT_LABEL = ("Segoe UI", 9, "bold")



# --- UI Dimensions ---
TREEVIEW_ROW_HEIGHT = 28

# --- Categories & Moods ---
CATEGORIES = ["All", "Indoor", "Outdoor", "Creative", "Relaxing"]
ACTIVITY_CATEGORIES = ["Indoor", "Outdoor", "Creative", "Relaxing"]

MOODS = ["All", "Energetic", "Calm", "Focused", "Playful", "Cozy"]
ACTIVITY_MOODS = ["Energetic", "Calm", "Focused", "Playful", "Cozy"]

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "boredom_data.json")

# --- Expanded Seed Data (84 Micro-Challenges: 21 per category) ---
DEFAULT_ACTIVITIES = [
    # --- INDOOR (21 tasks) ---
    {"title": "Learn a new magic coin trick", "category": "Indoor", "duration": "5 minutes", "mood": "Playful"},
    {"title": "Organize one bookshelf row by color", "category": "Indoor", "duration": "7 minutes", "mood": "Focused"},
    {"title": "Do a 5-minute dynamic stretching routine", "category": "Indoor", "duration": "5 minutes", "mood": "Energetic"},
    {"title": "Tidy up your desk space and cables", "category": "Indoor", "duration": "5 minutes", "mood": "Focused"},
    {"title": "Clean one small surface in your room", "category": "Indoor", "duration": "4 minutes", "mood": "Focused"},
    {"title": "Do 20 jumping jacks and 10 wall push-ups", "category": "Indoor", "duration": "3 minutes", "mood": "Energetic"},
    {"title": "Wipe down your phone and keyboard screen", "category": "Indoor", "duration": "3 minutes", "mood": "Focused"},
    {"title": "Make a cozy warm mug of herbal tea", "category": "Indoor", "duration": "5 minutes", "mood": "Cozy"},
    {"title": "Fluff your pillows and straighten your bed", "category": "Indoor", "duration": "3 minutes", "mood": "Cozy"},
    {"title": "Learn to juggle with three small rolled socks", "category": "Indoor", "duration": "6 minutes", "mood": "Playful"},
    {"title": "Put on upbeat music and do a 2-minute dance break", "category": "Indoor", "duration": "2 minutes", "mood": "Energetic"},
    {"title": "Water your indoor plants and wipe their leaves", "category": "Indoor", "duration": "4 minutes", "mood": "Calm"},
    {"title": "Sort through and delete 20 old phone screenshots", "category": "Indoor", "duration": "5 minutes", "mood": "Focused"},
    {"title": "Practice balancing on one foot for 60 seconds each side", "category": "Indoor", "duration": "2 minutes", "mood": "Energetic"},
    {"title": "Fold 5 items of clothing neatly", "category": "Indoor", "duration": "4 minutes", "mood": "Focused"},
    {"title": "Build a mini house of cards or coaster tower", "category": "Indoor", "duration": "5 minutes", "mood": "Playful"},
    {"title": "Dim the lights and light a scented candle or incense", "category": "Indoor", "duration": "3 minutes", "mood": "Cozy"},
    {"title": "Do a slow neck and shoulder tension release", "category": "Indoor", "duration": "4 minutes", "mood": "Calm"},
    {"title": "Clean out your wallet or pencil case", "category": "Indoor", "duration": "5 minutes", "mood": "Focused"},
    {"title": "Test your reflexes with an online speed test", "category": "Indoor", "duration": "3 minutes", "mood": "Playful"},
    {"title": "Wrap yourself in a blanket and listen to rain sounds", "category": "Indoor", "duration": "6 minutes", "mood": "Cozy"},

    # --- OUTDOOR (21 tasks) ---
    {"title": "Go for a short 5-minute brisk walk", "category": "Outdoor", "duration": "5 minutes", "mood": "Energetic"},
    {"title": "Take a macro photo of an interesting leaf or flower", "category": "Outdoor", "duration": "6 minutes", "mood": "Focused"},
    {"title": "Step outside and take 10 deep belly breaths", "category": "Outdoor", "duration": "2 minutes", "mood": "Calm"},
    {"title": "Look up at the clouds and find 3 recognizable shapes", "category": "Outdoor", "duration": "4 minutes", "mood": "Playful"},
    {"title": "Sit outside and close your eyes to notice 5 sounds", "category": "Outdoor", "duration": "3 minutes", "mood": "Calm"},
    {"title": "Do a quick sprint or jog down the block and back", "category": "Outdoor", "duration": "3 minutes", "mood": "Energetic"},
    {"title": "Find smooth stones and stack a 4-stone balance cairn", "category": "Outdoor", "duration": "5 minutes", "mood": "Focused"},
    {"title": "Feel sunlight or fresh wind on your face for 3 minutes", "category": "Outdoor", "duration": "3 minutes", "mood": "Cozy"},
    {"title": "Wave or smile at a neighbor or passerby", "category": "Outdoor", "duration": "1 minute", "mood": "Playful"},
    {"title": "Touch the bark of a nearby tree and notice its texture", "category": "Outdoor", "duration": "2 minutes", "mood": "Calm"},
    {"title": "Look for 3 different types of birds in your area", "category": "Outdoor", "duration": "5 minutes", "mood": "Focused"},
    {"title": "Do 10 calf raises on a stair or sidewalk curb", "category": "Outdoor", "duration": "2 minutes", "mood": "Energetic"},
    {"title": "Find a natural object that fits in your palm to keep", "category": "Outdoor", "duration": "4 minutes", "mood": "Playful"},
    {"title": "Check the temperature and observe current weather cues", "category": "Outdoor", "duration": "2 minutes", "mood": "Focused"},
    {"title": "Walk barefoot on grass or a clean patio surface", "category": "Outdoor", "duration": "4 minutes", "mood": "Calm"},
    {"title": "Take a photo of your shadow in an artistic pose", "category": "Outdoor", "duration": "3 minutes", "mood": "Playful"},
    {"title": "Sit on a bench with a warm sweater or jacket", "category": "Outdoor", "duration": "6 minutes", "mood": "Cozy"},
    {"title": "Find something in nature colored bright yellow or red", "category": "Outdoor", "duration": "3 minutes", "mood": "Playful"},
    {"title": "Do gentle arm circles while gazing toward the horizon", "category": "Outdoor", "duration": "3 minutes", "mood": "Energetic"},
    {"title": "Watch leaves swaying in the breeze without checking time", "category": "Outdoor", "duration": "4 minutes", "mood": "Calm"},
    {"title": "Find a cozy sunny spot outside and soak in warmth", "category": "Outdoor", "duration": "5 minutes", "mood": "Cozy"},

    # --- CREATIVE (21 tasks) ---
    {"title": "Draw something silly in 60 seconds", "category": "Creative", "duration": "60 seconds", "mood": "Playful"},
    {"title": "Make an aerodynamic paper plane and test fly it", "category": "Creative", "duration": "5 minutes", "mood": "Playful"},
    {"title": "Write a 3-line haiku or poem about your day", "category": "Creative", "duration": "4 minutes", "mood": "Focused"},
    {"title": "Origami a simple jumping frog from paper", "category": "Creative", "duration": "8 minutes", "mood": "Playful"},
    {"title": "Doodle your favorite comfort food in cute cartoon style", "category": "Creative", "duration": "3 minutes", "mood": "Playful"},
    {"title": "Design a custom decorated bookmark with highlighters", "category": "Creative", "duration": "8 minutes", "mood": "Focused"},
    {"title": "Make a tiny origami paper heart", "category": "Creative", "duration": "4 minutes", "mood": "Cozy"},
    {"title": "Write down 3 tiny things that brought you unexpected joy", "category": "Creative", "duration": "4 minutes", "mood": "Cozy"},
    {"title": "Sketch a simple everyday object nearby with continuous line", "category": "Creative", "duration": "6 minutes", "mood": "Focused"},
    {"title": "Invent an imaginary animal and write its 2 superpower traits", "category": "Creative", "duration": "5 minutes", "mood": "Playful"},
    {"title": "Write a micro flash-fiction story in exactly 50 words", "category": "Creative", "duration": "7 minutes", "mood": "Focused"},
    {"title": "Compose a funny rhyming couplet about boredom", "category": "Creative", "duration": "3 minutes", "mood": "Playful"},
    {"title": "Draw your mood right now as an abstract colorful pattern", "category": "Creative", "duration": "5 minutes", "mood": "Calm"},
    {"title": "Create a playlist title and pick 3 dream tracks for it", "category": "Creative", "duration": "4 minutes", "mood": "Energetic"},
    {"title": "Design a cool personal signature or monogram logo", "category": "Creative", "duration": "5 minutes", "mood": "Focused"},
    {"title": "Write a postcard message to your future self 1 year ahead", "category": "Creative", "duration": "6 minutes", "mood": "Cozy"},
    {"title": "Fold a paper fortune teller with 4 fun surprise actions", "category": "Creative", "duration": "7 minutes", "mood": "Playful"},
    {"title": "Take 3 photos from unusual angles (worms-eye or birds-eye)", "category": "Creative", "duration": "4 minutes", "mood": "Playful"},
    {"title": "Sketch a cartoon avatar of yourself with an oversized hat", "category": "Creative", "duration": "5 minutes", "mood": "Playful"},
    {"title": "Write down 5 creative dream goals with zero judgment", "category": "Creative", "duration": "5 minutes", "mood": "Energetic"},
    {"title": "Color in a doodle page with pastel or neon color scheme", "category": "Creative", "duration": "6 minutes", "mood": "Cozy"},

    # --- RELAXING (21 tasks) ---
    {"title": "Listen to your absolute favorite relaxing song with eyes closed", "category": "Relaxing", "duration": "5 minutes", "mood": "Calm"},
    {"title": "Drink a glass of cold water slowly and mindfully", "category": "Relaxing", "duration": "2 minutes", "mood": "Calm"},
    {"title": "Close your eyes and listen to quiet lo-fi beats for 3 minutes", "category": "Relaxing", "duration": "3 minutes", "mood": "Calm"},
    {"title": "Take a short full-body stretch and breathe deeply", "category": "Relaxing", "duration": "3 minutes", "mood": "Calm"},
    {"title": "Learn 1 beautiful new word in a foreign language", "category": "Relaxing", "duration": "3 minutes", "mood": "Focused"},
    {"title": "Take a mindful tea or warm water break without screens", "category": "Relaxing", "duration": "5 minutes", "mood": "Cozy"},
    {"title": "Do 4-7-8 relaxing breathing: Inhale 4s, hold 7s, exhale 8s", "category": "Relaxing", "duration": "3 minutes", "mood": "Calm"},
    {"title": "Rub your palms together until warm and rest them on your eyes", "category": "Relaxing", "duration": "2 minutes", "mood": "Calm"},
    {"title": "Massage your temples and jawline with gentle circular motions", "category": "Relaxing", "duration": "3 minutes", "mood": "Calm"},
    {"title": "Read 2 pages of a favorite physical book slowly", "category": "Relaxing", "duration": "5 minutes", "mood": "Cozy"},
    {"title": "Gently stretch your wrists and fingers to release typing strain", "category": "Relaxing", "duration": "2 minutes", "mood": "Calm"},
    {"title": "Look away from screens and focus on an object 20 feet away", "category": "Relaxing", "duration": "2 minutes", "mood": "Focused"},
    {"title": "Snuggle into your chair with relaxed posture and deep exhale", "category": "Relaxing", "duration": "3 minutes", "mood": "Cozy"},
    {"title": "Listen to peaceful ambient nature sounds (ocean or forest)", "category": "Relaxing", "duration": "5 minutes", "mood": "Calm"},
    {"title": "Roll your shoulders backward 10 times and forward 10 times", "category": "Relaxing", "duration": "2 minutes", "mood": "Energetic"},
    {"title": "Write down one worry on paper, crumple it, and toss it away", "category": "Relaxing", "duration": "3 minutes", "mood": "Playful"},
    {"title": "Hold a warm mug with both hands and enjoy the warmth", "category": "Relaxing", "duration": "3 minutes", "mood": "Cozy"},
    {"title": "Do a 3-minute progressive muscle relaxation from toes to head", "category": "Relaxing", "duration": "4 minutes", "mood": "Calm"},
    {"title": "Put your legs up on a couch or chair for quick circulation reset", "category": "Relaxing", "duration": "5 minutes", "mood": "Calm"},
    {"title": "Think of one person you appreciate and send a sweet 1-line text", "category": "Relaxing", "duration": "2 minutes", "mood": "Cozy"},
    {"title": "Practice quiet gratitude: identify 3 things going well right now", "category": "Relaxing", "duration": "3 minutes", "mood": "Calm"},
]

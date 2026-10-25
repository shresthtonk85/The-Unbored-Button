"""Data persistence and activity management for The Unbored Button."""
import json
import os
import time
from typing import Any, Dict, List, Optional

import config


class DataManager:
    """Handles loading, saving, normalization, and stats for activities and completion history."""

    def __init__(self, data_file: Optional[str] = None, default_activities: Optional[List[Dict[str, str]]] = None):
        self.data_file = data_file or config.DATA_FILE
        self.default_activities = list(default_activities if default_activities is not None else config.DEFAULT_ACTIVITIES)
        self.custom_activities: List[Dict[str, str]] = []
        self.completed_history: List[Dict[str, Any]] = []
        self.last_error: Optional[str] = None
        self.load_data()

    @staticmethod
    def normalize_activity(activity: Any) -> Optional[Dict[str, str]]:
        """Validates and trims activity fields with mood support and backward compatibility."""
        if not isinstance(activity, dict):
            return None
        title = str(activity.get("title", "")).strip()
        category = str(activity.get("category", "")).strip() or "Indoor"
        duration = str(activity.get("duration", "")).strip() or "5 minutes"
        mood = str(activity.get("mood", "")).strip() or "Calm"
        if not title:
            return None
        return {"title": title, "category": category, "duration": duration, "mood": mood}

    @classmethod
    def normalize_activity_list(cls, activities: Any) -> List[Dict[str, str]]:
        """Deduplicates and cleans a list of activities."""
        if not isinstance(activities, list):
            return []
        cleaned: List[Dict[str, str]] = []
        seen = set()
        for activity in activities:
            normalized = cls.normalize_activity(activity)
            if normalized is None:
                continue
            key = (
                normalized["title"].lower(),
                normalized["category"].lower(),
                normalized["duration"].lower(),
                normalized["mood"].lower(),
            )
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(normalized)
        return cleaned

    def get_all_activities(self) -> List[Dict[str, str]]:
        """Combines default and custom activities without duplicates."""
        return self.normalize_activity_list(self.default_activities + self.custom_activities)

    def get_filtered_activities(self, category: str = "All", mood: str = "All") -> List[Dict[str, str]]:
        """Returns activities matching category AND mood simultaneously."""
        activities = self.get_all_activities()
        filtered: List[Dict[str, str]] = []
        for entry in activities:
            cat_match = not category or category == "All" or entry.get("category") == category
            mood_match = not mood or mood == "All" or entry.get("mood") == mood
            if cat_match and mood_match:
                filtered.append(entry)
        return filtered

    def load_data(self) -> bool:
        """Loads activities and history from JSON with backward compatibility for mood."""
        self.last_error = None
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as file:
                    data = json.load(file)
            else:
                data = {"history": [], "custom_activities": [], "activities": []}

            if not isinstance(data, dict):
                data = {"history": [], "custom_activities": [], "activities": []}

            raw_history = data.get("history", []) if isinstance(data.get("history", []), list) else []
            self.completed_history = []
            for item in raw_history:
                if isinstance(item, dict):
                    # Ensure mood attribute exists on older history entries
                    entry = dict(item)
                    if "mood" not in entry or not entry["mood"]:
                        entry["mood"] = "Calm"
                    self.completed_history.append(entry)

            raw_custom = self.normalize_activity_list(data.get("custom_activities", []))
            # Separate truly custom activities from legacy saved defaults
            truly_custom = []
            for item in raw_custom:
                is_default = any(self.matches_activity(item, def_act) for def_act in self.default_activities)
                if not is_default:
                    truly_custom.append(item)
            self.custom_activities = truly_custom
            return True
        except (json.JSONDecodeError, OSError, ValueError) as exc:
            self.completed_history = []
            self.custom_activities = []
            self.last_error = f"Could not load saved boredom data: {exc}"
            return False

    def save_data(self) -> bool:
        """Saves current state to the JSON file."""
        self.last_error = None
        payload = {
            "history": self.completed_history,
            "custom_activities": self.custom_activities,
            "activities": self.get_all_activities(),
        }
        try:
            with open(self.data_file, "w", encoding="utf-8") as file:
                json.dump(payload, file, indent=2)
            return True
        except OSError as exc:
            self.last_error = f"Could not save boredom data: {exc}"
            return False

    @staticmethod
    def parse_duration(duration_text: Any) -> int:
        """Parses durations like '5 minutes' or '60 seconds' into seconds."""
        try:
            value = str(duration_text).strip().lower()
            if "minute" in value:
                return int(float(value.split()[0])) * 60
            if "second" in value:
                return int(float(value.split()[0]))
            return 60
        except (IndexError, ValueError):
            return 60

    @staticmethod
    def format_seconds(total_seconds: int) -> str:
        """Formats an integer seconds value as MM:SS string."""
        total_seconds = max(0, total_seconds)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def matches_activity(self, first: Any, second: Any) -> bool:
        """Checks equality between two activities based on title and category."""
        first_normalized = self.normalize_activity(first)
        second_normalized = self.normalize_activity(second)
        if first_normalized is None or second_normalized is None:
            return False
        return (
            first_normalized["title"].lower() == second_normalized["title"].lower()
            and first_normalized["category"].lower() == second_normalized["category"].lower()
        )

    def add_custom_activity(self, title: str, category: str, duration: str, mood: str = "Calm") -> Optional[Dict[str, str]]:
        """Creates and appends a new custom activity with category and mood."""
        activity = {
            "title": title.strip(),
            "category": category.strip() or "Indoor",
            "duration": duration.strip() or "5 minutes",
            "mood": mood.strip() or "Calm",
        }
        normalized = self.normalize_activity(activity)
        if not normalized:
            return None
        self.custom_activities.append(normalized)
        self.save_data()
        return normalized

    def edit_activity(self, original: Dict[str, str], replacement: Dict[str, str]) -> bool:
        """Replaces an activity in default or custom activities."""
        norm_rep = self.normalize_activity(replacement)
        if not norm_rep:
            return False

        for index, activity in enumerate(self.default_activities):
            if self.matches_activity(activity, original):
                self.default_activities[index] = norm_rep
                self.save_data()
                return True

        for index, activity in enumerate(self.custom_activities):
            if self.matches_activity(activity, original):
                self.custom_activities[index] = norm_rep
                self.save_data()
                return True

        self.custom_activities.append(norm_rep)
        self.save_data()
        return True

    # Alias replace_activity to edit_activity for backwards compatibility
    replace_activity = edit_activity

    def remove_activity(self, activity: Dict[str, str]) -> bool:
        """Deletes an activity from either list."""
        for index, item in enumerate(self.default_activities):
            if self.matches_activity(item, activity):
                del self.default_activities[index]
                self.save_data()
                return True

        for index, item in enumerate(self.custom_activities):
            if self.matches_activity(item, activity):
                del self.custom_activities[index]
                self.save_data()
                return True

        return False

    def add_completed(self, activity: Dict[str, str]) -> Dict[str, Any]:
        """Records an activity completion with current timestamp and mood."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "title": activity.get("title", "Untitled"),
            "category": activity.get("category", "General"),
            "duration": activity.get("duration", "—"),
            "mood": activity.get("mood", "Calm"),
            "completed_at": timestamp,
        }
        self.completed_history.insert(0, entry)
        self.save_data()
        return entry

    def clear_history(self) -> None:
        """Clears all completed records."""
        self.completed_history = []
        self.save_data()

    def get_stats(self) -> Dict[str, Any]:
        """Calculates summary statistics for completed challenges including category and mood."""
        total_completed = len(self.completed_history)
        category_counts: Dict[str, int] = {}
        mood_counts: Dict[str, int] = {}

        for item in self.completed_history:
            cat = str(item.get("category", "General")).strip() or "General"
            category_counts[cat] = category_counts.get(cat, 0) + 1
            mood = str(item.get("mood", "Calm")).strip() or "Calm"
            mood_counts[mood] = mood_counts.get(mood, 0) + 1

        if category_counts:
            top_category = max(category_counts.items(), key=lambda x: x[1])[0]
            top_category_count = category_counts[top_category]
        else:
            top_category = "None yet"
            top_category_count = 0

        if mood_counts:
            top_mood = max(mood_counts.items(), key=lambda x: x[1])[0]
            top_mood_count = mood_counts[top_mood]
        else:
            top_mood = "None yet"
            top_mood_count = 0

        total_activities = len(self.get_all_activities())
        return {
            "total_completed": total_completed,
            "top_category": top_category,
            "top_category_count": top_category_count,
            "top_mood": top_mood,
            "top_mood_count": top_mood_count,
            "total_activities": total_activities,
            "category_counts": category_counts,
            "mood_counts": mood_counts,
        }


# Alias for explicit naming mentioned in prompt
BoredomDataManager = DataManager

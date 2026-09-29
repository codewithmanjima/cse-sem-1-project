"""
utils.py
--------
Reusable input-validation and display helpers, so the same
"keep asking until valid" logic is not repeated across the program.
"""

from datetime import date


def print_header(title):
    """Print a consistent section header."""
    print("\n" + "=" * 50)
    print(title.center(50))
    print("=" * 50)


def pause():
    """Wait for Enter so the user can read the output."""
    input("\nPress Enter to continue...")


def get_non_empty_string(prompt):
    """Keep asking until the user types something non-empty."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again.")


def get_positive_int(prompt):
    """Keep asking until the user enters a whole number greater than 0."""
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        print("Please enter a whole number greater than 0.")


def get_menu_choice(prompt, valid_choices):
    """Keep asking until the input is one of the valid menu options."""
    while True:
        raw = input(prompt).strip()
        if raw in valid_choices:
            return raw
        print("Invalid menu choice. Please try again.")


def get_yes_no(prompt):
    """Ask a yes/no question. Returns True for yes, False for no."""
    while True:
        raw = input(prompt + " (y/n): ").strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Please answer with 'y' or 'n'.")


def today():
    """Return today's date (kept in one place for easy testing)."""
    return date.today()
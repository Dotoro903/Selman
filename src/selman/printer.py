#!/usr/bin/env python3
from enum import Enum, auto
import sys
from typing import Optional, Callable

from selman import ansi_control

FG = {
    "muted": "38;5;245",
    "accent": "38;5;117",
    "selected": "38;5;112",
}


class TextEffect(Enum):
    UNFOCUSED = auto()
    FOCUSED = auto()
    SELECTED = auto()
    SELECTED_FOCUSED = auto()
    BANNED = auto()
    BANNED_FOCUSED = auto()


def _restore_cursor_pos_col(col_offset: int):
    ansi_control.set_col_offset(col_offset)


def write_line(text: str, color_code: Optional[str] = None, restore_style=True):
    """Write a text line with optional color.
    When restore_style is True, reset SGR after the text.
    """
    if color_code is None:
        sys.stdout.write(text)
        return
    if restore_style:
        sys.stdout.write(f"\x1b[{color_code}m" + text + "\x1b[0m")
        return
    sys.stdout.write(f"\x1b[{color_code}m" + text)


def _render_at_row(
    relative_pos: Optional[int], col_offset: int, draw: Callable[[], None]
) -> None:
    """Render using draw() optionally at a relative row, then restore column."""
    if relative_pos is not None:
        restore_pos = ansi_control.move_cursor_by_relative_pos_row(relative_pos)
        try:
            draw()
        finally:
            restore_pos()
            _restore_cursor_pos_col(col_offset)
    else:
        draw()
        _restore_cursor_pos_col(col_offset)


def print_unfocused(text: str, col_offset: int = 0, relative_pos: Optional[int] = None) -> None:
    def draw():
        write_line(f"○ {text}", FG["muted"])
    _render_at_row(relative_pos, col_offset, draw)


def print_focused(text: str, col_offset: int = 0, relative_pos: Optional[int] = None) -> None:
    def draw():
        write_line(f"● {text}", FG["accent"])
    _render_at_row(relative_pos, col_offset, draw)


def print_selected(text: str, col_offset: int = 0, relative_pos: Optional[int] = None) -> None:
    def draw():
        write_line(f"● {text}", FG["selected"])
    _render_at_row(relative_pos, col_offset, draw)


def print_selected_focused(text: str, col_offset: int = 0, relative_pos: Optional[int] = None) -> None:
    def draw():
        write_line("● ", FG["accent"])
        write_line(text, FG["selected"])
    _render_at_row(relative_pos, col_offset, draw)


def print_banned_focused(text: str, col_offset: int = 0, relative_pos: Optional[int] = None) -> None:
    def draw():
        write_line("\x1b[9m● ", FG["accent"], restore_style=False)
        write_line(text + "\x1b[0m", FG["accent"], restore_style=False)
    _render_at_row(relative_pos, col_offset, draw)


def print_banned(text: str, col_offset: int = 0, relative_pos: Optional[int] = None) -> None:
    def draw():
        write_line(f"\x1b[9m○ {text}\x1b[29m", FG["muted"])
    _render_at_row(relative_pos, col_offset, draw)


print_effect = {
    TextEffect.UNFOCUSED: print_unfocused,
    TextEffect.FOCUSED: print_focused,
    TextEffect.SELECTED: print_selected,
    TextEffect.SELECTED_FOCUSED: print_selected_focused,
    TextEffect.BANNED: print_banned,
    TextEffect.BANNED_FOCUSED: print_banned_focused,
}


def print_text_effect(
    text: str,
    effect: TextEffect,
    col_offset: int = 0,
    relative_pos: Optional[int] = None,
) -> None:
    print_effect[effect](text, col_offset, relative_pos)

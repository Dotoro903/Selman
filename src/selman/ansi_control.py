#!/usr/bin/env python3

"""
ANSI terminal cursor and key utilities.
"""
import sys
import re
from typing import Callable

ANSI_KEY_UP = b"\x1b[A"
ANSI_KEY_DOWN = b"\x1b[B"
ANSI_KEY_RIGHT = b"\x1b[C"
ANSI_KEY_LEFT = b"\x1b[D"
ANSI_KEY_EOX = b"\x03"


def get_cursor_position():
    """Get current cursor position"""
    sys.stdout.write(f"\x1b[6n")
    sys.stdout.flush()

    buf = ""
    while (ch := sys.stdin.read(1)) != "R":
        buf += ch
    buf += "R"

    m = re.search(r"\x1b\[(\d+);(\d+)R", buf)
    sys.stdout.flush()
    return tuple(map(int, m.groups())) if m else None


def cursor_up(dist: int):
    """Move cursor up by dist rows. No-op when dist <= 0."""
    if dist == 0:
        return
    sys.stdout.write(f"\x1b[{dist}A")


def cursor_down(dist: int):
    """Move cursor down by dist rows. No-op when dist <= 0."""
    if dist == 0:
        return
    sys.stdout.write(f"\x1b[{dist}B")


def cursor_right(dist: int):
    """Move cursor right by dist rows. No-op when dist <= 0."""
    if dist == 0:
        return
    sys.stdout.write(f"\x1b[{dist}C")


def cursor_left(dist: int):
    """Move cursor left by dist rows. No-op when dist <= 0."""
    if dist == 0:
        return
    sys.stdout.write(f"\x1b[{dist}D")


def move_cursor_by_relative_pos_row(relative_pos_row: int) -> Callable[[], None]:
    """Move rows relative to current position and return a restoration callable.
    If relative_pos_row == 0, nothing is moved and a no-op restore is returned.
    """
    if relative_pos_row == 0:
        return lambda: None

    dist = abs(relative_pos_row)
    if relative_pos_row > 0:
        cursor_down(dist)
        return lambda: cursor_up(dist)
    cursor_up(dist)
    return lambda: cursor_down(dist)


def set_cursor_visibility(is_visible: bool) -> None:
    sys.stdout.write("\x1b[?25h" if is_visible else "\x1b[?25l")


def erase_line(col_offset: int) -> None:
    sys.stdout.write("\x1b[2K")
    set_col_offset(col_offset)


def enable_autowrap(enabled: bool) -> None:
    sys.stdout.write("\x1b[?7h" if enabled else "\x1b[?7l")


def set_col_offset(offset: int) -> None:
    if offset < 0:
        offset = 0
    sys.stdout.write(f"\x1b[{offset}G")


def is_ansi_key(target: bytes) -> bool:
    return target == b"\x1b"

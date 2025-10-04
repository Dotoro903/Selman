#!/usr/bin/env python3
"""
Selman: interactive selection manager.
- Preserves behavior and key bindings.
- Minor cleanups, explicit typing, small safety improvements.
"""
import sys
import termios
import tty
from typing import List, Optional

from selman.printer import (
    print_unfocused,
    write_line,
    print_text_effect,
    TextEffect,
)
from selman import ansi_control


class Selman:
    def __init__(
        self,
        selection: List[str],
        col_offset: int = 0,
        allow_multiple_selection: bool = False,
        mutex_group: Optional[set[frozenset]] = None,
        footer_comments: Optional[List[str]] = None,
        wipe_comments_after_select: bool = True,
    ):
        self.selection = selection
        self.col_offset = col_offset
        self.mutex_group = mutex_group
        self.allow_multiple_selection = allow_multiple_selection
        self.footer_comments = footer_comments
        self.wipe_comments_after_select = wipe_comments_after_select

        self.current_index = 0

        self.key_events = {
            # next option keys
            b"j": lambda: self.change_focus(1),
            ansi_control.ANSI_KEY_DOWN: lambda: self.change_focus(1),
            # previous option keys
            b"k": lambda: self.change_focus(-1),
            ansi_control.ANSI_KEY_UP: lambda: self.change_focus(-1),
            # select
            b"\r": self.select_option,
            b"\n": self.select_option,
            # proceed
            b"n": self.proceed,
            # exit
            b"q": self.terminate,
            ansi_control.ANSI_KEY_EOX: self.terminate,
        }

        self.sel_board = {item: False for item in selection}
        self.banned_board = {item: False for item in selection}
        self._terminate = False

    def terminate(self) -> None:
        self._terminate = True

    def print_comments(self) -> None:
        if self.footer_comments is None:
            return

        for c in self.footer_comments:
            ansi_control.set_col_offset(self.col_offset)
            write_line(c)
            print()

    def wipe_comments(self) -> None:
        if self.footer_comments is None:
            return
        dist = (len(self.selection) - self.current_index)
        try:
            ansi_control.cursor_down(dist)
            ansi_control.erase_line(self.col_offset)
            sys.stdout.flush()
        finally:
            ansi_control.cursor_up(dist)
            sys.stdout.flush()
        sys.stdout.flush()

    def run(self) -> str | None:
        """
        This function is the main entry of Selman
        returns name of single selection if allow_multilple_selection is False
        returns None if allow_multilple_selection is True, the result stores in sel_board
        """
        for i in range(len(self.selection)):
            ansi_control.set_col_offset(self.col_offset)
            print_unfocused(self.selection[i], self.col_offset)
            print()
        return self.selman_mainstream()

    def selman_mainstream(self) -> str | None:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            tty.setcbreak(fd)

            ansi_control.set_cursor_visibility(False)
            ansi_control.enable_autowrap(False)

            if self.allow_multiple_selection:
                ansi_control.set_col_offset(self.col_offset)
                # write_line("press 'n' to proceed..")

            self.print_comments()

            self.initialize_focus()

            sys.stdout.flush()

            while True:
                key_bytes = sys.stdin.buffer.read(1)
                last_selection = self.manage_key_input(key_bytes)
                sys.stdout.flush()

                if self._terminate:
                    break
        finally:

            if self.wipe_comments_after_select:
                self.wipe_comments()

            initial_cursor_relative_pos = len(self.selection) - self.current_index
            ansi_control.cursor_down(initial_cursor_relative_pos)

            termios.tcsetattr(fd, termios.TCSADRAIN, old)

            ansi_control.set_cursor_visibility(True)
            ansi_control.enable_autowrap(True)

            print()

        if self.allow_multiple_selection:
            return last_selection
        return None

    def manage_key_input(self, k: bytes) -> str | None:
        if ansi_control.is_ansi_key(k):
            seq = sys.stdin.buffer.read(2)
            k += seq
        action = self.key_events.get(k)
        if action:
            return action()
        return None

    def get_relative_pos_by_index(self, index: int) -> int:
        return index - self.current_index

    def initialize_focus(self) -> None:
        selection_count = len(self.selection)
        result_offset = selection_count
        if self.footer_comments is not None:
            comment_line_count = len(self.footer_comments)
            result_offset += comment_line_count

        ansi_control.set_col_offset(self.col_offset)
        ansi_control.cursor_up(result_offset)

        self.render_text_effect(TextEffect.FOCUSED)

    def is_index_valid(self, target_index: int) -> bool:
        return 0 <= target_index < len(self.selection)

    def is_index_selected(self, target_index: int) -> bool:
        return self.sel_board[self.selection[target_index]]

    def is_index_banned(self, target_index: int) -> bool:
        return self.banned_board[self.selection[target_index]]

    def set_to_focused(self, target_index: int) -> None:
        if self.is_index_selected(target_index):
            self.render_text_effect(TextEffect.SELECTED_FOCUSED, target_index)
        elif self.is_index_banned(target_index):
            self.render_text_effect(TextEffect.BANNED_FOCUSED, target_index)
        else:
            self.render_text_effect(TextEffect.FOCUSED)

    def set_to_unfocused(self, target_index: int) -> None:
        if self.is_index_selected(target_index):
            self.render_text_effect(TextEffect.SELECTED, target_index)
        elif self.is_index_banned(target_index):
            self.render_text_effect(TextEffect.BANNED, target_index)
        else:
            self.render_text_effect(TextEffect.UNFOCUSED, target_index)

    def change_focus(self, relative_move: int) -> None:
        target = self.current_index + relative_move
        if not (0 <= target < len(self.selection)):
            return

        self.set_to_unfocused(self.current_index)
        self.current_index = target
        ansi_control.move_cursor_by_relative_pos_row(relative_move)
        self.set_to_focused(self.current_index)

    def proceed(self) -> None:
        if self.sel_board[self.selection[self.current_index]]:
            self.render_text_effect(TextEffect.SELECTED)
        else:
            self.render_text_effect(TextEffect.UNFOCUSED)

        self.terminate()

    def get_opposite_mutex_index(self, target_index: int) -> int | None:
        if self.mutex_group is None:
            return None

        opposite: int | None = None
        for s in self.mutex_group:
            if target_index in s:
                opposite = next(iter(s - {target_index}))
                break

        return opposite

    def ban_selection_by_index(self, target_index: int, do_render: bool = True) -> None:
        if do_render:
            self.render_text_effect(TextEffect.BANNED, target_index)
        self.sel_board[self.selection[target_index]] = False
        self.banned_board[self.selection[target_index]] = True

    def unban_selection_by_index(
        self, target_index: int, do_render: bool = True
    ) -> None:
        if do_render:
            self.render_text_effect(TextEffect.UNFOCUSED, target_index)
        self.banned_board[self.selection[target_index]] = False

    def select_option(self) -> str | None:
        if not self.allow_multiple_selection:
            self.sel_board[self.selection[self.current_index]] = True
            self.render_text_effect(TextEffect.SELECTED)
            self.terminate()
            return self.selection[self.current_index]

        current = self.sel_board[self.selection[self.current_index]]
        if current:  # when toggle to unselect
            self.sel_board[self.selection[self.current_index]] = False
            self.render_text_effect(TextEffect.FOCUSED)

            opposite_index = self.get_opposite_mutex_index(self.current_index)
            if opposite_index is not None and self.is_index_banned(opposite_index):
                self.unban_selection_by_index(opposite_index)
        else:  # when toggle to select
            self.sel_board[self.selection[self.current_index]] = True
            self.unban_selection_by_index(self.current_index, do_render=False)
            self.render_text_effect(TextEffect.SELECTED_FOCUSED)

            opposite_index = self.get_opposite_mutex_index(self.current_index)
            if opposite_index is not None:
                self.ban_selection_by_index(opposite_index)

    def render_text_effect(
        self, effect: TextEffect, target_index: Optional[int] = None
    ):
        ansi_control.set_col_offset(self.col_offset)

        if target_index is not None and self.is_index_valid(target_index):
            relative_pos = self.get_relative_pos_by_index(target_index)
            restore = ansi_control.move_cursor_by_relative_pos_row(relative_pos)
            try:
                print_text_effect(self.selection[target_index], effect, self.col_offset)
            finally:
                restore()
            return

        print_text_effect(self.selection[self.current_index], effect, self.col_offset)

#!/usr/bin/env python3

import sys

from core import Selman
import assets


def setcursor(row, col):
    sys.stdout.write(f"\x1b[{row};{col}H")
    sys.stdout.flush()


def mainflow():

    footer_comments = ["press n to proceed..."]

    print("    Options:")
    sel = Selman(
        assets.install_options_list,
        col_offset=5,
        allow_multiple_selection=True,
        mutex_group=assets.install_options_mutex,
        footer_comments=footer_comments,
    )
    sel.run()

    if sel.sel_board["Install Dotfile"]:
        print("    Dotfiles to install:")
        dot_sel = Selman(
            assets.install_options_list,
            col_offset=5,
            allow_multiple_selection=True,
            mutex_group=assets.install_options_mutex,
        )
        dot_sel.run()

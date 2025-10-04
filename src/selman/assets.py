#!/usr/bin/env python

foreword = """
================================================================================

     ░█▀▄░█▀█░▀█▀░█▀▀░▀█▀░▀█▀░█░░░█▀▀░░░▀█▀░█▀█░█▀▀░▀█▀░█▀█░█░░░█░░░█▀▀░█▀▄
     ░█░█░█░█░░█░░█▀▀░░█░░░█░░█░░░█▀▀░░░░█░░█░█░▀▀█░░█░░█▀█░█░░░█░░░█▀▀░█▀▄
     ░▀▀░░▀▀▀░░▀░░▀░░░▀▀▀░▀▀▀░▀▀▀░▀▀▀░░░▀▀▀░▀░▀░▀▀▀░░▀░░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀░▀


Author     : Dotoro903
Repository : https://github.com/Dotoro903/Dotfile

================================================================================
⚠️ Disclaimer
This Install script is made for my personal environment.
It depends on my private files and directories which is not open in my public git repository.
It may not work on other system. I suggest to use it only as reference

================================================================================
"""

# install_options = """Options: 
# 1. Install Dotfile
# 2. Install Package
# 3. Update Dotfile
# 4. Update Package
# 5. Construct Home"""

install_options_list = [
    "Install Dotfile",
    "Install Package",
    "Update Dotfile",
    "Update Package",
    "Construct Home",
]

install_options_mutex = {
    frozenset({0, 2}),
    frozenset({1, 3})
}

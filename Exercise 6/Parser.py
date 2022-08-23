"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

import typing


class Parser:
    """
    Encapsulates access to the input code. Reads an assembly language
    command, parses it, and provides convenient access to the commands 
    components (fields and symbols). In addition, removes all white space and 
    comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """
        Opens the input file and gets ready to parse it.
        Args: input_file (typing.TextIO): input file.
        """
        self.input_lines = input_file.read().splitlines()
        self.res = []
        self.ind = 0  # represent the index of the line number
        while self.has_more_commands():
            if not self.is_white_space(self.input_lines[self.ind]):
                new_str = self.input_lines[self.ind].replace(" ", "")
                slash_ind = new_str.find("/")
                if slash_ind == -1:
                    self.res.append(new_str)
                else:
                    new_str = new_str[0:slash_ind] + " " + new_str[slash_ind:]
                    self.res.append(new_str)
            self.advance()
        self.input_lines = self.res
        self.ind = 0

    def is_white_space(self, line: str) -> bool:
        line.replace(" ", "")
        if line == "" or (line[0] == "/" and line[1] == "/"):
            return True
        return False

    def has_more_commands(self) -> bool:
        if self.ind != len(self.input_lines):
            return True
        return False

    def advance(self) -> None:
        """
        Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        self.ind += 1
        while len(self.input_lines) != self.ind:
            if self.is_white_space(self.input_lines[self.ind]):
                self.ind += 1
            else:
                return None

    def command_type(self) -> str:
        """
        Returns str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        curr_str = self.input_lines[self.ind].strip()
        space_ind = curr_str.find(" ")
        if space_ind != -1:
            curr_str = curr_str[0:space_ind]
        if curr_str[0] == "@":
            for i in range(len(self.input_lines)):
                new_str = self.input_lines[i].strip()
                space_ind = new_str.find(" ")
                if space_ind != -1:
                    new_str = new_str[0:space_ind]
                if new_str != "" and new_str[0] == "(" and new_str[1:-1] == curr_str[1:]:
                    return "L_COMMAND"
            return "A_COMMAND"
        elif curr_str[0] == "(":
            return "L_COMMAND"
        elif curr_str.find("=") != -1 or curr_str.find(";") != -1:
            return "C_COMMAND"
        elif curr_str.find("=") != -1 and curr_str.find(">") != -1:
            return "C_COMMAND"
        elif curr_str.find("=") != -1 and curr_str.find("<") != -1:
            return "C_COMMAND"
        else:
            return "NONE"

    def symbol(self) -> str:
        """
        Returns str: the symbol or decimal Xxx of the current command @Xxx or (Xxx).
        Should be called only when command_type() is "A_COMMAND" or "L_COMMAND"
        """
        curr_str = self.input_lines[self.ind].strip()
        space_ind = curr_str.find(" ")
        if space_ind != -1:
            curr_str = curr_str[0:space_ind]
        if curr_str[0] == "(":
            return curr_str[1:-1]
        elif curr_str[0] == "@":
            return curr_str[1:]
        return ""

    def dest(self) -> str:
        """
        Returns str: the dest mnemonic in the current C-command.
        Should be called only when commandType() is "C_COMMAND".
        """
        curr_str = self.input_lines[self.ind].strip()
        space_ind = curr_str.find(" ")
        if space_ind != -1:
            curr_str = curr_str[0:space_ind]
        tmp = curr_str.find("=")
        if tmp == -1:
            return "null"
        return curr_str[0:tmp]

    def comp(self) -> str:
        """
        Returns str: the comp mnemonic in the current C-command.
        Should be called only when commandType() is "C_COMMAND".
        """
        curr_str = self.input_lines[self.ind].strip()
        space_ind = curr_str.find(" ")
        if space_ind != -1:
            curr_str = curr_str[0:space_ind]
        tmp_dot = curr_str.find(";")
        tmp_eq = curr_str.find("=")
        if tmp_eq != -1 and tmp_dot != -1:
            return curr_str[tmp_eq + 1:tmp_dot]
        elif tmp_eq == -1 and tmp_dot != -1:
            return curr_str[0:tmp_dot]
        elif tmp_eq != -1 and tmp_dot == -1:
            return curr_str[tmp_eq + 1:]
        return ""

    def jump(self) -> str:
        """
        Returns str: the jump mnemonic in the current C-command.
        Should be called only when commandType() is "C_COMMAND".
        """
        curr_str = self.input_lines[self.ind].strip()
        space_ind = curr_str.find(" ")
        if space_ind != -1:
            curr_str = curr_str[0:space_ind]
        tmp = curr_str.find(";")
        if tmp == -1:
            return "null"
        return curr_str[tmp + 1:]

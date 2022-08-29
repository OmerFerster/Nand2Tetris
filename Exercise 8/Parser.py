
import typing


def is_white_space(line: str) -> bool:
    line.replace(" ", "")
    if line == "" or (line[0] == "/" and line[1] == "/"):
        return True
    return False


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """
        Gets ready to parse the input file.
        Args input_file (typing.TextIO): input file.
        """
        self.input_lines = input_file.read().splitlines()
        self.res = []
        self.ind = 0  # represent the index of the line number
        while self.has_more_commands():
            if not is_white_space(self.input_lines[self.ind]):
                curr_str = self.input_lines[self.ind]
                slash_ind = curr_str.find("/")
                if slash_ind == -1:
                    self.res.append(curr_str.strip())
                else:
                    self.res.append(curr_str[0:slash_ind].strip())
            self.advance()
        self.input_lines = self.res
        self.ind = 0

    def has_more_commands(self) -> bool:
        """
        Are there more commands in the input?
        Returns bool: True if there are more commands, False otherwise.
        """
        if self.ind != len(self.input_lines):
            return True
        return False

    def advance(self) -> None:
        """
        Reads the next command from the input and makes it the current
        command. Should be called only if has_more_commands() is true.
        Initially there is no current command.
        """
        self.ind += 1
        while len(self.input_lines) != self.ind:
            if is_white_space(self.input_lines[self.ind]):
                self.ind += 1
            else:
                return None

    def command_type(self) -> str:
        """
        Returns str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        # if this function works replace in ex7 comm_type function (replace)
        curr_str = self.input_lines[self.ind]
        if "push" in curr_str:
            return "C_PUSH"
        elif "pop" in curr_str:
            return "C_POP"
        elif "label" in curr_str:
            return "C_LABEL"
        elif "if-goto" in curr_str:
            return "C_IF"
        elif "goto" in curr_str:
            return "C_GOTO"
        elif "function" in curr_str:
            return "C_FUNCTION"
        elif "return" in curr_str:
            return "C_RETURN"
        elif "call" in curr_str:
            return "C_CALL"
        else:
            return "C_ARITHMETIC"

    def arg1(self) -> str:
        """
        Returns str: the first argument of the current command. In case of
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        com_type = self.command_type()
        curr_str = self.input_lines[self.ind]
        if com_type == "C_ARITHMETIC":
            return curr_str
        elif com_type != "C_RETURN":
            first_space_ind = curr_str.find(" ")
            second_space_ind = curr_str[first_space_ind + 1:].find(" ")
            return curr_str[first_space_ind + 1:second_space_ind + first_space_ind + 1]

    def arg2(self) -> int:
        """
        Returns int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP",
            "C_FUNCTION" or "C_CALL".
        """
        com_type = self.command_type()
        curr_str = self.input_lines[self.ind]
        legal = ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]
        if com_type in legal:
            first_space_ind = curr_str.find(" ")
            second_space_ind = curr_str[first_space_ind + 1:].find(" ")
            return int(curr_str[second_space_ind + 1 + first_space_ind:])

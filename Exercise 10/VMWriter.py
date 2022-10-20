"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

import typing


class VMWriter:
    """
    Writes VM commands into a file. Encapsulates the VM command syntax.
    """

    def __init__(self, output_stream: typing.TextIO) -> None:
        """
        Creates a new file and prepares it for writing VM commands
        """
        self.out = output_stream

    def write_push(self, segment: str, index: int) -> None:
        """
        Writes a VM push command.
        Args:
            segment (str): the segment to push to, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"
            index (int): the index to push to.
        """
        if segment not in ["CONST", "ARG", "LOCAL", "STATIC",
                           "THIS", "THAT", "POINTER", "TEMP", "FIELD", "VAR"]:
            return
        elif segment == "CONST":
            self.out.write("push constant " + str(index) + "\n")
        elif segment == "ARG":
            self.out.write("push argument " + str(index) + "\n")
        elif segment == "VAR":
            self.out.write("push local " + str(index) + "\n")
        elif segment == "FIELD":
            self.out.write("push this " + str(index) + "\n")
        elif segment == "STATIC":
            self.out.write("push " + segment.lower() + " " + str(index) + "\n")
        elif segment == "THIS":
            self.out.write("push " + segment.lower() + " " + str(index) + "\n")
        elif segment == "THAT":
            self.out.write("push " + segment.lower() + " " + str(index) + "\n")
        elif segment == "POINTER":
            self.out.write("push " + segment.lower() + " " + str(index) + "\n")
        elif segment == "TEMP":
            self.out.write("push " + segment.lower() + " " + str(index) + "\n")

    def write_pop(self, segment: str, index: int) -> None:
        """
        Writes a VM pop command.
        Args:
            segment (str): the segment to pop from, can be "ARG",
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP".
            index (int): the index to pop from.
        """
        if segment not in ["ARG", "VAR", "STATIC",
                           "THIS", "THAT", "POINTER", "TEMP", "FIELD"] or index < 0:
            return
        elif segment == "ARG":
            self.out.write("pop argument " + str(index) + "\n")
        elif segment == "VAR":
            self.out.write("pop local " + str(index) + "\n")
        elif segment == "FIELD":
            self.out.write("pop this " + str(index) + "\n")
        elif segment == "STATIC":
            self.out.write("pop " + segment.lower() + " " + str(index) + "\n")
        elif segment == "THIS":
            self.out.write("pop " + segment.lower() + " " + str(index) + "\n")
        elif segment == "THAT":
            self.out.write("pop " + segment.lower() + " " + str(index) + "\n")
        elif segment == "POINTER":
            self.out.write("pop " + segment.lower() + " " + str(index) + "\n")
        elif segment == "TEMP":
            self.out.write("pop " + segment.lower() + " " + str(index) + "\n")

    def write_arithmetic(self, command: str, is_neg = False) -> None:
        """
        Writes a VM arithmetic command.
        Args:
            command (str): the command to write, can be "ADD", "SUB", "NEG", 
            "EQ", "GT", "LT", "AND", "OR", "NOT", "SHIFTLEFT", "SHIFTRIGHT".
        """
        if command not in ["+", "-", "~", "=", ">", "<", "&", "|", "<<", ">>", "*", "/"]:
            return
        elif command == "*":
            self.out.write("call Math.multiply 2\n")
        elif command == "/":
            self.out.write("call Math.divide 2\n")
        elif command == "+":
            self.out.write("add\n")
        elif command == "-":
            if is_neg:
                self.out.write("neg\n")
            else:
                self.out.write("sub\n")
        elif command == "~":
            self.out.write("not\n")
        elif command == "=":
            self.out.write("eq\n")
        elif command == ">":
            self.out.write("gt\n")
        elif command == "<":
            self.out.write("lt\n")
        elif command == "&":
            self.out.write("and\n")
        elif command == "|":
            self.out.write("or\n")
        elif command == "<<":
            self.out.write("shiftleft\n")
        elif command == ">>":
            self.out.write("shiftright\n")

    def write_label(self, label: str) -> None:
        """
        Writes a VM label command.
        Args label (str): the label to write.
        """
        self.out.write("label " + label + "\n")

    def write_goto(self, label: str) -> None:
        """
        Writes a VM goto command.
        Args label (str): the label to go to.
        """
        self.out.write("goto " + label + "\n")
        # TODO check if upper or nothing 2 add

    def write_if(self, label: str) -> None:
        """
        Writes a VM if-goto command.
        Args label (str): the label to go to.
        """
        self.out.write("if-goto " + label + "\n")
        # TODO check if upper or nothing 2 add

    def write_call(self, name: str, n_args: int) -> None:
        """
        Writes a VM call command.
        Args:
            name (str): the name of the function to call.
            n_args (int): the number of arguments the function receives.
        """
        self.out.write("call " + name + " " + str(n_args) + "\n")

    def write_function(self, name: str, n_locals: int) -> None:
        """
        Writes a VM function command.
        Args:
            name (str): the name of the function.
            n_locals (int): the number of local variables the function uses.
        """
        self.out.write("function " + name + " " + str(n_locals) + "\n")

    def write_return(self) -> None:
        """
        Writes a VM return command.
        """
        self.out.write("return\n")

import typing


class CodeWriter:

    """
    Translates VM commands into Hack assembly code.
    """

    def __init__(self, output_stream: typing.TextIO) -> None:
        """
        Initializes the CodeWriter.
        Args output_stream (typing.TextIO): output stream.
        """
        self.out = output_stream
        self.file_name = ""
        self.arithmetic_counter = 0

    def set_file_name(self, filename: str) -> None:
        """
        Informs the code writer that the translation of a new VM file is started.
        Args filename (str): The name of the VM file.
        """
        # This function is useful when translating code that handles the
        # static segment.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self.file_name = filename

    def write_arithmetic(self, command: str) -> None:
        """
        Writes assembly code that is the translation of the given
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.
        Args command (str): an arithmetic command.
        """
        if command == "add":
            self.out.write("@SP\n")
            self.out.write("A=M-1\n")
            self.out.write("D=M\n")
            self.out.write("A=A-1\n")
            self.out.write("D=D+M\n")
            self.out.write("@SP\n")
            self.out.write("M=M-1\n")
            self.out.write("A=M-1\n")
            self.out.write("M=D\n")
        elif command == "sub":
            self.out.write("@SP\n")
            self.out.write("A=M-1\n")
            self.out.write("D=-M\n")
            self.out.write("A=A-1\n")
            self.out.write("D=D+M\n")
            self.out.write("@SP\n")
            self.out.write("M=M-1\n")
            self.out.write("A=M-1\n")
            self.out.write("M=D\n")
        elif command == "neg":
            self.out.write("@SP\n")
            self.out.write("A=M-1\n")
            self.out.write("M=-M\n")
        elif command == "eq":
            self.out.write("@SP\n")
            self.out.write("A=M-1\n")
            self.out.write("D=M\n")
            self.out.write("A=A-1\n")
            self.out.write("D=D-M\n")
            self.out.write("@EQUAL." + str(self.arithmetic_counter) + "\n")
            self.out.write("D;JEQ\n")
            # push false(0) to stack
            self.out.write("@SP\n")
            self.out.write("M=M-1\n")
            self.out.write("A=M-1\n")
            self.out.write("M=0\n")
            self.out.write("@CONT." + str(self.arithmetic_counter) + "\n")
            self.out.write("0;JMP\n")
            # push true(-1) to stack
            self.out.write("(EQUAL." + str(self.arithmetic_counter) + ")\n")
            self.out.write("    @SP\n")
            self.out.write("    M=M-1\n")
            self.out.write("    A=M-1\n")
            self.out.write("    M=-1\n")
            self.out.write("(CONT." + str(self.arithmetic_counter) + ")\n")
            self.arithmetic_counter += 1
        elif command == "gt":
            self.out.write("@SP\n")
            self.out.write("A=M-1\n")
            self.out.write("D=M\n")
            self.out.write("A=A-1\n")
            self.out.write("D=M-D\n")
            self.out.write("@LARGER." + str(self.arithmetic_counter) + "\n")
            self.out.write("D;JGT\n")
            # push false(0) to stack
            self.out.write("@SP\n")
            self.out.write("M=M-1\n")
            self.out.write("A=M-1\n")
            self.out.write("M=0\n")
            self.out.write("@CONT." + str(self.arithmetic_counter) + "\n")
            self.out.write("0;JMP\n")
            # push true(-1) to stack
            self.out.write("(LARGER." + str(self.arithmetic_counter) + ")\n")
            self.out.write("    @SP\n")
            self.out.write("    M=M-1\n")
            self.out.write("    A=M-1\n")
            self.out.write("    M=-1\n")
            self.out.write("(CONT." + str(self.arithmetic_counter) + ")\n")
            self.arithmetic_counter += 1
        elif command == "lt":
            self.out.write("@SP\n")
            self.out.write("A=M-1\n")
            self.out.write("D=M\n")
            self.out.write("A=A-1\n")
            self.out.write("D=M-D\n")
            self.out.write("@SMALLER." + str(self.arithmetic_counter) + "\n")
            self.out.write("D;JLT\n")
            # push false(0) to stack
            self.out.write("@SP\n")
            self.out.write("M=M-1\n")
            self.out.write("A=M-1\n")
            self.out.write("M=0\n")
            self.out.write("@CONT." + str(self.arithmetic_counter) + "\n")
            self.out.write("0;JMP\n")
            # push true(-1) to stack
            self.out.write("(SMALLER." + str(self.arithmetic_counter) + ")\n")
            self.out.write("    @SP\n")
            self.out.write("    M=M-1\n")
            self.out.write("    A=M-1\n")
            self.out.write("    M=-1\n")
            self.out.write("(CONT." + str(self.arithmetic_counter) + ")\n")
            self.arithmetic_counter += 1
        elif command == "and":
            self.out.write("@SP\n")
            self.out.write("A=M-1\n")
            self.out.write("D=M\n")
            self.out.write("A=A-1\n")
            self.out.write("D=D&M\n")
            self.out.write("@SP\n")
            self.out.write("M=M-1\n")
            self.out.write("A=M-1\n")
            self.out.write("M=D\n")
        elif command == "or":
            self.out.write("@SP\n")
            self.out.write("A=M-1\n")
            self.out.write("D=M\n")
            self.out.write("A=A-1\n")
            self.out.write("D=D|M\n")
            self.out.write("@SP\n")
            self.out.write("M=M-1\n")
            self.out.write("A=M-1\n")
            self.out.write("M=D\n")
        elif command == "not":
            self.out.write("@SP\n")
            self.out.write("A=M-1\n")
            self.out.write("M=!M\n")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """
        Writes assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.
        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Note: each reference to static i appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.
        if segment == "local":
            if command == "C_PUSH":
                self.out.write("@LCL\n")
                self.out.write("D=M\n")
                self.out.write("@" + str(index) + "\n")
                self.out.write("A=D+A\n")
                self.out.write("D=M\n")
                self.out.write("@SP\n")
                self.out.write("A=M\n")
                self.out.write("M=D\n")
                self.out.write("@SP\n")
                self.out.write("M=M+1\n")
            elif command == "C_POP":
                self.out.write("@LCL\n")
                self.out.write("D=M\n")
                self.out.write("@" + str(index) + "\n")
                self.out.write("D=D+A\n")
                self.out.write("@R13\n")
                self.out.write("M=D\n")
                self.out.write("@SP\n")
                self.out.write("M=M-1\n")
                self.out.write("A=M\n")
                self.out.write("D=M\n")
                self.out.write("@R13\n")
                self.out.write("A=M\n")
                self.out.write("M=D\n")
        elif segment == "argument":
            if command == "C_PUSH":
                self.out.write("@ARG\n")
                self.out.write("D=M\n")
                self.out.write("@" + str(index) + "\n")
                self.out.write("A=D+A\n")
                self.out.write("D=M\n")
                self.out.write("@SP\n")
                self.out.write("A=M\n")
                self.out.write("M=D\n")
                self.out.write("@SP\n")
                self.out.write("M=M+1\n")
            elif command == "C_POP":
                self.out.write("@ARG\n")
                self.out.write("D=M\n")
                self.out.write("@" + str(index) + "\n")
                self.out.write("D=D+A\n")
                self.out.write("@R13\n")
                self.out.write("M=D\n")
                self.out.write("@SP\n")
                self.out.write("M=M-1\n")
                self.out.write("A=M\n")
                self.out.write("D=M\n")
                self.out.write("@R13\n")
                self.out.write("A=M\n")
                self.out.write("M=D\n")
        elif segment == "this":
            if command == "C_PUSH":
                self.out.write("@THIS\n")
                self.out.write("D=M\n")
                self.out.write("@" + str(index) + "\n")
                self.out.write("A=D+A\n")
                self.out.write("D=M\n")
                self.out.write("@SP\n")
                self.out.write("A=M\n")
                self.out.write("M=D\n")
                self.out.write("@SP\n")
                self.out.write("M=M+1\n")
            elif command == "C_POP":
                self.out.write("@THIS\n")
                self.out.write("D=M\n")
                self.out.write("@" + str(index) + "\n")
                self.out.write("D=D+A\n")
                self.out.write("@R13\n")
                self.out.write("M=D\n")
                self.out.write("@SP\n")
                self.out.write("M=M-1\n")
                self.out.write("A=M\n")
                self.out.write("D=M\n")
                self.out.write("@R13\n")
                self.out.write("A=M\n")
                self.out.write("M=D\n")
        elif segment == "that":
            if command == "C_PUSH":
                self.out.write("@THAT\n")
                self.out.write("D=M\n")
                self.out.write("@" + str(index) + "\n")
                self.out.write("A=D+A\n")
                self.out.write("D=M\n")
                self.out.write("@SP\n")
                self.out.write("A=M\n")
                self.out.write("M=D\n")
                self.out.write("@SP\n")
                self.out.write("M=M+1\n")
            elif command == "C_POP":
                self.out.write("@THAT\n")
                self.out.write("D=M\n")
                self.out.write("@" + str(index) + "\n")
                self.out.write("D=D+A\n")
                self.out.write("@R13\n")
                self.out.write("M=D\n")
                self.out.write("@SP\n")
                self.out.write("M=M-1\n")
                self.out.write("A=M\n")
                self.out.write("D=M\n")
                self.out.write("@R13\n")
                self.out.write("A=M\n")
                self.out.write("M=D\n")
        elif segment == "constant":
            if command == "C_PUSH":
                self.out.write("@" + str(index) + "\n")
                self.out.write("D=A\n")
                self.out.write("@SP\n")
                self.out.write("A=M\n")
                self.out.write("M=D\n")
                self.out.write("@SP\n")
                self.out.write("M=M+1\n")
        elif segment == "static":
            res = self.file_name + "." + str(index)
            if command == "C_PUSH":
                self.out.write("@" + res + "\n")
                self.out.write("D=M\n")
                self.out.write("@SP\n")
                self.out.write("A=M\n")
                self.out.write("M=D\n")
                self.out.write("@SP\n")
                self.out.write("M=M+1\n")
            elif command == "C_POP":
                self.out.write("@" + res + "\n")
                self.out.write("D=A\n")
                self.out.write("@R13\n")
                self.out.write("M=D\n")
                self.out.write("@SP\n")
                self.out.write("M=M-1\n")
                self.out.write("A=M\n")
                self.out.write("D=M\n")
                self.out.write("@R13\n")
                self.out.write("A=M\n")
                self.out.write("M=D\n")
        elif segment == "temp":
            if command == "C_PUSH":
                self.out.write("@5\n")
                self.out.write("D=A\n")
                self.out.write("@" + str(index) + "\n")
                self.out.write("A=D+A\n")
                self.out.write("D=M\n")
                self.out.write("@SP\n")
                self.out.write("A=M\n")
                self.out.write("M=D\n")
                self.out.write("@SP\n")
                self.out.write("M=M+1\n")
            elif command == "C_POP":
                self.out.write("@5\n")
                self.out.write("D=A\n")
                self.out.write("@" + str(index) + "\n")
                self.out.write("D=D+A\n")
                self.out.write("@R13\n")
                self.out.write("M=D\n")
                self.out.write("@SP\n")
                self.out.write("M=M-1\n")
                self.out.write("A=M\n")
                self.out.write("D=M\n")
                self.out.write("@R13\n")
                self.out.write("A=M\n")
                self.out.write("M=D\n")
        elif segment == "pointer":
            res = ""
            if index == 0:
                res += "THIS"
            else:
                res += "THAT"
            if command == "C_PUSH":
                self.out.write("@" + res + "\n")
                self.out.write("A=M\n")
                self.out.write("D=M\n")
                self.out.write("@SP\n")
                self.out.write("A=M\n")
                self.out.write("M=D\n")
                self.out.write("@SP\n")
                self.out.write("M=M+1\n")
            elif command == "C_POP":
                self.out.write("@" + res + "\n")
                self.out.write("D=M\n")
                self.out.write("@R13\n")
                self.out.write("M=D\n")
                self.out.write("@SP\n")
                self.out.write("M=M-1\n")
                self.out.write("A=M\n")
                self.out.write("D=M\n")
                self.out.write("@R13\n")
                self.out.write("A=M\n")
                self.out.write("M=D\n")

    def write_label(self, label: str) -> None:
        """
        Writes assembly code that affects the label command.
        Let "foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".
        Args label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_goto(self, label: str) -> None:
        """
        Writes assembly code that affects the goto command.
        Args label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_if(self, label: str) -> None:
        """
        Writes assembly code that affects the if-goto command.
        Args label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_function(self, function_name: str, n_vars: int) -> None:
        """
        Writes assembly code that affects the function command.
        The handling of each "function foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.
        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "foo" be a function within the file Xxx.vm.
        The handling of each "call" command within foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.
        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_return(self) -> None:
        """
        Writes assembly code that affects the return command.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def close(self) -> None:
        """
        Closes the output file.
        """
        self.out.close()

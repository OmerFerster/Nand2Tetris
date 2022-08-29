import os
import sys
import typing
from Parser import Parser
from CodeWriter import CodeWriter


def make_str_pretty(new_str: str) -> str:
    new_str = new_str.strip()
    space_ind = new_str.find(" ")
    if space_ind != -1:
        new_str = new_str[0:space_ind]
    return new_str


def translate_file(input_file: typing.TextIO, output_file: typing.TextIO, bootstrap: bool) -> None:
    """
    Translates a single file.
    Args input_file (typing.TextIO): the file to translate.
    Args output_file (typing.TextIO): writes all output to this file.
    Args bootstrap (bool): if this is True, the current file is the
    first file we are translating.
    """
    first_pass = Parser(input_file)
    code = CodeWriter(output_file)
    input_filename, input_extension = os.path.splitext(
        os.path.basename(input_file.name))
    code.set_file_name(input_filename)
    if bootstrap:
        """
        SP = 256
        Call Sys.init
        """
        code.out.write("@256\n")
        code.out.write("D=A\n")
        code.out.write("@SP\n")
        code.out.write("M=D\n")
        code.write_call("Sys.init", 0)
    while first_pass.has_more_commands():
        com_type = first_pass.command_type()
        curr_str = first_pass.input_lines[first_pass.ind]
        if com_type in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
            segment = first_pass.arg1()
            index = first_pass.arg2()
            if com_type in ["C_PUSH", "C_POP"]:
                code.write_push_pop(com_type, segment, index)
            elif com_type == "C_FUNCTION":
                code.write_function(segment, index)
            elif com_type == "C_CALL":
                code.write_call(segment, index)
        elif com_type == "C_ARITHMETIC":
            code.write_arithmetic(curr_str)
        elif com_type == "C_LABEL":
            code.write_label(curr_str)
        elif com_type == "C_GOTO":
            code.write_goto(curr_str)
        elif com_type == "C_IF":
            code.write_if(curr_str)
        elif com_type == "C_RETURN":
            code.write_return()
        first_pass.advance()


if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    bootstrap = True
    with open(output_path, 'w') as output_file:
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file, bootstrap)
            bootstrap = False

"""
    In this project, we will extend the basic translator developed in project
    7 to a full-scale VM-to-Hack translator which will conform to the VM
    Specification, Part II (book section 8.2) and to the Standard VM-on-Hack
    Mapping, Part II (book section 8.3.1). To do this, you can use your
    submission for project 7 as a template. If you implemented everything
    correctly, the parser from project 7 can be used as-is, without any
    modifications. But, you will need to add the following functions to your
    CodeWriter: write_label, write_goto, write_if, write_function,
    write_call, write_return.

    We recommend completing the implementation of the VM translator in two
    stages. 
    1. First, implement and test the translation of the VM language's
    branching commands. This stage can be tested using the basic test
    BasicLoop and the slightly more advanced FibonacciSeries.
    2. Next, implement and test the translation of the function call and
    return commands. "SimpleFunction" is a basic test for this step, while
    "NestedCall" is slightly more advanced, and also contains in-depth
    instructions on how to run the test (in NestedCall.html) and step-by-step
    visualizations of the stack's state in NestedCallStack.html.
    3. Finally, add the bootstrap code, which initializes the SP to 256, and
    calls the function "Sys.init". After this step, some previous tests will
    stop working, specifically BasicLoop, FibonacciSeries and SimpleFunction!
    In order to test your implementation, you can use the FibonacciElement
    test, which includes a relatively simple recursive function, and the
    StaticsTest test, which includes multiple classes that utilize static
    variables.
    This will allow you to unit-test your implementation incrementally, using
    the test programs we supplied you with.

    For each one of the five test programs, follow these steps:
    - To get acquainted with the intended behavior of the supplied test
    program Xxx.vm, run it on the supplied VM emulator using the supplied
    XxxVME.tst script (if the program consists of one ore more files residing
    in a directory, load the *entire* directory into the VM emulator and
    proceed to execute the code).)
    - Use your VM translator to translate the supplied Xxx.vm file, or Xxx
    directory, as needed. The result should be a new text file containing
    Hack assembly code. The name of this file should be Xxx.asm.
    - Inspect the translated Xxx.asm program. If there are visible syntax (or
    any other) errors, debug and fix your VM translator.
    - To check if the translated code performs properly, use the supplied
    Xxx.tst and Xxx.cmp files to run the translated Xxx.asm program on the
    supplied CPU emulator. If there are any problems, debug and fix your VM
    translator.

    Implementation order:
    The supplied test programs were carefully planned to test the incremental
    features introduced by each stage in your VM implementation. Therefore,
    it's important to implement your VM translator in the proposed order, and
    to test it using the supplied test programs at each stage. Implementing a
    later stage before an early one may cause the test programs to fail.

    Initialization:
    In order for the translated VM code to execute on the host computer
    platform, the translated code stream (written in the machine language of
    the host platform) must include some bootstrap code that maps the stack
    on the host RAM and starts executing the code proper. The first three
    test programs in this project assume that the bootstrap code was not yet
    implemented, and include test scripts that effect the necessary
    initializations (as was done in project 7). The last two test programs
    assume that the bootstrap code is generated by the VM translator. In
    other words, the assembly code that the final version of your VM
    translator generates must start with some code that sets the stack
    pointer and calls the Sys.init function. Sys.init will then call the
    Main.main function, and the program will start running (similar to how
    Java's JVM always looks for, and starts executing, a method named main).

    Use your VM translator to translate the VM programs supplied as tests,
    yielding corresponding programs written in the Hack assembly language.
    When executed on the supplied CPU emulator, the translated code generated
    by your VM translator should deliver the results mandated by the test
    scripts and compare files supplied.

    Tools:
    Before setting out to extend your basic VM translator, we recommend
    playing with the supplied .vm test programs. This will allow you to
    experiment with branching and function call-and-return commands, using
    the supplied VM emulator.
    For more information, see the VM emulator tutorial in the lectures and in
    the submission page.
    """

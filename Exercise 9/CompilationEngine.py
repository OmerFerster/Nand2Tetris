"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

import typing


def is_int(token: str) -> bool:
    if token.isdigit():
        if 0 <= int(token) <= 32767:
            return True
    return False


def token_type(token) -> str:
    if token[0] == '"' and token[-1] == '"':
        return "STRING_CONST"
    elif token in SYMBOL:
        return "SYMBOL"
    elif token in KEYWORD:
        return "KEYWORD"
    elif is_int(token):
        return "INT_CONST"
    return "IDENTIFIER"


def print_tabs(num_of_tabs, output_stream):
    for i in range(num_of_tabs):
        output_stream.write("\t")
    return


def handle_token(token, output_stream, num_tabs):
    print_tabs(num_tabs, output_stream)
    type_tok = token_type(token)
    if type_tok == "STRING_CONST":
        output_stream.write("<stringConstant> " + token[1:-1] + " </stringConstant>\n")
    elif type_tok == "SYMBOL":
        if token == "<":
            output_stream.write("<symbol> " + "&lt;" + " </symbol>\n")
        elif token == ">":
            output_stream.write("<symbol> " + "&gt;" + " </symbol>\n")
        elif token == "&":
            output_stream.write("<symbol> " + "&amp;" + " </symbol>\n")
        else:
            output_stream.write("<symbol> " + token + " </symbol>\n")
    elif type_tok == "KEYWORD":
        output_stream.write("<keyword> " + token + " </keyword>\n")
    elif type_tok == "INT_CONST":
        output_stream.write("<integerConstant> " + token + " </integerConstant>\n")
    elif type_tok == "IDENTIFIER":
        output_stream.write("<identifier> " + token + " </identifier>\n")


SYMBOL = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&',
          '|', '<', '>', '=', '~', '^', '#']

KEYWORD = ['class', 'constructor', 'function', 'method', 'field', 'static',
           'var', 'int', 'char', 'boolean', 'void', 'true', 'false',
           'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']

OP = ['+', '-', '*', '/', '&', '|', '<', '>', '=', '~']

UNARY = ["-", "~", "^", "#"]

KEYCONST = ["true", "false", "null", "this"]


class CompilationEngine:
    """
    Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = input_stream
        self.out = output_stream
        self.tabs = 0

    def compile_class(self) -> None:
        """
        Compiles a complete class
        """
        # class className { classVarDec*, subroutineDec* }
        if self.tokenizer.input_tokens[self.tokenizer.ind] != "class":
            return
        print_tabs(self.tabs, self.out)
        self.out.write("<class>\n")
        self.tabs += 1
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # class
        self.tokenizer.advance()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # className
        self.tokenizer.advance()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # {
        self.tokenizer.advance()
        self.compile_class_var_dec()
        while (self.tokenizer.input_tokens[self.tokenizer.ind] == "static") or \
                (self.tokenizer.input_tokens[self.tokenizer.ind] == "field"):
            self.compile_class_var_dec()
        while self.tokenizer.input_tokens[self.tokenizer.ind] in ["function", "constructor", "method"]:
            self.compile_subroutine()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # }
        self.tabs -= 1
        print_tabs(self.tabs, self.out)
        self.out.write("</class>\n")

    def compile_class_var_dec(self) -> None:
        """
        Compiles a static declaration or a field declaration
        """
        # static | field varName (, varName)* ;
        if (self.tokenizer.input_tokens[self.tokenizer.ind] != "static") and \
                (self.tokenizer.input_tokens[self.tokenizer.ind] != "field"):
            return
        print_tabs(self.tabs, self.out)
        self.out.write("<classVarDec>\n")
        self.tabs += 1
        while self.tokenizer.input_tokens[self.tokenizer.ind] != ";":
            handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)
            self.tokenizer.advance()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # ;
        self.tokenizer.advance()
        self.tabs -= 1
        print_tabs(self.tabs, self.out)
        self.out.write("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11
        """
        # construct | func | method (void | type) subName (para list) { body }
        if self.tokenizer.input_tokens[self.tokenizer.ind] not in ["function", "constructor", "method"]:
            return
        print_tabs(self.tabs, self.out)
        self.out.write("<subroutineDec>\n")
        self.tabs += 1
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # construct | func | method
        self.tokenizer.advance()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # void | type
        self.tokenizer.advance()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # subName
        self.tokenizer.advance()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # (
        self.tokenizer.advance()
        self.compile_parameter_list()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # )
        self.tokenizer.advance()
        # sub BODY
        print_tabs(self.tabs, self.out)
        self.out.write("<subroutineBody>\n")
        self.tabs += 1
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # {
        self.tokenizer.advance()
        while self.tokenizer.input_tokens[self.tokenizer.ind] == "var":
            self.compile_var_dec()
        self.compile_statements()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # }
        self.tabs -= 1
        print_tabs(self.tabs, self.out)
        self.out.write("</subroutineBody>\n")
        if self.tokenizer.ind < len(self.tokenizer.input_tokens) - 1:
            self.tokenizer.advance()
        self.tabs -= 1
        print_tabs(self.tabs, self.out)
        self.out.write("</subroutineDec>\n")

    def compile_parameter_list(self) -> None:
        """
        Compiles a (possibly empty) parameter list, not including the
        enclosing "()"
        """
        print_tabs(self.tabs, self.out)
        self.out.write("<parameterList>\n")
        self.tabs += 1
        while self.tokenizer.input_tokens[self.tokenizer.ind] != ")":
            handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)
            self.tokenizer.advance()
        self.tabs -= 1
        print_tabs(self.tabs, self.out)
        self.out.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """
        Compiles a var declaration
        """
        # var type varName (, varName)* ;
        if self.tokenizer.input_tokens[self.tokenizer.ind] != "var":
            return
        else:
            print_tabs(self.tabs, self.out)
            self.out.write("<varDec>\n")
            self.tabs += 1
            while self.tokenizer.input_tokens[self.tokenizer.ind] != ";":
                handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)
                self.tokenizer.advance()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)
        self.tokenizer.advance()
        self.tabs -= 1
        print_tabs(self.tabs, self.out)
        self.out.write("</varDec>\n")

    def compile_statements(self) -> None:
        """
        Compiles a sequence of statements, not including the enclosing "{}"
        """
        # statements* (0 or more statements)
        print_tabs(self.tabs, self.out)
        self.out.write("<statements>\n")
        self.tabs += 1
        while self.tokenizer.input_tokens[self.tokenizer.ind] in ["do", "let", "while", "return", "if"]:
            key = self.tokenizer.input_tokens[self.tokenizer.ind].upper()
            if key == "DO":
                self.compile_do()
            elif key == "LET":
                self.compile_let()
            elif key == "WHILE":
                self.compile_while()
            elif key == "RETURN":
                self.compile_return()
            elif key == "IF":
                self.compile_if()
        self.tabs -= 1
        print_tabs(self.tabs, self.out)
        self.out.write("</statements>\n")

    def compile_do(self) -> None:
        """
        Compiles a do statement
        """
        # do subroutineCall;
        # subroutineCall - subName(expressionList) | className|varName.subName(expressionList)
        if self.tokenizer.input_tokens[self.tokenizer.ind] != "do":
            return
        print_tabs(self.tabs, self.out)
        self.out.write("<doStatement>\n")
        self.tabs += 1
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # do
        self.tokenizer.advance()
        curr_name = self.tokenizer.input_tokens[self.tokenizer.ind]
        self.tokenizer.advance()
        next_token = self.tokenizer.input_tokens[self.tokenizer.ind]
        if next_token == ".":
            handle_token(curr_name, self.out, self.tabs)  # className|varName
            handle_token(next_token, self.out, self.tabs)  # .
            self.tokenizer.advance()
            handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # subName
            self.tokenizer.advance()
            handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # (
            self.tokenizer.advance()
            self.compile_expression_list()
        elif next_token == "(":
            handle_token(curr_name, self.out, self.tabs)  # subName
            handle_token(next_token, self.out, self.tabs)  # (
            self.tokenizer.advance()
            self.compile_expression_list()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # ;
        self.tokenizer.advance()
        self.tabs -= 1
        print_tabs(self.tabs, self.out)
        self.out.write("</doStatement>\n")

    def compile_let(self) -> None:
        """
        Compiles a let statement
        """
        # let varName ([expression])? = expression ;
        if self.tokenizer.input_tokens[self.tokenizer.ind] != "let":
            return
        print_tabs(self.tabs, self.out)
        self.out.write("<letStatement>\n")
        self.tabs += 1
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # let
        self.tokenizer.advance()
        var_name = self.tokenizer.input_tokens[self.tokenizer.ind]
        self.tokenizer.advance()
        next_token = self.tokenizer.input_tokens[self.tokenizer.ind]
        if next_token == "[":
            handle_token(var_name, self.out, self.tabs)  # varName
            handle_token(next_token, self.out, self.tabs)  # [
            self.tokenizer.advance()
            self.compile_expression()
            handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # ]
            self.tokenizer.advance()
            handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # =
            self.tokenizer.advance()
            self.compile_expression()
        elif next_token == "=":
            handle_token(var_name, self.out, self.tabs)  # varName
            handle_token(next_token, self.out, self.tabs)  # =
            self.tokenizer.advance()
            self.compile_expression()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # ;
        self.tokenizer.advance()
        self.tabs -= 1
        print_tabs(self.tabs, self.out)
        self.out.write("</letStatement>\n")

    def compile_while(self) -> None:
        """
        Compiles a while statement
        """
        # while ( expression ) { statements }
        if self.tokenizer.input_tokens[self.tokenizer.ind] != "while":
            return
        print_tabs(self.tabs, self.out)
        self.out.write("<whileStatement>\n")
        self.tabs += 1
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # while
        self.tokenizer.advance()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # (
        self.tokenizer.advance()
        self.compile_expression()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # )
        self.tokenizer.advance()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # {
        self.tokenizer.advance()
        self.compile_statements()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # }
        self.tokenizer.advance()
        self.tabs -= 1
        print_tabs(self.tabs, self.out)
        self.out.write("</whileStatement>\n")

    def compile_return(self) -> None:
        """
        Compiles a return statement
        """
        # return expression? ;
        if self.tokenizer.input_tokens[self.tokenizer.ind] != "return":
            return
        print_tabs(self.tabs, self.out)
        self.out.write("<returnStatement>\n")
        self.tabs += 1
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind],self.out, self.tabs)  # return
        self.tokenizer.advance()
        if self.tokenizer.input_tokens[self.tokenizer.ind] != ";":
            self.compile_expression()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # ;
        self.tokenizer.advance()
        self.tabs -= 1
        print_tabs(self.tabs, self.out)
        self.out.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """
        Compiles a if statement, possibly with a trailing else clause
        """
        # if ( expression ) { statements } handle else later
        if self.tokenizer.input_tokens[self.tokenizer.ind] != "if":
            return
        print_tabs(self.tabs, self.out)
        self.out.write("<ifStatement>\n")
        self.tabs += 1
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # if
        self.tokenizer.advance()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # (
        self.tokenizer.advance()
        self.compile_expression()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # )
        self.tokenizer.advance()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # {
        self.tokenizer.advance()
        self.compile_statements()
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # }
        self.tokenizer.advance()
        next_token = self.tokenizer.input_tokens[self.tokenizer.ind]
        if next_token == "else":
            handle_token(next_token, self.out, self.tabs)  # else
            self.tokenizer.advance()
            handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # {
            self.tokenizer.advance()
            self.compile_statements()
            handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # }
            self.tokenizer.advance()
        self.tabs -= 1
        print_tabs(self.tabs, self.out)
        self.out.write("</ifStatement>\n")

    def compile_expression(self) -> None:
        """
        Compiles an expression
        """
        # term (op term)*
        print_tabs(self.tabs, self.out)
        self.out.write("<expression>\n")
        self.tabs += 1
        self.compile_term()
        if self.tokenizer.input_tokens[self.tokenizer.ind] in OP:
            while self.tokenizer.input_tokens[self.tokenizer.ind] in OP:
                # self.compile_term()
                handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)
                self.tokenizer.advance()
                self.compile_term()
        self.tabs -= 1
        print_tabs(self.tabs, self.out)
        self.out.write("</expression>\n")

    def compile_term(self) -> None:
        """
        Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # intConst | strConst | keywordConst | varName | varName[expression]
        # | subRoutineCall | ( expression ) | unaryOP term
        print_tabs(self.tabs, self.out)
        self.out.write("<term>\n")
        self.tabs += 1
        tok_type = token_type(self.tokenizer.input_tokens[self.tokenizer.ind])
        if tok_type != "SYMBOL" and tok_type != "IDENTIFIER":
            handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)
            self.tokenizer.advance()
        elif tok_type == "IDENTIFIER":
            handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)
            self.tokenizer.advance()
            if self.tokenizer.input_tokens[self.tokenizer.ind] == "[":
                handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # [
                self.tokenizer.advance()
                self.compile_expression()
                handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # ]
                self.tokenizer.advance()
            elif self.tokenizer.input_tokens[self.tokenizer.ind] in ["(", "."]:
                next_token = self.tokenizer.input_tokens[self.tokenizer.ind]
                if next_token == ".":
                    handle_token(next_token, self.out, self.tabs)  # .
                    self.tokenizer.advance()
                    handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # subName
                    self.tokenizer.advance()
                    handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # (
                    self.tokenizer.advance()
                    self.compile_expression_list()
                elif next_token == "(":
                    handle_token(next_token, self.out, self.tabs)  # (
                    self.tokenizer.advance()
                    self.compile_expression_list()
        elif tok_type == "SYMBOL":
            if self.tokenizer.input_tokens[self.tokenizer.ind] == "(":
                handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # (
                self.tokenizer.advance()
                self.compile_expression()
                handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # ) got <
                self.tokenizer.advance()
            elif self.tokenizer.input_tokens[self.tokenizer.ind] in UNARY:
                handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # ~
                self.tokenizer.advance()
                self.compile_term()
        self.tabs -= 1
        print_tabs(self.tabs, self.out)
        self.out.write("</term>\n")

    def compile_expression_list(self) -> None:
        """
        Compiles a (possibly empty) comma-separated list of expressions
        """
        print_tabs(self.tabs, self.out)
        self.out.write("<expressionList>\n")
        self.tabs += 1
        # (expression (, expression)*)?
        while self.tokenizer.input_tokens[self.tokenizer.ind] != ")":
            if self.tokenizer.input_tokens[self.tokenizer.ind] == ",":
                handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)
                self.tokenizer.advance()
            else:
                self.compile_expression()
        self.tabs -= 1
        print_tabs(self.tabs, self.out)
        self.out.write("</expressionList>\n")
        handle_token(self.tokenizer.input_tokens[self.tokenizer.ind], self.out, self.tabs)  # )
        self.tokenizer.advance()

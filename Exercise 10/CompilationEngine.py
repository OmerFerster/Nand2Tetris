"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

import typing
from SymbolTable import SymbolTable
from VMWriter import VMWriter

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
        if token in KEYCONST:
            return "KEYCONST"
        else:
            return "KEYWORD"
    elif is_int(token):
        return "INT_CONST"
    return "IDENTIFIER"


SYMBOL = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&',
          '|', '<', '>', '=', '~', '^', '#']

KEYWORD = ['class', 'constructor', 'function', 'method', 'field', 'static',
           'var', 'int', 'char', 'boolean', 'void', 'true', 'false',
           'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']

OP = ['+', '-', '*', '/', '&', '|', '<', '>', '=', '~']

UNARY = ["-", "~", "^", "#"]

KEYCONST = ["true", "false", "null", "this"]

NOT_FOUND = -999

NONE = "NONE"

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
        self.curr_class_name = ""
        self.curr_func_return_type = ""
        self.is_para_list = False
        self.is_var_list = False
        self.func_calls = []
        self.para_list_nums = 0
        self.if_count = 0
        self.while_count = 0
        self.needed_num_of_args = 0
        self.sub_local_num = 0
        self.symbol_table = SymbolTable()
        self.writer = VMWriter(output_stream)

    def __handle_token(self, token):
        type_tok = token_type(token)
        if type_tok == "IDENTIFIER":
            prev_prev_ind = self.tokenizer.ind - 2
            prev_ind = self.tokenizer.ind - 1
            next_ind = self.tokenizer.ind + 1
            self.__handle_identifier(self.tokenizer.input_tokens[prev_prev_ind],
                                     self.tokenizer.input_tokens[prev_ind],
                                     token, self.tokenizer.input_tokens[next_ind])

    def __handle_identifier(self, prev_prev, prev, name, next):
        type_tok = token_type(name)
        if type_tok != "IDENTIFIER":
            return
        if prev_prev.upper() in ["STATIC", "FIELD", "ARG", "VAR"]:
            self.symbol_table.define(name, prev, prev_prev.upper())
            if self.is_para_list:
                self.para_list_nums += 1
            if self.is_var_list:
                self.sub_local_num += 1
        elif prev == ",":
            self.symbol_table.define(name,
                                     self.symbol_table.type_of(prev_prev),
                                     self.symbol_table.kind_of(prev_prev).upper())
            if self.is_para_list:
                self.para_list_nums += 1
            if self.is_var_list:
                self.sub_local_num += 1
        elif prev_prev == "(" or next == "," or next == ")":
            if self.is_para_list:
                self.symbol_table.define(name, prev, "ARG")
                self.para_list_nums += 1
            if self.is_var_list:
                self.sub_local_num += 1

    def compile_class(self) -> None:
        """
        Compiles a complete class
        """
        # class className { classVarDec*, subroutineDec* }
        if self.tokenizer.input_tokens[self.tokenizer.ind] != "class":
            return
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # class
        self.tokenizer.advance()
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # className
        self.curr_class_name = self.tokenizer.input_tokens[self.tokenizer.ind]
        self.tokenizer.advance()
        self.symbol_table.field_ind, self.symbol_table.static_ind = 0, 0
        self.symbol_table.class_table = []  # reset class symbol-table
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # {
        self.tokenizer.advance()
        self.compile_class_var_dec()
        while (self.tokenizer.input_tokens[self.tokenizer.ind] == "static") or \
                (self.tokenizer.input_tokens[self.tokenizer.ind] == "field"):
            self.compile_class_var_dec()
        while self.tokenizer.input_tokens[self.tokenizer.ind] in ["function",
                                                                  "constructor",
                                                                  "method"]:
            self.compile_subroutine()
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # }

    def compile_class_var_dec(self) -> None:
        """
        Compiles a static declaration or a field declaration
        """
        # static | field varName (, varName)* ;
        if (self.tokenizer.input_tokens[self.tokenizer.ind] != "static") and \
                (self.tokenizer.input_tokens[self.tokenizer.ind] != "field"):
            return
        while self.tokenizer.input_tokens[self.tokenizer.ind] != ";":
            self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])
            self.tokenizer.advance()
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # ;
        self.tokenizer.advance()

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11
        """
        # construct | func | method (void | type) subName (para list) { body }
        if self.tokenizer.input_tokens[self.tokenizer.ind] not in ["function",
                                                                   "constructor",
                                                                   "method"]:
            return
        sub_type = self.tokenizer.input_tokens[self.tokenizer.ind].upper()
        self.symbol_table.start_subroutine()
        if sub_type == "METHOD":
            self.symbol_table.define("this", self.curr_class_name, "ARG")
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # construct | func | method
        self.tokenizer.advance()
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # void | type
        self.curr_func_return_type = self.tokenizer.input_tokens[self.tokenizer.ind]
        self.tokenizer.advance()
        func_name = self.curr_class_name + "." + self.tokenizer.input_tokens[self.tokenizer.ind]
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # subName
        self.tokenizer.advance()
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # (
        self.tokenizer.advance()
        self.para_list_nums = 0
        self.compile_parameter_list()
        self.func_calls.append([self.curr_class_name + "." + func_name, self.para_list_nums])
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # )
        self.tokenizer.advance()
        # sub BODY
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # {
        self.tokenizer.advance()
        self.sub_local_num = 0
        while self.tokenizer.input_tokens[self.tokenizer.ind] == "var":
            self.compile_var_dec()
        self.writer.write_function(func_name, self.sub_local_num)
        self.sub_local_num = 0
        if sub_type == "METHOD":
            self.writer.write_push("ARG", 0)
            self.writer.write_pop("POINTER", 0)
        if func_name == self.curr_class_name + ".new":
            if self.symbol_table.field_ind > 0:
                self.writer.write_push("CONST", self.symbol_table.field_ind)
                self.writer.write_call("Memory.alloc", 1)
                self.writer.write_pop("POINTER", 0)
        self.para_list_nums = 0
        self.compile_statements()
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # }
        if self.tokenizer.ind < len(self.tokenizer.input_tokens) - 1:
            self.tokenizer.advance()

    def compile_parameter_list(self) -> None:
        """
        Compiles a (possibly empty) parameter list, not including the
        enclosing "()"
        """
        self.is_para_list = True
        while self.tokenizer.input_tokens[self.tokenizer.ind] != ")":
            self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])
            self.tokenizer.advance()
        self.is_para_list = False

    def compile_var_dec(self) -> None:
        """
        Compiles a var declaration
        """
        # var type varName (, varName)* ;
        if self.tokenizer.input_tokens[self.tokenizer.ind] != "var":
            return
        else:
            self.is_var_list = True
            while self.tokenizer.input_tokens[self.tokenizer.ind] != ";":
                self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])
                self.tokenizer.advance()
            self.is_var_list = False
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])
        self.tokenizer.advance()

    def compile_statements(self) -> None:
        """
        Compiles a sequence of statements, not including the enclosing "{}"
        """
        # statements* (0 or more statements)
        while self.tokenizer.input_tokens[self.tokenizer.ind] in ["do", "let",
                                                                  "while",
                                                                  "return",
                                                                  "if"]:
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

    def compile_do(self) -> None:
        """
        Compiles a do statement
        """
        # do subroutineCall;
        # subroutineCall - subName(expressionList) | className|varName.subName(expressionList)
        if self.tokenizer.input_tokens[self.tokenizer.ind] != "do":
            return
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # do
        self.tokenizer.advance()
        later_call = self.tokenizer.input_tokens[self.tokenizer.ind]
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # className|varName
        self.tokenizer.advance()
        next_token = self.tokenizer.input_tokens[self.tokenizer.ind]
        self.needed_num_of_args = 0
        method = False
        if next_token == ".":
            name = later_call
            if self.symbol_table.kind_of(later_call) != NONE:
                later_call = self.symbol_table.type_of(later_call)
                method = True
                a = self.symbol_table.kind_of(name).upper()
                b = self.symbol_table.index_of(name)
                self.writer.write_push(a, b)
            later_call += "."
            self.__handle_token(next_token)  # .
            self.tokenizer.advance()
            later_call += self.tokenizer.input_tokens[self.tokenizer.ind]
            self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # subName
            self.tokenizer.advance()
            self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # (
            self.tokenizer.advance()
            self.compile_expression_list()
        elif next_token == "(":
            # call a method (this arg 0 need to be pusHED AND CALLED)
            method = True
            self.writer.write_push("POINTER", 0)
            later_call = self.curr_class_name + "." + later_call
            self.__handle_token(next_token)  # (
            self.tokenizer.advance()
            self.compile_expression_list()
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # ;
        self.tokenizer.advance()
        if method:
            self.needed_num_of_args += 1
        self.writer.write_call(later_call, self.needed_num_of_args)
        self.writer.write_pop("TEMP", 0)
        self.needed_num_of_args = 0

    def compile_let(self) -> None:
        """
        Compiles a let statement
        """
        # let varName ([expression])? = expression ;
        if self.tokenizer.input_tokens[self.tokenizer.ind] != "let":
            return
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # let
        self.tokenizer.advance()
        var_name = self.tokenizer.input_tokens[self.tokenizer.ind]
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # varName
        self.tokenizer.advance()
        next_token = self.tokenizer.input_tokens[self.tokenizer.ind]
        if next_token == "[":
            self.__handle_token(next_token)  # [
            self.tokenizer.advance()
            self.compile_expression()
            a = self.symbol_table.kind_of(var_name).upper()
            b = self.symbol_table.index_of(var_name)
            self.writer.write_push(a, b)
            self.writer.write_arithmetic("+")
            self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # ]
            self.tokenizer.advance()
            self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # =
            self.tokenizer.advance()
            self.compile_expression()
            self.writer.write_pop("TEMP", 0)
            self.writer.write_pop("POINTER", 1)
            self.writer.write_push("TEMP", 0)
            self.writer.write_pop("THAT", 0)
        elif next_token == "=":
            self.__handle_token(next_token)  # =
            self.tokenizer.advance()
            self.compile_expression()
            self.writer.write_pop(self.symbol_table.kind_of(var_name).upper(),
                                  self.symbol_table.index_of(var_name))
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # ;
        self.tokenizer.advance()

    def compile_while(self) -> None:
        """
        Compiles a while statement
        """
        # while ( expression ) { statements }
        if self.tokenizer.input_tokens[self.tokenizer.ind] != "while":
            return
        l1 = self.curr_class_name + ".While.L" + str(self.while_count)
        self.while_count += 1
        l2 = self.curr_class_name + ".While.L" + str(self.while_count)
        self.while_count += 1
        self.writer.write_label(l1)
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # while
        self.tokenizer.advance()
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # (
        self.tokenizer.advance()
        self.compile_expression()
        self.writer.write_arithmetic("~")  # NEG the expression
        self.writer.write_if(l2)
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # )
        self.tokenizer.advance()
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # {
        self.tokenizer.advance()
        self.compile_statements()
        self.writer.write_goto(l1)
        self.writer.write_label(l2)
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # }
        self.tokenizer.advance()

    def compile_return(self) -> None:
        """
        Compiles a return statement
        """
        # return expression? ;
        if self.tokenizer.input_tokens[self.tokenizer.ind] != "return":
            return
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # return
        self.tokenizer.advance()
        if self.tokenizer.input_tokens[self.tokenizer.ind] != ";":
            self.compile_expression()
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # ;
        self.tokenizer.advance()
        if self.curr_func_return_type == "void":
            self.writer.write_push("CONST", 0)
        self.writer.write_return()

    def compile_if(self) -> None:
        """
        Compiles a if statement, possibly with a trailing else clause
        """
        # if ( expression ) { statements } handle else later
        if self.tokenizer.input_tokens[self.tokenizer.ind] != "if":
            return
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # if
        self.tokenizer.advance()
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # (
        self.tokenizer.advance()
        self.compile_expression()
        self.writer.write_arithmetic("~")  # NEG the expression
        l1 = self.curr_class_name + ".If.L" + str(self.if_count)
        self.if_count += 1
        l2 = self.curr_class_name + ".If.L" + str(self.if_count)
        self.if_count += 1
        self.writer.write_if(l1)
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # )
        self.tokenizer.advance()
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # {
        self.tokenizer.advance()
        self.compile_statements()
        self.writer.write_goto(l2)
        self.writer.write_label(l1)
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # }
        self.tokenizer.advance()
        next_token = self.tokenizer.input_tokens[self.tokenizer.ind]
        if next_token == "else":
            self.__handle_token(next_token)  # else
            self.tokenizer.advance()
            self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # {
            self.tokenizer.advance()
            self.compile_statements()
            self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # }
            self.tokenizer.advance()
        self.writer.write_label(l2)

    def compile_expression(self) -> None:
        """
        Compiles an expression
        """
        # term (op term)*
        self.compile_term()
        if self.tokenizer.input_tokens[self.tokenizer.ind] in OP:
            while self.tokenizer.input_tokens[self.tokenizer.ind] in OP:
                op = self.tokenizer.input_tokens[self.tokenizer.ind]
                self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])
                self.tokenizer.advance()
                self.compile_term()
                self.writer.write_arithmetic(op)

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
        tok_type = token_type(self.tokenizer.input_tokens[self.tokenizer.ind])
        if tok_type != "SYMBOL" and tok_type != "IDENTIFIER":
            if tok_type == "INT_CONST":
                self.writer.write_push("CONST", int(self.tokenizer.input_tokens[self.tokenizer.ind]))
            if tok_type == "STRING_CONST":
                string_name = self.tokenizer.input_tokens[self.tokenizer.ind]
                self.writer.write_push("CONST", len(string_name) - 2)
                self.writer.write_call("String.new", 1)
                for i in range(1, len(string_name) - 1):
                    self.writer.write_push("CONST", ord(string_name[i]))
                    self.writer.write_call("String.appendChar", 2)
            if tok_type == "KEYCONST":
                if self.tokenizer.input_tokens[self.tokenizer.ind] == "this":
                    self.writer.write_push("POINTER", 0)
                elif self.tokenizer.input_tokens[self.tokenizer.ind] in ["false", "null"]:
                    self.writer.write_push("CONST", 0)
                elif self.tokenizer.input_tokens[self.tokenizer.ind] == "true":
                    self.writer.write_push("CONST", 0)
                    self.writer.write_arithmetic("~", True)  # TODO check this
            self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])
            self.tokenizer.advance()
        elif tok_type == "IDENTIFIER":
            name = self.tokenizer.input_tokens[self.tokenizer.ind]
            curr_obj = name
            if self.symbol_table.kind_of(name) != NONE:
                kind = self.symbol_table.kind_of(self.tokenizer.input_tokens[self.tokenizer.ind])
                ind = self.symbol_table.index_of(self.tokenizer.input_tokens[self.tokenizer.ind])
                self.writer.write_push(kind.upper(), ind)
                name = self.symbol_table.type_of(name)
            self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])
            self.tokenizer.advance()
            if self.tokenizer.input_tokens[self.tokenizer.ind] == "[":
                self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # [
                self.tokenizer.advance()
                self.compile_expression()
                self.writer.write_arithmetic("+")
                self.writer.write_pop("POINTER", 1)
                self.writer.write_push("THAT", 0)
                self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # ]
                self.tokenizer.advance()
            elif self.tokenizer.input_tokens[self.tokenizer.ind] in ["(", "."]:
                is_method = False
                next_token = self.tokenizer.input_tokens[self.tokenizer.ind]
                if next_token == ".":
                    if self.symbol_table.kind_of(curr_obj) != NONE:
                        is_method = True
                    name += "."
                    self.__handle_token(next_token)  # .
                    self.tokenizer.advance()
                    self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # subName
                    name += self.tokenizer.input_tokens[self.tokenizer.ind]
                    self.tokenizer.advance()
                    self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # (
                    self.tokenizer.advance()
                    self.needed_num_of_args = 0
                    self.compile_expression_list()
                    if is_method:
                        self.needed_num_of_args += 1
                    self.writer.write_call(name, self.needed_num_of_args)
                    self.needed_num_of_args = 0
                elif next_token == "(":
                    self.__handle_token(next_token)  # (
                    self.tokenizer.advance()
                    self.needed_num_of_args = 0
                    self.compile_expression_list()
                    self.writer.write_call(name, self.needed_num_of_args)
                    self.needed_num_of_args = 0
        elif tok_type == "SYMBOL":
            if self.tokenizer.input_tokens[self.tokenizer.ind] == "(":
                self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # (
                self.tokenizer.advance()
                self.compile_expression()
                self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # )
                self.tokenizer.advance()
            elif self.tokenizer.input_tokens[self.tokenizer.ind] in UNARY:
                self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # ~
                op = self.tokenizer.input_tokens[self.tokenizer.ind]
                self.tokenizer.advance()
                self.compile_term()
                if op == "-":
                    self.writer.write_arithmetic(op, True)
                else:
                    self.writer.write_arithmetic(op)

    def compile_expression_list(self) -> None:
        """
        Compiles a (possibly empty) comma-separated list of expressions
        """
        # (expression (, expression)*)?
        self.para_list_nums = 0
        if self.tokenizer.input_tokens[self.tokenizer.ind] != ")":
            self.needed_num_of_args += 1
        while self.tokenizer.input_tokens[self.tokenizer.ind] != ")":
            if self.tokenizer.input_tokens[self.tokenizer.ind] == ",":
                self.needed_num_of_args += 1
                self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])
                self.tokenizer.advance()
            else:
                self.compile_expression()
        self.__handle_token(self.tokenizer.input_tokens[self.tokenizer.ind])  # )
        self.tokenizer.advance()

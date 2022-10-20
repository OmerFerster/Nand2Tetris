"""
This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

import typing

TRASH = ["/", "*"]


def is_white_space(line: str) -> bool:
    line = line.replace(" ", "")
    line = line.lstrip()
    if line == "":
        return True
    if len(line) > 1 and ((line[0] == "/" and line[1] in TRASH) or (line[0] == "*")):
        return True
    return False


def token_helper(token: str) -> list:
    res = []
    last = 0
    me = ""
    for i in range(len(token)):
        if token[i] in SYMBOL:
            res.append(token[last:i])
            res.append(token[i])
            last = i + 1
            me = ""
        else:
            me += token[i]
    res.append(me)
    return res


def is_int(token: str) -> bool:
    if token.isdigit():
        if 0 <= int(token) <= 32767:
            return True
    return False


SYMBOL = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&',
          '|', '<', '>', '=', '~', '^', '#']

KEYWORD = ['class', 'constructor', 'function', 'method', 'field', 'static',
           'var', 'int', 'char', 'boolean', 'void', 'true', 'false',
           'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']


class JackTokenizer:
    """
    Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    An Xxx .jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of space characters, 
    newline characters, and comments, which are ignored. There are three 
    possible comment formats: /* comment until closing */ , /** API comment 
    until closing */ , and // comment until the line’s end.

    ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’);
    xxx: regular typeface is used for names of language constructs 
    (‘non-terminals’);
    (): parentheses are used for grouping of language constructs;
    x | y: indicates that either x or y can appear;
    x?: indicates that x appears 0 or 1 times;
    x*: indicates that x appears 0 or more times.

    ** Lexical elements **
    The Jack language includes five types of terminal elements (tokens).
    1. keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
        'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' | 'false'
        | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 'while' | 'return'
    2. symbol:  '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
        '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    3. integerConstant: A decimal number in the range 0-32767.
    4. StringConstant: '"' A sequence of Unicode characters not including 
        double quote or newline '"'
    5. identifier: A sequence of letters, digits, and underscore ('_') not 
        starting with a digit.


    ** Program structure **
    A Jack program is a collection of classes, each appearing in a separate 
    file. The compilation unit is a class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    class: 'class' className '{' classVarDec* subroutineDec* '}'
    classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    type: 'int' | 'char' | 'boolean' | className
    subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    subroutineName '(' parameterList ')' subroutineBody
    parameterList: ((type varName) (',' type varName)*)?
    subroutineBody: '{' varDec* statements '}'
    varDec: 'var' type varName (',' varName)* ';'
    className: identifier
    subroutineName: identifier
    varName: identifier


    ** Statements **
    statements: statement*
    statement: letStatement | ifStatement | whileStatement | doStatement | 
        returnStatement
    letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
        statements '}')?
    whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    doStatement: 'do' subroutineCall ';'
    returnStatement: 'return' expression? ';'


    ** Expressions **
    expression: term (op term)*
    term: integerConstant | stringConstant | keywordConstant | varName | 
        varName '['expression']' | subroutineCall | '(' expression ')' | 
        unaryOp term
    subroutineCall: subroutineName '(' expressionList ')' | (className | 
        varName) '.' subroutineName '(' expressionList ')'
    expressionList: (expression (',' expression)* )?
    op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    unaryOp: '-' | '~' | '^' | '#'
    keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    If you are wondering whether some Jack program is valid or not, you should
    use the built-in JackCompiler to compiler it. If the compilation fails, it
    is invalid. Otherwise, it is valid.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """
        Opens the input stream and gets ready to tokenize it.
        Args input_stream (typing.TextIO): input stream.
        """
        self.input_tokens = input_stream.read().splitlines()
        self.res = []
        self.ind = 0  # represent the index of the token number
        while self.has_more_tokens():
            if not is_white_space(self.input_tokens[self.ind]):
                curr_str = self.input_tokens[self.ind]
                slash_ind = curr_str.find("//")
                if slash_ind == -1:
                    curr_str = curr_str.strip()
                else:
                    curr_str = curr_str[0:slash_ind].strip()
                helper_list = curr_str.split()
                for token in helper_list:
                    last = token_helper(token)
                    for elem in last:
                        if elem != """""":
                            self.res.append(elem)
            self.advance()
        self.input_tokens = self.res
        after_string = []
        flag = False
        last_str = ""
        for elem in self.res:
            if elem[0] == '"':
                flag = True
            if not flag:
                after_string.append(elem)
            else:
                last_str += elem + " "
            if elem[-1] == '"':
                flag = False
                after_string.append(last_str[0:-1])
                last_str = ""
        self.input_tokens = after_string
        self.ind = 0

    def has_more_tokens(self) -> bool:
        """
        Do we have more tokens in the input?
        Returns bool: True if there are more tokens, False otherwise.
        """
        if self.ind != len(self.input_tokens):
            return True
        return False

    def advance(self) -> None:
        """
        Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.ind += 1
        while len(self.input_tokens) != self.ind:
            if is_white_space(self.input_tokens[self.ind]):
                self.ind += 1
            else:
                return None

    def token_type(self) -> str:
        """
        Returns str: the type of the current token, can be
        "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        curr_token = self.input_tokens[self.ind]
        if curr_token[0] == '"' and curr_token[-1] == '"':
            return "STRING_CONST"
        elif curr_token in SYMBOL:
            return "SYMBOL"
        elif curr_token in KEYWORD:
            return "KEYWORD"
        elif is_int(curr_token):
            return "INT_CONST"
        return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Returns str: the keyword which is the current token.
        Should be called only when token_type() is "KEYWORD".
        Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
        "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO",
        "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        if self.token_type() == "KEYWORD":
            for elem in KEYWORD:
                if elem == self.input_tokens[self.ind]:
                    return elem.upper()
        return ""

    def symbol(self) -> str:
        """
        Returns str: the character which is the current token.
        Should be called only when token_type() is "SYMBOL".
        """
        if self.token_type() == "SYMBOL":
            for elem in SYMBOL:
                if elem == self.input_tokens[self.ind]:
                    if elem == "<":
                        return "&lt;"
                    elif elem == ">":
                        return "&gt;"
                    elif elem == "&":
                        return "&amp;"
                    else:
                        return elem
        return ""

    def identifier(self) -> str:
        """
        Returns str: the identifier which is the current token.
        Should be called only when token_type() is "IDENTIFIER".
        """
        if self.token_type() == "IDENTIFIER":
            return self.input_tokens[self.ind]
        return ""

    def int_val(self) -> int:
        """
        Returns str: the integer value of the current token.
        Should be called only when token_type() is "INT_CONST".
        """
        if self.token_type() == "INT_CONST":
            return int(self.input_tokens[self.ind])

    def string_val(self) -> str:
        """
        Returns str: the string value of the current token, without the double
        quotes. Should be called only when token_type() is "STRING_CONST".
        """
        if self.token_type() == "STRING_CONST":
            return self.input_tokens[self.ind][1:-1]

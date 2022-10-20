"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

import typing

NOT_FOUND = -999
NONE = "NONE"


class SymbolTable:
    """
    A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    if symbol not found (subVAR / classVar ) is perhaps subName / className
    """

    def __init__(self) -> None:
        """
        Creates a new empty symbol table.
        List[0] is Class Table, List[1] is Subroutine Table
        [ [classTable], [subroutineTable] ]
        each variable looks like this in the Table: [name, type, kind, ind]
        """
        self.field_ind, self.static_ind, self.arg_ind, self.local_ind = 0, 0, 0, 0
        self.class_table, self.sub_table = [], []

    def start_subroutine(self) -> None:
        """
        Starts a new subroutine scope (i.e., resets the subroutine's symbol table).
        """
        self.arg_ind, self.local_ind = 0, 0
        self.sub_table = []

    def define(self, name: str, type: str, kind: str) -> None:
        """
        Defines a new identifier of a given name, type and kind and assigns
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.
        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
            VAR = LOCAL segment
            FIELD = THIS segment
        """
        if self.kind_of(name) != NONE:
            return
        if kind == "STATIC":
            self.class_table.append([name, type, kind.lower(), self.static_ind])
            self.static_ind += 1
        elif kind == "FIELD":
            self.class_table.append([name, type, kind.lower(), self.field_ind])
            self.field_ind += 1
        elif kind == "ARG":
            self.sub_table.append([name, type, kind.lower(), self.arg_ind])
            self.arg_ind += 1
        elif kind == "VAR":
            self.sub_table.append([name, type, kind.lower(), self.local_ind])
            self.local_ind += 1

    def var_count(self, kind: str) -> int:
        """
        Args kind (str): can be "STATIC", "FIELD", "ARG", "VAR".
        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        if kind == "STATIC":
            return self.static_ind
        elif kind == "FIELD":
            return self.field_ind
        elif kind == "ARG":
            return self.arg_ind
        elif kind == "VAR":
            return self.local_ind

    def kind_of(self, name: str) -> str:
        """
        Args name (str): name of an identifier.
        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        for elem in self.sub_table:
            if elem[0] == name:
                return elem[2]
        for elem in self.class_table:
            if elem[0] == name:
                return elem[2]
        return NONE  # The identifier is UNKNOWN in the SymbolTable atm

    def type_of(self, name: str) -> str:
        """
        Args: name (str):  name of an identifier.
        Returns:
            str: the type of the named identifier in the current scope.
        """
        for elem in self.sub_table:
            if elem[0] == name:
                return elem[1]
        for elem in self.class_table:
            if elem[0] == name:
                return elem[1]
        return NONE  # The identifier is UNKNOWN in the SymbolTable atm

    def index_of(self, name: str) -> int:
        """
        Args name (str):  name of an identifier.
        Returns int: the index assigned to the named identifier.
        """
        for elem in self.sub_table:
            if elem[0] == name:
                return elem[-1]
        for elem in self.class_table:
            if elem[0] == name:
                return elem[-1]
        return NOT_FOUND  # The identifier is UNKNOWN in the SymbolTable atm

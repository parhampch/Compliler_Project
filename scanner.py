import re

class Node:
    def __init__(self, name: int, is_final: bool, has_star: bool, is_error: bool) -> None:
        self.name = name
        self.is_final = is_final
        self.has_star = has_star
        self.is_error = is_error


class DFA:
    def __init__(self, states: dict, transition_function: dict, start_state: int, trash_state: int) -> None:
        self.states = states
        self.transition_function = transition_function
        self.start_state = start_state
        self.trash_state = trash_state
        self.current_state = self.states[self.start_state]

    def next_state(self, char: str) -> Node:
        if self.current_state.is_final:
            self.current_state = self.states[self.start_state]
        for regex in self.transition_function[self.current_state.name].keys():
            if re.search(regex, char) != None:
                self.current_state = self.states[self.transition_function[self.current_state.name][regex]]
                break
        else: self.current_state = self.states[self.trash_state]
        return self.current_state


class Scanner:
    def __init__(self) -> None:
        self.start_state = 0

        self.eof_state = 20

        self.trash_state = 23

        self.states = {0: Node(0, False, False, False), 1: Node(1, False, False, False), 2: Node(2, False, False, False), 3: Node(3, False, False, False), 
                       4: Node(4, True, True, False), 5: Node(5, False, False, False), 6: Node(6, True, True, False), 7: Node(7, True, False, False),
                       8: Node(8, False, False, False), 9: Node(9, False, False, False), 10: Node(10, True, True, False), 11: Node(11, True, False, False),
                       12: Node(12, False, False, False), 13: Node(13, False, False, False), 14: Node(14, False, False, False),15: Node(15, False, False, False),
                       16: Node(16, True, False, False), 17: Node(17, True, False, True), 18: Node(18, True, False, False), 19: Node(19, True, True, True), 
                       20: Node(20, True, False, False), 21: Node(21, True, True, False), 22: Node(22, True, False, True), 23: Node(23, True, False, True), 
                       24: Node(24, True, True, True)}

        self.transition_function = {0: {"[0-9]": 1, "[a-zA-Z]": 5, "[\[\]\<;:()+\-]": 7, "\*": 8, "=": 9,
                                        "[\x09\x0A\x0B\x0C\x0D\x20]": 11, "/": 12, "\#": 15, "\x1A": 20},
                                    1: {"[0-9]": 1, "[.]": 2, "[\x09\x0A\x0B\x0C\x0D\x20\[\]\<;:()+\-/\#\x1A=*]": 4,
                                        "[^\x09\x0A\x0B\x0C\x0D\x20\[\]\<;:()+\-/\#\x1A0-9.=*]": 17}, 2: {"[0-9]": 3,
                                                                                                        "[^0-9]": 17},
                                    3: {"[0-9]": 3, "[\x09\x0A\x0B\x0C\x0D\x20\[\]\<;:()+\-/\#\x1A=*]": 4,
                                        "[^\x09\x0A\x0B\x0C\x0D\x20\[\]\<;:()+\-/\#\x1A0-9=*]": 17}, 4: {},
                                    5: {"[a-zA-Z0-9]": 5, "[^a-zA-Z0-9]": 6}, 6: {}, 7: {},
                                    8: {"\*": 7, "[^\*/]": 10, "/": 22}, 9: {"=": 7, "[^=]": 10}, 10: {}, 11: {},
                                    12: {"\*": 13, "[^\*]": 24}, 13: {"\*": 14,"\x1A": 19, "[^\*]": 13},
                                    14: {"\*": 14, "[^\*/]": 13, "/": 18, "\x1A": 19},
                                    15: {"\x1A": 21, "\n": 16, "[^\x0A\n]": 15}, 16: {}, 17: {}, 18: {}, 19: {},
                                    20: {}, 21: {}, 22: {}}

        self.classes = {4: "NUMBER", 6: "keyword_token", 7: "SYMBOL", 10: "SYMBOL", 11: "whiteSpace", 16: "comment", 18: "comment", 21: "comment", 20: "Finish"}

        self.errors ={17: "Invalid number", 22: "Unmatched comment", 19: "Unclosed comment", 23: "Invalid input", 24: "Invalid input"}

        self.key_words = ["break", "continue", "def", "else", "if", "return", "while"]

        self.symbol_table = {1: {'lexeme': 'break'}, 2: {'lexeme': 'continue'}, 3: {'lexeme': 'def'}, 4: {'lexeme': 'else'}, 5: {'lexeme': 'if'},
                             6: {'lexeme': 'return'}, 7: {'lexeme': 'while'}}
        
        self.symbol_code = len(self.symbol_table) + 1

        self.dfa = DFA(self.states, self.transition_function, self.start_state, self.trash_state)

    def run(self, input_path: str = 'input.txt') -> None:
        token = ""
        line_of_file = 1
        is_start_of_line = True
        has_error = False
        file_ended = False
        # program = "def main () :    a = 0**2;	# comment1\n    a = 2 + 2.5;    a = a - 3;    cde = a;    if (b /* commenمطالب طنزt2 */ == 3d) :        a = 3;        cd!e = 7;    else */    : 5/        b = a < cde; *$        cde = @2; if/    return; /* comment 3"
        program = open(input_path, 'r')
        tokens_file = open('tokens.txt', 'w')
        errors_file = open('lexical_errors.txt', 'w')
        symbol_table_file = open('symbol_table.txt', 'w')
        while True:
            char = program.read(1)
            if not char:
                file_ended = True
                char = '\x1A'
            # print(ord(char)) #to get ascii value
            state = self.dfa.next_state(char)
            if state.name == self.eof_state:
                break

            token += char
            if state.is_error:
                has_error = True
                if state.has_star:
                    if not file_ended: program.seek(program.tell() - 1)
                    token = token[0:-1]
                errors_file.write("{}.\t({}, {})\n".format(line_of_file, token, self.errors[state.name]))
                token = ""
                continue
            
            
            if state.is_final:
                if state.has_star:
                    if not file_ended: program.seek(program.tell() - 1)
                    token = token[0:-1]
                if state.name != 11 and state.name != 16:
                    if is_start_of_line:
                        is_start_of_line = False
                        tokens_file.write("{}.\t".format(line_of_file))
                    if state.name == 6:
                        if token in self.key_words:
                            tokens_file.write("({}, {}) ".format('KEYWORD', token))
                        else:
                            tokens_file.write("({}, {}) ".format('ID', token))
                            if not (token in self.symbol_table.values()):
                                self.symbol_table[self.symbol_code] = {'lexeme': token}
                                self.symbol_code += 1
                    else:
                        tokens_file.write("({}, {}) ".format(self.classes[state.name], token))
                if re.search("\x0A", token):
                    line_of_file += 1
                    tokens_file.write("\n")
                    is_start_of_line = True
                token = ""
                state = 0
        errors_file
        if not has_error:
            errors_file.write('There is no lexical error.')
        
        for key in self.symbol_table.keys():
            symbol_table_file.write("{}.\t{}\n".format(key, self.symbol_table[key]['lexeme']))
        errors_file.close()
        tokens_file.close()
        symbol_table_file.close()


sc = Scanner()
sc.run()
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
        else:
            self.current_state = self.states[self.trash_state]
        return self.current_state


class Scanner:
    def __init__(self, st) -> None:
        self.initialize()

        self.start_state = 0

        self.eof_state = 20

        self.trash_state = 23

        self.states = {0: Node(0, False, False, False), 1: Node(1, False, False, False),
                       2: Node(2, False, False, False), 3: Node(3, False, False, False),
                       4: Node(4, True, True, False), 5: Node(5, False, False, False), 6: Node(6, True, True, False),
                       7: Node(7, True, False, False),
                       8: Node(8, False, False, False), 9: Node(9, False, False, False),
                       10: Node(10, True, True, False), 11: Node(11, True, False, False),
                       12: Node(12, False, False, False), 13: Node(13, False, False, False),
                       14: Node(14, False, False, False), 15: Node(15, False, False, False),
                       16: Node(16, True, False, False), 17: Node(17, True, False, True),
                       18: Node(18, True, False, False), 19: Node(19, True, True, True),
                       20: Node(20, True, False, False), 21: Node(21, True, True, False),
                       22: Node(22, True, False, True), 23: Node(23, True, False, True),
                       24: Node(24, True, True, True), 25: Node(25, True, True, True)}

        self.valid_char_regex = "[\x09\x0A\x0B\x0C\x0D\x20\[\]\<;,:()+\-=*/\#\x1A0-9a-zA-Z.]"

        self.transition_function = {0: {"[0-9]": 1, "[a-zA-Z]": 5, "[\[\]\<;,:()+\-]": 7, "\*": 8, "=": 9,
                                        "[\x09\x0A\x0B\x0C\x0D\x20]": 11, "/": 12, "\#": 15, "\x1A": 20},
                                    1: {"[0-9]": 1, "[.]": 2, "[\x09\x0A\x0B\x0C\x0D\x20\[\]\<;,:()+\-=*/\#\x1A]": 4,
                                        "[^\x09\x0A\x0B\x0C\x0D\x20\[\]\<;,:()+\-=*/\#\x1A0-9.]": 17},
                                    2: {"[0-9]": 3, "[^0-9\x1A]": 17, "[\x1A]": 25},
                                    3: {"[0-9]": 3, "[\x09\x0A\x0B\x0C\x0D\x20\[\]\<;,:()+\-=*/\#\x1A]": 4,
                                        "[^\x09\x0A\x0B\x0C\x0D\x20\[\]\<;,:()+\-=*/\#\x1A0-9]": 17},
                                    4: {},
                                    5: {"[a-zA-Z0-9]": 5, "[\x09\x0A\x0B\x0C\x0D\x20\[\]\<;,:()+\-=*/\#\x1A]": 6},
                                    6: {},
                                    7: {},
                                    8: {"\*": 7, "[\x09\x0A\x0B\x0C\x0D\x20\[\]\<;,:()+\-=\#\x1A0-9a-zA-Z]": 10,
                                        "/": 22},
                                    9: {"=": 7, "[\x09\x0A\x0B\x0C\x0D\x20\[\]\<;,:()+\-*/\#\x1A0-9a-zA-Z]": 10},
                                    10: {},
                                    11: {},
                                    12: {"\*": 13, "[^\*]": 24},
                                    13: {"\*": 14, "\x1A": 19, "[^\*\x1A]": 13},
                                    14: {"\*": 14, "[^\*/\x1A]": 13, "/": 18, "\x1A": 19},
                                    15: {"\x1A": 21, "\n": 16, "[^\x1A\n]": 15},
                                    16: {},
                                    17: {},
                                    18: {},
                                    19: {},
                                    20: {},
                                    21: {},
                                    22: {}
                                    }

        self.classes = {4: "NUMBER", 6: "keyword_token", 7: "SYMBOL", 10: "SYMBOL", 11: "whiteSpace", 16: "comment",
                        18: "comment", 21: "comment", 20: "Finish"}

        self.errors = {17: "Invalid number", 25: "Invalid number", 22: "Unmatched comment", 19: "Unclosed comment",
                       23: "Invalid input", 24: "Invalid input"}

        self.key_words = ["break", "continue", "def", "else", "if", "return", "while", "global"]

        self.symbol_table = st

        # self.symbol_table = {1: {'lexeme': 'break'}, 2: {'lexeme': 'continue'}, 3: {'lexeme': 'def'},
        #                      4: {'lexeme': 'else'}, 5: {'lexeme': 'if'},
        #                      6: {'lexeme': 'return'}, 7: {'lexeme': 'while'}}

        self.symbol_table[1] = {'scope': 0, 'address': '', 'lexeme': 'break'}
        self.symbol_table[2] = {'scope': 0, 'address': '', 'lexeme': 'continue'}
        self.symbol_table[3] = {'scope': 0, 'address': '', 'lexeme': 'def'}
        self.symbol_table[4] = {'scope': 0, 'address': '', 'lexeme': 'else'}
        self.symbol_table[5] = {'scope': 0, 'address': '', 'lexeme': 'if'}
        self.symbol_table[6] = {'scope': 0, 'address': '', 'lexeme': 'return'}
        self.symbol_table[7] = {'scope': 0, 'address': '', 'lexeme': 'while'}
        self.symbol_table[8] = {'scope': 0, 'address': '500', 'lexeme': 'output', 'num': 1, 'type': 'func', 'returns': False}


        self.symbol_code = len(self.symbol_table) + 1

        self.dfa = DFA(self.states, self.transition_function, self.start_state, self.trash_state)

    def get_next_token(self):
        while True:
            if not self.is_cache:
                char = self.program.read(1)
            else:
                char = self.cached
                self.is_cache = False
            if not char:
                self.file_ended = True
                char = '\x1A'
            self.state = self.dfa.next_state(char)
            if self.state.name == self.eof_state:
                self.close()
                return "$", "$", self.line_of_file

            self.token += char
            if self.state.is_error:
                self.has_error = True
                self.line_of_errors_has_text = True
                if self.is_start_of_line_of_errors:
                    self.is_start_of_line_of_errors = False
                    # self.errors_file.write("{}.\t".format(self.line_of_file))
                if self.state.has_star:
                    self.cached = self.token[-1]
                    self.is_cache = True
                    self.token = self.token[0:-1]
                if self.state.name == 19 and len(self.token) > 10: self.token = self.token[:10] + '...'
                # self.errors_file.write("({}, {}) ".format(self.token, self.errors[self.state.name]))
                self.token = ""
                continue
            token_type, token_lexeme = "", ""
            if self.state.is_final:
                # print(self.token)
                # if "recursive sample" in self.token or "Recursive Sample" in self.token or "# === sample 9 ====" in self.token:
                #     0/0
                if self.state.has_star:
                    self.cached = self.token[-1]
                    self.is_cache = True
                    self.token = self.token[0:-1]
                if self.state.name != 11 and self.state.name != 16 and self.state.name != 18:
                    self.line_of_tokens_has_text = True
                    if self.is_start_of_line_of_tokens:
                        self.is_start_of_line_of_tokens = False
                        # self.tokens_file.write("{}.\t".format(self.line_of_file))
                    if self.state.name == 6:
                        if self.token in self.key_words:
                            token_type, token_lexeme = 'KEYWORD', self.token
                            # self.tokens_file.write("({}, {}) ".format(token_type, token_lexeme))
                        else:
                            token_type, token_lexeme = 'ID', self.token
                            # self.tokens_file.write("({}, {}) ".format(token_type, token_lexeme))
                            # for symbol in self.symbol_table.values():
                            #     if self.token == symbol['lexeme']:
                            #         if 'scope' in symbol:
                            #             if symbol['scope'] != -1:
                            #                 break
                            # else:  # if the token was not in file before, adds it.
                            #     self.symbol_table[self.symbol_code] = {'lexeme': self.token}
                            #     self.symbol_code += 1
                    else:
                        token_type, token_lexeme = self.classes[self.state.name], self.token
                        # self.tokens_file.write("({}, {}) ".format(token_type, token_lexeme))
                if re.search("\x0A", self.token):
                    self.line_of_file += 1
                    # if self.line_of_tokens_has_text: self.tokens_file.write("\n")
                    # if self.line_of_errors_has_text: self.errors_file.write("\n")
                    self.is_start_of_line_of_tokens = True
                    self.is_start_of_line_of_errors = True
                    self.line_of_tokens_has_text = False
                    self.line_of_errors_has_text = False
                self.token = ""
                self.state = 0
                if token_type.strip() != "": return (token_type, token_lexeme, self.line_of_file)

    def initialize(self, input_path: str = 'input.txt'):
        self.token = ""
        self.line_of_file = 1
        self.cached = ''
        self.is_cache = False
        self.is_start_of_line_of_tokens = True
        self.is_start_of_line_of_errors = True
        self.line_of_tokens_has_text = False
        self.line_of_errors_has_text = False
        self.has_error = False
        self.file_ended = False
        self.program = open(input_path, 'r')
        # self.tokens_file = open('tokens.txt', 'w')
        # self.errors_file = open('lexical_errors.txt', 'w')
        # self.symbol_table_file = open('symbol_table.txt', 'w')
        pass

    def close(self):
        # if not self.has_error:
        # self.errors_file.write('There is no lexical error.')

        # for key in self.symbol_table.keys():
        # self.symbol_table_file.write("{}.\t{}\n".format(key, self.symbol_table[key]['lexeme']))
        # self.errors_file.close()
        # self.tokens_file.close()
        # self.symbol_table_file.close()
        pass

# todo: graceful termination/ no uncaught exception

import re
class Node:
    def __init__(self, name: int, is_final: bool, has_star: bool) -> None:
        self.name = name
        self.is_final = is_final
        self.has_star = has_star


class DFA:
    def __init__(self, states: dict, transition_function: dict, start_state: Node) -> None:
        self.states = states
        self.transition_function = transition_function
        self.start_state = start_state
        self.current_state = self.states[self.start_state]

    def next_state(self, char: str) -> Node:
        if self.current_state.is_final:
            self.current_state = self.states[self.start_state]
        for regex in self.transition_function[self.current_state.name].keys():
            if re.search(regex, char) != None:
                self.current_state = self.states[self.transition_function[self.current_state.name][regex]]
                break
        return self.current_state


class Scanner:
    def __init__(self) -> None:
        self.start_state = 0

        self.states = {0: Node(0, False, False), 1: Node(1, False, False), 2: Node(2, False, False), 3: Node(3, False, False), 4: Node(4, True, True),
                 5: Node(5, False, False), 6: Node(6, True, True), 7: Node(7, True, False), 8: Node(8, False, False), 9: Node(9, False, False),
                 10: Node(10, True, True), 11: Node(11, True, False), 12: Node(12, False, False), 13: Node(13, False, False), 14: Node(14, False, False),
                 15: Node(15, False, False), 16: Node(16, True, False)}

        self.transition_function = {0: {"[0-9]": 1, "[a-zA-Z]": 5, "[\[\]\<;:()+\-]": 7, "\*": 8, "=": 9, "[\x09\x0A\x0B\x0C\x0D\x20]": 11, "/": 12, "\#": 15},
                               1: {"[0-9]": 1, "[.]": 2, "[^0-9.a-zA-Z]": 4, }, 2: {"[0-9]": 3}, 3: {"[0-9]": 3, "[^0-9.]": 4}, 4: {},
                               5: {"[a-zA-Z0-9]": 5, "[^a-zA-Z0-9]": 6}, 6: {}, 7:{}, 8: {"\*": 7, "[^\*/]": 10}, 9: {"=": 7, "[^=]": 10}, 10: {}, 11: {},
                               12: {"\*": 13}, 13: {"\*": 14, "[^\*]": 13}, 14: {"\*": 14, "[^\*/]": 13, "/": 16}, 15: {"\x0A": 16, "[^\x0A]": 15}, 16: {}}

        self.classes = {4: "number", 6: "keyword_token", 7: "symbol", 10: "symbol", 11: "whiteSpace", 16: "comment"}

        self.dfa = DFA(self.states, self.transition_function, self.start_state)

    def run(self, input_path: str = 'input.txt') -> None:
        index = 0
        token = ""
        # program = "def main () :    a = 0**2;	# comment1\n    a = 2 + 2.5;    a = a - 3;    cde = a;    if (b /* commenمطالب طنزt2 */ == 3d) :        a = 3;        cd!e = 7;    else */    : 5/        b = a < cde; *$        cde = @2; if/    return; /* comment 3"
        program = open(input_path, 'r')
        while True:
            char = program.read(1)
            if not char:
                break
            # print(ord(char)) #to get ascii value
            state = self.dfa.next_state(char)
            token += char
            if (state.is_final):
                if state.has_star:
                    program.seek(program.tell() - 1)
                    index -= 1
                    token = token[0:-1]
                if state != 11:
                    print("%s, %s" % (token, self.classes[state.name]))
                    pass
                token = ""
                state = 0
            index += 1


sc = Scanner()
sc.run()
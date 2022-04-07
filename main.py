import re


def get_next_state(next_state_dict, character):
    for expression in next_state_dict:
        x = re.search(expression, character)
        if (x != None):
            return next_state_dict[expression]
    return 0


class main:
    star = "\*"
    final_states = {4: "number", 6: "keyword_token", 7: "symbol", 10: "symbol", 11: "whiteSpace", 16: "comment"}
    starred_states = {4, 6, 10}
    token = ""
    currentState = 0
    states = {}
    states[0] = {"[0-9]": 1, "[a-zA-Z]": 5, "[\[\]\<;:()+\-]": 7, star: 8, "=": 9, "[\x09\x0A\x0B\x0C\x0D\x20]": 11,
                 "/": 12, "\#": 15}
    states[1] = {"[0-9]": 1, "[.]": 2, "[^0-9.a-zA-Z]": 4, }
    states[2] = {"[0-9]": 3}
    states[3] = {"[0-9]": 3, "[^0-9.]": 4}
    states[4] = {}
    states[5] = {"[a-zA-Z0-9]": 5, "[^a-zA-Z0-9]": 6}
    states[6] = {}
    states[7] = {}
    states[8] = {star: 7, "[^\*/]": 10}
    states[9] = {"=": 7, "[^=]": 10}
    states[10] = {}
    states[11] = {}
    states[12] = {star: 13}
    states[13] = {star: 14, "[^\*]": 13}
    states[14] = {star: 14, "[^\*/]": 13, "/": 16}
    states[15] = {"\x0A": 16, "[^\x0A]": 15}  # EOF?
    states[16] = {}
    states[17] = {}  # when a number is ill formed

    index = 0
    program = "def main () :    a = 0**2;	# comment1\n    a = 2 + 2.5;    a = a - 3;    cde = a;    if (b /* commenمطالب طنزt2 */ == 3d) :        a = 3;        cd!e = 7;    else */    : 5/        b = a < cde; *$        cde = @2; if/    return; /* comment 3"
    while index != len(program):
        char = program[index]
        # print(ord(char)) #to get ascii value
        currentState = get_next_state(states[currentState], char)
        token = token + char
        if (currentState in final_states):
            if currentState in starred_states:
                index -= 1
                token = token[0:-1]
            if currentState != 11:
                print("%s, %s" % (token, final_states[currentState]))
                pass
            token = ""
            currentState = 0
        index += 1

    print("\033[1;32mFINISH")

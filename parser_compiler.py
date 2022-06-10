from code_generator import code_generator
from scanner import Scanner
from anytree import Node, RenderTree


parsing_table = {
    "Program": {";": "",
                 "break": "Statements",
                 "continue": "Statements",
                 "ID": "Statements",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "",
                 ",": "",
                 "return": "Statements",
                 "global": "Statements",
                 "def": "Statements",
                 ":": "",
                 "if": "Statements",
                 "else": "",
                 "while": "Statements",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "Statements",
                 },
    "Statements": {";": "epsilon",
                 "break": "Statement ; Statements",
                 "continue": "Statement ; Statements",
                 "ID": "Statement ; Statements",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "",
                 ",": "",
                 "return": "Statement ; Statements",
                 "global": "Statement ; Statements",
                 "def": "Statement ; Statements",
                 ":": "",
                 "if": "Statement ; Statements",
                 "else": "epsilon",
                 "while": "Statement ; Statements",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "epsilon",
                 },
    "Statement": {";": "synch",
                 "break": "Simple_stmt",
                 "continue": "Simple_stmt",
                 "ID": "Simple_stmt",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "",
                 ",": "",
                 "return": "Simple_stmt",
                 "global": "Simple_stmt",
                 "def": "Compound_stmt",
                 ":": "",
                 "if": "Compound_stmt",
                 "else": "",
                 "while": "Compound_stmt",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": ""
                 },
    "Simple_stmt": {";": "synch",
                 "break": "break \\break",
                 "continue": "continue \\continue",
                 "ID": "Assignment_Call",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "",
                 ",": "",
                 "return": "Return_stmt",
                 "global": "Global_stmt",
                 "def": "",
                 ":": "",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "Compound_stmt": {";": "synch",
                 "break": "",
                 "continue": "",
                 "ID": "",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "",
                 ",": "",
                 "return": "",
                 "global": "",
                 "def": "Function_def",
                 ":": "",
                 "if": "If_stmt",
                 "else": "",
                 "while": "Iteration_stmt",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "Assignment_Call": {";": "synch",
                 "break": "",
                 "continue": "",
                 "ID": "ID \\pid B",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "",
                 ",": "",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "B": {";": "synch",
                 "break": "",
                 "continue": "",
                 "ID": "",
                 "=": "= C \\assign",
                 "[": "[ Expression ] = C \\assignArr",
                 "]": "",
                 "(": "( Arguments ) \\funcRes",
                 ")": "",
                 ",": "",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "C": {";": "synch",
                 "break": "",
                 "continue": "",
                 "ID": "Expression",
                 "=": "",
                 "[": "[ \\start_list Expression \\append List_Rest ]",
                 "]": "",
                 "(": "",
                 ")": "",
                 ",": "",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "Expression",
                 "$": "",
                 },
    "List_Rest": {";": "",
                 "break": "",
                 "continue": "",
                 "ID": "",
                 "=": "",
                 "[": "",
                 "]": "epsilon \\endList",
                 "(": "",
                 ")": "",
                 ",": ", Expression \\append List_Rest",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "Return_stmt": {";": "synch",
                 "break": "",
                 "continue": "",
                 "ID": "",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "",
                 ",": "",
                 "return": "return Return_Value \\return",
                 "global": "",
                 "def": "",
                 ":": "",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "Return_Value": {";": "epsilon \\return_zero",
                 "break": "",
                 "continue": "",
                 "ID": "Expression",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "",
                 ",": "",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "Expression",
                 "$": "",
                 },
    "Global_stmt": {";": "synch",
                 "break": "",
                 "continue": "",
                 "ID": "",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "",
                 ",": "",
                 "return": "",
                 "global": "global ID \\pidGlobal",
                 "def": "",
                 ":": "",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "Function_def": {";": "synch",
                 "break": "",
                 "continue": "",
                 "ID": "",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "",
                 ",": "",
                 "return": "",
                 "global": "",
                 "def": "def ID \\func_def ( Params ) : \\func_line Statements \\end_func",
                 ":": "",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "Params": {";": "",
                 "break": "",
                 "continue": "",
                 "ID": "ID \\param Params_Prime",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "epsilon",
                 ",": "",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "Params_Prime": {";": "",
                 "break": "",
                 "continue": "",
                 "ID": "",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "epsilon",
                 ",": ", ID \\param Params_Prime",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "If_stmt": {";": "synch",
                 "break": "",
                 "continue": "",
                 "ID": "",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "",
                 ",": "",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "",
                 "if": "if Relational_Expression \\save : Statements Else_block",
                 "else": "",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "Else_block": {";": "\\jpf epsilon",
                 "break": "",
                 "continue": "",
                 "ID": "",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "",
                 ",": "",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "",
                 "if": "",
                 "else": "else : \\jpf_save Statements \\jp",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "Iteration_stmt": {";": "synch",
                 "break": "",
                 "continue": "",
                 "ID": "",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "",
                 ",": "",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "",
                 "if": "",
                 "else": "",
                 "while": "while \\label ( Relational_Expression ) \\save Statements \\while",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "Relational_Expression": {";": "",
                 "break": "",
                 "continue": "",
                 "ID": "Expression Relop Expression \\relationalExpression",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "synch",
                 ",": "",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "synch",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "Expression Relop Expression \\relationalExpression",
                 "$": "",
                 },
    "Relop": {";": "",
                 "break": "",
                 "continue": "",
                 "ID": "synch",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "",
                 ",": "",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "== \\eRelop",
                 "<": "< \\lRelop",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "synch",
                 "$": "",
                 },
    "Expression": {";": "synch",
                 "break": "",
                 "continue": "",
                 "ID": "Term Expression_Prime",
                 "=": "",
                 "[": "",
                 "]": "synch",
                 "(": "",
                 ")": "synch",
                 ",": "synch",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "synch",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "synch",
                 "<": "synch",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "Term Expression_Prime",
                 "$": "",
                 },
    "Expression_Prime": {";": "epsilon",
                 "break": "",
                 "continue": "",
                 "ID": "",
                 "=": "",
                 "[": "",
                 "]": "epsilon",
                 "(": "",
                 ")": "epsilon",
                 ",": "epsilon",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "epsilon",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "epsilon",
                 "<": "epsilon",
                 "+": "+ Term \\add Expression_Prime",
                 "-": "- Term \\sub Expression_Prime",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "Term": {";": "synch",
                 "break": "",
                 "continue": "",
                 "ID": "Factor Term_Prime",
                 "=": "",
                 "[": "",
                 "]": "synch",
                 "(": "",
                 ")": "synch",
                 ",": "synch",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "synch",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "synch",
                 "<": "synch",
                 "+": "synch",
                 "-": "synch",
                 "*": "",
                 "**": "",
                 "NUM": "Factor Term_Prime",
                 "$": "",
                 },
    "Term_Prime": {";": "epsilon",
                 "break": "",
                 "continue": "",
                 "ID": "",
                 "=": "",
                 "[": "",
                 "]": "epsilon",
                 "(": "",
                 ")": "epsilon",
                 ",": "epsilon",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "epsilon",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "epsilon",
                 "<": "epsilon",
                 "+": "epsilon",
                 "-": "epsilon",
                 "*": "* Factor \\mult Term_Prime",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "Factor": {";": "synch",
                 "break": "",
                 "continue": "",
                 "ID": "Atom Power",
                 "=": "",
                 "[": "",
                 "]": "synch",
                 "(": "",
                 ")": "synch",
                 ",": "synch",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "synch",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "synch",
                 "<": "synch",
                 "+": "synch",
                 "-": "synch",
                 "*": "synch",
                 "**": "",
                 "NUM": "Atom Power",
                 "$": "",
                 },
    "Power": {";": "Primary",
                 "break": "",
                 "continue": "",
                 "ID": "",
                 "=": "",
                 "[": "Primary",
                 "]": "Primary",
                 "(": "Primary",
                 ")": "Primary",
                 ",": "Primary",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "Primary",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "Primary",
                 "<": "Primary",
                 "+": "Primary",
                 "-": "Primary",
                 "*": "Primary",
                 "**": "** Factor \\pow",
                 "NUM": "",
                 "$": "",
                 },
    "Primary": {";": "epsilon",
                 "break": "",
                 "continue": "",
                 "ID": "",
                 "=": "",
                 "[": "[ Expression \\calculate_primary ] Primary",
                 "]": "epsilon",
                 "(": "( \\func_call Arguments ) Primary",
                 ")": "epsilon",
                 ",": "epsilon",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "epsilon",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "epsilon",
                 "<": "epsilon",
                 "+": "epsilon",
                 "-": "epsilon",
                 "*": "epsilon",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "Arguments": {";": "",
                 "break": "",
                 "continue": "",
                 "ID": "Expression Arguments_Prime",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "epsilon",
                 ",": "",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "Expression Arguments_Prime",
                 "$": "",
                 },
    "Arguments_Prime": {";": "",
                 "break": "",
                 "continue": "",
                 "ID": "",
                 "=": "",
                 "[": "",
                 "]": "",
                 "(": "",
                 ")": "epsilon",
                 ",": ", Expression Arguments_Prime",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "",
                 "<": "",
                 "+": "",
                 "-": "",
                 "*": "",
                 "**": "",
                 "NUM": "",
                 "$": "",
                 },
    "Atom": {";": "synch",
                 "break": "",
                 "continue": "",
                 "ID": "ID \\pid",
                 "=": "",
                 "[": "synch",
                 "]": "synch",
                 "(": "synch",
                 ")": "synch",
                 ",": "synch",
                 "return": "",
                 "global": "",
                 "def": "",
                 ":": "synch",
                 "if": "",
                 "else": "",
                 "while": "",
                 "==": "synch",
                 "<": "synch",
                 "+": "synch",
                 "-": "synch",
                 "*": "synch",
                 "**": "synch",
                 "NUM": "NUM \\pnum",
                 "$": "",
                 }
}

class Parser:

    def __init__(self, st):
        self.st = st

    def start(self):
        root, has_syntax_error = self.parse_program()
        # parse_tree_output = open("parse_tree.txt", "w", encoding="utf-8")
        buffer = ''
        for pre, fill, node in RenderTree(root):
            buffer = buffer + "{:s}{:s}".format(pre, node.name) + "\n"
        # parse_tree_output.write(buffer)
        # parse_tree_output.close()
        if not has_syntax_error:
            self.syntax_error_output.write("There is no syntax error.")
        self.syntax_error_output.close()


    def parse_program(self):
        self.syntax_error_output = open("syntax_errors.txt", "w", encoding="utf-8")
        has_syntax_error = False
        terminals = ["break", "continue", "def", "else", "if", "return", "while", "global", "[", "]", "(", ")",
                     "ID", "=", ";", ",", ":", "==", "<", "+", "-", "*", "**", "NUM", "$"]
        sc = Scanner(self.st)
        cg = code_generator(self.st)
        cg_input = ""
        stack = []
        root = Node("Program")
        stack.append(root)
        while True:
            token_type, token_lexeme, line_number = sc.get_next_token()
            effective_token = ""
            if token_type == "NUMBER":
                token_type = "NUM"
                effective_token = "NUM"
            elif token_type == "ID": effective_token = "ID"
            elif token_type in ("KEYWORD", "SYMBOL"): effective_token = token_lexeme
            elif token_type == "$": effective_token = "$"
            else: continue # comments and whitespaces
            while True:
                if (len(stack) == 0):
                    Node(name="$", parent=root)
                    cg.dump()
                    return root, has_syntax_error
                current_node = stack.pop()
                current_sentential = current_node.name
                if current_sentential[0] == "\\":
                    cg.codegen(cg_input, current_sentential)
                    continue
                if current_sentential in terminals:
                    if effective_token == current_sentential:
                        current_node.name = "({:s}, {:s})".format(token_type, token_lexeme)
                        cg_input = token_lexeme
                        break
                    else:
                        has_syntax_error = True
                        self.syntax_error_output.write("#{} : syntax error, missing {}\n".format(line_number, current_sentential))
                        current_node.parent = None
                        cg_input = token_lexeme
                        continue
                else:
                    next_tokens = parsing_table[current_sentential][effective_token].split(" ")
                    if "" in next_tokens:
                        if effective_token == "$":
                            has_syntax_error = True
                            stack.append(current_node)
                            self.syntax_error_output.write("#{} : syntax error, Unexpected EOF\n".format(line_number))
                            for remaining_node in stack:
                                remaining_node.parent = None
                            cg.dump()
                            return root, has_syntax_error
                        has_syntax_error = True
                        stack.append(current_node)
                        self.syntax_error_output.write("#{} : syntax error, illegal {}\n".format(line_number, effective_token))
                        cg_input = token_lexeme
                        break
                    elif "synch" in next_tokens:
                        has_syntax_error = True
                        self.syntax_error_output.write("#{} : syntax error, missing {}\n".format(line_number, current_sentential))
                        current_node.parent = None
                        cg_input = token_lexeme
                        continue
                    new_nodes_list = []
                    for i in range (len(next_tokens)):
                        name = next_tokens[i]
                        new_node = Node(name= name, parent=current_node)
                        new_nodes_list.append(new_node)
                    for node in reversed(new_nodes_list):
                        if node.name != "epsilon":
                            stack.append(node)
                cg_input = token_lexeme
        cg.dump()
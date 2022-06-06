class code_generator:
    def __init__(self, st):
        self.symbol_table = st
        self.scope_stack = list()
        self.ss = list()
        self.pb = dict()
        self.i = 0
        self.data_pointer = 500
        self.temporary_pointer = 1000
        self.terminals = ["break", "continue", "def", "else", "if", "return", "while", "global", "[", "]", "(", ")",
                     "ID", "=", ";", ",", ":", "==", "<", "+", "-", "*", "**", "NUM", "$"]
    pass


    def find_id(self, id):
        '''
        used in get_symbol_table_row()
        :param id: lexeme
        :return: row(if exists) and False (if does not)
        '''
        for column in self.symbol_table:
            if self.symbol_table[column]['lexeme'] == id:
                return self.symbol_table[column]
        return False

    def gettemp(self):
        value = "{}".format(self.temporary_pointer)
        self.temporary_pointer += 4
        return value


    def get_symbol_table_row(self, input):
        '''
        searches symbol table for input. if no lexeme with that name exists, or one exists without an address, it will
        assign an address to it and return its row with format: ({'lexeme': 'x', 'address': '500'})
        '''
        column = self.find_id(input)
        if column == False:
            column = {'lexeme': input, 'address': self.data_pointer}
            self.symbol_table[len(self.symbol_table)] = column
            self.data_pointer += 4
        elif 'address' not in column:
            column = {'lexeme': input, 'address': self.data_pointer}
            self.symbol_table[len(self.symbol_table)] = column
            self.data_pointer += 4
        return column

    def codegen(self, input, action):
        print("codegen executed with input: {} and action: {}".format(input, action))
        if action == "\\pid":
            if input in self.terminals:
                return
            column = self.get_symbol_table_row(input)
            self.ss.append(column['address'])
        elif action == "\\add":
            t = self.gettemp()
            self.pb[self.i] = ("+", self.ss.pop(), self.ss.pop(), t)
            self.i += 1
            pass
        elif action == "\\mult":
            t = self.gettemp()
            self.pb[self.i] = ("*", self.ss.pop(), self.ss.pop(), t)
            self.i += 1
            pass
        elif action == "\\pnum":
            self.ss.append("#" + input)
        elif action == "\\assign":
            R = self.ss.pop()
            A = self.ss.pop()
            self.pb[self.i] = ("ASSIGN", A, R, )
            self.i += 1
        elif action == "\\assignArr":
            # arr id -> index -> new value
            new_value = self.ss.pop()
            index = self.ss.pop()
            arr_id = self.ss.pop()
            t = self.gettemp()
            t2 = self.gettemp()
            self.pb[self.i] = ("MULT", index, "#4", t)
            self.pb[self.i + 1] = ("ADD", t, arr_id, t2)
            self.pb[self.i + 2] = ("ASSIGN", new_value, t2)
            self.i += 3
            pass
        elif action == "\\funcRes":

            pass
        elif action == "\\append":

            pass
        elif action == "\\lRelop":
            self.ss.append(1)
        elif action == "\\eRelop":
            self.ss.append(0)
        elif action == "\\relational_expression":
            rhs = self.ss.pop()
            relop = self.ss.pop()
            lhs = self.ss.pop()
            if relop == "0": relop = "EQ"
            elif relop == "1": relop = "LT"
            t = self.gettemp()
            self.pb[self.i] = (relop, lhs, rhs, t)
            self.i += 1
            self.ss.append(t)
        elif action == "\\add":
            rhs = self.ss.pop()
            lhs = self.ss.pop()
            t = self.gettemp()
            self.pb[self.i] = ("ADD", lhs, rhs, t)
            self.i += 1
            self.ss.append(t)
        elif action == "\\sub":
            rhs = self.ss.pop()
            lhs = self.ss.pop()
            t = self.gettemp()
            self.pb[self.i] = ("SUB", lhs, rhs, t)
            self.i += 1
            self.ss.append(t)
        elif action == "\\pow":
            exponent = self.ss.pop()
            base = self.ss.pop()
            t = self.gettemp()
            t2 = self.gettemp()
            self.pb[self.i] = ("ASSIGN", "#1", t)
            self.pb[self.i+1] = ("ASSIGN", exponent, t2)
            self.pb[self.i+2] = ("JPF", t2, self.i+6)
            self.pb[self.i+3] = ("MULT", t, base, t)
            self.pb[self.i+4] = ("SUB", t2, "#1", t2)
            self.pb[self.i+5] = ("JP", self.i+2)
            self.i += 6
            self.ss.append(t)
        elif action == "\\relationalExpression":
            op2 = self.ss.pop()
            op = self.ss.pop()
            op1 = self.ss.pop()
            if op == 0:
                op = "EQ"
            elif op == 1:
                op = "LT"
            dest = self.gettemp()
            self.pb[self.i] = (op, op1, op2, dest)
            self.i += 1
            self.ss.append(dest)
        elif action == "\\param":
            self.pb[self.i] = ("ASSIGN", "#0", self.data_pointer)
            column = self.get_symbol_table_row(input)
            self.ss.append(column['address'])
            self.i += 1
            pass
        elif action == "\\return":
            value = self.ss.pop()
            address = self.ss.pop()
            return_value_pointer = self.gettemp()
            return_address = self.gettemp()
            self.pb[self.i] = ("ADD", "#8", address, return_value_pointer)
            self.pb[self.i+1] = ("ASSIGN", value, "@" + return_value_pointer)
            self.pb[self.i+2] = ("ADD", "#4", address, return_address)
            self.pb[self.i+3] = ("JP", "@"+return_address)
            self.i += 4
            pass
        elif action == "\\return_zero":
            return_value_pointer = self.gettemp()
            self.pb[self.i] = ("ASSIGN", "#0", return_value_pointer)
            self.i += 1
        elif action == "\\func_def":
            self.pb[self.i] = ("ASSIGN", "#0", self.data_pointer)
            column = {'lexeme': input, 'address': self.data_pointer}
            self.symbol_table[len(self.symbol_table)] = column
            self.ss.append(column['address'])
            self.data_pointer += 4
            if input != "main":
                self.pb[self.i+1] = ("JP",)
                self.ss.append(self.i+1)
                self.i += 1
            else:
                # fill all the previous JPs
                pass
            self.i += 1
        else:
            print('\033[91m' + "unknown semantic action: :{}".format(action) +  '\033[0m')


    def dump(self):
        '''
        outputs program into output.txt
        needs slight modification for final submition but works for now.

        :return: None
        '''
        output = open('output.txt', 'w')
        for key in self.pb:
            output.write("{}\t{}\n".format(key, self.pb[key]))
        output.close()


'''
    symbol table:
    lexeme| address| 
'''
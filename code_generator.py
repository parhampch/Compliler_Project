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
        self.incomplete_funcs = list()
        self.return_scope = list()
    pass


    def find_id(self, id):
        '''
        used in get_symbol_table_row()
        :param id: lexeme
        :return: row(if exists) and False (if does not)
        '''
        for row in self.symbol_table:
            if self.symbol_table[row]['lexeme'] == id:
                return self.symbol_table[row]
        return False

    def gettemp(self):
        value = "{}".format(self.temporary_pointer)
        self.temporary_pointer += 4
        return value

    def add_instruction(self, instruction, option):
        self.pb[self.i] = instruction
        self.i+= 1


    def get_symbol_table_row(self, input):
        '''
        searches symbol table for input. if no lexeme with that name exists, or one exists without an address, it will
        assign an address to it and return its row with format: ({'lexeme': 'x', 'address': '500'})
        '''
        row = self.find_id(input)
        if row == False:
            row = {'lexeme': input, 'address': self.data_pointer}
            self.symbol_table[len(self.symbol_table)] = row
            self.data_pointer += 4
        elif 'address' not in row:
            row = {'lexeme': input, 'address': self.data_pointer}
            self.symbol_table[len(self.symbol_table)] = row
            self.data_pointer += 4
        return row

    def codegen(self, input, action):
        print("codegen executed with input: {} and action: {}".format(input, action))
        if action == "\\pid":
            if input in self.terminals:
                return
            row = self.get_symbol_table_row(input)
            self.ss.append(row['address'])
        elif action == "\\add":
            t = self.gettemp()
            self.pb[self.i] = ("ADD", self.ss.pop(), self.ss.pop(), t)
            self.i += 1
            pass
        elif action == "\\mult":
            t = self.gettemp()
            self.pb[self.i] = ("MULT", self.ss.pop(), self.ss.pop(), t)
            self.i += 1
            self.ss.append(t)
            pass
        elif action == "\\pnum":
            self.ss.append("#" + input)
        elif action == "\\assign":
            R = self.ss.pop()
            A = self.ss.pop()
            self.pb[self.i] = ("ASSIGN", R, A)
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
            row = self.get_symbol_table_row(input)
            # self.ss.append(row['address'])
            self.i += 1
            self.data_pointer += 4
            pass
        elif action == "\\return":

            '''return value is at the top of the stack.
            we also have the address of our method at the return_scope
            we need to assign value to return value (address + 4) and jump to where
            return address (address + 8) shows'''

            function_pointer = int(self.return_scope[-1])
            value = self.ss.pop()
            return_value_address = "{}".format(function_pointer + 4)
            return_address_pointer = "@{}".format(function_pointer + 8)
            self.pb[self.i] = ("ASSIGN", value, return_value_address)
            self.pb[self.i+1] = ("JP", return_address_pointer)
            self.i += 2

        elif action == "\\return_zero":

            function_pointer = int(self.return_scope[-1])
            return_address_pointer = "@{}".format(function_pointer + 8)
            self.pb[self.i] = ("JP", return_address_pointer)
            self.i += 1

        elif action == "\\save":
            boolean_result = self.ss[-1]
            self.pb[self.i] = ("JPF", boolean_result, "X")
            self.ss.append(self.i)
            self.i += 1

        elif action == "\\jpf_save":
            address = self.ss.pop()
            address2 = self.ss.pop()
            self.pb[address] = ("JPF", address2, self.i+1)
            self.ss.append(self.i)
            self.i+= 1

        elif action == "\\jp":
            self.pb[self.ss.pop()] = ("JP", self.i)

        elif action == "\\jpf":
            address = self.ss.pop()
            address2 = self.ss.pop()
            self.pb[address] = ("JPF", address2, self.i)

        elif action == "\\func_def":
            self.pb[self.i] = ("ASSIGN", "#0", self.data_pointer)
            row = {'lexeme': input, 'address': self.data_pointer}
            self.symbol_table[len(self.symbol_table)] = row
            self.return_scope.append(row['address'])
            self.data_pointer += 4
            if input != "main":
                self.pb[self.i+1] = ("JP",)
                self.pb[self.i+2] = ("ASSIGN", "#0", self.data_pointer) # return value.
                self.pb[self.i+3] = ("ASSIGN", "#0", self.data_pointer + 4) # return address.
                self.incomplete_funcs.append(self.i+1)
                self.i += 3
                self.data_pointer += 8
            else:
                # fill all the previous JPs
                while(len(self.incomplete_funcs) > 0):
                    JP_address = self.incomplete_funcs.pop()
                    self.pb[JP_address] = ("JP", self.i+1)
                pass
            self.i += 1
        elif action == "\\start_list":
            self.ss.append(self.i + 1)
            self.ss.append(self.data_pointer)
            self.i += 1
        elif action == "\\append":
            self.pb[self.i] = ("ASSIGN", "#" + str(input), self.data_pointer)
            self.data_pointer += 4
        elif action == "\\endList":
            self.pb[self.ss[-1]] = ("ASSIGN", "#" + str(self.ss[-2]), self.data_pointer)
            self.data_pointer += 4
            self.ss.pop()
            self.ss.pop()
        elif action == "\\while_label":
            self.ss.append(self.i)
        elif action == "\\while_save":
            self.ss.append(self.i)
            self.i = self.i + 1
        elif action == "\\end_while":
            self.pb[self.ss[-1]] = ("JPF", self.ss[-2], self.i + 1)
            self.pb[self.i] = ("JP", self.ss[-3])
            i = self.i + 1
            self.ss.pop()
            self.ss.pop()
            self.ss.pop()
        elif action == "\\end_func":
            self.return_scope.pop()
        else:
            print('\033[91m' + "unknown semantic action: :{}".format(action) +  '\033[0m')


    def dump(self):
        '''
        outputs program into output.txt
        needs slight modification for final submition but works for now.

        :return: None
        '''
        output = open('output.txt', 'w')
        for key in range(len(self.pb)):
            output.write("{}\t{}\n".format(key, self.pb[key]))
        output.close()


'''
    symbol table:
    lexeme| address| 
'''
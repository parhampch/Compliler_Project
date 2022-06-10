class code_generator:
    def __init__(self, st):
        self.symbol_table = st
        self.scope_stack = list()
        self.ss = list()
        self.pb = dict()
        self.i = 0
        self.data_pointer = 504
        self.temporary_pointer = 1000
        self.terminals = ["break", "continue", "def", "else", "if", "return", "while", "global", "[", "]", "(", ")",
                     "ID", "=", ";", ",", ":", "==", "<", "+", "-", "*", "**", "NUM", "$"]
        self.incomplete_funcs = list()
        self.return_scope = list()
        self.current_func = None
        self.scope = 0
    pass


    def find_id(self, id):
        '''
        used in get_symbol_table_row()
        :param id: lexeme
        :return: row(if exists) and False (if does not)
        '''
        for row in self.symbol_table:
            if self.symbol_table[row]['lexeme'] == id:
                if 'scope' in self.symbol_table[row]:
                    if self.symbol_table[row]['scope'] == -1:
                        continue
                return self.symbol_table[row]
        return False

    def gettemp(self):
        value = "{}".format(self.temporary_pointer)
        self.temporary_pointer += 4
        return value

    def add_instruction(self, instruction, option):
        self.pb[self.i] = instruction
        self.i+= 1
    
    def get_row_by_address(self, address):
        for row in self.symbol_table:
            if self.symbol_table[row]['address'] == address:
                return row
        return -1


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
            self.ss.append(t)
            pass
        elif action == "\\mult":
            t = self.gettemp()
            self.pb[self.i] = ("MULT", self.ss.pop(), self.ss.pop(), t)
            self.i += 1
            self.ss.append(t)
            pass
        elif action == "\\sub":
            t = self.gettemp()
            rhs = self.ss.pop()
            lhs = self.ss.pop()
            self.pb[self.i] = ("SUB", lhs, rhs, t)
            self.i += 1
            self.ss.append(t)
            pass
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
        elif action == "\\pnum":
            # self.ss.append("#" + input)
            temp = self.gettemp()
            self.pb[self.i] = ("ASSIGN", "#" + input, temp)
            self.ss.append(temp)
            self.i += 1
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
            self.pb[self.i + 2] = ("ASSIGN", new_value, "@{}".format(t2))
            self.i += 3
            pass
        elif action == "\\funcRes":
            print('\033[91m' + "semantic action not implemented: :{}".format(action) + '\033[0m')
            pass
        elif action == "\\lRelop":
            self.ss.append(1)
        elif action == "\\eRelop":
            self.ss.append(0)

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
            row2 = self.get_symbol_table_row(self.current_func)
            row2['num'] += 1
            self.i += 1
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
            row = {'lexeme': input, 'address': self.data_pointer, 'type': 'func', 'num': 0, 'scope': self.scope}
            self.current_func = input
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
            self.scope += 1
            self.i += 1
        elif action == "\\start_list":
            # self.ss.append(self.i)
            # self.i += 1
            pass
        elif action == "\\append":
            num = self.ss.pop()
            self.pb[self.i] = ("ASSIGN",num , self.data_pointer)
            self.data_pointer += 4
            self.i += 1
        elif action == "\\endList":
            define_address = self.ss.pop()
            first_element_address = define_address + 4
            start_address = "#{}".format(first_element_address)
            self.ss.append(define_address)
            self.ss.append(start_address)
            # self.data_pointer += 4
        elif action == "\\while_label":
            self.ss.append(self.i)
        elif action == "\\calculate_primary":

            '''
            this will calculate an array's element location 
            var1 = arr[arr[1] - 1];
            will result in 
            ('MULT', '#4', '#1', '1000')
            ('ADD', '1000', 500, '1000')
            ('SUB', '@1000', '#1', '1004')
            ('MULT', '#4', '1004', '1008')
            ('ADD', '1008', 500, '1008')
            ('ASSIGN', '@1008', 516)
            '''

            t = self.gettemp()
            index = self.ss.pop()
            arr = self.ss.pop()
            self.pb[self.i] = ("MULT", "#4", index, t)
            self.pb[self.i+1] = ("ADD", t, arr, t)
            self.ss.append("@{}".format(t))
            self.i += 2
            pass
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

        elif action == "\\while":
            a = self.ss.pop()
            b = self.ss.pop()
            c = self.ss.pop()
            self.pb[a] = ("JPF", b, self.i+1)
            self.pb[self.i] = ("JP", c)
            self.i += 1
            pass
        elif action == "\\label":
            self.ss.append(self.i)
            pass
        elif action == "\\func_line":
            func_row = self.get_symbol_table_row(self.current_func)
            func_row['start_line'] = self.i
            self.current_func = None
        elif action == "\\argument":
            argument = self.ss[-1]
            func_name = self.ss[-2]
            self.ss.pop()
            self.ss.pop()
            self.ss.append(argument)
            self.ss.append(func_name)
        elif action == "\\func_call":
            func_address = self.ss.pop()
            func_row = self.get_row_by_address(func_address)
            if self.symbol_table[func_row]['lexeme'] == 'output':
                self.pb[self.i] = ("PRINT", self.ss.pop())
                self.i += 1
                return
            arg_address = func_address + 8 + self.symbol_table[func_row]['num'] * 4
            for _ in range(self.symbol_table[func_row]['num']):
                self.pb[self.i] = ("ASSIGN",self.ss.pop() , arg_address)
                arg_address -= 4
                self.i += 1
            self.pb[self.i] = ("ASSIGN","#{}".format(self.i + 2) , func_address + 8)
            self.i += 1
            self.pb[self.i] = ("JP", self.symbol_table[func_row]['start_line'])
            self.i += 1
            self.ss.append(func_address + 4)


            
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
            output.write("{}\t(".format(key))
            counter = 0
            for element in self.pb[key]:
                output.write("{}".format(element))
                counter += 1
                if counter != 4:
                    output.write(", ")
            while counter < 3 :
                output.write(", ")
                counter += 1
            output.write(")\n")
        output.close()


'''
    symbol table:
    lexeme| address| 
'''
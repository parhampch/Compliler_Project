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
        self.while_scope_continue = list()
        self.while_scope_break = list()
        self.semantic_errors = list()
        self.inside_while_loop = False
        self.expecting_return = False
        self.func_def_stack = list()
        self.no_more_global_variable = False

    pass

    def find_id(self, id):
        '''
        used in get_symbol_table_row()
        :param id: lexeme
        :return: row(if exists) and False (if does not)
        '''
        ans = False
        max_scope = -1
        for row in self.symbol_table:
            if self.symbol_table[row]['lexeme'] == id:
                if 'scope' in self.symbol_table[row]:
                    if self.symbol_table[row]['scope'] > max_scope:
                        ans = self.symbol_table[row]
                        max_scope = ans['scope']
                else:
                    self.symbol_table[row]['scope'] = self.scope
                    ans = self.symbol_table[row]
                    max_scope = ans['scope']
        return ans

    def gettemp(self):
        value = "{}".format(self.temporary_pointer)
        self.temporary_pointer += 4
        return value

    def get_row_by_address(self, address):
        for row in self.symbol_table:
            if self.symbol_table[row]['address'] == address:
                # todo: does it always have a scope?
                if self.symbol_table[row]['scope'] != -1:
                    return row
        return -1

    def get_symbol_table_row(self, input):
        '''
        searches symbol table for input. if no lexeme with that name exists, or one exists without an address, it will
        assign an address to it and return its row with format: ({'lexeme': 'x', 'address': '500'})
        '''
        row = self.find_id(input)
        if row == False:
            row = {'lexeme': input, 'address': self.data_pointer, 'scope': self.scope}
            self.symbol_table[len(self.symbol_table) + 1] = row
            self.data_pointer += 4
        elif 'address' not in row:
            row = {'lexeme': input, 'address': self.data_pointer, 'scope': self.scope}
            self.symbol_table[len(self.symbol_table)] = row
            self.data_pointer += 4
        return row

    def codegen(self, input, action, line_number):
        print("codegen executed with input: {} and action: {}".format(input, action))
        if action == "\\pid":
            if input in self.terminals:
                return
            row = self.get_symbol_table_row(input)
            self.ss.append(row['address'])
        elif action == "\\add":
            t = self.gettemp()
            arg1, arg2 = self.ss.pop(), self.ss.pop()
            if arg1 == "NULL" or arg2 == "NULL":
                self.semantic_errors.append("#{}\t:Semantic Error! Void type in operands".format(line_number))
            self.pb[self.i] = ("ADD", arg1, arg2, t)
            self.i += 1
            self.ss.append(t)
            pass
        elif action == "\\mult":
            t = self.gettemp()
            arg1, arg2 = self.ss.pop(), self.ss.pop()
            if arg1 == "NULL" or arg2 == "NULL":
                self.semantic_errors.append("#{}\t:Semantic Error! Void type in operands".format(line_number))
            self.pb[self.i] = ("MULT", arg1, arg2, t)
            self.i += 1
            self.ss.append(t)
            pass
        elif action == "\\sub":
            t = self.gettemp()
            rhs = self.ss.pop()
            lhs = self.ss.pop()
            if rhs == "NULL" or lhs == "NULL":
                self.semantic_errors.append("#{}\t:Semantic Error! Void type in operands".format(line_number))
            self.pb[self.i] = ("SUB", lhs, rhs, t)
            self.i += 1
            self.ss.append(t)
            pass
        elif action == "\\pow":
            exponent = self.ss.pop()
            base = self.ss.pop()
            if exponent == "NULL" or base == "NULL":
                self.semantic_errors.append("#{}\t:Semantic Error! Void type in operands".format(line_number))
            t = self.gettemp()
            t2 = self.gettemp()
            self.pb[self.i] = ("ASSIGN", "#1", t)
            self.pb[self.i + 1] = ("ASSIGN", exponent, t2)
            self.pb[self.i + 2] = ("JPF", t2, self.i + 6)
            self.pb[self.i + 3] = ("MULT", t, base, t)
            self.pb[self.i + 4] = ("SUB", t2, "#1", t2)
            self.pb[self.i + 5] = ("JP", self.i + 2)
            self.i += 6
            self.ss.append(t)
        elif action == "\\pnum":
            self.ss.append("#" + input)
            # temp = self.gettemp()
            # self.pb[self.i] = ("ASSIGN", "#" + input, temp)
            # self.ss.append(temp)
            # self.i += 1
        elif action == "\\assign": # R -> A
            R = self.ss.pop()
            A = self.ss.pop()
            row = self.get_row_by_address(A)
            row = self.symbol_table[row]
            if self.scope != row['scope']:
                self.symbol_table[len(self.symbol_table)] =\
                    {'lexeme': row['lexeme'], "scope": self.scope, 'address': self.data_pointer}
                # self.data_pointer += 4
                A = self.get_symbol_table_row(row['lexeme'])['address']
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
        # elif action == "\\funcRes":
        #     print('\033[91m' + "semantic action not implemented: :{}".format(action) + '\033[0m')
        #     pass
        elif action == "\\lRelop":
            temp = self.gettemp()
            value = self.ss.pop()
            self.pb[self.i] = ("ASSIGN", value, temp)
            self.i += 1
            self.ss.append(temp)
            self.ss.append(1)
        elif action == "\\eRelop":
            temp = self.gettemp()
            value = self.ss.pop()
            self.pb[self.i] = ("ASSIGN", value, temp)
            self.i += 1
            self.ss.append(temp)
            self.ss.append(0)

        elif action == "\\relationalExpression":
            op2 = self.ss.pop()
            op = self.ss.pop()
            op1 = self.ss.pop()
            if op1 == "NULL" or op2 == "NULL":
                self.semantic_errors.append("#{}\t:Semantic Error! Void type in operands".format(line_number))
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
            self.func_def_stack[-1]["arguments"] += 1
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
            self.pb[self.i + 1] = ("JP", return_address_pointer)
            self.i += 2
            self.func_def_stack[-1]["returns"] = True

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
            self.pb[address] = ("JPF", address2, self.i + 1)
            self.ss.append(self.i)
            self.i += 1

        elif action == "\\jp":
            self.pb[self.ss.pop()] = ("JP", self.i)

        elif action == "\\jpf":
            address = self.ss.pop()
            address2 = self.ss.pop()
            self.pb[address] = ("JPF", address2, self.i)

        elif action == "\\func_def":
            self.no_more_global_variable = True
            self.pb[self.i] = ("ASSIGN", "#0", self.data_pointer)
            row = {'lexeme': input, 'address': self.data_pointer, 'type': 'func', 'num': 0, 'scope': self.scope}
            self.current_func = input
            self.symbol_table[len(self.symbol_table)] = row
            self.return_scope.append(row['address'])
            self.data_pointer += 4
            self.func_def_stack.append({"id": len(self.symbol_table), "name": input, "returns": False, "arguments": 0})
            if input != "main":
                self.pb[self.i + 1] = ("JP",)
                self.pb[self.i + 2] = ("ASSIGN", "#0", self.data_pointer)  # return value.
                self.pb[self.i + 3] = ("ASSIGN", "#0", self.data_pointer + 4)  # return address.
                self.incomplete_funcs.append(self.i + 1)
                self.i += 3
                self.data_pointer += 8
            else:
                # fill all the previous JPs
                while (len(self.incomplete_funcs) > 0):
                    JP_address = self.incomplete_funcs.pop()
                    self.pb[JP_address] = ("JP", self.i + 1)
                pass
            self.scope += 1
            self.i += 1
        elif action == "\\start_list":
            # self.ss.append(self.i)
            # self.i += 1
            pass
        elif action == "\\append":
            num = self.ss.pop()
            self.pb[self.i] = ("ASSIGN", num, self.data_pointer)
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
            self.pb[self.i + 1] = ("ADD", t, arr, t)
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
            function_pointer = int(self.return_scope.pop())
            for row in self.symbol_table:
                if 'scope' in self.symbol_table[row]:
                    if self.symbol_table[row]['scope'] == self.scope:
                        self.symbol_table[row]['scope'] = -1
            self.scope -= 1
            func_info = self.func_def_stack.pop()
            self.symbol_table[func_info["id"]]["returns"] = func_info["returns"]
            self.symbol_table[func_info["id"]]["arguments"] = func_info["arguments"]
            if func_info['name'] != 'main':
                return_address_pointer = "@{}".format(function_pointer + 8)
                self.pb[self.i] = ("JP", return_address_pointer)
                self.i += 1


        elif action == "\\while":
            a = self.ss.pop()
            b = self.ss.pop()
            c = self.ss.pop()
            self.pb[a] = ("JPF", b, self.i + 1)
            self.pb[self.i] = ("JP", c)
            self.inside_while_loop = False

            break_list = self.while_scope_break.pop()
            for break_address in break_list:
                self.pb[break_address] = ("JP", self.i + 1)

            continue_list = self.while_scope_continue.pop()
            for continue_address in continue_list:
                self.pb[continue_address] = ("JP", c)

            self.i += 1
            pass
        elif action == "\\label":
            self.ss.append(self.i)
            self.while_scope_continue.append(list())
            self.while_scope_break.append(list())
            self.inside_while_loop = True
            pass
        elif action == "\\func_line":
            func_row = self.get_symbol_table_row(self.current_func)
            func_row['start_line'] = self.i
            self.current_func = None
        elif action == "\\arguments_count":
            self.ss.append(0)
            pass
        elif action == "\\argument":
            argument = self.ss[-1]
            arguments_count = self.ss[-2]
            func_name = self.ss[-3]
            self.ss.pop()
            self.ss.pop()
            self.ss.pop()
            self.ss.append(argument)
            self.ss.append(func_name)
            self.ss.append(arguments_count+1)
        elif action == "\\func_call":
            arguments_count = self.ss.pop()
            func_address = self.ss.pop()
            func_row = self.get_row_by_address(func_address)
            func_row = self.symbol_table[func_row]
            if arguments_count != func_row['num']:
                self.semantic_errors.append("#{}\t:Semantic Error! Mismatch in numbers of arguments of {}"
                                            .format(line_number, func_row['lexeme']))
            if func_row['lexeme'] == 'output':
                self.pb[self.i] = ("PRINT", self.ss.pop())
                self.i += 1
                return
            arg_address = func_address + 8 + func_row['num'] * 4
            for _ in range(func_row['num']):
                self.pb[self.i] = ("ASSIGN", self.ss.pop(), arg_address)
                arg_address -= 4
                self.i += 1
            self.pb[self.i] = ("ASSIGN", "#{}".format(self.i + 2), func_address + 8)
            self.i += 1
            self.pb[self.i] = ("JP", func_row['start_line'])
            self.i += 1
            # self.ss.append("{}".format(func_address + 4))

        elif action == "\\func_call_primary":
            arguments_count = self.ss.pop()
            func_address = self.ss.pop()
            func_row = self.symbol_table[self.get_row_by_address(func_address)]

            if func_row['lexeme'] == 'output':
                self.pb[self.i] = ("PRINT", self.ss.pop())
                self.i += 1
                return
            if arguments_count != func_row['num']:
                self.semantic_errors.append("#{}\t:Semantic Error! Mismatch in numbers of arguments of {}"
                                            .format(line_number, func_row['lexeme']))
            arg_address = func_address + 8 + func_row['num'] * 4
            for _ in range(func_row['num']):
                self.pb[self.i] = ("ASSIGN", self.ss.pop(), arg_address)
                arg_address -= 4
                self.i += 1
            self.pb[self.i] = ("ASSIGN", "#{}".format(self.i + 2), func_address + 8)
            self.i += 1
            self.pb[self.i] = ("JP", func_row['start_line'])
            self.i += 1
            if func_row["returns"]:
                self.ss.append("{}".format(func_address + 4))
            else:
                self.ss.append("NULL")

        elif action == "\\break":
            self.while_scope_break[len(self.while_scope_break) - 1].append(self.i)
            self.i += 1
            if not self.inside_while_loop:
                self.semantic_errors.append((line_number, "No 'while' found for 'break'"))
        elif action == "\\continue":
            self.while_scope_continue[len(self.while_scope_continue) - 1].append(self.i)
            self.i += 1
            pass
            if not self.inside_while_loop:
                self.semantic_errors.append((line_number, "No 'while' found for 'continue'"))
        elif action == "\\sem_main":
            for key in self.symbol_table:
                entry = self.symbol_table[key]
                if entry['lexeme'] == 'main' and entry['scope'] == 0 and entry['type'] == "func":
                    break
            else:
                self.semantic_errors.append("#{}\t:Semantic Error! main function not found".format(line_number))
        elif action == "\\pidGlobal":
            if self.no_more_global_variable:
                self.semantic_errors.append("#{}\t:Semantic Error! {} is not defined appropriately}"
                                            .format(line_number, input))



        # else:
        #     print('\033[91m' + "unknown semantic action: :{}".format(action) + '\033[0m')

    def dump(self):
        '''
        outputs program into output.txt
        needs slight modification for final submition but works for now.

        :return: None
        '''
        output = open('output.txt', 'w')
        semantic_errors_output = open('semantic_errors.txt', 'w')
        if len(self.semantic_errors) > 0:
            output.write("The output code has not been generated")
            output.close()
            for error in self.semantic_errors:
                semantic_errors_output.write(error + '\n')
            return
        else :
            semantic_errors_output.write("The input program is semantically correct")
        semantic_errors_output.close()
        for key in range(len(self.pb)):
            output.write("{}\t(".format(key))
            counter = 0
            for element in self.pb[key]:
                output.write("{}".format(element))
                counter += 1
                if counter != 4:
                    output.write(", ")
            while counter < 3:
                output.write(", ")
                counter += 1
            output.write(")\n")
        output.close()


'''
    symbol table:
    lexeme| address| 
'''
# xfedor14

import xml.etree.ElementTree as ElementTree # zpracovani xml formatu
import argparse # parsovani prikazove radky
import sys #st err vypisy
from os import path # manipulace s cestami v souborovem systemu

# definice classu
class Context:
    __instance = None

    def __init__(self):
        # pouze jedna instance 
        if Context.__instance is not None:
            raise Exception("Context class muze byt pouze jednou")
        else:
            Context.__instance = self
            self.program = {}
            self.label = {}

            # vstup
            self.src = None
            self.input = None
            
            # countery pro instrukce a radky instrukci
            self.cnt_instr = []
            self.cnt_line = 0

            # framy
            self.GF = {}
            self.TF = {}
            self.TF_flag = False

            # stack pro data, framy
            self.st_frame = []
            self.st_data = []
            self.st_jump = []
            
    @staticmethod
    def get_instance():
        if Context.__instance is None:
            Context()
        return Context.__instance

class Argument:
    def __init__(self):
        self.argument = argparse.ArgumentParser()
        self.argument.add_argument("--source", metavar="SOURCE_FILE", nargs=1, type=str)
        self.argument.add_argument("--input", metavar="INPUT_FILE", nargs=1, type=str)

    def parse(self):
        return self.argument.parse_args()

    def parse_arg(self):
        args = self.parse()
        if args.input is None and args.source is None:
            exit(10)
        if args.source:
            # kontrola existence souboru na vstupu
            if path.exists(args.source[0]):
                Context.get_instance().src = open(args.source[0], "r")
            else:
                exit(10)
        else:
            # nacitani ze stdin
            Context.get_instance().src = sys.stdin
        if args.input:
            # kontrola existence souboru na vstupu
            if path.exists(args.input[0]):
                Context.get_instance().input = open(args.input[0], "r")
                Context.get_instance().input = Context.get_instance().input.readlines()
            else:
                exit(10)

class XML:
    def __init__(self):
        self.source_file = Context.get_instance().src
    # nacteni xml a parsing
    def parse(self):
        try:
            el_tree = ElementTree.parse(self.source_file)
        except ElementTree.ParseError:
            exit(31)
        prog = el_tree.getroot()
        if prog.tag != "program":
            exit(32)
        if len(prog.attrib) > 3:
            exit(31)
        for attribute in prog.attrib:
            if attribute not in ["language", "name", "description"]:
                exit(32)
        # kontrola zadaneho jazyka
        if "language" not in prog.attrib:
            exit(31)
        if prog.attrib["language"].upper() != "IPPCODE23":
            exit(32)
        # zpracovani instrukci a jejich argumentu
        for instruction in prog:
            self.get_instr(instruction)
            self.get_arg(instruction)
        
        # serazeni nactenych instrukci
        Context.get_instance().cnt_instr = list(i for i in Context.get_instance().program)
        Context.get_instance().cnt_instr.sort()
        self.get_label()
        Context.get_instance().cnt_instr.append(0)

    # zpracovani instrukci a jeji atributu
    def get_instr(self, instruction):
        if instruction.tag != "instruction":
            exit(32)
        # pocet atributu pouze 2 (order, opcode), jinak chyba
        if len(instruction.attrib) != 2:
            exit(32)
        for attribute in instruction.attrib:
            if attribute not in ["order", "opcode"]:
                exit(32)
        # kontrola formatu order
        if not instruction.attrib["order"].isdigit():
            exit(32)
        # nastaveni opcode formatu
        instruction.attrib["opcode"] = instruction.attrib["opcode"].upper()

    # pridani instrukce do programu
    def get_arg(self, instruction):
        #argumenty instrukce
        args_instr = []
        #pocet argumentu instrukce
        args_cnt = 1

        # kontrola poctu argumentu pro jednotlive instrukci
        if instruction.attrib["opcode"] in ["CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK"]:
            if len(list(instruction)) != 0:
                exit(32)
        elif instruction.attrib["opcode"] in ["DEFVAR", "POPS", "CALL", "LABEL", "JUMP", "PUSHS", "WRITE", "DPRINT", "EXIT"]:
            if len(list(instruction)) != 1:
                exit(32)
        elif instruction.attrib["opcode"] in ["MOVE", "TYPE", "INT2CHAR", "STRLEN", "NOT", "READ"]:
            if len(list(instruction)) != 2:
                exit(32)
        elif instruction.attrib["opcode"] in ["AND", "OR", "ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR", "JUMPIFEQ", "JUMPIFNEQ"]:
            if len(list(instruction)) != 3:
                exit(32)
        else:
            exit(32)
        
        # kontrola tagu a poctu argumentu
        for i in range(len(list(instruction))):
            args_instr.append(None)
        for argument in instruction:
            if (argument.tag not in ["arg1"] and len(list(instruction)) == 1) or (
                    argument.tag not in ["arg1", "arg2"] and len(list(instruction)) == 2) or (
                    argument.tag not in ["arg1", "arg2", "arg3"] and len(list(instruction)) == 3):
                exit(32)
                
            # nastaveni hodnoty pro order
            args_order = int(argument.tag[-1]) - 1

            # atribut instrukce = type
            if (len(argument.attrib) > 1) or ("type" not in argument.attrib):
                exit(32)

            # typ atrubitu nabyva pouze povolenych hodnot
            if argument.attrib["type"] not in ["int", "bool", "string", "var", "label", "type", "nil"]:
                exit(32)
            if argument.text is not None:
                argument.text = argument.text.strip()
            # argument + instrukce
            args_instr[args_order] = {"type": argument.attrib["type"], "value": argument.text}
            args_cnt += 1

        Context.get_instance().program[int(instruction.attrib["order"])] = {instruction.attrib["opcode"]: args_instr}

    # pridani label do programu
    def get_label(self):
        # hledame instrukci LABEL
        for instruction in Context.get_instance().program.items():
            for name in instruction[1]:
                if name == "LABEL":
                    # kontrola redefenice, stejny label
                    if instruction[1][name][0]["value"] in Context.get_instance().label:
                        exit(52)

                    Context.get_instance().label[instruction[1][name][0]["value"]] = instruction[0]

# class, do ktereho jsou pridany vsechny zbyvajici metody
class Interpreter:
    def __init__(self):
        self.index = 0
        self.instr_done = 0 # kolik instrukci zpracovano
        self.instr_order = Context.get_instance().cnt_instr[self.index]
        # nazvy instrukci a prislusne funkci
        self.functions = {
            "CREATEFRAME": self._create_frame, "PUSHFRAME": self._push_frame, "POPFRAME": self._pop_frame,
            "RETURN": self._return, "BREAK": self._break, "DEFVAR": self._defvar, "POPS": self._pops,
            "CALL": self._call, "JUMP": self._jump, "PUSHS": self._pushs, "WRITE": self._write, "DPRINT": self._dprint,
            "EXIT": self._exit, "MOVE": self._move, "TYPE": self._type, "INT2CHAR": self._int2char,
            "STRLEN": self._strlen, "NOT": self._not, "READ": self._read, "AND": self._and, "OR": self._or,
            "ADD": self._add, "SUB": self._sub, "MUL": self._mul, "IDIV": self._idiv, "LT": self._lt, "GT": self._gt,
            "EQ": self._eq, "STRI2INT": self._stri2int, "CONCAT": self._concat, "GETCHAR": self._get_char,
            "SETCHAR": self._set_char, "JUMPIFEQ": self._jumpifeq, "JUMPIFNEQ": self._jumpifneq,
        }

    # metoda pro skoky
    def jump(self, name_label):
        if name_label in Context.get_instance().label:
            return Context.get_instance().label[name_label]
        else:
            exit(52)
    # metoda pro vraceni framu (globalni/lokalni/docasny) v zavislosti na name_frame
    def get_frame(self, frame_name):
        if frame_name == "GF":
            return Context.get_instance().GF
        elif frame_name == "LF":
            if len(Context.get_instance().st_frame):
                return Context.get_instance().st_frame[-1]
            else:
                exit(55)
        elif frame_name == "TF":
            if Context.get_instance().TF_flag:
                return Context.get_instance().TF
            else:
                exit(55)
        else:
            exit(55)

    # zpracovani type = int
    def if_int(self, argument):
        try:
            argument["value"] = int(argument["value"])
        except ValueError:
            exit(32)

    # zpracovani type = bool
    def if_bool(self, argument):
        if argument["value"] == "true":
            argument["value"] = True
        elif argument["value"] == "false":
            argument["value"] = False
        else:
            exit(53)

    # zpracovani type = string
    def if_string(self, argument):

        # escape sekvence
        # https://docs.splunk.com/Documentation/SCS/current/Search/Escapecharacters
        # https://stackoverflow.com/questions/20106330/escape-character-using-indexof
        if argument["value"] is None:
            argument["value"] = ""
        index = argument["value"].find('\\')
        while index != -1:
            escapeSequence = argument["value"][index + 1: index + 4]
            argument["value"] = \
                argument["value"][:index] + chr(int(escapeSequence.lstrip('0'))) + argument["value"][index + 4:]
            index = argument["value"].find('\\')

    # zpracovani type = varible
    def if_varible(self, argument, type_flag):
        # frame, var
        frame, variable_name = argument["value"].split("@", 1)
        frame = self.get_frame(frame)

        # kontrola existence deklarace promenne
        if variable_name not in frame:
            exit(54)
        else:
            # kontrola existence definice promenne
            if frame[variable_name]["var_def_flag"] == False:
                if type_flag:
                    return {"type": "", "value": None}
                exit(56)
            else:
                return frame[variable_name]
            
    # zpracovani typu a hodnoty pro promennou
    def get_var_type_and_value(self, variableArg, newType, newValue):
        # frame, var
        frame, variable_name = variableArg["value"].split("@", 1)
        frame = self.get_frame(frame)

        # kontrola existence deklarace promenne
        if variable_name not in frame:
            exit(54)
        else:
            frame[variable_name] = {"type": newType, "value": newValue, "isDeclared": True, "var_def_flag": True}

    # zpracovani argumentu, jejich hodnot
    def get_arg_type_and_value(self, argument, type_flag=False):
        if argument["type"] == "int":
            self.if_int(argument)
        elif argument["type"] == "bool":
            self.if_bool(argument)
        elif argument["type"] == "string":
            self.if_string(argument)
        elif argument["type"] == "var":
            return self.if_varible(argument, type_flag)
        return argument

    # operace nad framy
    def _create_frame(self):
        Context.get_instance().TF = {}
        Context.get_instance().TF_flag = True

    def _push_frame(self):
        if Context.get_instance().TF_flag:
            Context.get_instance().st_frame.append(Context.get_instance().TF)
            Context.get_instance().TF_flag = False
        else:
            exit(55)

    def _pop_frame(self):
        if len(Context.get_instance().st_frame):
            Context.get_instance().TF = Context.get_instance().st_frame.pop()
            Context.get_instance().TF_flag = True
        else:
            exit(55)

    def _return(self):
        if len(Context.get_instance().st_jump):
            instr_order = Context.get_instance().st_jump.pop()
            self.index = Context.get_instance().cnt_instr.index(instr_order)
        else:
            exit(56)

    # BREAK, vypis stavu interpretu
    def _break(self):
        print("Instrukce BREAK: ", self.instr_order, "\n")
        print("Pocet zpracovanych instrukci: ", self.instr_done, "\n")
        # GF
        print("GF obsah: ", "\n")
        for variable in Context.get_instance().GF:
            print("VAR: ", "\n")
            print("Nazev: ", variable, "\n")
            print("Typ: ", Context.get_instance().GF[variable]["type"], "\n")
            print("Hodnota: ", Context.get_instance().GF[variable]["value"], "\n")
        # TF
        print("TF obsah: ", "\n")  
        if Context.get_instance().TF_flag:
            for variable in Context.get_instance().TF:
                print("VAR: ", "\n")
                print("Nazev: ", variable, "\n")
                print("Typ: ", Context.get_instance().TF[variable]["type"], "\n")
                print("Hodnota: ", Context.get_instance().TF[variable]["value"], "\n")
        # LF
        print("LF obsah: ", "\n")  
        for frame in Context.get_instance().st_frame:
            for variable in frame:
                print("VAR: ", "\n")
                print("Nazev: ", variable, "\n")
                print("Typ: ", frame[variable]["value"], "\n")
                print("Hodnota: ", Context.get_instance().TF[variable]["value"], "\n")
            print("\n")

    # DEFVAR, definice promenne
    def _defvar(self, instruction):
        # frame, var
        frame, variable_name = instruction[0]["value"].split("@", 1)
        frame = self.get_frame(frame)
        if variable_name not in frame:
            frame[variable_name] = {"type": None, "value": None, "isDeclared": True, "var_def_flag": False}
        else:
            exit(52)
    
    # CALL, skok na label
    def _call(self, instruction):
        Context.get_instance().st_jump.append(self.instr_order)
        self.instr_order = self.jump(instruction[0]["value"])
        self.index = Context.get_instance().cnt_instr.index(self.instr_order)
        return
    
    # JUMP, skok na label
    def _jump(self, instruction):
        self.instr_order = self.jump(instruction[0]["value"])
        self.index = Context.get_instance().cnt_instr.index(self.instr_order)
        return

    # PUSH, umisteni info na stack
    def _pushs(self, instruction):
        data = self.get_arg_type_and_value(instruction[0])
        Context.get_instance().st_data.append(data)

    # POPS, typ/hodnota se vyzvedne ze stacku
    def _pops(self, instruction):
        if len(Context.get_instance().st_data):
            data = Context.get_instance().st_data.pop()
            self.get_var_type_and_value(instruction[0], data["type"], data["value"])
        else:
            exit(56)

    # JUMP, skok na label
    def _jump(self, instruction):
        self.instr_order = self.jump(instruction[0]["value"])
        self.index = Context.get_instance().cnt_instr.index(self.instr_order)
        return
    def _jumpifeq(self, instruction):
        first = self.get_arg_type_and_value(instruction[1])
        second = self.get_arg_type_and_value(instruction[2])
        if first["type"] == second["type"]:
            if first["value"] == second["value"]:
                self.instr_order = self.jump(instruction[0]["value"])
                self.index = Context.get_instance().cnt_instr.index(self.instr_order)
                return
        elif first["type"] == "nil":
            if second["value"] is None:
                self.instr_order = self.jump(instruction[0]["value"])
                self.index = Context.get_instance().cnt_instr.index(self.instr_order)
                return
        elif second["type"] == "nil":
            if first["value"] is None:
                self.instr_order = self.jump(instruction[0]["value"])
                self.index = Context.get_instance().cnt_instr.index(self.instr_order)
                return
        else:
            exit(53)
    def _jumpifneq(self, instruction):
        first = self.get_arg_type_and_value(instruction[1])
        second = self.get_arg_type_and_value(instruction[2])
        if first["type"] == second["type"]:
            if first["value"] != second["value"]:
                self.instr_order = self.jump(instruction[0]["value"])
                self.index = Context.get_instance().cnt_instr.index(self.instr_order)
                return
        elif first["type"] == "nil":
            if second["value"] is not None:
                self.instr_order = self.jump(instruction[0]["value"])
                self.index = Context.get_instance().cnt_instr.index(self.instr_order)
                return
        elif second["type"] == "nil":
            if first["value"] is not None:
                self.instr_order = self.jump(instruction[0]["value"])
                self.index = Context.get_instance().cnt_instr.index(self.instr_order)
                return
        else:
            exit(53)
    
    # WRITE, DPRINT print info
    def _write_and_dprint(self, instruction, instr_name):
        data = self.get_arg_type_and_value(instruction[0])
        if data["value"] is not None:
            printString = data["value"]
            if data["type"] == "nil" and data["value"] == "nil":
                printString = ""
            if data["type"] == "bool":
                if data["value"] == True:
                    printString = "true"
                else:
                    printString = "false"
            if instr_name == "WRITE":
                print(printString, end='')
            else:
                sys.stderr.write(printString)
        else:
            exit(56)
    # WRITE, print info
    def _write(self, instruction):
        self._write_and_dprint(instruction, "WRITE")
    # DPRINT, print info
    def _dprint(self, instruction):
        self._write_and_dprint(instruction, "DPRINT")

    # EXIT, exit kod
    def _exit(self, instruction):
        data = self.get_arg_type_and_value(instruction[0])
        if data["type"] == "int":
            if data["value"] in range(0, 50):
                exit(data["value"])
            else:
                exit(57)
        else:
            exit(53)

    # MOVE, TYPE, zpracovani dat o promenne
    def _move(self, instruction):
        data = self.get_arg_type_and_value(instruction[1])
        self.get_var_type_and_value(instruction[0], data["type"], data["value"])
    def _type(self, instruction):
        data = self.get_arg_type_and_value(instruction[1], True)
        self.get_var_type_and_value(instruction[0], "string", data["type"])

    # INT2CHAR, konverze typu
    def _int2char(self, instruction):
        data = self.get_arg_type_and_value(instruction[1])
        if data["type"] == "int":
            try:
                self.get_var_type_and_value(instruction[0], "string", chr(data["value"]))
            except ValueError:
                exit(58)
        else:
            exit(53)
    
    # STR2INT, konverze typu
    def _stri2int(self, instruction):
        first = self.get_arg_type_and_value(instruction[1])
        second = self.get_arg_type_and_value(instruction[2])
        if first["type"] == "string" and second["type"] == "int":
            if second["value"] in range(0, len(first["value"])):
                self.get_var_type_and_value(instruction[0], "int", ord(first["value"][second["value"]]))
            else:
                exit(58)
        else:
            exit(53)
    
    # STRLEN, delka retezce
    def _strlen(self, instruction):
        data = self.get_arg_type_and_value(instruction[1])
        if data["type"] == "string":
            self.get_var_type_and_value(instruction[0], "int", len(data["value"]))
        else:
            exit(53)

    # READ, cteni ze vstupu
    def _read(self, instruction):
        data = self.get_arg_type_and_value(instruction[1])
        data_input = None
        # kontrola formatu inputu
        if Context.get_instance().input is not None:
            if Context.get_instance().cnt_line in range(0, len(Context.get_instance().input)):
                data_input = Context.get_instance().input[Context.get_instance().cnt_line]
            else:
                self.get_var_type_and_value(instruction[0], "nil", "")
            Context.get_instance().cnt_line += 1
        else:
            try:
                data_input = input()
            except:
                exit(10)

        if data_input != None:
            data_input = data_input.rstrip()
            if data["value"].strip() == "int":
                try:
                    data_input = int(data_input)
                    self.get_var_type_and_value(instruction[0], "int", data_input)
                except:
                    self.get_var_type_and_value(instruction[0], "nil", "")
            elif data["value"].strip() == "bool":
                if data_input.lower() == "true":
                    self.get_var_type_and_value(instruction[0], "bool", True)
                else:
                    self.get_var_type_and_value(instruction[0], "bool", False)
            else:
                self.get_var_type_and_value(instruction[0], "string", data_input)

    # logicke operatory
    def _not(self, instruction):
        data = self.get_arg_type_and_value(instruction[1])
        if data["type"] == "bool":
            result = False
            if data["value"] == False:
                result = True
            self.get_var_type_and_value(instruction[0], "bool", result)
        else:
            exit(53)

    def _and_or(self, instruction, instr_name):
        first = self.get_arg_type_and_value(instruction[1])
        second = self.get_arg_type_and_value(instruction[2])
        if first["type"] == "bool" and second["type"] == "bool":
            result = False
            if instr_name == "AND":
                if first["value"] == True and second["value"] == True:
                    result = True
            else:
                if first["value"] == True or second["value"] == True:
                    result = True
            self.get_var_type_and_value(instruction[0], "bool", result)
        else:
            exit(53)
    def _and(self, instruction):
        self._and_or(instruction, "AND")

    def _or(self, instruction):
        self._and_or(instruction, "OR")


    def _add_sub_mul_idiv(self, instruction, instr_name):
        first = self.get_arg_type_and_value(instruction[1])
        second = self.get_arg_type_and_value(instruction[2])
        if first["type"] == "int" and second["type"] == "int":
            if instr_name == "ADD":
                self.get_var_type_and_value(instruction[0], "int", first["value"] + second["value"])
            elif instr_name == "SUB":
                self.get_var_type_and_value(instruction[0], "int", first["value"] - second["value"])
            elif instr_name == "MUL":
                self.get_var_type_and_value(instruction[0], "int", first["value"] * second["value"])
            elif instr_name == "IDIV":
                if second["value"] == 0:
                    exit(57)
                self.get_var_type_and_value(instruction[0], "int", int(first["value"] / second["value"]))
        else:
            exit(53)
    def _add(self, instruction):
        self._add_sub_mul_idiv(instruction, "ADD")
    def _sub(self, instruction):
        self._add_sub_mul_idiv(instruction, "SUB")
    def _mul(self, instruction):
        self._add_sub_mul_idiv(instruction, "MUL")
    def _idiv(self, instruction):
        self._add_sub_mul_idiv(instruction, "IDIV")


    def _lt_gt_eq(self, instruction, instr_name):
        first = self.get_arg_type_and_value(instruction[1])
        second = self.get_arg_type_and_value(instruction[2])
        if first["type"] == second["type"]:
            if instr_name == "LT":
                self.get_var_type_and_value(instruction[0], "bool", first["value"] < second["value"])
            elif instr_name == "GT":
                self.get_var_type_and_value(instruction[0], "bool", first["value"] > second["value"])
            else:
                self.get_var_type_and_value(instruction[0], "bool", first["value"] == second["value"])
        elif first["type"] == "nil" and instr_name == "EQ":
            self.get_var_type_and_value(instruction[0], "bool", None == second["value"])
        elif second["type"] == "nil" and instr_name == "EQ":
            self.get_var_type_and_value(instruction[0], "bool", first["value"] == None)
        else:
            exit(53)
    def _lt(self, instruction):
        self._lt_gt_eq(instruction, "LT")
    def _gt(self, instruction):
        self._lt_gt_eq(instruction, "GT")
    def _eq(self, instruction):
        self._lt_gt_eq(instruction, "EQ")

    # CONCAT, konkatenace retezcu
    def _concat(self, instruction):
        first = self.get_arg_type_and_value(instruction[1])
        second = self.get_arg_type_and_value(instruction[2])
        if first["type"] == "string" and second["type"] == "string":
            if first["value"] == None:
                first["value"] = ""
            if second["value"] == None:
                second["value"] = ""
            self.get_var_type_and_value(instruction[0], "string", first["value"] + second["value"])
        else:
            exit(53)

    # operace c CHAR
    def _get_char(self, instruction):
        first = self.get_arg_type_and_value(instruction[1])
        second = self.get_arg_type_and_value(instruction[2])
        if first["type"] == "string" and second["type"] == "int":
            if second["value"] in range(0, len(first["value"])):
                self.get_var_type_and_value(instruction[0], "string", first["value"][second["value"]])
            else:
                exit(58)
        else:
            exit(53)
    def _set_char(self, instruction):
        variable = self.get_arg_type_and_value(instruction[0])
        first = self.get_arg_type_and_value(instruction[1])
        second = self.get_arg_type_and_value(instruction[2])
        if first["type"] == "int" and second["type"] == "string" and variable["type"] == "string":
            if first["value"] in range(0, len(variable["value"])) and second["value"] != "":
                self.get_var_type_and_value(instruction[0], "string",
                                 variable["value"][:first["value"]] + second["value"][0] +
                                 variable["value"][first["value"] + 1:])
            else:
                exit(58)
        else:
            exit(53)

    # metoda zajistujici pruchod instukcemi for
    def process_instruction_for(self, instr_name):
        instruction = Context.get_instance().program[self.instr_order][instr_name]
        if instr_name == "LABEL":
            pass
        elif instr_name in ["CREATEFRAME", "PUSHFRAME", "POPFRAME", "BREAK"]:
            self.functions[instr_name]()
        elif instr_name in ["DEFVAR", "POPS", "PUSHS", "WRITE", "DPRINT", "MOVE", "TYPE", "INT2CHAR",
                                 "STRLEN", "NOT", "READ", "AND", "OR", "ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ",
                                 "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR", "EXIT"]:
            self.functions[instr_name](instruction)
        elif instr_name == "RETURN":
            self.functions[instr_name]()
            return False
        elif instr_name in ["CALL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ"]:
            self.functions[instr_name](instruction)
            return False
        else:
            exit(32)
        return True

    def interpret(self):
        # pruchod instukcemi
        while self.instr_order != 0:
            for instr_name in Context.get_instance().program[self.instr_order]:
                if not self.process_instruction_for(instr_name):
                    continue
            self.index += 1
            self.instr_order = Context.get_instance().cnt_instr[self.index]
            self.instr_done += 1

if __name__ == '__main__':
    argumentParser = Argument()
    argumentParser.parse_arg()

    xmlParser = XML()
    xmlParser.parse()

    interpret = Interpreter()
    interpret.interpret()
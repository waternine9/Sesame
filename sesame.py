import json, os
file = open("input.json", "r")

tokens = json.load(file)

output_lines = '#include "header.h"\n'
INSERT_VARS = len(output_lines)
variables = {}
_top_levels = {}
links = {}


def recursive_operators(values2, fields2, opcode2):
    if opcode2 == "operator_mathop":
        cur_operator = fields2["OPERATOR"][0]
        cur_expression = f"{cur_operator}f("
        move_on = False
        if isinstance(values2["NUM"][1], str):
            if values2["NUM"][1] in links.keys():
                next_node = links[values2["NUM"][1]]

                next_values = next_node["inputs"]
                next_fields = next_node["fields"]
                next_opcode = next_node["opcode"]
                cur_expression += f"{recursive_operators(next_values, next_fields, next_opcode)})"
                move_on = True
        elif isinstance(values2["NUM"][1][-1], str) and not move_on:
            if values2["NUM"][1][-1] in variables.keys():
                cur_expression += f"{variables[values2['NUM'][1][-1]][1]})"
        elif not move_on:
            cur_expression += f"{values2['NUM'][-1][1]})"
        return cur_expression
    elif opcode2 == "operator_random":
        values2["NUM1"] = values2["FROM"]

        values2["NUM2"] = values2["TO"]
        cur_expression = ""
        move_on = False
        if isinstance(values2["NUM1"][1], str):
            if values2["NUM1"][1] in links.keys():
                next_node = links[values2["NUM1"][1]]

                next_values = next_node["inputs"]
                next_fields = next_node["fields"]
                next_opcode = next_node["opcode"]
                cur_expression = f"({recursive_operators(next_values, next_fields, next_opcode)} + rand() %"
                move_on = True
            if values2["NUM1"][1] in variables.keys():
                cur_expression = f"({variables[values2['NUM1'][1]][1]} + rand() % "
        elif isinstance(values2["NUM1"][1][-1], str) and not move_on:
            if values2["NUM1"][1][-1] in variables.keys():
                cur_expression = f"({variables[values2['NUM1'][1][-1]][1]} + rand() % "
        if len(values2["NUM1"]) == 2:
            cur_expression = f"({values2['NUM1'][-1][1]} + rand() % "
        move_on = False
        if isinstance(values2["NUM2"][1], str):
            if values2["NUM2"][1] in links.keys():
                next_node = links[values2["NUM2"][1]]

                next_values = next_node["inputs"]
                next_fields = next_node["fields"]
                next_opcode = next_node["opcode"]
                cur_expression += f"{recursive_operators(next_values, next_fields, next_opcode)})"
                move_on = True
        elif isinstance(values2["NUM2"][1][-1], str) and not move_on:
            if values2["NUM2"][1][-1] in variables.keys():
                cur_expression += f"{variables[values2['NUM2'][1][-1]][1]})"
        if len(values2["NUM2"]) == 2:
            cur_expression += f"{values2['NUM2'][-1][1]})"
        return cur_expression
    elif opcode2 == "operator_join":
        values2["NUM1"] = values2["STRING1"]

        values2["NUM2"] = values2["STRING2"]
        cur_expression = ""
        move_on = False
        if isinstance(values2["NUM1"][1], str):
            if values2["NUM1"][1] in links.keys():
                next_node = links[values2["NUM1"][1]]

                next_values = next_node["inputs"]
                next_fields = next_node["fields"]
                next_opcode = next_node["opcode"]
                cur_expression = f"({recursive_operators(next_values, next_fields, next_opcode)} + "
                move_on = True
            if values2["NUM1"][1] in variables.keys():
                add_p = ""
                insert = ""
                if isinstance(variables[values2['NUM1'][1]][0], int) or isinstance(variables[values2['NUM1'][1]][0], float):
                    insert += "std::to_string("
                    add_p += ")"
                cur_expression = f"({insert}{variables[values2['NUM1'][1]][1]}{add_p} + "
        else:
            if values2["NUM1"][1][-1] in variables.keys():
                add_p = ""
                insert = ""
                if isinstance(variables[values2['NUM1'][1][-1]][0], int) or isinstance(variables[values2['NUM1'][1][-1]][0], float):
                    insert += "std::to_string("
                    add_p += ")"
                cur_expression = f"({insert}{variables[values2['NUM1'][1][-1]][1]}{add_p} + "
        if len(values2["NUM1"]) == 2:
            temp = values2['NUM1'][-1][1]
            cur_expression = f'("{temp}" + '
        move_on = False
        if isinstance(values2["NUM2"][1], str):
            if values2["NUM2"][1] in links.keys():
                next_node = links[values2["NUM2"][1]]

                next_values = next_node["inputs"]
                next_fields = next_node["fields"]
                next_opcode = next_node["opcode"]
                cur_expression += f"{recursive_operators(next_values, next_fields, next_opcode)})"
                move_on = True
            if values2["NUM2"][1] in variables.keys():
               insert = ""
               add_p = ""
               if isinstance(variables[values2['NUM2'][1]][0], int) or isinstance(variables[values2['NUM2'][1]][0], float):
                   insert += "std::to_string("
                   add_p += ")"
               cur_expression += f"{insert}{variables[values2['NUM2'][1]][1]}{add_p})"
        elif isinstance(values2["NUM2"][1][-1], str) and not move_on:
            if values2["NUM2"][1][-1] in variables.keys():
                add_p = ""
                insert = ""
                if isinstance(variables[values2['NUM2'][1][-1]][-1], int) or isinstance(variables[values2['NUM2'][1][-1]][0], float):
                    cur_expression += "std::to_string("
                    add_p = ")"
                cur_expression += f"{insert}{variables[values2['NUM2'][1][-1]][1]}{add_p})"
        if len(values2["NUM2"]) == 2:
            cur_expression += f"{values2['NUM2'][-1][1]})"
        return cur_expression
    elif opcode2.startswith("operator_"):

        cur_operator = ""
        if opcode2 == "operator_add": cur_operator = "+"
        if opcode2 == "operator_subtract": cur_operator = "-"
        if opcode2 == "operator_divide": cur_operator = "/"
        if opcode2 == "operator_multiply": cur_operator = "*"
        if opcode2 == "operator_equals": cur_operator = "=="
        if "OPERAND1" in values2.keys():
            values2["NUM1"] = values2["OPERAND1"]
            values2["NUM2"] = values2["OPERAND2"]
        cur_expression = ""
        move_on = False
        to_float = False
        to_str = False
        if isinstance(values2["NUM1"][1], str):
            if values2["NUM1"][1] in links.keys():
                next_node = links[values2["NUM1"][1]]

                next_values = next_node["inputs"]
                next_fields = next_node["fields"]
                next_opcode = next_node["opcode"]
                cur_expression = f"({recursive_operators(next_values, next_fields, next_opcode)} {cur_operator} "
                move_on = True
            if values2["NUM1"][1] in variables.keys():
                if isinstance(variables[values2['NUM1'][1]][0], int) or isinstance(variables[values2['NUM1'][1]][0], float):
                    to_float = True
                else:
                    to_str = True
                cur_expression = f"({variables[values2['NUM1'][1]][1]} {cur_operator} "
        else:
            if values2["NUM1"][1][-1] in variables.keys():
                if isinstance(variables[values2['NUM1'][1][-1]][0], int) or isinstance(variables[values2['NUM1'][1][-1]][0], float):
                    to_float = True
                else:
                    to_str = True
                cur_expression = f"({variables[values2['NUM1'][1][-1]][1]} {cur_operator} "
        if len(values2["NUM1"]) == 2:
            cur_expression = f"({values2['NUM1'][-1][1]} {cur_operator} "
        move_on = False
        if isinstance(values2["NUM2"][1], str):
            if values2["NUM2"][1] in links.keys():
                next_node = links[values2["NUM2"][1]]

                next_values = next_node["inputs"]
                next_fields = next_node["fields"]
                next_opcode = next_node["opcode"]
                cur_expression += f"{recursive_operators(next_values, next_fields, next_opcode)})"
                move_on = True
        elif isinstance(values2["NUM2"][1][-1], str) and not move_on:
            if values2["NUM2"][1][-1] in variables.keys():
                if to_float and isinstance(variables[values2['NUM2'][1][-1]][0], str):
                    cur_expression += "std::stof("
                elif to_str and not isinstance(variables[values2['NUM2'][1][-1]][0], str):
                    cur_expression += "std::to_string("
                cur_expression += f"{variables[values2['NUM2'][1][-1]][1]})"
                if to_str and not isinstance(variables[values2['NUM2'][1][-1]][0], str):
                    cur_expression += ")"
                elif to_float and isinstance(variables[values2['NUM2'][1][-1]][0], str):
                    cur_expression += ")"
        if len(values2["NUM2"]) == 2:
            cur_expression += f"{values2['NUM2'][-1][1]})"
        return cur_expression
print("LOG: TOKENIZING...", end="")
for target in tokens["targets"]:
    for _variable in target["variables"].keys():
        variable = target["variables"][_variable]


        variables[_variable] = [variable[1], variable[0].replace(" ", "_")]
    for block in target["blocks"].keys():
        try:
            if target["blocks"][block]["topLevel"]:
                if target["blocks"][block]["next"] != None:
                    _top_levels[block] = target["blocks"][block]
            else:
                links[block] = target["blocks"][block]
            if target["blocks"][block]["opcode"] == "sensing_answer":
                variables[block] = ["0", "answer"]
                links.pop(block)
            if target["blocks"][block]["opcode"] == "sensing_timer":
                variables[block] = [0, "timer"]

                links.pop(block)
        except TypeError:
            print("WARN: TypeError OCCURRED IN TOKENIZE")
            pass
print("DONE\nLOG: LINKING...", end="")
already_got_answer_variable = False
for variable in variables.keys():
    if variables[variable][1] == "answer":
        if already_got_answer_variable: continue
        already_got_answer_variable = True
    elif variables[variable][1] == "timer":
        output_lines += "auto timer = std::chrono::system_clock::now();\n"
        variables[variable][1] = "std::chrono::duration_cast<std::chrono::microseconds>((std::chrono::system_clock::now().time_since_epoch() - timer.time_since_epoch())).count() * 0.001f * 0.001f"
        timer_variable = True
    elif isinstance(variables[variable][0], str):

        output_lines += f'std::string {variables[variable][1]} = "{variables[variable][0]}";\n'
    else:
        output_lines += f"float {variables[variable][1]} = {variables[variable][0]};\n"



main_func = ""
num_fors = 0
def link(top_levels, NO_NEW_FUNC = False, TOP_LEVEL_INCLUDED = False):
    global num_fors
    output_lines, main_func = "", ""
    for _top_level_block in top_levels.keys():
        top_level_block = top_levels[_top_level_block]
        opcode = top_level_block["opcode"]
        returned_function = False
        cur_func = ""
        if not NO_NEW_FUNC:
            if opcode == "procedures_definition":
                proccode = links[top_level_block['inputs']['custom_block'][1]]['mutation']['proccode']
                cur_func = f"void {proccode.split('%')[0]}("
                arg_idx = 0
                for splitted in proccode.split('%')[1:]:


                    arg_idx += 1
                    if arg_idx != len(proccode.split('%')[1:]):
                        if splitted.trim() == "s":
                            cur_func += f"arg{arg_idx}, "

                    else: cur_func += f"arg{arg_idx}"
                cur_func += ")\n{\n"
            elif opcode != "procedures_prototype":
                cur_func = "int main()\n{\n"
                returned_function = True
        # Linked list style linking
        i = -1
        final_i = -2
        cur_node = top_level_block
        while True:
            i += 1
            if i - 1 == final_i:
                break
            if TOP_LEVEL_INCLUDED and i == 0:
                cur_node = top_level_block
            else:
                cur_node = links[cur_node["next"]]
            if cur_node["next"] is None:
                final_i = i
            opcode = cur_node["opcode"]
            values = cur_node["inputs"]
            fields = cur_node["fields"]

            try:
                if opcode == "data_setvariableto":
                    cur_func += f"    {fields['VARIABLE'][0].replace(' ', '_')} = "
                    next_node = values["VALUE"][1]

                    if isinstance(next_node, str):
                        next_node = links[next_node]
                        cur_func += recursive_operators(next_node["inputs"], next_node["fields"], next_node["opcode"]) + ";\n"
                    else:
                        if isinstance(variables[fields['VARIABLE'][1]][0], float) or isinstance(variables[fields['VARIABLE'][1]][0], int): cur_func += f"{next_node[1]};\n"
                        else: cur_func += f'"{next_node[1]}";\n'
                elif opcode == "sensing_askandwait":
                    prompt = values["QUESTION"]
                    if isinstance(prompt[1], str):
                        next_node = links[prompt[1]]
                        cur_func += "    std::cout << " + recursive_operators(next_node["inputs"], next_node["fields"], next_node["opcode"]) + " << std::endl;\n"
                    else: cur_func += f'    std::cout << "{prompt[1][1]}" << std::endl;\n'
                    cur_func += "    std::cin >> answer;\n"
                elif opcode == "control_if":
                    condition_node = links[values["CONDITION"][1]]
                    cur_func += f"    if ({recursive_operators(condition_node['inputs'], condition_node['fields'], condition_node['opcode'])})\n" + "{\n"

                    link_result = link({ values["SUBSTACK"][1]: links[values["SUBSTACK"][1]] }, True, True)
                    cur_func += link_result[0]
                elif opcode == "control_if_else":
                    condition_node = links[values["CONDITION"][1]]
                    cur_func += f"    if ({recursive_operators(condition_node['inputs'], condition_node['fields'], condition_node['opcode'])})\n" + "{\n"

                    link_result = link({values["SUBSTACK"][1]: links[values["SUBSTACK"][1]]}, True, True)
                    cur_func += link_result[0]
                    cur_func += "else\n{\n"
                    link_result = link({values["SUBSTACK2"][1]: links[values["SUBSTACK2"][1]]}, True, True)
                    cur_func += link_result[0]
                elif opcode == "control_forever":
                    cur_func += "    while (true)\n{\n"
                    link_result = link({ values["SUBSTACK"][1]: links[values["SUBSTACK"][1]] }, True, True)
                    cur_func += link_result[0]

                elif opcode == "control_repeat":
                    num_fors += 1
                    if isinstance(values["TIMES"][1], list):
                        cur_func += f"    for (int i{num_fors} = 0;i{num_fors} < {values['TIMES'][1][1]};i{num_fors}++)\n" + "{\n"
                    else:

                        node = links[values["TIMES"][1]]
                        cur_func += f"    for (int i{num_fors} = 0;i{num_fors} < {recursive_operators(node['inputs'], node['fields'], node['opcode'])});i{num_fors}++)\n" + "{\n"
                    link_result = link({values["SUBSTACK"][1]: links[values["SUBSTACK"][1]]}, True, True)
                    cur_func += link_result[0]
                elif opcode == "control_wait":
                    if isinstance(values["DURATION"][1], list):
                        cur_func += f"    Sleep({values['DURATION'][1][1]} * 1000);\n"
                    else:

                        node = links[values["DURATION"][1]]
                        cur_func += f"    Sleep({recursive_operators(node['inputs'], node['fields'], node['opcode'])} * 1000);\n"
                elif opcode == "looks_say":
                    cur_func += f"    std::cout << "
                    next_node = values["MESSAGE"][1]

                    if isinstance(next_node, str):
                        if not next_node in links.keys():
                            next_node = variables[next_node]
                            cur_func += f"{next_node[1]});\n"
                        else:
                            next_node = links[next_node]
                            cur_func += recursive_operators(next_node["inputs"], next_node["fields"], next_node["opcode"]) + " << std::endl;\n"
                    else:
                        try:
                            cur_func += f'{variables[next_node[-1]][1]} << std::endl;\n'
                        except:
                            cur_func += f'"{next_node[-1]}" << std::endl;\n'
                elif opcode == "looks_sayforsecs":
                    cur_func += f"    std::cout << "
                    next_node = values["MESSAGE"][1]

                    if isinstance(next_node, str):
                        if not next_node in links.keys():
                            next_node = variables[next_node]
                            cur_func += f"{next_node[1]});\n"
                        else:
                            next_node = links[next_node]
                            cur_func += recursive_operators(next_node["inputs"], next_node["fields"], next_node["opcode"]) + " << std::endl;\n"
                    else:
                        try:
                            cur_func += f'{variables[next_node[-1]][1]} << std::endl;\n'
                        except:
                            cur_func += f'"{next_node[-1]}" << std::endl;\n'
                    if isinstance(values["SECS"][1], list):
                        cur_func += f"    Sleep({values['SECS'][1][1]} * 1000);\n"
                    else:

                        node = links[values["SECS"][1]]
                        cur_func += f"    Sleep({recursive_operators(node['inputs'], node['fields'], node['opcode'])} * 1000);\n"
                elif opcode == "procedures_call":
                    cur_func += f"    {cur_node['mutation']['proccode'].split('%')[0]}();\n"
                elif opcode == "sensing_resetimer":
                    cur_func += "    timer = std::chrono::system_clock::now();\n"
                elif opcode == "data_changevariableby":
                    cur_func += f"    {variables[fields['VARIABLE'][1]][1]} += "
                    next_node = values["VALUE"][1]

                    if isinstance(next_node, str):
                        if not next_node in links.keys():
                            next_node = variables[next_node]
                            cur_func += f"{next_node[1]});\n"
                        else:
                            next_node = links[next_node]
                            cur_func += f'{recursive_operators(next_node["inputs"], next_node["fields"], next_node["opcode"])};\n'

                    else:
                        try:
                            cur_func += f'{variables[next_node[-1]][1]};\n'

                        except:
                            cur_func += f"{next_node[-1]};\n"
            except:
                break
        if returned_function: cur_func += "    return 0;\n"
        cur_func += "}\n"

        if not returned_function: output_lines += cur_func

        else: main_func = cur_func
    return [output_lines, main_func]
link_result = link(_top_levels)
output_lines += link_result[0]
output_lines += link_result[1]
file.close()
out_file = open("output.cpp", "w")
out_file.write(output_lines)
out_file.close()
print("DONE\nLOG: COMPILING...", end="")
cwd = os.getcwd()
os.system(f'g++ output.cpp -o output -O3 -std=c++11 -pthread')
print(f"DONE\nRUNNING FILE {cwd}\output.exe")
os.system(f"output")

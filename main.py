import argparse
import typing
import yaml
from time import gmtime, strftime

parser = argparse.ArgumentParser()
parser.add_argument("input", type=str, help="OpCode definition file path")
parser.add_argument("template", type=str, help="Template file path")
parser.add_argument("output", type=str, help="Output file name")

args = parser.parse_args()


class Indent:
    def __init__(self):
        self.step_size = 4
        self.value = 0

    def increase(self):
        self.value += 1

    def decrease(self):
        self.value -= 1

    def reset(self):
        self.value = 0

    def generate_spaces(self):
        return " " * (self.step_size * self.value)


class OpCodeCppListGenerator:
    def __init__(self):
        self.prefix = ''
        self.indent = Indent()

    def format_name(self, name):
        return str.upper(name).replace('.', '_')

    def generate_key(self, name):
        return self.prefix + name

    def generate_value(self, code):
        return code

    def prepare_items(self, items):
        result = []

        for i in items:
            if type(i['name']) == type(list()):
                primary_name = i['name'][0]

                for n in i['name']:
                    string_to_append = self.indent.generate_spaces() + self.generate_key(self.format_name(n)) \
                                       + " = " + self.generate_value(i['code'])

                    if (n != primary_name):
                        string_to_append += " /* alias for " + self.format_name(primary_name) + " */"

                    result.append(string_to_append)
            else:
                result.append(self.indent.generate_spaces() + self.generate_key(self.format_name(i['name'])) + " = " + self.generate_value(i['code']))

        return result

    def generate_enumeration_lines(self, items):
        lines = self.prepare_items(items)

        # Do not use 'os.linesep' on Windows. It generates an extra line break
        return str.join(',\n', lines)


current_time = strftime("%Y-%m-%d %H:%M:%S %z", gmtime())

# Read definition file
input_file = open(args.input, 'r')
opcode_list = yaml.load(input_file)
opcode_list = opcode_list['mnemonics']
input_file.close()

# Read template
template_file = open(args.template, mode='r')
template_content = template_file.read()
template_file.close()

output_file_name = args.output

if output_file_name is None:
    output_file_name = '/._opcodes.h'

opcodes_file_generator_settings = {
    "outputFileName": output_file_name,
    "fileTemplate": template_content,
    "name": "_GeneratedOpCodes",
    "prefix": "OPCODE_",
}

with open(opcodes_file_generator_settings["outputFileName"], 'w') as f:
    cpp_enumeration_generator = OpCodeCppListGenerator()
    cpp_enumeration_generator.prefix = opcodes_file_generator_settings["prefix"]

    cpp_enumeration_generator.indent.increase()
    renderedItems = cpp_enumeration_generator.generate_enumeration_lines(
        opcode_list)
    cpp_enumeration_generator.indent.reset()

    result = opcodes_file_generator_settings["fileTemplate"]

    parameters = {
        "${generated_at}": current_time,
        '${name}': opcodes_file_generator_settings["name"],
        '${items}': renderedItems
    }

    for k, v in parameters.items():
        result = result.replace(k, v)

    f.write(result)

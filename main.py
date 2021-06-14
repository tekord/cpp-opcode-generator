import argparse
import pathlib
import yaml

from datetime import datetime
from jinja2 import Environment, FunctionLoader, Template, select_autoescape


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

    def as_string(self, whitespace=" "):
        return whitespace * (self.step_size * self.value)


def load_template_file_contents(id: str) -> str:
    with open(pathlib.Path("templates") / id) as f:
        return f.read()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Opcode definition file path")
    parser.add_argument("template", type=str, help="Template name")
    parser.add_argument("--output", dest="output", type=str, help="Output file path")

    args = parser.parse_args()

    with open(args.input, 'r') as f:
        opcode_list = yaml.load(f)
        opcode_list = opcode_list['mnemonics']

    template_environment_variables = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    }


    def render_c_lines(items, prefix="") -> str:
        indent = Indent()
        indent.increase()

        lines = []

        def format_name(name):
            return prefix + str.upper(name).replace('.', '_')

        def render_item(name, code):
            return indent.as_string() + format_name(name) + " = " + code

        for i in items:
            if type(i['name']) == type(list()):
                primary_name = i['name'][0]

                for n in i['name']:
                    string_to_append = render_item(n, i["code"])

                    if n != primary_name:
                        string_to_append += " // alias for " + format_name(primary_name)

                    lines.append(string_to_append)
            else:
                lines.append(render_item(i["name"], i["code"]))

        lines = str.join(',\n', lines)

        return lines


    def render_c_template(template: Template) -> str:
        lines = render_c_lines(opcode_list, "OPCODE_")

        template_variables = {
            "environment": template_environment_variables,
            "name": "_GeneratedOpCodes",
            "lines": lines,
        }

        return template.render(**template_variables)


    def render_cpp_template(template: Template) -> str:
        lines = render_c_lines(opcode_list, "OPCODE_")

        template_variables = {
            "environment": template_environment_variables,
            "name": "_GeneratedOpCodes",
            "lines": lines,
        }

        return template.render(**template_variables)


    def render_rust_template(template: Template) -> str:
        lines = render_c_lines(opcode_list)

        template_variables = {
            "environment": template_environment_variables,
            "name": "Opcodes",
            "lines": lines,
        }

        return template.render(**template_variables)


    template_map = {
        "c": {
            "template": "c-header.template",
            "renderer": render_c_template,
        },
        "cpp": {
            "template": "cpp-header.template",
            "renderer": render_cpp_template,
        },
        "rust": {
            "template": "rust.template",
            "renderer": render_rust_template,
        }
    }

    jinja_environment = Environment(
        loader=FunctionLoader(load_template_file_contents),
        autoescape=select_autoescape(),
        keep_trailing_newline=True
    )

    requested_template = args.template

    template_descriptor = template_map[requested_template]

    jinja_template = jinja_environment.get_template(template_descriptor["template"])

    result = template_descriptor["renderer"](jinja_template)

    if args.output:
        output_file_path = pathlib.Path(args.output)

        with open(output_file_path, 'w+') as f:
            f.write(result)
    else:
        print(result)

    exit(0)

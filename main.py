import argparse
import os
import typing
import yaml
from enum import Enum
from string import Template
from time import gmtime, strftime

parser = argparse.ArgumentParser()
parser.add_argument("input", type=str, help="OpCode definition file path")
parser.add_argument("template", type=str, help="Template file path")
parser.add_argument("output", type=str, help="Output file name")

args = parser.parse_args()

class Indent:
    stepSize = 4
    value = 0

    def __init__(self):
        pass

    def increase(self):
        self.value += 1

    def decrease(self):
        self.value -= 1

    def reset(self):
        self.value = 0

    def generateSpaces(self):
        return " " * (self.stepSize * self.value)

class OpCodeCppListGenerator:
    prefix = ''
    indent = Indent()

    def formatName(self, name):
        return str.upper(name).replace('.', '_')

    def generateKey(self, name):
        return self.prefix + name

    def generateValue(self, code):
        return code

    def prepareItems(self, items):
        result = []

        for i in items:
            if type(i['name']) == type(list()):
                primaryName = i['name'][0]

                for n in i['name']:
                    stringToAppend = self.indent.generateSpaces() + self.generateKey(self.formatName(n)) \
                                     + " = " + self.generateValue(i['code'])

                    if (n != primaryName):
                        stringToAppend += " /* alias for " + self.formatName(primaryName) + " */"

                    result.append(stringToAppend)
            else:
                result.append(self.indent.generateSpaces() + self.generateKey(self.formatName(i['name'])) + " = " + self.generateValue(i['code']))

        return result

    def generateEnumerationLines(self, items):
        lines = self.prepareItems(items)

        # Do not use 'os.linesep' on Windows. It generates extra line break
        return str.join(',\n', lines)

currentTime = strftime("%Y-%m-%d %H:%M:%S %z", gmtime())

# Read definition file
inputFile = open(args.input, 'r')
opCodeList = yaml.load(inputFile)
opCodeList = opCodeList['opcodes']
inputFile.close()

# Read template
templateFile = open(args.template, mode='r')
templateContent = templateFile.read()
templateFile.close()

outputFileName = args.output

if outputFileName == None:
    outputFileName = '/._opcodes.h'


opCodesFileGeneratorSettings = {
    "outputFileName": outputFileName,
    "fileTemplate": templateContent,
    "name": "_GeneratedOpCodes",
    "prefix": "OPCODE_",
}

with open(opCodesFileGeneratorSettings["outputFileName"], 'w') as f:
    cppEnumerationGenerator = OpCodeCppListGenerator()
    cppEnumerationGenerator.prefix = opCodesFileGeneratorSettings["prefix"]

    cppEnumerationGenerator.indent.increase()
    renderedItems = cppEnumerationGenerator.generateEnumerationLines(
        opCodeList)
    cppEnumerationGenerator.indent.reset()

    result = opCodesFileGeneratorSettings["fileTemplate"]

    parameters = {
        "${generated_at}":currentTime,
        '${name}':opCodesFileGeneratorSettings["name"],
        '${items}':renderedItems
    }

    for k, v in parameters.items():
        result = result.replace(k, v)

    f.write(result)

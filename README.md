# Opcode constant generator for C++

This script generates C++ header file with opcode constants based on YAML file definition. It may be useful for virtual machine developers. Defining opcodes in external file instead of direct C++ enum has some advantages:

1. It is easier to read. Definition file contains only relevant information, no C++ code.
2. You can automate the building of documentation.
3. Opcode definition is isolated from your virtual machine implementation, so you can use it in non-C++ implementation
(of course you'll have to modify this script a little bit).

Written on Python 3.

## Installation

Execute the following command to install dependencies:

```
pip3 install -r requirements.txt
```

## Usage

Copy the `opcodes.example.yaml` file to your application's folder, define all the opcodes you need in this file. 
Then run the script with the following arguments:

```shell
python main.py <opcode-list> <language> [--output path/to/file]
```

where `opcode-list` is a path to file with opcodes (.yaml file); `language` is one of the following options: `c`, `cpp`, `rust`;
 `--output` specified the output file path. If the `output` option is not provided then result will be printed to the standard 
 output. 
 
The result may look like this:

```cpp
enum _GeneratedOpCodes {
    OPCODE_NOP = 0x00,
    OPCODE_B = 0xA0,
    OPCODE_BZ = 0xA1,
    OPCODE_B_FALSE = 0xA1 /* alias for BZ */,
    OPCODE_B_ZERO = 0xA1 /* alias for BZ */,
    OPCODE_B_NULL = 0xA1 /* alias for BZ */,
    OPCODE_BNZ = 0xA2,
    OPCODE_B_TRUE = 0xA2 /* alias for BNZ */,
    OPCODE_B_NOT_ZERO = 0xA2 /* alias for BNZ */,
    OPCODE_B_NOT_NULL = 0xA2 /* alias for BNZ */
};
```

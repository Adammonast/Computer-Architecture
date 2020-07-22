"""CPU functionality."""

import sys

LDI = 0b10000010  # load value into register
PRN = 0b01000111  # print value
HLT = 0b00000001  # halt execution


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""

        # 256 bytes of memory
        self.ram = [0] * 256
        # 8 registers
        self.reg = [0] * 8
        # program counter
        self.pc = 0
        # branch table for instruction set
        self.instruction_set = {}
        # load the branch table
        self.instruction_set[LDI] = self.LDI
        self.instruction_set[PRN] = self.PRN
        self.instruction_set[HLT] = self.HLT
        self.running = False

    def ram_read(self, slot):
        # accept the address to read and return the value stored there
        return self.ram[slot]

    def ram_write(self, slot, value):
        # accept a value to write, and the address to write it to
        self.ram[slot] = value

    def load(self):
        """Load a program into memory."""

        # -- LOAD PROGRAM --

        # handle no argument for program
        if len(sys.argv) < 2:
            print('Please enter a program to run')
            sys.exit(1)

        filename = sys.argv[1]

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        with open(filename) as f:
            for line in f:
                line = line.split('#')
                try:
                    v = int(line[0], 2)
                except ValueError:
                    continue

                self.ram_write(address, v)
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')
        for i in range(8):
            print(" %02X" % self.reg[i], end='')
        print()

    def LDI(self):
        # get the register slot we want to write the value to
        reg_num = self.ram_read(self.pc+1)
        # get the value that we want to write to the register
        value = self.ram_read(self.pc+2)
        # set the register at the desired slot to the desired value
        self.reg[reg_num] = value

    def PRN(self):
        # get the register slot we want to print the value of
        reg_num = self.ram_read(self.pc+1)
        # get that value by its slot
        value = self.reg[reg_num]
        # print!
        print(value)

    def HLT(self):
        self.running = False

    def run(self):
        """Run the CPU."""

        # LDI = 0b10000010  # load value into register
        # PRN = 0b01000111  # print value
        # HLT = 0b00000001  # halt execution

        self.running = True
        while self.running:
            ir = self.ram_read(self.pc)
            # if the instruction exists in the instruction set,
            if ir in self.instruction_set:
                # perform the instruction
                self.instruction_set[ir]()
                # increment the pc using bitwise and shifting
                num_operands = (ir & 0b11000000) >> 6
                pc_move_to = num_operands + 1
                self.pc += pc_move_to

            else:
                print(f'Unknown instruction {ir} at address {self.pc}')
                sys.exit(1)

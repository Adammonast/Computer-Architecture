"""CPU functionality."""

import sys

LDI = 0b10000010  # load value into register
PRN = 0b01000111  # print value
HLT = 0b00000001  # halt execution
MUL = 0b10100010  # multiply
PUSH = 0b01000101  # push to stack
POP = 0b01000110  # pop off stack
CALL = 0b01010000  # call subroutine
RET = 0b00010001  # return from subroutine
CMP = 0b10100111  # compare two different registers


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
        # set the flag: 00000LGE less,greater,equal
        self.fl = 0b00000000
        # set register 7 to point to stack top
        self.reg[7] = 0xf4
        # branch table for instruction set
        self.instruction_set = {}
        # load the branch table
        self.instruction_set[LDI] = self.LDI
        self.instruction_set[PRN] = self.PRN
        self.instruction_set[HLT] = self.HLT
        self.instruction_set[MUL] = self.MUL
        self.instruction_set[PUSH] = self.PUSH
        self.instruction_set[POP] = self.POP
        self.instruction_set[CALL] = self.CALL
        self.instruction_set[RET] = self.RET
        self.instruction_set[CMP] = self.CMP
        self.running = False

    def ram_read(self, mar):
        # accept the address to read and return the value stored there
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        # accept a value to write, and the address to write it to
        self.ram[mar] = mdr

    def load(self):
        """Load a program into memory."""

        # handle no argument for program
        if len(sys.argv) < 2:
            print('Please enter a program to run')
            sys.exit(1)

        filename = sys.argv[1]

        address = 0

        with open(filename) as f:
            for line in f:
                # check blank lines and ignore them
                # ignore everything after a #
                line = line.split('#')
                try:
                    # convert binary string to integer
                    v = int(line[0], 2)
                except ValueError:
                    continue

                # call ram_write function
                self.ram_write(address, v)
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "CMP":
            # 00000LGE less,greater,equal
            # get the values
            val_a = self.reg[reg_a]
            val_b = self.reg[reg_b]
            # set what the flags should be
            if val_a == val_b:
                self.fl = 0b00000001
            elif val_a > val_b:
                self.fl = 0b00000010
            else:  # val_a is less
                self.fl = 0b00000100
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
        # get the register slot we're writing the value to
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
        # print
        print(value)

    def MUL(self):
        # get the register slot of the first number
        reg_num1 = self.ram_read(self.pc+1)
        # get the register slot of the second number
        reg_num2 = self.ram_read(self.pc+2)
        # pass them off to the ALU
        self.alu("MUL", reg_num1, reg_num2)

    def PUSH(self):
        # stack pointer
        SP = 7
        # decrement stack pointer, stacks going towards the bottom
        self.reg[SP] -= 1
        # get the value we're storing
        reg_num = self.ram_read(self.pc+1)
        # get the value
        value = self.reg[reg_num]
        # figure out where to store it
        top_of_stack_addr = self.reg[SP]
        # actually store it
        self.ram_write(top_of_stack_addr, value)

    def POP(self):
        # stack pointer
        SP = 7
        # get the address that the stack pointer is pointing to
        address = self.reg[SP]
        # get the value of that address from RAM
        value = self.ram_read(address)
        # get the number for the given register
        reg_num = self.ram_read(self.pc+1)
        # write the value to this register
        self.reg[reg_num] = value
        # increment the stack pointer, stacks going towards the bottom
        self.reg[SP] += 1

    def CALL(self):
        # get return address
        # this command has one parameter -> increments by 2
        return_addr = self.pc+2
        # push the return address to stack
        SP = 7
        # decrement stack pointer, stacks going towards the bottom
        self.reg[SP] -= 1
        # write to the stack with the return address
        self.ram_write(self.reg[SP], return_addr)
        # get the address that we want to call
        # move program counter to
        reg_num = self.ram_read(self.pc+1)
        subroutine_addr = self.reg[reg_num]
        # call subroutine
        self.pc = subroutine_addr
        # This has to return true because we are moving
        return True

    def RET(self):
        # stack pointer
        SP = 7
        # get the address that the stack pointer is pointing to
        address = self.reg[SP]
        # get the value of that address from RAM
        return_addr = self.ram_read(address)
        # set the program counter to the return address
        self.pc = return_addr
        # increment the stack pointer, stacks going towards the bottom
        self.reg[SP] += 1
        return True

    def CMP(self):
        # target first register address
        reg_a = self.ram_read(self.pc+1)
        # target second register address
        reg_b = self.ram_read(self.pc+2)
        # pass to the ALU
        self.alu("CMP", reg_a, reg_b)

    def HLT(self):
        self.running = False

    def run(self):
        """Run the CPU."""

        self.running = True
        while self.running:
            ir = self.ram_read(self.pc)
            # if the instruction exists in the instruction set,
            if ir in self.instruction_set:
                # perform the instruction
                self.instruction_set[ir]()
                # increment the program counter using bitwise and shifting
                instruction_length = (ir & 0b11000000) >> 6
                # program counter should be incremented by this much
                pc_move_to = instruction_length + 1
                # increment program counter
                self.pc += pc_move_to

            else:
                print(f'Unknown instruction {ir} at address {self.pc}')
                sys.exit(1)

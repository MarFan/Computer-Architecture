"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
ADD = 0b10100000
RET = 0b00010001

SP = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.halted = False
        self.pc = 0
        self.reg[SP] = 0xf4
        self.inst_set_pc = 0

        self.branchtable = {}
        self.branchtable[HLT] = self.hlt
        self.branchtable[LDI] = self.ldi
        self.branchtable[PRN] = self.prn
        self.branchtable[MUL] = self.mul
        self.branchtable[PUSH] = self.push
        self.branchtable[POP] = self.pop
        self.branchtable[CALL] = self.call
        self.branchtable[ADD] = self.add
        self.branchtable[RET] = self.ret


        # pass

    def load(self):
        """Load a program into memory."""

        address = 0

        program = []
    
        with open(sys.argv[1]) as f:
            for line in f:
                if len(line.strip().split('#')[0]):
                    self.ram[address] = int(line.strip().split('#')[0], 2)
                    address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        return self.ram[address]
    
    def ram_write(self, address, value):
        self.ram[address] = value
        return self.ram[address]

    def hlt(self, operand_a=None, operand_b=None):
        self.halted = True

    def ldi(self, operand_a=None, operand_b=None):
        self.reg[operand_a] = operand_b

    def prn(self, operand_a=None, operand_b=None):
        print(self.reg[operand_a])

    def mul(self, operand_a=None, operand_b=None):
        self.alu("MUL", operand_a, operand_b)

    def push(self, operand_a=None, operand_b=None):
        self.reg[SP] -= 1
        value = self.reg[operand_a]
        self.ram_write(self.reg[SP], value)

    def pop(self, operand_a=None, operand_b=None):
        if self.reg[SP] == 0xF4:
            return 'Empty Stack'
        value = self.ram_read(self.reg[SP])
        self.reg[operand_a] = value
        self.reg[SP] += 1

    def call(self, operand_a=None, operand_b=None):
        return_addr = self.pc + 2
        
        self.reg[SP] -= 1
        top_of_stack_addr = self.reg[SP]
        self.ram_write(self.reg[SP], return_addr)

        reg_num = self.ram[self.pc + 1]
        subroutine_addr = self.reg[reg_num]
        
        self.pc = subroutine_addr

    def add(self, operand_a=None, operand_b=None):
        self.alu("ADD", operand_a, operand_b)

    def ret(self, operand_a=None, operand_b=None):
        value = self.reg[SP]
        return_addr = self.ram[value]
        self.reg[SP] += 1        
        self.pc = self.ram[value]

    def run(self):
        """Run the CPU."""
        while not self.halted:
            instruction = self.ram_read(self.pc)

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            instruction_size = ((instruction >> 6) & 0b11) + 1

            if instruction in self.branchtable:
                self.branchtable[instruction](operand_a, operand_b)
            else:
                self.halted = True

            if ((instruction >> 4) & 0b1) != 1:
                self.pc += instruction_size
            
        # print(self.reg)
        # print(self.ram)
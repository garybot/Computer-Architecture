"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8 # registers
        # R5 is reserved as the interrupt mask (IM)
        # R6 is reserved as the interrupt status (IS)
        self.reg[7] = 0xF4 # R7 is reserved as the stack pointer (SP)

        # Program Counter, address of the currently executing instruction
        self.pc = 0b00000000

        # Instruction Register, contains a copy of the currently executing instruction
        # self.ir = 0b00000000

        # Memory Address Register, holds the memory address we're reading or writing
        # self.mar = 0b00000000

        # Memory Data Register, holds the value to write or the value just read
        # self.mdr = 0b00000000

        # The flags register FL holds the current flags status.
        self.fl = 0b00000000

        self.ram = [0] * 256

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        mar %= 256 # not sure if this matters yet
        self.ram[mar] = mdr

    def load(self):
        """Load a program into memory."""

        address = 0
        if len(sys.argv) < 2:
            print("Remember to pass second filename")
            print("Usage: python3 fileio.py <second_file_name.ls8>")
            exit()

        file = sys.argv[1]

        try:
            with open(file, 'r') as f:
                for line in f:
                    if line != "\n" and line[0] != "#":
                        # self.ram[address] = int(line[0:8], 2)
                        self.ram_write(address, int(line[0:8], 2))
                        address += 1

        except FileNotFoundError:
            print(f'Error from {sys.argv[0]}: file {sys.argv[1]} not found!')
            exit()

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
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]

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

    def run(self):
        """Run the CPU."""
        running = True
        # self.pc = 0 # program counter
        while running:
            ir = self.ram_read(self.pc) # Instruction Register
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            alu = (ir >> 5) & 0b001
            sets_pointer = (ir >> 4) & 0b0001
            # self.trace()

            if ir == 0b10000010: # LDI
                self.reg[operand_a] = operand_b

            elif ir == 0b01000111: # PRN
                print(self.reg[operand_a])

            elif ir == 0b10100010: # MUL
                self.alu("MUL", operand_a, operand_b)

            elif ir == 0b10100000: # ADD
                self.alu("ADD", operand_a, operand_b)

            elif ir == 0b01000101: # PUSH
                self.reg[7] -= 1
                self.ram_write(self.reg[7], self.reg[operand_a])

            elif ir == 0b01000110: # POP
                self.reg[operand_a] = self.ram_read(self.reg[7])
                self.reg[7] += 1

            elif ir == 0b01000111: # PRN
                print(self.reg[operand_a])

            elif ir == 0b01010100: # JMP
                self.pc = operand_a

            elif ir == 0b00000001: # HLT
                running = False

            else:
                print('Unknown Command!')
                running = False

            if not sets_pointer:
                self.pc += (ir >> 6) + 1

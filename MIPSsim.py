import sys
import getopt

class MIPSSimulator(object):
    
    __begin_addr = 128
    __instr_len = 4
    
    __category1 = {
        "000" : lambda bin_instr: "J #%d" % (int(bin_instr[6:]+"00", 2)), 
        "010" : lambda bin_instr: "BEQ R%d, R%d, #%d" % (int(bin_instr[6:11], 2), 
                                                         int(bin_instr[11:16], 2), 
                                                         MIPSSimulator.__bin2dec(bin_instr[16:]+"00")), 
        "100" : lambda bin_instr: "BGTZ R%d, #%d" % (int(bin_instr[6:11], 2), 
                                                     MIPSSimulator.__bin2dec(bin_instr[16:]+"00")), 
        "101" : lambda bin_instr: "BREAK", 
        "110" : lambda bin_instr: "SW R%d, %d(R%d)" % (int(bin_instr[11:16], 2),
                                                       MIPSSimulator.__bin2dec(bin_instr[16:]),
                                                       int(bin_instr[6:11], 2)), 
        "111" : lambda bin_instr: "LW R%d, %d(R%d)" % (int(bin_instr[11:16], 2),
                                                       MIPSSimulator.__bin2dec(bin_instr[16:]),
                                                       int(bin_instr[6:11], 2))
    }
    
    __category2 = {
        "000" : lambda bin_instr: "ADD R%d, R%d, R%d" % MIPSSimulator.__format_category2(bin_instr),
        "001" : lambda bin_instr: "SUB R%d, R%d, R%d" % MIPSSimulator.__format_category2(bin_instr), 
        "010" : lambda bin_instr: "MUL R%d, R%d, R%d" % MIPSSimulator.__format_category2(bin_instr), 
        "011" : lambda bin_instr: "AND R%d, R%d, R%d" % MIPSSimulator.__format_category2(bin_instr), 
        "100" : lambda bin_instr: "OR R%d, R%d, R%d" % MIPSSimulator.__format_category2(bin_instr), 
        "101" : lambda bin_instr: "XOR R%d, R%d, R%d" % MIPSSimulator.__format_category2(bin_instr), 
        "110" : lambda bin_instr: "NOR R%d, R%d, R%d" % MIPSSimulator.__format_category2(bin_instr)
    }
    
    __category3 = {
        "000" : lambda bin_instr: "ADDI R%d, R%d, #%d" % MIPSSimulator.__format_category3(bin_instr), 
        "001" : lambda bin_instr: "ANDI R%d, R%d, #%d" % MIPSSimulator.__format_category3(bin_instr), 
        "010" : lambda bin_instr: "ORI R%d, R%d, #%d" % MIPSSimulator.__format_category3(bin_instr), 
        "011" : lambda bin_instr: "XORI R%d, R%d, #%d" % MIPSSimulator.__format_category3(bin_instr)
    }
    
    __instrs = {
        "000" : lambda bin_instr: MIPSSimulator.__category1[bin_instr[3:6]](bin_instr), 
        "110" : lambda bin_instr: MIPSSimulator.__category2[bin_instr[13:16]](bin_instr),
        "111" : lambda bin_instr: MIPSSimulator.__category3[bin_instr[13:16]](bin_instr)
    }    
    
    def __init__(self):
        self.disassembly = ""
        self.simulation = ""
        self.__assembly_code = {}
        self.__data = {}
        self.__registers = []
        self.__data_addr = 0
        self.__data_addr_end = 0

    @staticmethod
    def __bin2dec(binary):
        if binary[0] == "0":
            return int(binary[1:], 2)
        else:
            s = ""
            for bit in binary[1:]:
                if bit == "0":
                    s += "1"
                else:
                    s += "0"
            return -(int(s, 2)+1)
 
    @staticmethod
    def __format_category2(bin_instr):
        return (int(bin_instr[16:21], 2), int(bin_instr[3:8], 2), int(bin_instr[8:13], 2))
    
    @staticmethod
    def __format_category3(bin_instr):
        return (int(bin_instr[8:13], 2), int(bin_instr[3:8], 2), MIPSSimulator.__bin2dec(bin_instr[16:])) 
 
    def disassemble(self, binary_path):
        try:
            binary_file = open(binary_path, "r")
        except:
            print "[!!!] Can't not open binary file."
            sys.exit(1)          
        try:
            binary = binary_file.read()
        except:
            print "[!!!] Can't not read binary file."
            sys.exit(1)
        finally:
            binary_file.close()
        iscode = True
        addr = self.__begin_addr        
        self.disassembly = ""
        self.__assembly_code = {}
        self.__data = {}
        for bin_instr in binary.split("\n"):
            if iscode:
                instr = self.__instrs[bin_instr[0:3]](bin_instr)
                self.disassembly += "%s\t%d\t%s\n" % (bin_instr, addr, instr)
                self.__assembly_code[addr] = instr
                if instr == "BREAK":
                    iscode = False
                    self.__data_addr = addr + self.__instr_len
            else:
                data = self.__bin2dec(bin_instr)
                self.disassembly += "%s\t%d\t%d\n" % (bin_instr, addr, data)
                self.__data[addr] = data
            addr += self.__instr_len
        self.__data_addr_end = addr
        return self.disassembly
    
    def write2file(self, output, file_path):
        try:
            f = open(file_path, "w")
        except:
            print "[!!!] Can't not open file."
            sys.exit(1)          
        try:
            f.write(output)
        except:
            print "[!!!] Can't not write file."
            sys.exit(1)
        finally:
            f.close()
    
    def __format_simulation_data(self):
        output = "Data\n"
        addrs = range(self.__data_addr, self.__data_addr_end, self.__instr_len)
        i = 0
        while i < len(addrs)-1:
            alignment = []
            for addr in addrs[i:i+8]:
                alignment.append(self.__data[addr])            
            output += "%d:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" % ((addrs[i],) + tuple(alignment))
            i += 8    
        output+="\n"
        return output

    def __format_simulation_output(self, cycle, addr, instr):
        output = "--------------------\nCycle:%d\t%d\t%s\n\n" % (cycle, addr, instr)
        output += "Registers\n"\
            "R00:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n"\
            "R08:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n"\
            "R16:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n"\
            "R24:\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n\n" % tuple(self.__registers)
        output += self.__format_simulation_data()
        return output
    
    __do_category2 = {
        "ADD" : lambda rs, rt : rs + rt,
        "SUB" : lambda rs, rt : rs - rt,
        "MUL" : lambda rs, rt : rs * rt,
        "AND" : lambda rs, rt : rs & rt,
        "OR" : lambda rs, rt : rs | rt,
        "XOR" : lambda rs, rt : rs ^ rt,
        "NOR" : lambda rs, rt : ~(rs | rt)
    }
    
    __do_category3 = {
        "ADDI" : lambda rs, immed: rs + immed,
        "ANDI" : lambda rs, immed: rs & immed,
        "ORI" : lambda rs, immed: rs | immed,
        "XORI" : lambda rs, immed: rs ^ immed
    }
    
    def __do_instruction(self, instr, pc):
        is_break = False
        pc += self.__instr_len
        l = instr.replace(",", "").split(" ")
        if l[0] in ("ADD", "SUB", "MUL", "AND", "OR", "XOR", "NOR"):
            rdi = int(l[1].replace("R", ""))
            rsi = int(l[2].replace("R", ""))
            rti = int(l[3].replace("R", ""))
            self.__registers[rdi] = MIPSSimulator.__do_category2[l[0]](self.__registers[rsi], self.__registers[rti])
        elif l[0] in ("ADDI", "ANDI", "ORI", "XORI"):
            rti = int(l[1].replace("R", ""))
            rsi = int(l[2].replace("R", ""))
            immed = int(l[3].replace("#", ""))
            self.__registers[rti] = MIPSSimulator.__do_category3[l[0]](self.__registers[rsi], immed)
        elif l[0] == "J":
            pc = int(l[1].replace("#", ""))
        elif l[0] == "BEQ":
            rsi = int(l[1].replace("R", ""))
            rti = int(l[2].replace("R", ""))
            if self.__registers[rsi] == self.__registers[rti]:
                pc += int(l[3].replace("#", ""))
        elif l[0] == "BGTZ":
            rsi = int(l[1].replace("R", ""))
            if self.__registers[rsi] > 0:
                pc += int(l[2].replace("#", ""))
        elif l[0] in ("SW", "LW"):
            rti = int(l[1].replace("R", ""))
            [offset, base] = l[2].split("(")
            offset = int(offset)
            base = self.__registers[int(base.replace("R", "").replace(")", ""))]
            if l[0] == "SW":
                self.__data[base+offset] = self.__registers[rti]
            elif l[0] == "LW":
                self.__registers[rti] = self.__data[base+offset]      
        elif l[0] == "BREAK":
            is_break = True
        return is_break, pc
    
    def simulate(self, binary_path):
        self.disassemble(binary_path)
        pc = self.__begin_addr
        cycle = 1
        self.__registers = [
            0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0
        ]
        self.simulation = ""
        while True:
            addr = pc
            instr = self.__assembly_code[pc]
            is_break, pc = self.__do_instruction(instr, pc)
            self.simulation += self.__format_simulation_output(cycle, addr, instr)
            cycle += 1
            if is_break:
                break
        return self.simulation

def usage():
    print "Usage: "
    print "-h                              - help"
    print "--help                          - help"
    print "-b binary_file                  - input binary to run"
    print "--binary=binary_file            - input binary to run"
    print "-d                              - disassemble and print to screen"
    print "--disassemble=disassembly_file  - disassemble and output disassembly to file"
    print "-s                              - simulate and print to screen"
    print "--simulate=simulation_file      - simulate and output simulation to file"
    print "Examples: "
    print "python MIPSsim.py -b sample.txt -d"
    print "python MIPSsim.py --binary=sample.txt --disassemble=disassembly.txt"
    print "python MIPSsim.py -b sample.txt --simulate=simulation.txt"
    print "python MIPSsim.py -b sample.txt -d -s"
    sys.exit(0)

if __name__ == '__main__':
    if not len(sys.argv[1:]):
        usage()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hb:ds", ["help", "binary=", "disassemble=", "simulate="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
    binary_file = ""
    disassembly_file = ""
    d = False
    simulation_file = ""
    s = False
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-b", "--binary"):
            binary_file = a
        elif o in ("-d", "--disassemble"):
            disassembly_file = a
            d = True
        elif o in ("-s", "--simulate"):
            simulation_file = a
            s = True
        else:
            assert False, "Unhandled Option."
    mipssim = MIPSSimulator()
    if binary_file != "":
        if d:
            disassembly = mipssim.disassemble(binary_file)
            if disassembly_file != "":
                mipssim.write2file(disassembly, disassembly_file)
            else:
                print disassembly
        if s:
            simulation = mipssim.simulate(binary_file)
            if simulation_file != "":
                mipssim.write2file(simulation, simulation_file)
            else:
                print simulation
        if not d and not s:
            print "No action to perform. Exit."
    else:
        print "No input binary file. Exit."
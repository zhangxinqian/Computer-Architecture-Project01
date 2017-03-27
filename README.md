#Computer-Architecture-Project01

Python env: 2.7

Usage:

-h - help

--help - help

-b binary_file - input binary to run

--binary=binary_file - input binary to run

-d - disassemble and print to screen

--disassemble=disassembly_file - disassemble and output disassembly to file

-s - simulate and print to screen

--simulate=simulation_file - simulate and output simulation to file

Examples:

python MIPSsim.py -b sample.txt -d

python MIPSsim.py --binary=sample.txt --disassemble=disassembly.txt

python MIPSsim.py -b sample.txt --simulate=simulation.txt

python MIPSsim.py -b sample.txt -d -s
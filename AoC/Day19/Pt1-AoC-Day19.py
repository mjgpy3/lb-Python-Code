# Pt2-AoCDay19.py
# 2018 Advent of Code
# Day 19
# Part 1
# https://adventofcode.com/2018/day/19

import time
import re
import os

"""
--- Day 19: Go With The Flow ---
With the Elves well on their way constructing the North Pole base, 
you turn your attention back to understanding the inner workings of programming the device.

You can't help but notice that the device's opcodes don't contain any flow control like jump instructions. 
The device's manual goes on to explain:

"In programs where flow control is required, the instruction pointer can be bound to a register 
so that it can be manipulated directly. 
This way, setr/seti can function as absolute jumps, addr/addi can function as relative jumps, 
and other opcodes can cause truly fascinating effects."

This mechanism is achieved through a declaration like #ip 1, 
which would modify register 1 so that accesses to it let the program indirectly access the 
instruction pointer itself. 
To compensate for this kind of binding, there are now six registers (numbered 0 through 5); 
the five not bound to the instruction pointer behave as normal. 
Otherwise, the same rules apply as the last time you worked with this device.

When the instruction pointer is bound to a register, its value is written to that register 
just before each instruction is executed, and the value of that register is written back 
to the instruction pointer immediately after each instruction finishes execution. 
Afterward, move to the next instruction by adding one to the instruction pointer, 
even if the value in the instruction pointer was just updated by an instruction. 
(Because of this, instructions must effectively set the instruction pointer to the 
instruction before the one they want executed next.)

The instruction pointer is 0 during the first instruction, 1 during the second, and so on. 
If the instruction pointer ever causes the device to attempt to load an instruction outside 
the instructions defined in the program, the program instead immediately halts. 
The instruction pointer starts at 0.

It turns out that this new information is already proving useful: 
the CPU in the device is not very powerful, and a background process is occupying most of its time. 
You dump the background process' declarations and instructions to a file (your puzzle input), 
making sure to use the names of the opcodes rather than the numbers.

For example, suppose you have the following program:

#ip 0
seti 5 0 1
seti 6 0 2
addi 0 1 0
addr 1 2 3
setr 1 0 0
seti 8 0 4
seti 9 0 5

When executed, the following instructions are executed. Each line contains the value of the instruction pointer at the time the instruction started, the values of the six registers before executing the instructions (in square brackets), the instruction itself, and the values of the six registers after executing the instruction (also in square brackets).

ip=0 [0, 0, 0, 0, 0, 0] seti 5 0 1 [0, 5, 0, 0, 0, 0]
ip=1 [1, 5, 0, 0, 0, 0] seti 6 0 2 [1, 5, 6, 0, 0, 0]
ip=2 [2, 5, 6, 0, 0, 0] addi 0 1 0 [3, 5, 6, 0, 0, 0]
ip=4 [4, 5, 6, 0, 0, 0] setr 1 0 0 [5, 5, 6, 0, 0, 0]
ip=6 [6, 5, 6, 0, 0, 0] seti 9 0 5 [6, 5, 6, 0, 0, 9]
In detail, when running this program, the following events occur:

The first line (#ip 0) indicates that the instruction pointer should be bound to register 0 in this program. 
This is not an instruction, and so the value of the instruction pointer does not change during 
the processing of this line.
The instruction pointer contains 0, and so the first instruction is executed (seti 5 0 1). 
It updates register 0 to the current instruction pointer value (0), sets register 1 to 5, 
sets the instruction pointer to the value of register 0 (which has no effect, as the instruction 
did not modify register 0), and then adds one to the instruction pointer.
The instruction pointer contains 1, and so the second instruction, seti 6 0 2, is executed. 
This is very similar to the instruction before it: 6 is stored in register 2, and the instruction pointer 
is left with the value 2.
The instruction pointer is 2, which points at the instruction addi 0 1 0. 
This is like a relative jump: the value of the instruction pointer, 2, is loaded into register 0. 
Then, addi finds the result of adding the value in register 0 and the value 1, storing the result, 3, 
back in register 0. Register 0 is then copied back to the instruction pointer, 
which will cause it to end up 1 larger than it would have otherwise and skip the next instruction 
(addr 1 2 3) entirely. Finally, 1 is added to the instruction pointer.
The instruction pointer is 4, so the instruction setr 1 0 0 is run. 
This is like an absolute jump: it copies the value contained in register 1, 5, into register 0, 
which causes it to end up in the instruction pointer. The instruction pointer is then incremented, 
leaving it at 6.
The instruction pointer is 6, so the instruction seti 9 0 5 stores 9 into register 5. 
The instruction pointer is incremented, causing it to point outside the program, and so the program ends.
What value is left in register 0 when the background process halts?

===================================================================================
Notes about this problem.

The opcodes have already been translated into their mnemonic. 
Could either use the opcode directly and add a "parser" or could translate the opcode into the previous opcode numbers.
Probably easier to use the opcode directly and parse it.

"""

def printList(listToPrint):
	for row in listToPrint:
		print row

def readtextFileAsListOfLinesToList(fileName):
	"""readtextFileAsListOfLinesAndSrtToList - open file and read the content to a list
	File is sorted to produce a date/time ordered file
	:returns: the text file as a list of input lines
	"""
	textFileAsListOfLines = []
	with open(fileName,'r') as filehandle:  
		for line in filehandle:
			textFileAsListOfLines.append(line.strip())
	return textFileAsListOfLines
	
def abbyTerminate(strToPrint):
	print 'abbyTerminate: terminating due to',
	print strToPrint
	exit()
	
#########################################################################
## The 16 instructions
## Do the operation indicated and return what the value would be for the operation
## Higher level code can determine if that matches the expected value

#######################################################################################
## Implement the instruction set in the emulator
##
## Instruction format
## Vector values
## OPCODE[0:3]...BEFORE[4:7]...After[8:11]
## OPCODE[0] = Opcodes with values from 0-15
## OPCODE[1] = Register Select/Immediate A
## OPCODE[2] = Register Select/Immediate B
## OPCODE[3] = Register Select C which register gets the result
## BEFORE[4:7] = The register values before the operation
## AFTER[8:11] = The register values after the operation

class CPU:
	"""The register set is globals to the class
	"""
	CPU_Reg0 = 0
	CPU_Reg1 = 0
	CPU_Reg2 = 0
	CPU_Reg3 = 0
	CPU_Reg4 = 0
	CPU_Reg5 = 0
	CPU_IP = 0
	
	def emulator(self,vector):
		"""emulator - The function that calls the ALU and returns the return value
		Extended from Day 16 example to load (if necessary) and increment the CPU Instruction Pointer.
		
		:param vector: The instruction vector fields 0-3
		:returns: the contents of the registers.
		"""
		debug_emulator = False
		global instructionPointerRegisterNumber
		global instructionPointer
		if debug_emulator:
			print 'emulator:',vector
		self.setRegToIPValue()
		print 'IP =',instructionPointer,
		print self.getRegisterAfterValues(),
		print vector[0],
		print vector[1],
		print vector[2],
		print vector[3],
		self.doALU(vector[0:4])
		print self.getRegisterAfterValues()
		if instructionPointerRegisterNumber == vector[3]:	# Only load if there was a change to the register
			if debug_emulator:
				print 'changed IP register'
			self.loadAddressForJump(vector[0][3])
		instructionPointer += 1		# Always increment address pointer regardless of the previous
		self.setIPReg(instructionPointer)
		return self.getRegisterAfterValues()
	
	def setRegToIPValue(self):
		global instructionPointer
		if instructionPointerRegisterNumber == 0:
			self.CPU_Reg0 = instructionPointer
		elif instructionPointerRegisterNumber == 1:
			self.CPU_Reg1 = instructionPointer
		elif instructionPointerRegisterNumber == 2:
			self.CPU_Reg2 = instructionPointer
		elif instructionPointerRegisterNumber == 3:
			self.CPU_Reg3 = instructionPointer
		elif instructionPointerRegisterNumber == 4:
			self.CPU_Reg4 = instructionPointer
		elif instructionPointerRegisterNumber == 5:
			self.CPU_Reg5 = instructionPointer
	
	def setIPReg(self,IPRegVal):
		if instructionPointerRegisterNumber == 0:
			self.CPU_Reg0 = IPRegVal
		elif instructionPointerRegisterNumber == 1:
			self.CPU_Reg1 = IPRegVal
		elif instructionPointerRegisterNumber == 2:
			self.CPU_Reg2 = IPRegVal
		elif instructionPointerRegisterNumber == 3:
			self.CPU_Reg3 = IPRegVal
		elif instructionPointerRegisterNumber == 4:
			self.CPU_Reg4 = IPRegVal
		elif instructionPointerRegisterNumber == 5:
			self.CPU_Reg5 = IPRegVal
	
	def loadAddressForJump(self,relAbsFlag):
		"""loadAddressForJump - Load the instruction pointer (address) from the register 
		selected by the #IP directive.
		The instruction pointer is 4, so the instruction setr 1 0 0 is run. 
		This is like an absolute jump: it copies the value contained in register 1, 5, into register 0, 
		which causes it to end up in the instruction pointer. 
		The instruction pointer is then incremented, leaving it at 6.
		"""
		global instructionPointerRegisterNumber
		global instructionPointer
		print 'loadAddressForJump: reached jmp function',
		operation = ''
		if relAbsFlag == 'r':
			operation = 'absolute'
		else:
			operation = 'relative'
		print operation,
		print 'IP before',instructionPointer,
		if instructionPointerRegisterNumber == 0:
			if relAbsFlag == 'absolute':
				instructionPointer = self.CPU_Reg0
			elif relAbsFlag == 'relative':
				instructionPointer += self.CPU_Reg0
		elif instructionPointerRegisterNumber == 1:
			if relAbsFlag == 'absolute':
				instructionPointer = self.CPU_Reg1
			elif relAbsFlag == 'relative':
				instructionPointer += self.CPU_Reg1
		elif instructionPointerRegisterNumber == 2:
			if relAbsFlag == 'absolute':
				instructionPointer = self.CPU_Reg2
			elif relAbsFlag == 'relative':
				instructionPointer += self.CPU_Reg2
		elif instructionPointerRegisterNumber == 3:
			if relAbsFlag == 'absolute':
				instructionPointer = self.CPU_Reg3
			elif relAbsFlag == 'relative':
				instructionPointer += self.CPU_Reg3
		elif instructionPointerRegisterNumber == 4:
			if relAbsFlag == 'absolute':
				instructionPointer = self.CPU_Reg4
			elif relAbsFlag == 'relative':
				instructionPointer += self.CPU_Reg4
		elif instructionPointerRegisterNumber == 5:
			if relAbsFlag == 'absolute':
				instructionPointer = self.CPU_Reg5
			elif relAbsFlag == 'relative':
				instructionPointer += self.CPU_Reg5
		print 'IP after',instructionPointer
	
	def initializeCPU(self):
		"""Sets the registers in the CPU to zeros.
		Used at the start of the program to ensure known values in registers.
		
		:returns: no return value
		"""
		self.CPU_Reg0 = 0
		self.CPU_Reg1 = 0
		self.CPU_Reg2 = 0
		self.CPU_Reg3 = 0
		self.CPU_Reg4 = 0
		self.CPU_Reg5 = 0
		self.CPU_IP = 0

	def setBeforeOperationRegisterValues(self,beforeRegs):
		"""setBeforeOperationRegisterValues
		
		:param beforeRegs: The registers before the operation.
		:returns: nothing
		"""
		#print 'setBeforeOperationRegisterValues: beforeRegs',beforeRegs
		self.CPU_Reg0 = beforeRegs[0]
		self.CPU_Reg1 = beforeRegs[1]
		self.CPU_Reg2 = beforeRegs[2]
		self.CPU_Reg3 = beforeRegs[3]
		self.CPU_Reg4 = beforeRegs[4]
		self.CPU_Reg5 = beforeRegs[5]
		return
	
	def getRegisterAfterValues(self):
		"""getRegisterAfterValues - get the contents of the register after the operation completes
		
		:returns: CPU registers as a vector (6 elements long)
		"""
		return [self.CPU_Reg0, self.CPU_Reg1, self.CPU_Reg2, self.CPU_Reg3, self.CPU_Reg4, self.CPU_Reg5]
		
	def getRegA(self,regSelA):
		"""getRegA - Simulates a 1:6 de-multiplexer
		
		:param regSelA: the select for the the A input to the ALU
		:returns: content of the selected register
		"""
		if regSelA == 0:
			return self.CPU_Reg0
		elif regSelA == 1:
			return self.CPU_Reg1
		elif regSelA == 2:
			return self.CPU_Reg2
		elif regSelA == 3:
			return self.CPU_Reg3
		elif regSelA == 4:
			return self.CPU_Reg4
		elif regSelA == 5:
			return self.CPU_Reg5
		abbyTerminate('getRegA: passed unexpected value for select')

	def getInputA(self,regSelA,immedVsRegFlag):
		"""getInputA - Implement a 2:1 multiplexer.
		
		:param regSelA: The regSelA value itself (immediate value)
		:param immedVsRegFlag: Flags whether the immediate value or the register value is returned
		:returns: The output of the 2:1 multiplexer
		"""
		if immedVsRegFlag == 'Immediate':
			return regSelA
		elif immedVsRegFlag == 'Register':
			return self.getRegA(regSelA)
		abbyTerminate('getInputA: needs flag of Immediate or Register')

	def getRegB(self,regSelB):
		"""getRegB - Simulates a 1:6 de-multiplexer
		
		:param regSelB: the select for the the A input to the ALU
		:returns: content of the selected register
		"""
		if regSelB == 0:
			return self.CPU_Reg0
		elif regSelB == 1:
			return self.CPU_Reg1
		elif regSelB == 2:
			return self.CPU_Reg2
		elif regSelB == 3:
			return self.CPU_Reg3
		elif regSelB == 4:
			return self.CPU_Reg4
		elif regSelB == 5:
			return self.CPU_Reg5
		abbyTerminate('getRegA: passed unexpected value')

	def getInputB(self,regSelB,immedVsRegFlag):
		"""getInputA - Implement a 2:1 multiplexer.
		
		:param regSelA: The regSelA value itself (immediate value)
		:param immedVsRegFlag: Flags whether the immediate value or the register value is returned
		:returns: The output of the 2:1 multiplexer
		"""
		if immedVsRegFlag == 'Immediate':
			return regSelB
		elif immedVsRegFlag == 'Register':
			return self.getRegB(regSelB)
		abbyTerminate('getInputB: needs flag of Immediate or Register')

	def storeCVal(self,regSel,cVal):
		"""storeCVal - Takes the output of the ALU (called C) and routes it to the correct register.
		Implements a 1:6 demultiplexer into the six registers to load the correct register
		In hardware this would be one common bus to all register inputs and a LOAD line to clock the correct register
		
		:param regSel: Register Select value (0-5) which selects which register gets written.
		:param: cVal: Output from the ALU (aka "C")
		"""
		debug_storeCVal = False
		if debug_storeCVal:
			print 'storeCVal: regSel,cVal',regSel,cVal
		if regSel == 0:
			self.CPU_Reg0 = cVal
		elif regSel == 1:
			self.CPU_Reg1 = cVal
		elif regSel == 2:
			self.CPU_Reg2 = cVal
		elif regSel == 3:
			self.CPU_Reg3 = cVal
		elif regSel == 4:
			self.CPU_Reg4 = cVal
		elif regSel == 5:
			self.CPU_Reg5 = cVal
		else:
			abbyTerminate('storeCVal: passed unexpected value')
	
	def doALU(self,opcodeVector):
		"""doALU - Do the Arithmetic Logic Unit worked
		Calls the individual routines for each of the opcodes
		
		:param opcodeVector: The vector for the instruction.
		Vector is [opcodeNumber][regs_before][regs_after]
		"""
		debug_doALU = False
		if debug_doALU:
			print 'doALU: vector',opcodeVector
			print 'doALU: opcode =',opcodesList[opcodeVector[0]]
		if opcodeVector[0] == 'addr':
			self.INSTR_addr(opcodeVector)
		elif opcodeVector[0] == 'addi':
			self.INSTR_addi(opcodeVector)
		elif opcodeVector[0] == 'mulr':
			self.INSTR_mulr(opcodeVector)
		elif opcodeVector[0] == 'muli':
			self.INSTR_muli(opcodeVector)
		elif opcodeVector[0] == 'banr':
			self.INSTR_banr(opcodeVector)
		elif opcodeVector[0] == 'bani':
			self.INSTR_bani(opcodeVector)
		elif opcodeVector[0] == 'borr':
			self.INSTR_borr(opcodeVector)
		elif opcodeVector[0] == 'bori':
			self.INSTR_bori(opcodeVector)
		elif opcodeVector[0] == 'setr':
			self.INSTR_setr(opcodeVector)
		elif opcodeVector[0] == 'seti':
			self.INSTR_seti(opcodeVector)
		elif opcodeVector[0] == 'gtir':
			self.INSTR_gtir(opcodeVector)
		elif opcodeVector[0] == 'gtri':
			self.INSTR_gtri(opcodeVector)
		elif opcodeVector[0] == 'gtrr':
			self.INSTR_gtrr(opcodeVector)
		elif opcodeVector[0] == 'eqir':
			self.INSTR_eqir(opcodeVector)
		elif opcodeVector[0] == 'eqri':
			self.INSTR_eqri(opcodeVector)
		elif opcodeVector[0] == 'eqrr':
			self.INSTR_eqrr(opcodeVector)
		else:
			print 'doALU: opcode =',opcodeVector[0]
			abbyTerminate('doALU: passed bad opcode, exiting...')
		return

	def INSTR_addr(self,vector):	# (add register) stores into register C the result of adding register A and register B.
		aVal = self.getInputA(vector[1],'Register')
		bVal = self.getInputB(vector[2],'Register')
		cVal = aVal + bVal
		self.storeCVal(vector[3],cVal)

	def INSTR_addi(self,vector):
		"""# (add immediate) stores into register C the result of adding register A and value B.
		"""
		#print 'INSTR_addi: vector',vector
		aVal = self.getInputA(vector[1],'Register')
		#print 'INSTR_addi: aVal',aVal
		bVal = self.getInputB(vector[2],'Immediate')
		#print 'INSTR_addi: bVal',bVal
		cVal = aVal + bVal
		#print 'INSTR_addi: cVal',cVal
		self.storeCVal(vector[3],cVal)

	def INSTR_mulr(self,vector):
		"""(multiply register) stores into register C the result of multiplying register A and register B.
		"""
		#print 'INSTR_mulr: vector',vector
		aVal = self.getInputA(vector[1],'Register')
		bVal = self.getInputB(vector[2],'Register')
		cVal = aVal * bVal
		self.storeCVal(vector[3],cVal)

	def INSTR_muli(self,vector):	# (multiply immediate) stores into register C the result of multiplying register A and value B.
		aVal = self.getInputA(vector[1],'Register')
		bVal = self.getInputB(vector[2],'Immediate')
		cVal = aVal * bVal
		self.storeCVal(vector[3],cVal)

	def INSTR_banr(self,vector):	# (bitwise AND register) stores into register C the result of the bitwise AND of register A and register B.
		aVal = self.getInputA(vector[1],'Register')
		bVal = self.getInputB(vector[2],'Register')
		cVal = aVal & bVal
		self.storeCVal(vector[3],cVal)

	def INSTR_bani(self,vector):	# (bitwise AND immediate) stores into register C the result of the bitwise AND of register A and value B.
		aVal = self.getInputA(vector[1],'Register')
		bVal = self.getInputB(vector[2],'Immediate')
		cVal = aVal & bVal
		self.storeCVal(vector[3],cVal)

	def INSTR_borr(self,vector):	# (bitwise OR register) stores into register C the result of the bitwise OR of register A and register B.
		aVal = self.getInputA(vector[1],'Register')
		bVal = self.getInputB(vector[2],'Register')
		cVal = aVal | bVal
		self.storeCVal(vector[3],cVal)

	def INSTR_bori(self,vector):	# (bitwise OR immediate) stores into register C the result of the bitwise OR of register A and value B.
		aVal = self.getInputA(vector[1],'Register')
		bVal = self.getInputB(vector[2],'Immediate')
		cVal = aVal | bVal
		self.storeCVal(vector[3],cVal)

	def INSTR_setr(self,vector):	# (set register) copies the contents of register A into register C. (Input B is ignored.) 
		aVal = self.getInputA(vector[1],'Register')
		cVal = aVal
		self.storeCVal(vector[3],cVal)

	def INSTR_seti(self,vector):
		"""(set immediate) stores value A into register C. (Input B is ignored.)
		"""
		#print 'seti instruction decode'
		aVal = self.getInputA(vector[1],'Immediate')
		cVal = aVal
		self.storeCVal(vector[3],cVal)

	def INSTR_gtir(self,vector):	# (greater-than immediate/register) sets register C to 1 if value A is greater than register B. Otherwise, register C is set to 0.
		aVal = self.getInputA(vector[1],'Immediate')
		bVal = self.getInputB(vector[2],'Register')
		if aVal > bVal:
			cVal = 1
		else:
			cVal = 0
		self.storeCVal(vector[3],cVal)

	def INSTR_gtri(self,vector):	# gtri (greater-than register/immediate) sets register C to 1 if register A is greater than value B. Otherwise, register C is set to 0.
		aVal = self.getInputA(vector[1],'Register')
		bVal = self.getInputB(vector[2],'Immediate')
		if aVal > bVal:
			cVal = 1
		else:
			cVal = 0
		self.storeCVal(vector[3],cVal)

	def INSTR_gtrr(self,vector):	# gtrr (greater-than register/register) sets register C to 1 if register A is greater than register B. Otherwise, register C is set to 0.
		aVal = self.getInputA(vector[1],'Register')
		bVal = self.getInputB(vector[2],'Register')
		if aVal > bVal:
			cVal = 1
		else:
			cVal = 0
		self.storeCVal(vector[3],cVal)
		
	def INSTR_eqir(self,vector):	# (equal immediate/register) sets register C to 1 if value A is equal to register B. Otherwise, register C is set to 0.
		aVal = self.getInputA(vector[1],'Immediate')
		bVal = self.getInputB(vector[2],'Register')
		if aVal == bVal:
			cVal = 1
		else:
			cVal = 0
		self.storeCVal(vector[3],cVal)

	def INSTR_eqri(self,vector):	# (equal register/immediate) sets register C to 1 if register A is equal to value B. Otherwise, register C is set to 0.
		aVal = self.getInputA(vector[1],'Register')
		bVal = self.getInputB(vector[2],'Immediate')
		if aVal == bVal:
			cVal = 1
		else:
			cVal = 0
		self.storeCVal(vector[3],cVal)

	def INSTR_eqrr(self,vector):	# (equal register/register) sets register C to 1 if register A is equal to register B. Otherwise, register C is set to 0.
		aVal = self.getInputA(vector[1],'Register')
		bVal = self.getInputB(vector[2],'Register')
		if aVal == bVal:
			cVal = 1
		else:
			cVal = 0
		self.storeCVal(vector[3],cVal)
	
#########################################################################
## This is the workhorse of this assignment

opcodesList = ['eqri','bori','mulr','seti','banr','bani','borr','gtrr','gtir','addi','setr','eqrr','addr','eqir','gtri','muli',]

def convertOpcodeStringToVector(opcodeString):
	"""convertOpcodeStringToVector - Convert the string from the file into a list
	Two types of strings
	Instruction Pointer updates
	Opcode plus operands.
	
	:param opcodeString: Example - addi 1 16 1
	:returns: list of the instruction with the operand strings converted to ints
	"""
	debug_convertOpcodeStringToVector = False
	opcodeList = opcodeString.split()
	opcodeVector = [opcodeList[0],int(opcodeList[1]),int(opcodeList[2]),int(opcodeList[3])]
	if debug_convertOpcodeStringToVector:
		print 'convertOpcodeStringToVector: opcodeVector',opcodeVector
	if opcodeVector[0] not in opcodesList:
		abbyTerminate('convertOpcodeStringToVector: opcode not in the opcode list, exiting')
	return opcodeVector

instructionPointer = 0
instructionPointerRegisterNumber = 0

def loadProgramToList(textFileAsListOfLines,myCPU):
	"""Convert the text file into a list
	
	:param textFileAsListOfLines: the input file as a list of strings where each string is one line of the input file
	:param myCPU: - points to the CPU class
	"""
	programListing = []
	for line in textFileAsListOfLines:
		if len(line) == 0:				# skip blank lines
			continue
		elif line[0:4] == '#ip ':		# Bind the Instruction Counter to a particular register
			instructionPointerRegisterNumber = int(line[4])
		else:							# opcode case
			newOpCode = convertOpcodeStringToVector(line)
			programListing.append(newOpCode)
	print 'loadProgramToList: program is'
	for location in programListing:
		print location
	return programListing

def runTillDone(programCode,myCPU):
	while instructionPointer < len(programCode):
		vector = programCode[instructionPointer]
		myCPU.emulator(vector)
	return

########################################################################
## Code

print 'Reading in file',time.strftime('%X %x %Z')

textList = readtextFileAsListOfLinesToList('input2.txt')

myCPU = CPU()

programCode = loadProgramToList(textList,myCPU)
runTillDone(programCode,myCPU)

print 'Completed processing',time.strftime('%X %x %Z')

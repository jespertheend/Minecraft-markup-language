import mcrcon
import os
import sys
import math

rcon = mcrcon.MCRcon()
rcon.connect("localhost",25575)
rcon.login("yourPassword")

START_POS = (0,0,0)

def cmd(cmd):
	rcon.command(cmd)

	#use this if you want to use gnu screen for some reason

	# cmd = cmd.replace("'","'\"'\"'")
	# os.system("screen -S mc -X stuff '"+cmd+"'")
	# os.system("screen -S mc -X stuff '\r'")


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

def placeCmd(pos,command="",direction=(0,-1,0),t=0,conditional=False,needsRedstone=False):
	typeString = "command_block"
	if t == 1:
		typeString = "chain_"+typeString
	if t == 2:
		typeString = "repeating_"+typeString
	# if direction == 
	tupleDir = tuple(direction)
	blockData = 0
	if tupleDir == (0,-1,0):
		blockData = 0
	elif tupleDir == (0,1,0):
		blockData = 1
	elif tupleDir == (0,0,-1):
		blockData = 2
	elif tupleDir == (0,0,1):
		blockData = 3
	elif tupleDir == (-1,0,0):
		blockData = 4
	elif tupleDir == (1,0,0):
		blockData = 5
	if conditional:
		blockData += 8
	blockData = str(blockData)
	command = command.replace("\\","\\\\").replace("\"","\\\"")
	posString = posToString(pos)
	if t == 0:
		auto = "0"
	else:
		auto = "1"
	commandWithoutNBT = "setblock "+posString+" "+typeString+" "+blockData+" replace "
	placeCommand = commandWithoutNBT+"{Command:\""+command+"\",auto:"+auto+"b}"
	cmd(placeCommand)
	return commandWithoutNBT+"{Command:\""+command+"\",auto:1b}"

def posToString(pos):
	pos = tuple(pos)
	return str(pos[0])+" "+str(pos[1])+" "+str(pos[2])

inputPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),"input.mcm")
commands = None
with open(inputPath) as f:
	commands = f.readlines()

if commands is None:
	sys.exit("file doesn't exist!")

# strip trailing tabs and spaces
commands = [command.strip() for command in commands]

# remove empty lines
commands = filter(None, commands)

# make things starting with # work
prefixes = []
variables = {}

for i in range(len(commands)):
	command = commands[i]
	if command.startswith("#if"):
		selector = command[4:]
		prefixes.append(selector)
	elif command.startswith("#endif"):
		del prefixes[-1]
	elif command.startswith("#var"):
		splitCommand = command.split(" ",2)
		varName = splitCommand[1]
		varValue = splitCommand[2]
		variables[varName] = varValue
	else:
		# add variables
		for varName in variables:
			command = command.replace("$"+varName,variables[varName])
		# add if statements
		if len(prefixes) > 0:
			longPrefixes = []
			for prefix in prefixes:
				prefix = "execute "+prefix
				if prefix.endswith("]"):
					prefix = prefix+" ~ ~ ~"
				prefix = prefix+" "
				longPrefixes.append(prefix)
			prefixString = "".join(longPrefixes)
			# prefixString = "execute "+" ~ ~ ~ execute ".join(prefixes)+" ~ ~ ~ "
		else:
			prefixString = ""
		commands[i] = prefixString + command

functions = {}
currentFuncCommands = []
isAddingFuncCommands = False
firstFuncLine = len(commands)
lastFuncName = ""
for i in range(len(commands)):
	command = commands[i]
	if command.startswith("#func"):
		splitCommand = command.split(" ")
		lastFuncName = splitCommand[1]
		if not isAddingFuncCommands:
			isAddingFuncCommands = True
			firstFuncLine = i
	elif command.startswith("#endfunc"):
		functions[lastFuncName] = []
		functions[lastFuncName].extend(currentFuncCommands)
		currentFuncCommands = []
	elif isAddingFuncCommands:
		currentFuncCommands.append(command)

commands = commands[:firstFuncLine]

# remove lines starting with # or //
def removeHashAndSlash(l):
	return [command for command in l if not command.startswith(("#if","#endif","#var","#func","#endfunc","//"))]
commands = removeHashAndSlash(commands)
for function in functions:
	functions[function] = removeHashAndSlash(functions[function])

# make a new list of commands with the functions at the start
totalCommands = []
functionPositions = {}
for function in functions:
	functionPositions[function] = len(totalCommands)
	totalCommands.extend(functions[function])
mainLoopPosition = len(totalCommands)
totalCommands.extend(commands)

totalBlockCount = len(totalCommands)
cubeSize = int(math.ceil(totalBlockCount ** (1/3.0)))

#fill area with air
cmd("fill "+posToString(START_POS)+" "+posToString((START_POS[0]+cubeSize+20,START_POS[1]+cubeSize+20,START_POS[2]+cubeSize+20))+" air")

def getBlockType(index):
	if index == mainLoopPosition:
		return (2,None)
	for funcPos in functionPositions:
		if index == functionPositions[funcPos]:
			return (0,funcPos)
	return (1,None)

functionSetBlocks = {}
def loopedPlaceCommand():
	global commandIndex, x, y, z, direction
	blockTypeData = getBlockType(commandIndex)
	blockType = blockTypeData[0]
	command = totalCommands[commandIndex]
	# if the command contains a $function
	splitCommand = command.split(" ")
	if splitCommand[-1].startswith("$") and splitCommand[-1][1:] in functionSetBlocks:
		command = command.replace(splitCommand[-1],functionSetBlocks[splitCommand[-1][1:]])
	setBlockCommand = placeCmd((x,y,z),command,direction,blockType)
	if blockType == 0:
		functionSetBlocks[blockTypeData[1]] = setBlockCommand
	commandIndex += 1

curPos = list(START_POS)
yPositive = True
zPositive = True
commandIndex = 0
for z in range(START_POS[0], START_POS[0]+cubeSize):
	if yPositive:
		for y in range(START_POS[1], START_POS[1]+cubeSize):
			if zPositive:
				for x in range(START_POS[2], START_POS[2]+cubeSize):
					if commandIndex < len(totalCommands):
						if x == START_POS[2]+cubeSize-1:
							if y == START_POS[1]+cubeSize-1:
								direction = (0,0,1)
							else:
								direction = (0,1,0)
						else:
							direction = (1,0,0)
						loopedPlaceCommand()
			else:
				for x in range(START_POS[2]+cubeSize-1,START_POS[2]-1,-1):
					if commandIndex < len(totalCommands):
						if x == START_POS[2]:
							if y == START_POS[1]+cubeSize-1:
								direction = (0,0,1)
							else:
								direction = (0,1,0)
						else:
							direction = (-1,0,0)
						loopedPlaceCommand()
			zPositive = not zPositive
	else:
		for y in range(START_POS[1]+cubeSize-1, START_POS[1]-1, -1):
			if zPositive:
				for x in range(START_POS[2], START_POS[2]+cubeSize):
					if commandIndex < len(totalCommands):
						if x == START_POS[2]+cubeSize-1:
							if y == START_POS[1]:
								direction = (0,0,1)
							else:
								direction = (0,-1,0)
						else:
							direction = (1,0,0)
						loopedPlaceCommand()
			else:
				for x in range(START_POS[2]+cubeSize-1,START_POS[2]-1,-1):
					if commandIndex < len(totalCommands):
						if x == START_POS[2]:
							if y == START_POS[1]:
								direction = (0,0,1)
							else:
								direction = (0,-1,0)
						else:
							direction = (-1,0,0)
						loopedPlaceCommand()
			zPositive = not zPositive
	yPositive = not yPositive

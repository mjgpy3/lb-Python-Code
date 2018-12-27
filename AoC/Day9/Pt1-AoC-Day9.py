# Pt1-AoCDay9.py
# 2018 Advent of Code
# Day 9
# Part 1
# https://adventofcode.com/2018/day/9

import time
import os

"""

--- Day 9: Marble Mania ---
You talk to the Elves while you wait for your navigation system to initialize. To pass the time, they introduce you to their favorite marble game.

The Elves play this game by taking turns arranging the marbles in a circle according to very particular rules. The marbles are numbered starting with 0 and increasing by 1 until every marble has a number.

First, the marble numbered 0 is placed in the circle. At this point, while it contains only a single marble, it is still a circle: the marble is both clockwise from itself and counter-clockwise from itself. This marble is designated the current marble.

Then, each Elf takes a turn placing the lowest-numbered remaining marble into the circle between the marbles that are 1 and 2 marbles clockwise of the current marble. (When the circle is large enough, this means that there is one marble between the marble that was just placed and the current marble.) The marble that was just placed then becomes the current marble.

However, if the marble that is about to be placed has a number which is a multiple of 23, something entirely different happens. First, the current player keeps the marble they would have placed, adding it to their score. In addition, the marble 7 marbles counter-clockwise from the current marble is removed from the circle and also added to the current player's score. The marble located immediately clockwise of the marble that was removed becomes the new current marble.

For example, suppose there are 9 players. After the marble with value 0 is placed in the middle, each player (shown in square brackets) takes a turn. The result of each of those turns would produce circles of marbles like this, where clockwise is to the right and the resulting current marble is in parentheses:

[-] (0)
[1]  0 (1)
[2]  0 (2) 1 
[3]  0  2  1 (3)
[4]  0 (4) 2  1  3 
[5]  0  4  2 (5) 1  3 
[6]  0  4  2  5  1 (6) 3 
[7]  0  4  2  5  1  6  3 (7)
[8]  0 (8) 4  2  5  1  6  3  7 
[9]  0  8  4 (9) 2  5  1  6  3  7 
[1]  0  8  4  9  2(10) 5  1  6  3  7 
[2]  0  8  4  9  2 10  5(11) 1  6  3  7 
[3]  0  8  4  9  2 10  5 11  1(12) 6  3  7 
[4]  0  8  4  9  2 10  5 11  1 12  6(13) 3  7 
[5]  0  8  4  9  2 10  5 11  1 12  6 13  3(14) 7 
[6]  0  8  4  9  2 10  5 11  1 12  6 13  3 14  7(15)
[7]  0(16) 8  4  9  2 10  5 11  1 12  6 13  3 14  7 15 
[8]  0 16  8(17) 4  9  2 10  5 11  1 12  6 13  3 14  7 15 
[9]  0 16  8 17  4(18) 9  2 10  5 11  1 12  6 13  3 14  7 15 
[1]  0 16  8 17  4 18  9(19) 2 10  5 11  1 12  6 13  3 14  7 15 
[2]  0 16  8 17  4 18  9 19  2(20)10  5 11  1 12  6 13  3 14  7 15 
[3]  0 16  8 17  4 18  9 19  2 20 10(21) 5 11  1 12  6 13  3 14  7 15 
[4]  0 16  8 17  4 18  9 19  2 20 10 21  5(22)11  1 12  6 13  3 14  7 15 
[5]  0 16  8 17  4 18(19) 2 20 10 21  5 22 11  1 12  6 13  3 14  7 15 
[6]  0 16  8 17  4 18 19  2(24)20 10 21  5 22 11  1 12  6 13  3 14  7 15 
[7]  0 16  8 17  4 18 19  2 24 20(25)10 21  5 22 11  1 12  6 13  3 14  7 15
The goal is to be the player with the highest score after the last marble is used up. Assuming the example above ends after the marble numbered 25, the winning score is 23+9=32 (because player 5 kept marble 23 and removed marble 9, while no other player got any points in this very short example game).

Here are a few more examples:

10 players; last marble is worth 1618 points: high score is 8317
13 players; last marble is worth 7999 points: high score is 146373
17 players; last marble is worth 1104 points: high score is 2764
21 players; last marble is worth 6111 points: high score is 54718
30 players; last marble is worth 5807 points: high score is 37305
What is the winning Elf's score?

464 players; last marble is worth 71730 points

"""

#####################################################################################
## Functions which operate on the marbles list
## listOfMarbles is a linked list with links in both directions
## 	marble = [marbleNumber,marbleToLeft,marbleToRight,playerNumber]

class MarblesClass():
	"""The class that handles the marble lists
	
	"""
	## Class values
	endMarbleValue = 1618
	currentPlayerNumber = 0
	currentMarbleValue = 0
	currentMarbleNumber = 0
	listOfMarbles = []
	playersAndScores = []
	
	def initializePlayersAndScores(self,numberOfPlayers):
		"""Creates a list of player scores
		Player numbers go from 1 to the number of players.
		Player 0 is non-existent.
		"""
		debug_initializePlayersAndScores = True
		if debug_initializePlayersAndScores:
			print 'initializePlayersAndScores: Initializing the player scores'
		for player in xrange(numberOfPlayers+1):
			playerScore = [0]
			self.playersAndScores.append(playerScore)
		return player

	def incMarbleNumber(self):
		self.currentMarbleNumber += 1
		
	def getNextMarbleNumber(self):
		"""Return the marbleNumber
		
		:returns: nextMarbleNumber after the increment
		"""
		return self.currentMarbleNumber

	def addMarbleToList(self):
		"""Add another marble to the listOfMarbles
		listOfMarbles has elements [marbleNumber,marbleToLeft,marbleToRight,playerNumber]
		"""
		debug_addMarbleToList = True
		if debug_addMarbleToList:
			print 'addMarbleToList: reached function'
		currentPlayerNumber = self.getNextPlayerNumber()
		if self.listOfMarbles == []:	# empty list case
			if debug_addMarbleToList:
				print 'addMarbleToList: empty list case'
			self.listOfMarbles.append([self.currentMarbleNumber,self.currentMarbleNumber,self.currentMarbleNumber,currentPlayerNumber])
		else:
			if debug_addMarbleToList:
				print 'addMarbleToList: list has marbles already'
			self.insertMarbleIntoList(nextMarbleSpot)
			self.currentMarbleValue = [self.currentMarbleNumber,self.currentMarbleNumber,self.currentMarbleNumber,currentPlayerNumber]
		self.incNextPlayerNumber()
		return self.getNextMarbleNumber()
			
	def insertMarbleIntoList(self,nextMarbleSpot):
		"""
		
		:param nextMarbleSpot: Vector [marbleNumber,marbleToTheLeft,marbleToTheRight,playerNumber]
		"""
		debug_insertMarbleIntoList = True
		if debug_insertMarbleIntoList:
			print 'insertMarbleIntoList: nextMarbleSpot',nextMarbleSpot
		marbleOneAwayListEntry = self.listOfMarbles[self.currentMarbleNumber][2]	#Get the marble nodes for the two marbles to the right
		marbleTwoAwayListEntry = self.listOfMarbles[marbleOneAwayListEntry][2]
		if debug_insertMarbleIntoList:
			print 'insertMarbleIntoList: marble vector',nextMarbleSpot
		self.listOfMarbles.append(nextMarbleSpot)
		newMarbleNumber = self.incMarbleNumber()
		self.listOfMarbles[marbleTwoAwayListEntry][2] = newMarbleNumber
		self.listOfMarbles[marbleOneAwayListEntry][1] = newMarbleNumber
		self.listOfMarbles[newMarbleNumber][2] = marbleTwoAwayListEntry
		self.listOfMarbles[newMarbleNumber][1] = marbleOneAwayListEntry
		return

	def getNextPositionToInsertMarble(self):
		"""
		listOfMarbles has elements [marbleNumber,marbleToLeft,marbleToRight,playerNumber]
		Each Elf takes a turn placing the lowest-numbered remaining marble 
		into the circle between the marbles that are 1 and 2 marbles clockwise of the current 
		marble.
		However, if the marble that is about to be placed has a number 
		which is a multiple of 23, something entirely different happens. 
		First, the current player keeps the marble they would have placed, 
		adding it to their score. 
		:returns: pair of the offsets in the list to the next pair to insert 
		marble between
		"""
		debug_getNextPositionToInsertMarble = True
		if debug_getNextPositionToInsertMarble:
			print 'getNextPositionToInsertMarble: reached function'
		if self.getNextMarbleNumber() % 23 == 0:
			pass
		else:
			pass
		marbleToTheLeft = 0
		marbleToTheRight = 0
		return [marbleToTheLeft,marbleToTheRight]
		
	def getNextPlayerNumber(self):
		return self.currentPlayerNumber

	def incNextPlayerNumber(self):
		if self.currentPlayerNumber < numberOfPlayers - 1:
			self.currentPlayerNumber += 1
		else:
			self.currentPlayerNumber = 0
		return self.currentPlayerNumber

	def dumpMarblesList(self):
		return self.listOfMarbles
		
	def takeMarbleFromList(self):
		return

########################################################################
## Code

numberOfPlayers = 464
lastMarbleValue = 71730

debug_main = True

if debug_main:
	os.system('cls')
	print 'main: there are',numberOfPlayers,'players'
	print 'main: the last marble value will be',lastMarbleValue

Marbles = MarblesClass()	# Create the marbles class
Marbles.initializePlayersAndScores(numberOfPlayers)
Marbles.addMarbleToList()	# Add the first marble to the list

while True:
	if debug_main:
		print '\nmain: marbles list',Marbles.dumpMarblesList()
		print 'main: next marble number',Marbles.getNextMarbleNumber()
		print 'main: next player number',Marbles.getNextPlayerNumber()
		os.system('pause')
	Marbles.addMarbleToList()
	
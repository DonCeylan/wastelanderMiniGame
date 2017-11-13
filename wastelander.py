#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Ett spel där man ska ta sig från ena sidan av kartan till den andra. Man har begränsat med 
# energi/health och man förlorar energi för varje steg man tar. På vägen förlorar man 1 energienhet
# per steg och i öknen förlorar man 2. I öknen kan man dock hitta mat som ger en mer energi.
# Det kostar 1 energienhet att söka efter mat, men man kan få mycket energi tillbaka!
# Det finns även några träd där man garanterat hittar mat. Dock finns det en liten risk att
# maten från träden är giftig vilket gör att man förlorar extra energi.
# Målet är att nå andra sidan kartan, markerat med ett 'X' med så mycket energi (health) som möjligt!

# Written by Ciwan Ceylan November 2017
import random
import string

class Tile:
	''' The basic component of the game board. Has a type which determines the fatigue damage taken
		and the string representation. Tiles can contain food or not (food = None)'''
	def __init__(self, tileType, food = None):
		self.tileType = tileType
			# types: road_vertical, road_horizontal, corner, tree, ground
		self.food = food
		
	def fatigue(self):
		# 6 types of tiles
		if self.tileType == 'road_vertical':
			return -1
		elif self.tileType == 'road_horizontal':
			return -1
		elif self.tileType == 'corner':
			return -1
		elif self.tileType == 'tree':
			return -3
		elif self.tileType == 'ground':
			return -2
		elif self.tileType == 'goal':
			return 0
		else:
			return 0
	
	def __str__(self):
		# the string representation of each tile
		if self.tileType == 'road_vertical':
			return '| '
		elif self.tileType == 'road_horizontal':
			return '= '
		elif self.tileType == 'corner':
			return '# '
		elif self.tileType == 'tree':
			return '* '
		elif self.tileType == 'ground':
			return '. '
		elif self.tileType == 'goal':
			return 'X '
		else:
			return '? '

class Food:
	''' Food items have a name and a value. Value is negative for poisonous food.'''
	def __init__(self, foodName, value):
		self.name = foodName
		self.value = value
				
	def __str__(self):
		if value < 0:
			return "Poisonous " + self.name
		else:
			return self.name

class Player:
	''' The player class contains the players name, current health and current position '''
	def __init__(self, name, health, position = (0, 0)):
		self.name = name
		self.health = health
		self.position = position
	def __str__(self):
		return self.name[0] + ' ' # player representation on the game board
	

class GameBoard:
	'''Keeping track of the gameboard, the player score and  game over status'''

	def __init__(self, size):
		''' Set the basic stats for the game. Take size when game is created. '''
		self.treeRatio = 0.05 # 5 % of tiles are trees
		self.groundFoodRatio = 0.5 # 50 % for ground tiles contain food
		self.poisonousTreeFoodRatio = 0.1 # 10 % poisonous trees
		self.size = size
		self.player = None # player is created in runGame()
		self.makeBoard()
		# these are set inside makeBoard()
			# self.board = board
			# self.totalRoadSize = totalRoadSize
			# self.endTile = endTile
		
	def runGame(self):
		''' Runs the game. Loops until gameOver. Asks which action to take then executes action. '''
		playerName = input('What is your name? ')
		playerHealth = int(0.9 * self.totalRoadSize) # set stating health, 90 % of road length
		self.player = Player(playerName, playerHealth)
		# Print "story"
		print(self.player.name, 'is lost in the wastelands and must find a way home!')
		print('You have', self.player.health, 'food items, but the road is', self.totalRoadSize, 
		'steps long!\n')
		print(self.player.name, 'must find additional food by searching the wastes...\n')

		gameOver = False
		while not gameOver:
			print(self) # calls __str__ and prints the game board
			print(self.player.name, 'has', self.player.health, 'health left...')
			action = input('Choose an action: 1. Move \t 2. Search \t 3. Quit\n')
			
			if action == '1':
				dir, steps = self.getDirandSteps()
				self.movePlayer(dir, steps)
			elif action == '2':
				self.searchTile()
			elif action == '3':
				break
			else:
				print('-----------> Please choose a valid action!')
			# Check if game is over
			gameOver = self.player.health < 1 or self.player.position == self.endTile
			print(60 * '-' )
		if self.player.position == self.endTile:
			print(self.player.name + ' escapes the wastelands and returns home!')
		elif self.player.health < 1:
			print(self.player.name + ' dies in the wastelands...')
		else:
			print(self.player.name + ' wakes with a start! Phew, it was all just a dream!')
			
		score = int( 100 * self.player.health/playerHealth)
		print('Your final score is: ', score)
			
	def __str__(self):
		'''Get a string representation of the game board'''
		alphabet = string.ascii_uppercase + string.ascii_lowercase # Gets a string of the alphabet
		boardString = 3 *' ' # Adjust to that everything lines up
		
		for r in range(self.size):
			boardString += alphabet[r] + ' ' # Top row with letters
		boardString += '\n'
		for r in range(self.size):
			nr =  str(r) if r > 9 else ' ' + str(r) # First column with numbers
			boardString += nr + ' '
			for c in range(self.size):
				if not self.player is None and (r, c) == self.player.position:
					boardString += str(self.player) # Add the player icon on the correct position
				else:
					boardString += str(self.board[r][c]) # otherwise add tile icon
			boardString += '\n'
		return boardString
			
	def searchTile(self):
		''' Search the current location for food '''
		print(60 * '-' ) # prints a line
		pos = self.player.position
		food = self.board[pos[0]][pos[1]].food
		self.player.health += -1 # Loose 1 for searching
		if food is None:
			print(self.player.name, 'searches the area but finds nothing.')
			return
		print(self.player.name, 'searches the area and finds a ', food.name, '!')
		if food.value < 0:
			print('Oh no!', self.player.name, 'loses', -1*food.value, ' health!')
		else:
			print(self.player.name, 'gains', food.value, ' health!')

		self.player.health += food.value # gain health or take poison damage
		self.board[pos[0]][pos[1]].food = None # remove food
		
			
	def getDirandSteps(self):
		''' Get move input from player, direction and number of steps '''
		dirs = ['up', 'right', 'down', 'left']
		dir = ''
		while not dir.lower() in dirs: # make sure it is a valid direction
			dir = input('Choose a direction: ')
			
		while True:
			try:
				steps = int(input('Choose number of steps: '))
				print(60 * '-' )
				break
			except ValueError:
				print('Steps needs to be an integer!')
				continue
		return dir, steps
		
		
	def movePlayer(self, dir, steps):
		''' Move the player on the board and add fatigue damage '''
		# One step at a time to add fatigue damage
		for i in range(steps):
			oldPos = self.player.position
			if dir == 'up':
				newPos = (oldPos[0] - 1, oldPos[1])
			elif dir == 'right':
				newPos = (oldPos[0], oldPos[1] + 1)
			elif dir == 'down':
				newPos = (oldPos[0] + 1, oldPos[1])
			elif dir == 'left':
				newPos = (oldPos[0], oldPos[1] - 1)
			else:
				raise ValueError
			# Check so we dont move outside the map
			if (newPos[0] >= self.size or 
				newPos[1] >= self.size or
				newPos[0] < 0 or newPos[1] < 0):
				print(self.player.name, ' hits and invisible wall...')
				break
			# take fatigue damage
			self.player.health += self.board[oldPos[0]][oldPos[1]].fatigue()
			if self.player.health < 0:
				break
			# move player
			self.player.position = newPos
	
	def makeBoard(self):
		''' Sets up the board with all tiles one at the time. First generates the road. '''
		board = []
		roadTilesDict, totalRoadSize, endTile = self.makeRoadTiles() # 
		for r in range(self.size):
			row = []
			for c in range(self.size):
				if (r, c) in roadTilesDict:
					row.append(roadTilesDict[(r, c)]) # add the road tile from the dictionary
				elif random.random() < self.treeRatio:
					treeTile = self.makeTreeTile()
					row.append(treeTile)
				else:
					groundTile = self.makeGroundTile()
					row.append(groundTile)
			board.append(row)
		self.board = board
		self.totalRoadSize = totalRoadSize
		self.endTile = endTile

	def makeTreeTile(self):
		''' Make a tree tile with random content. Can contain poisonous food.'''
		if random.random() < self.poisonousTreeFoodRatio:
			value = random.randrange(-3, 0) # random value between -3 and -1
		else:
			value = random.randrange(7, 15) # random value between 7 and 14
		foodName = random.choice(['Berry', 'Fruit'])
		food = Food(foodName, value)
		treeTile = Tile('tree', food)
		return treeTile
	
	def makeGroundTile(self):
		''' Make a ground tile with random content'''
		foodName = random.choice(['Root', 'Mushroom'])
		if random.random() < self.groundFoodRatio:
			value = random.randrange(5, 11) # random value between 5 and 10
			food = Food(foodName, value)
			groundTile = Tile('ground', food)
		else:
			groundTile = Tile('ground')
		return groundTile
		
	def makeRoadTiles(self):
		'''Set up a road which does from top-left to 'other side' of the map '''
		roadTilesDict = dict() # Dict to store the RoadTiles
		# Set up starting point
		tilePoint = (0, 0)
		oldDir = 'down' if random.random() > 0.5 else 'right'
		if oldDir == 'down':
			roadTilesDict[tilePoint] = Tile('road_vertical') 
		else:
			roadTilesDict[tilePoint] = Tile('road_horizontal')
		# Create a random road one step at the time
		totalSize = 0 # Total size of the road. Needed to set the stating health
		# While not reached the other side of the map
		while tilePoint[0] + 1 < self.size and tilePoint[1] + 1 < self.size:
			newDir = 'down' if random.random() > 0.5 else 'right' # Move down or right
			if oldDir == 'down':
				tilePoint = (tilePoint[0] + 1, tilePoint[1])
			else:
				tilePoint = (tilePoint[0], tilePoint[1] + 1)
			if (newDir == 'down' and oldDir == 'down'):
				roadTilesDict[tilePoint] = Tile('road_vertical')
			elif newDir == 'right' and oldDir == 'right':
				roadTilesDict[tilePoint] = Tile('road_horizontal')
			else:
				roadTilesDict[tilePoint] = Tile('corner')
			oldDir = newDir
			totalSize += 1
		roadTilesDict[tilePoint] = Tile('goal') # Set last road tile to goal
		return roadTilesDict, totalSize, tilePoint # Return the location of the goal


if __name__ == '__main__':
	game = GameBoard(15)
	game.runGame()
	
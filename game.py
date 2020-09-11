import pygame, sys, os, time
import data.engine as e
from pygame.locals import *
from settings import *

class Player:
	def __init__(self):
		self.entity = e.entity(50,200,14,29,'player')
		self.movingRight = False
		self.movingLeft = False
		self.momentum = 0
		self.airTimer = 0
		self.movement = [0,0]
		self.platformCollision = False
		self.onPlatform = False
		self.through = False

	def events(self, event, dt):
		if event.type == KEYDOWN:
			if event.key == K_RIGHT:
				self.movingRight = True
			elif event.key == K_LEFT:
				self.movingLeft = True
			elif event.key == K_UP:
				if self.airTimer == 0:
					self.momentum = -5
			elif event.key == K_DOWN:
				if self.onPlatform:
					self.through = True
		if event.type == KEYUP:
			if event.key == K_RIGHT:
				self.movingRight = False
			elif event.key == K_LEFT:
				self.movingLeft = False

	def update(self, tile_rects, enemiesList, movingList, vertRects, screen, scroll, dt, distance):
		#self.tile_rects, self.enemiesList, self.movingList, [], self.screen, self.scroll, dt, distance
		self.movement = [0,0]
		if self.movingRight == True:
			self.movement[0] += 300 * dt
		if self.movingLeft == True:
			self.movement[0] -= 300 * dt
		self.movement[1] += self.momentum*2.4
		self.momentum += 20 * dt
		if self.momentum > 5:
			self.momentum = 5

		if self.movement[0] == 0:
			self.entity.set_action('idle')
		elif self.movement[0] > 0:
			self.entity.set_flip(False)
			self.entity.set_action('run')
		elif self.movement[0] < 0:
			self.entity.set_flip(True)
			self.entity.set_action('run')

		collision_types = self.entity.move(self.movement, tile_rects, enemiesList, movingList, vertRects)

		for platform in collision_types['data']:
			if platform[1][3]:
				self.airTimer = 0
				self.momentum = 0
				self.platformCollision = False
			else:
				self.airTimer = 0
				self.platformCollision = False
			if platform[2] == 'horizontal':
				self.entity.obj.x += distance
			if platform[2] == "static":
				self.onPlatform = True
			else:
				self.onPlatform = False
			#print(platform[2])
			if platform[2] == "spikeTop":
				return True

		if not collision_types['bottom']:
			self.airTimer += 1

		self.entity.change_frame(1)
		self.entity.display(screen, scroll)

class MovingPlatform:
	def __init__(self, screen, x, y, type, maxAxis, speed):
		self.entity = e.entity(x, y, 64, 32, 'platform')
		self.type = type
		self.movement = [x,y]
		if self.type == "horizontal":
			self.maxAxis = x + maxAxis
			self.minAxis = x - maxAxis
		else:
			self.maxAxis = y + maxAxis
			self.minAxis = y - maxAxis
		self.forward = True
		self.speed = speed
		self.screen = screen

	def update(self, scroll):
		distance = 0
		if self.type == "horizontal":
			if self.movement[0] >= self.maxAxis or self.movement[0] <= self.minAxis:
				self.forward = not self.forward
			if self.forward:
				self.movement[0] += self.speed
				distance = self.speed
			else:
				self.movement[0] -= self.speed
				distance = - self.speed
		else:
			if self.movement[1] >= self.maxAxis or self.movement[1] <= self.minAxis:
				self.forward = not self.forward
			if self.forward:
				self.movement[1] += self.speed
			else:
				self.movement[1] -= self.speed
		if self.entity.obj.x <= 0:
			self.entity.obj.x = 0
		self.entity.set_pos(self.movement[0], self.movement[1])
		self.entity.change_frame(1)
		self.entity.display(self.screen, scroll)
		return distance

class StaticPlatform:
	def __init__(self, screen, x, y):
		self.entity = e.entity(x, y, 64, 32, 'static')
		self.type = "static"
		self.entity.obj.x = x
		self.entity.obj.y = y
		self.screen = screen

	def update(self, scroll):
		self.entity.change_frame(1)
		self.entity.display(self.screen, scroll)

		return MOVING_SPEED

class Spike:
	def __init__(self, screen, x, y, type):
		self.entity = e.entity(x, y, 32, 16, type)
		self.screen = screen
		self.type = type
		self.entity.obj.x = x
		self.entity.obj.y = y

	def update(self, scroll):
		self.entity.change_frame(1)
		self.entity.display(self.screen, scroll)

class ThroughPlat:
	def __init__(self, screen, x, y, type):
		self.entity = e.entity(x, y, 32, 16, type)
		self.screen = screen
		self.type = type
		self.entity.obj.x = x
		self.entity.obj.y = y

	def update(self, scroll):
		self.entity.change_frame(1)
		self.entity.display(self.screen, scroll)

class EndBall:
	def __init__(self, screen, x, y, type):
		self.entity = e.entity(x, y, 0, 0, type)
		self.screen = screen
		self.type = type
		self.entity.obj.x = x
		self.entity.obj.y = y

	def update(self):
		self.entity.change_frame(1)
		self.entity.display(self.screen, scroll)

class Level01:
	def __init__(self, screen):
		self.screen = screen

		self.layer00 = e.loadImage('data/images/background30.png', alpha=True)
		self.layer01 = e.loadImage('data/images/background31.png', alpha=True)
		self.layer02 = e.loadImage('data/images/background32.png', alpha=True)
		self.layerList = [self.layer00, self.layer01, self.layer02]

		self.leftPlat = e.loadImage('data/images/plat07.png')
		self.rightPlat = e.loadImage('data/images/plat10.png')
		self.middlePlat00 = e.loadImage('data/images/plat08.png')
		self.middlePlat01 = e.loadImage('data/images/plat09.png')
		self.middlePlat02 = e.loadImage('data/images/plat06.png')
		self.middlePlat03 = e.loadImage('data/images/plat11.png', alpha=True)

		self.cornerPlat00 = e.loadImage('data/images/plat24.png', alpha=True)
		self.cornerPlat01 = e.loadImage('data/images/plat25.png', alpha=True)

		self.barrelBottom = e.loadImage('data/images/deco04.png', alpha=True)
		self.barrelTop = e.loadImage('data/images/deco03.png', alpha=True)
		self.cable00 = e.loadImage('data/images/deco00.png', alpha=True)
		self.cable01 = e.loadImage('data/images/deco01.png', alpha=True)
		self.cable02 = e.loadImage('data/images/deco02.png', alpha=True)
		self.chainBottom = e.loadImage('data/images/chainBottom.png', alpha=True)
		self.chain = e.loadImage('data/images/chain.png', alpha=True)

		self.spikes = e.loadImage('data/images/chainBottom.png', alpha=True)

		self.static = e.loadImage('data/images/plat12.png', alpha=True)
		self.gameMap = e.load_map('map01')
		self.player = Player()
		self.movingList = []
		self.enemiesList = []
		self.trueScroll = [0, 0]
		self.create = True

	def draw(self, dt):
		self.screen.fill(BEIGE)

		self.trueScroll[0] += (self.player.entity.x -
							   self.trueScroll[0] - (WIDTH/2))/20
		self.trueScroll[1] += (self.player.entity.y -
							   self.trueScroll[1] - (HEIGHT/2))/20

		self.scroll = self.trueScroll.copy()
		self.scroll[0] = int(self.scroll[0])
		self.scroll[1] = int(self.scroll[1])

		i = 0
		for layer in self.layerList:
			self.screen.blit(layer, (-100 - self.scroll[0]*FAST_SPEED[i],
									 -150 - (self.scroll[1] / 1)*FAST_SPEED[i]))
			i += 1

		self.tile_rects = []
		self.jumpRects = []
		self.platRects = []

		y = 0
		for layer in self.gameMap:
			x = 0
			for tile in layer:
				if x >= 0 and x <= WIDTH and y >= 0 and y <= HEIGHT:
					if self.create:
						if tile == '1':
							plat = StaticPlatform(self.screen, x*TILE_SIZE, y*TILE_SIZE)
							self.movingList.append(plat)
						elif tile == '2':
							plat = MovingPlatform(self.screen,
												  x * TILE_SIZE, y * TILE_SIZE,
												  "vertical", 90, 3)
							self.movingList.append(plat)
						elif tile == '3':
							plat = MovingPlatform(self.screen,
												  x * TILE_SIZE, y * TILE_SIZE,
												  "horizontal", 90, 3.5)
							self.movingList.append(plat)
						elif tile == 'b':
							enemy = Spike(self.screen,
										  x * TILE_SIZE, y * TILE_SIZE + 16,
										  "spikeTop")
							self.enemiesList.append(enemy)
						elif tile == 'k':
							plat = ThroughPlat(self.screen, x*TILE_SIZE, y*TILE_SIZE, 'throughMiddle')
							self.movingList.append(plat)
						elif tile == 'l':
							plat = ThroughPlat(self.screen, x*TILE_SIZE, y*TILE_SIZE, 'throughLeft')
							self.movingList.append(plat)
						elif tile == 'm':
							plat = ThroughPlat(self.screen, x*TILE_SIZE, y*TILE_SIZE, 'throughRight')
							self.movingList.append(plat)
					elif tile == '7':
						e.displayTile(self.middlePlat02, self.screen, self.scroll, x, y)
					elif tile == '4':
						e.displayTile(self.leftPlat, self.screen, self.scroll, x, y)
					elif tile == '5':
						e.displayTile(self.middlePlat00, self.screen, self.scroll, x, y)
					elif tile == '6':
						e.displayTile(self.middlePlat01, self.screen, self.scroll, x, y)
					elif tile == '8':
						e.displayTile(self.rightPlat, self.screen, self.scroll, x, y)
					elif tile == '9':
						e.displayTile(self.cornerPlat00, self.screen, self.scroll, x, y)
					elif tile == 'a':
						e.displayTile(self.cornerPlat01, self.screen, self.scroll, x, y)
					elif tile == 'c':
						e.displayTile(self.barrelBottom, self.screen, self.scroll, x, y)
					elif tile == 'd':
						e.displayTile(self.barrelTop, self.screen, self.scroll, x, y)
					elif tile == 'e':
						e.displayTile(self.chain, self.screen, self.scroll, x, y)
					elif tile == 'f':
						e.displayTile(self.chainBottom, self.screen, self.scroll, x, y)
					elif tile == 'g':
						e.displayTile(self.cable00, self.screen, self.scroll, x, y)
					elif tile == 'h':
						e.displayTile(self.cable01, self.screen, self.scroll, x, y)
					elif tile == 'i':
						e.displayTile(self.cable02, self.screen, self.scroll, x, y)
					elif tile == 'j':
						e.displayTile(self.middlePlat03, self.screen, self.scroll, x, y)
					if tile not in ['0', '1', '2', '3', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l', 'm']:
						self.tile_rects.append(pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
				x += 1
			y += 1
		self.create = False

	def events(self, event, dt):
		self.player.events(event, dt)

	def update(self, dt):
		distance = 0
		for platform in self.movingList:
			distance = platform.update(self.scroll)
		# for enemy in self.enemiesList:
		# 	enemy.update(self.scroll)
		if self.player.update(self.tile_rects, self.enemiesList, self.movingList, [], self.screen, self.scroll, dt, distance):
			# self.restart()
			pass
		return [self.player.entity.obj.x, self.player.entity.obj.y], self.player.airTimer, self.player.momentum, self.scroll

	def restart(self):
		self.player = Player()

	def restartVariables(self, pos):
		self.player.movingRight = False
		self.player.movingLeft = False
		self.player.momentum = 0
		self.player.airTimer = 0
		self.player.movement = [0,0]
		self.player.entity.set_pos(pos[0], pos[1])

class Game:
	def __init__(self, screen, clock, smallFont, largeFont):
		e.load_animations('data/images/entities/')
		self.screen = screen
		self.clock = clock
		self.smallFont = smallFont
		self.largeFont = largeFont
		self.pause = Pause(self.screen)
		self.levelList = [Level01(self.screen),
						  ]
		self.level01 = Level01(self.screen)
		self.running = True
		self.isPaused = False
		self.fullscreen = False
		self.restart = False
		self.levelIndex = 0
		self.screen.set_alpha(None)

		self.startTime: int = 0
		self.inverseFPS: float = 1 / FPS
		self.dt: float = self.inverseFPS
		self.timeElapsed: int = 0
		self.delay: float = 1000 / FPS
		self.currentFPS: int = FPS
		self.fpsCounter: list = [0, 0]

	def start(self, showFPS):
		self.showFPS = showFPS
		while self.running:
			self.startTime: int = pygame.time.get_ticks()
			self.fpsCounter[0] += self.timeElapsed
			self.fpsCounter[1] += self.delay
			if self.fpsCounter[1] >= 1000:
				if self.fpsCounter[0] > 0:
					self.currentFPS = str(int((self.fpsCounter[1] / self.fpsCounter[0]) * FPS))
				else:
					self.currentFPS = "MAX"
				self.fpsCounter = [0, 0]
			self.draw()
			self.events()
			pygame.event.pump()
			self.update()
			self.timeElapsed = pygame.time.get_ticks() - self.startTime
			self.dt = max(self.inverseFPS, self.timeElapsed / 1000)
			pygame.time.delay(max(0, int(self.delay - self.timeElapsed)))

	def draw(self):
		self.level01.draw(self.dt)

	def events(self):
		self.running = e.checkCloseButtons()

		for event in pygame.event.get():
			self.level01.events(event, self.dt)
			self.running, self.fullscreen, self.screen = e.checkEvents(event, self.running, self.fullscreen, self.screen)
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					self.isPaused = not self.isPaused
				if event.key == K_RETURN:
					self.restart = True

	def update(self):
		movement, airTimer, momentum, scroll = self.level01.update(self.dt)
		if self.isPaused:
			pos = [self.level01.player.entity.x, self.level01.player.entity.y]
			self.level01.restartVariables(pos)
			screenshot = self.screen.copy()
			self.pause.start(screenshot)
			self.isPaused = not self.isPaused
		if self.restart:
			self.level01.restart()
			self.restart = False
		if movement[1] >= 1200:
			self.restart = True

		if self.showFPS :
			self.smallFont.render(self.screen, str(self.currentFPS), (WIDTH - 40, 20), RED)
		self.smallFont.render(self.screen, "movement: " + str(int(movement[0])) + ", " +
									str(int(movement[1])), (20, 20), WHITE)
		self.smallFont.render(self.screen, "air timer: " + str(airTimer), (20, 40), WHITE)
		self.smallFont.render(self.screen, "momentum: " + str(int(momentum)), (20, 60), WHITE)
		self.smallFont.render(self.screen, "scroll: " + str(int(scroll[0])) + ", " +
									str(int(scroll[1])), (20, 80), WHITE)

		pygame.display.update()

class Video:
	def __init__(self, screen, clock, smallFont, largeFont):
		self.clock = clock
		self.screen = screen
		self.smallFont = smallFont
		self.largeFont = largeFont
		self.showFPS = True
		self.fullscreen = False
		self.background = e.entity(0, 0, 640, 480, 'background')
		self.button = pygame.image.load('data/images/button.png').convert_alpha()
		self.selectedButton = pygame.image.load('data/images/buttonPressed.png').convert_alpha()
		self.stateList = [True, False, False]
		self.buttonList = ['Fullscreen', 'Show FPS', 'Back']
		self.descriptions = [['Yes', 'No'], ['Yes', 'No'], 'Go back to Options']

	def start(self, showFPS):
		self.showFPS = showFPS
		self.running = True
		while self.running:
			self.start_time = time.time()
			self.draw()
			self.events()
			self.update()

	def draw(self):
		self.background.display(self.screen, [0, 0])
		self.background.change_frame(1)

		self.largeFont.render(self.screen, 'Video', (20, 55), WHITE)

	def events(self):
		self.running = e.checkCloseButtons()
		index = self.stateList.index(True)
		for event in pygame.event.get():
			self.running, self.fullscreen, self.screen = e.checkEvents(event, self.running, self.fullscreen, self.screen)
			if event.type == KEYDOWN:
				if event.key == K_RETURN:
					if index == 0:
						self.fullscreen = e.fullscreenToggle(self.fullscreen, self.screen)
					elif index == 1:
						self.showFPS = not self.showFPS
					elif index == 2:
						self.running = False
				elif event.key == K_DOWN:
					if index < len(self.stateList) - 1:
						self.stateList[index] = False
						self.stateList[index + 1] = True
				elif event.key == K_UP:
					if index != 0:
						self.stateList[index] = False
						self.stateList[index - 1] = True

	def update(self):
		y = 180
		i = 0
		for state in self.stateList:
			if state:
				self.screen.blit(self.selectedButton, (40, y))
				description = None
				if i == 0:
					if self.fullscreen:
						description = self.descriptions[i][0]
					else:
						description = self.descriptions[i][1]
				elif i == 1:
					if self.showFPS:
						description = self.descriptions[i][0]
					else:
						description = self.descriptions[i][1]
				else:
					description = self.descriptions[i]
				self.smallFont.render(self.screen, description,
									  (200, y + 12), WHITE)
			else:
				self.screen.blit(self.button, (40, y))
			self.smallFont.render(self.screen, self.buttonList[i],
								  (65, y + 12), WHITE)
			y += 43
			i += 1
		if self.showFPS:
			fps = str(int(1.0 / (time.time() - self.start_time)))
			self.smallFont.render(self.screen, fps, (WIDTH - 40, 20))
		pygame.display.update()
		self.clock.tick(FPS)

class Options:
	def __init__(self, screen, clock, smallFont, largeFont):
		self.clock = clock
		self.screen = screen
		self.smallFont = smallFont
		self.largeFont = largeFont
		self.background = e.entity(0, 0, 640, 480, 'background')
		self.video = Video(self.screen, self.clock, self.smallFont, self.largeFont)
		self.button = pygame.image.load('data/images/button.png').convert_alpha()
		self.selectedButton = pygame.image.load('data/images/buttonPressed.png').convert_alpha()
		self.stateList = [True, False, False]
		self.buttonList = ['Video', 'Controls', 'Back']
		self.descriptions = ['Video options',
							 'See controls in game',
							 'Go back to Main Menu']
		self.fullscreen = False
		self.showFPS = True

	def start(self, showFPS):
		self.showFPS = showFPS
		self.running = True
		while self.running:
			self.start_time = time.time()
			self.draw()
			self.events()
			self.update()

	def draw(self):
		self.background.display(self.screen, [0, 0])
		self.background.change_frame(1)

		self.largeFont.render(self.screen, 'Options', (20, 55), WHITE)

	def events(self):
		self.running = e.checkCloseButtons()
		index = self.stateList.index(True)
		for event in pygame.event.get():
			self.running, self.fullscreen, self.screen = e.checkEvents(event, self.running, self.fullscreen, self.screen)
			if event.type == KEYDOWN:
				if event.key == K_RETURN:
					if index == 0:
						self.video.start(self.showFPS)
					elif index == 1:
						pass
					elif index == 2:
						self.running = False
				if event.key == K_DOWN:
					if index < len(self.stateList) - 1:
						self.stateList[index] = False
						self.stateList[index + 1] = True
				if event.key == K_UP:
					if index != 0:
						self.stateList[index] = False
						self.stateList[index - 1] = True
	def update(self):
		y = 180
		i = 0
		for state in self.stateList:
			if state:
				self.screen.blit(self.selectedButton, (40, y))
				self.smallFont.render(self.screen, self.descriptions[i],
									  (200, y + 12), WHITE)
			else:
				self.screen.blit(self.button, (40, y))
			self.smallFont.render(self.screen, self.buttonList[i],
								  (65, y + 12), WHITE)
			y += 43
			i += 1
		self.showFPS = self.video.showFPS
		if self.showFPS:
			fps = str(int(1.0 / (time.time() - self.start_time)))
			self.smallFont.render(self.screen, fps, (WIDTH - 40, 20))
		pygame.display.update()
		self.clock.tick(FPS)

class MainMenu:
	def __init__(self, screen, game, smallFont, largeFont, clock):
		self.screen = screen
		self.clock = clock
		self.game = game
		self.smallFont = smallFont
		self.largeFont = largeFont
		self.background = e.entity(0, 0, 640, 480, 'background')
		self.options = Options(self.screen, self.clock, self.smallFont, self.largeFont)
		self.button = pygame.image.load('data/images/button.png').convert_alpha()
		self.selectedButton = pygame.image.load('data/images/buttonPressed.png').convert_alpha()
		self.stateList = [True, False, False, False]
		self.buttonList = ['Start', 'Options', 'About', 'Quit']
		self.descriptions = ['Start a new game',
							 'Explore game options',
							 'About this game',
							 'Exit to desktop']
		self.showFPS = True

	def draw(self):
		self.start_time = time.time()
		self.background.display(self.screen, [0, 0])
		self.background.change_frame(1)

		self.largeFont.render(self.screen, 'Main Menu', (20, 55), WHITE)

	def events(self, event):
		index = self.stateList.index(True)
		if event.type == KEYDOWN:
			if event.key == K_RETURN:
				if index == 0:
					self.game.start(self.showFPS)
				elif index == 1:
					self.options.start(self.showFPS)
				elif index == 2:
					pass
				else:
					return False
			if event.key == K_DOWN:
				if index < len(self.stateList) - 1:
					self.stateList[index] = False
					self.stateList[index + 1] = True
			if event.key == K_UP:
				if index != 0:
					self.stateList[index] = False
					self.stateList[index - 1] = True
		return True

	def update(self):
		y = 180
		i = 0
		for state in self.stateList:
			if state:
				self.screen.blit(self.selectedButton, (40, y))
				self.smallFont.render(self.screen, self.descriptions[i],
									  (200, y + 14), WHITE)
				self.smallFont.render(self.screen, self.buttonList[i],
								     (65, y + 14), WHITE)
			else:
				self.screen.blit(self.button, (40, y))
				self.smallFont.render(self.screen, self.buttonList[i],
								     (65, y + 10), WHITE)
			y += 43
			i += 1
		#fps = str(int(1.0 / (time.time() - self.start_time)))
		self.showFPS = self.options.showFPS
		if self.showFPS:
			fps = str(int(self.clock.get_fps()))
			self.smallFont.render(self.screen, fps, (WIDTH - 40, 20))

class Pause:
	def __init__(self, screen):
		self.screen = screen
		self.background = pygame.image.load('data/images/pauseBackground.png').convert_alpha()
		self.fullscreen = False

	def start(self, screenshot):
		self.running = True
		screenshot = e.blurSurf(screenshot, 4.5)
		while self.running:
			self.draw(screenshot)
			self.events()
			self.update()

	def draw(self, screenshot):
		self.screen.blit(screenshot, (0, 0))
		self.screen.blit(self.background, (0, 0))

	def events(self):
		self.running = e.checkCloseButtons()

		for event in pygame.event.get():
			self.running, self.fullscreen, self.screen = e.checkEvents(event, self.running, self.fullscreen, self.screen)
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					self.running = False

	def update(self):
		pygame.display.update()

class Core:
	def __init__(self):
		pygame.init()
		pygame.mixer.pre_init(44100, -16, 2, 512)
		pygame.mixer.set_num_channels(64)
		pygame.display.set_caption('game')
		self.screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
		self.clock = pygame.time.Clock()
		pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])
		self.fullscreen = False
		self.running = True

	def new(self):
		self.smallFont = e.Font('data/images/small_font2.png')
		self.largeFont = e.Font('data/images/large_font.png')
		self.game = Game(self.screen, self.clock, self.smallFont, self.largeFont)
		self.menu = MainMenu(self.screen, self.game, self.smallFont, self.largeFont, self.clock)
		self.run()

	def run(self):
		self.running = True
		while self.running:
			self.draw()
			self.events()
			self.update()

	def draw(self):
		self.menu.draw()

	def events(self):
		self.running = e.checkCloseButtons()

		for event in pygame.event.get():
			self.running = self.menu.events(event)
			self.running, self.fullscreen, self.screen = e.checkEvents(event, self.running, self.fullscreen, self.screen)

	def update(self):
		self.menu.update()
		pygame.display.update()
		self.clock.tick(FPS)

c = Core()
while c.running:
	c.new()
pygame.quit()

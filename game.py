import pygame, sys, os, time, numpy
import data.engine as e
from pygame.locals import *
from settings import *

class Player:
    def __init__(self, x, y):
        self.entity = e.entity(x, y, 14, 29, 'player')
        self.movingRight = False
        self.movingLeft = False
        self.momentum = 0
        self.airTimer = 0
        self.movement = [0,0]
        self.platformCollision = False
        self.onPlatform = False
        self.through = False
        self.levelOver = False

    def events(self, event, dt):
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                self.movingRight = True
            if event.key == K_d:
                self.movingRight = True
            if event.key == K_LEFT:
                self.movingLeft = True
            if event.key == K_a:
                self.movingLeft = True
            if event.key == K_UP:
                if self.airTimer == 0:
                    self.momentum = -5
            if event.key == K_w:
                if self.airTimer == 0:
                    self.momentum = -5
            if event.key == K_DOWN:
                self.through = not self.through
            if event.key == K_s:
                self.through = not self.through

        if event.type == KEYUP:
            if event.key == K_RIGHT:
                self.movingRight = False
            if event.key == K_d:
                self.movingRight = False
            if event.key == K_LEFT:
                self.movingLeft = False
            if event.key == K_a:
                self.movingLeft = False

    def update(self, tile_rects, enemiesList, movingList, notCollisionable, screen, scroll, dt, distance):
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

        collisionList = self.entity.move(self.movement, tile_rects, enemiesList, movingList, notCollisionable, self.airTimer)

        exitData = [False, False]

        for platform in collisionList['data']:
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
            if platform[2] == 'throughMiddle':
                if self.through:
                    #HERE IS WHERE I DONT KNOW WHAT TO DO
                    pass
            else:
                self.onPlatform = False
            if platform[2] == "spikeTop":
                exitData[0] = True
            if platform[2] == "endBall":
                self.levelOver = True
                exitData[1] = True

        if not collisionList['bottom']:
            self.airTimer += 1

        self.entity.changeFrame(1)
        self.entity.display(screen, scroll)
        return exitData

class MapObject:
    def __init__(self, screen, x, y, xSize, ySize, type):
        self.entity = e.entity(x, y, xSize, ySize, type)
        self.screen = screen
        self.type = type

    def update(self, scroll):
        self.entity.changeFrame(1)
        self.entity.display(self.screen, scroll)

class MovingPlatform(MapObject):
    def __init__(self, screen, x, y, xSize, ySize, type, maxAxis, speed):
        super().__init__(screen, x, y, xSize, ySize, type)
        self.movement = [x,y]
        self.forward = True
        self.speed = speed
        if self.type == "horizontal":
            self.maxAxis = x + maxAxis
            self.minAxis = x - maxAxis
        else:
            self.maxAxis = y + maxAxis
            self.minAxis = y - maxAxis

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
        self.entity.changeFrame(1)
        self.entity.display(self.screen, scroll)

        return distance

class StaticPlatform(MapObject):
    def __init__(self, screen, x, y, xSize, ySize, type):
        super().__init__(screen, x, y, xSize, ySize, type)
        self.entity.obj.x = x
        self.entity.obj.y = y

    def update(self, scroll):
        self.entity.changeFrame(1)
        self.entity.display(self.screen, scroll)

        return MOVING_SPEED

class MapLevel:
    def __init__(self, screen, x, y, map):
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

        self.barrelBottom = e.loadImage('data/images/barrelBottom.png', alpha=True)
        self.barrelTop = e.loadImage('data/images/barrelTop.png', alpha=True)
        self.cable00 = e.loadImage('data/images/deco00.png', alpha=True)
        self.cable01 = e.loadImage('data/images/deco01.png', alpha=True)
        self.cable02 = e.loadImage('data/images/deco02.png', alpha=True)
        self.chainBottom = e.loadImage('data/images/chainBottom.png', alpha=True)
        self.chain = e.loadImage('data/images/chain.png', alpha=True)

        self.spikes = e.loadImage('data/images/chainBottom.png', alpha=True)

        self.static = e.loadImage('data/images/plat12.png', alpha=True)
        self.gameMap = e.load_map('data/' + map)
        self.player = Player(x, y)
        self.playerX = x
        self.playerY = y
        self.movingList = []
        self.enemiesList = []
        self.notCollisionable = []
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
                            plat = StaticPlatform(self.screen, x*TILE_SIZE, y*TILE_SIZE, 64, 32, 'static')
                            self.movingList.append(plat)
                        elif tile == '2':
                            plat = MovingPlatform(self.screen, x * TILE_SIZE, y * TILE_SIZE, 64, 32, 'vertical', 90, 3)
                            self.movingList.append(plat)
                        elif tile == '3':
                            plat = MovingPlatform(self.screen, x * TILE_SIZE, y * TILE_SIZE, 64, 32, 'horizontal', 90, 3.5)
                            self.movingList.append(plat)
                        elif tile == 'b':
                            enemy = MapObject(self.screen, x * TILE_SIZE, y * TILE_SIZE + 16, 32, 16, 'spikeTop')
                            self.enemiesList.append(enemy)
                        elif tile == 'k':
                            plat = MapObject(self.screen, x*TILE_SIZE, y*TILE_SIZE, 32, 16, 'throughMiddle')
                            self.movingList.append(plat)
                        elif tile == 'l':
                            plat = MapObject(self.screen, x*TILE_SIZE, y*TILE_SIZE, 32, 16, 'throughLeft')
                            self.movingList.append(plat)
                        elif tile == 'm':
                            plat = MapObject(self.screen, x*TILE_SIZE, y*TILE_SIZE, 32, 16, 'throughRight')
                            self.movingList.append(plat)
                        elif tile == 'n':
                            plat = MapObject(self.screen, x*TILE_SIZE, y*TILE_SIZE, 32, 32, 'endBall')
                            self.notCollisionable.append(plat)
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
                    if tile not in ['0', '1', '2', '3', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l', 'm', 'n']:
                        self.tile_rects.append(pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
                x += 1
            y += 1
        self.create = False

    def events(self, event, dt):
        self.player.events(event, dt)

    def update(self, dt):
        distance = 0
        levelIsOver = False
        for platform in self.movingList:
            distance = platform.update(self.scroll)
        for platform in self.notCollisionable:
            platform.update(self.scroll)
        for enemy in self.enemiesList:
            enemy.update(self.scroll)
        levelData = self.player.update(self.tile_rects, self.enemiesList, self.movingList, self.notCollisionable, self.screen, self.scroll, dt, distance)
        if levelData[0]: # restart level
            self.restart()
        if levelData[1]: #level is over, go to next level
            levelIsOver = True

        return [self.player.entity.obj.x, self.player.entity.obj.y], self.player.airTimer, self.player.momentum, self.scroll, levelIsOver

    def restart(self):
        self.player = Player(self.playerX, self.playerY)

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
        self.levelList = [MapLevel(self.screen, 50, 200, 'map01'),
                          MapLevel(self.screen, 140, 500, 'map02')]
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
        self.levelList[self.levelIndex].draw(self.dt)

    def events(self):
        self.running = e.checkCloseButtons()

        for event in pygame.event.get():
            self.levelList[self.levelIndex].events(event, self.dt)
            self.running, self.fullscreen, self.screen = e.checkEvents(event, self.running, self.fullscreen, self.screen)
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.isPaused = not self.isPaused
                if event.key == K_RETURN:
                    self.restart = True

    def update(self):
        movement, airTimer, momentum, scroll, levelIsOver = self.levelList[self.levelIndex].update(self.dt)
        if self.isPaused:
            pos = [self.levelList[self.levelIndex].player.entity.x, self.levelList[self.levelIndex].player.entity.y]
            self.levelList[self.levelIndex].restartVariables(pos)
            screenshot = self.screen.copy()
            self.pause.start(screenshot)
            self.isPaused = not self.isPaused
        if self.restart:
            self.levelList[self.levelIndex].restart()
            self.restart = False
        if levelIsOver:
            self.levelIndex += 1
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

class MenuScreen:
    def __init__(self, screen, clock, smallFont, largeFont, background):
        self.clock = clock
        self.screen = screen
        self.smallFont = smallFont
        self.largeFont = largeFont
        self.showFPS = True
        self.fullscreen = False
        self.background = e.entity(0, 0, 640, 480, background)
        self.button = pygame.image.load('data/images/button.png').convert_alpha()
        self.selectedButton = pygame.image.load('data/images/buttonPressed.png').convert_alpha()

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
        self.background.changeFrame(1)
        self.largeFont.render(self.screen, self.title, (20, 55), WHITE)

    def events(self):
        pass

    def update(self):
        pass

    def fillArray(self, array):
        for x in range(len(array)):
            array[x] = False
        return array

class VideoMenu(MenuScreen):
    def __init__(self, screen, clock, smallFont, largeFont, background):
        super().__init__(screen, clock, smallFont, largeFont, background)
        self.stateList = [True, False, False]
        self.buttonList = ['Fullscreen', 'Show FPS', 'Back']
        self.descriptions = [['Yes', 'No'],
                             ['Yes', 'No'],
                             'Go back to Options']
        self.title = 'Video'

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
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if pos[0] >= 44 and pos[0] <= 174:
                    if pos[1] >= 187 and pos[1] <= 216:
                        self.fullscreen = e.fullscreenToggle(self.fullscreen, self.screen)
                    elif pos[1] >= 228 and pos[1] <= 261:
                        self.showFPS = not self.showFPS
                    elif pos[1] >= 271 and pos[1] <= 301:
                        self.running = False

    def update(self):
        pos = pygame.mouse.get_pos()
        if pos[0] >= 44 and pos[0] <= 174:
            if pos[1] >= 187 and pos[1] <= 216:
                self.stateList = self.fillArray(self.stateList)
                self.stateList[0] = True
            elif pos[1] >= 228 and pos[1] <= 261:
                self.stateList = self.fillArray(self.stateList)
                self.stateList[1] = True
            elif pos[1] >= 271 and pos[1] <= 301:
                self.stateList = self.fillArray(self.stateList)
                self.stateList[2] = True
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

class OptionsMenu(MenuScreen):
    def __init__(self, screen, clock, smallFont, largeFont, background):
        super().__init__(screen, clock, smallFont, largeFont, background)
        self.stateList = [True, False, False]
        self.buttonList = ['Video', 'Controls', 'Back']
        self.descriptions = ['Video options',
                             'See controls in game',
                             'Go back to Main Menu']
        self.title = 'Options'
        self.video = VideoMenu(self.screen, self.clock, self.smallFont, self.largeFont, 'background')

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
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if pos[0] >= 44 and pos[0] <= 174:
                    if pos[1] >= 187 and pos[1] <= 216:
                        self.video.start(self.showFPS)
                    elif pos[1] >= 228 and pos[1] <= 261:
                        pass
                    elif pos[1] >= 271 and pos[1] <= 301:
                        self.running = False

    def update(self):
        pos = pygame.mouse.get_pos()
        if pos[0] >= 44 and pos[0] <= 174:
            if pos[1] >= 187 and pos[1] <= 216:
                self.stateList = self.fillArray(self.stateList)
                self.stateList[0] = True
            elif pos[1] >= 228 and pos[1] <= 261:
                self.stateList = self.fillArray(self.stateList)
                self.stateList[1] = True
            elif pos[1] >= 271 and pos[1] <= 301:
                self.stateList = self.fillArray(self.stateList)
                self.stateList[2] = True
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
        self.options = OptionsMenu(self.screen, self.clock, self.smallFont, self.largeFont, 'background')
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
        self.background.changeFrame(1)

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
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if pos[0] >= 44 and pos[0] <= 174:
                if pos[1] >= 187 and pos[1] <= 216:
                    self.game.start(self.showFPS)
                elif pos[1] >= 228 and pos[1] <= 261:
                    self.options.start(self.showFPS)
                elif pos[1] >= 271 and pos[1] <= 301:
                    pass
                elif pos[1] >= 314 and pos[1] <= 346:
                    return False
        return True

    def update(self):
        pos = pygame.mouse.get_pos()
        if pos[0] >= 44 and pos[0] <= 174:
            if pos[1] >= 187 and pos[1] <= 216:
                self.stateList = self.fillArray(self.stateList)
                self.stateList[0] = True
            elif pos[1] >= 228 and pos[1] <= 261:
                self.stateList = self.fillArray(self.stateList)
                self.stateList[1] = True
            elif pos[1] >= 271 and pos[1] <= 301:
                self.stateList = self.fillArray(self.stateList)
                self.stateList[2] = True
            elif pos[1] >= 314 and pos[1] <= 346:
                self.stateList = self.fillArray(self.stateList)
                self.stateList[3] = True
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
        self.showFPS = self.options.showFPS
        if self.showFPS:
            fps = str(int(self.clock.get_fps()))
            self.smallFont.render(self.screen, fps, (WIDTH - 40, 20))

    def fillArray(self, array):
        for x in range(len(array)):
            array[x] = False
        return array

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
        pygame.display.set_caption('platformer')
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

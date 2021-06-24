import math
import random
import numpy as np
import pygame
import math
import time
from gym import spaces
SCALE = 20
WINDOW_WIDTH = 40*SCALE
WINDOW_HEIGHT = 30*SCALE
IMAGES = True
ST = 6
# ST = 3

# enemies
NUM_ENEMIES = 30  # 30
ENEMYBULLET_SPEED = 10/600 * WINDOW_HEIGHT  # 10
ENEMYSPEED_X = 2/800 * WINDOW_WIDTH  # 2
ENEMYSPEED_Y = 20/800 * WINDOW_WIDTH  # 20
TARGET = "random"
BULLET_FACTOR = 1

VERBOSE = False
# player
PLAYERSPEED_X = 10/800 * WINDOW_WIDTH   # 10
PLAYERBULLET_SPEED = 50/600 * WINDOW_HEIGHT   # 50
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 110, 255)
ROCKET = (100, 180, 255)


class Player:
    def __init__(self, screen, graphics=False):

        self.img = pygame.image.load('player.png')
        self.x = 370/800 * WINDOW_WIDTH
        self.y = 480/600 * WINDOW_HEIGHT
        self.screen = screen
        self.width = self.img.get_size()[0]
        self.height = self.img.get_size()[1]
        if(not graphics):
            self.width = self.width/800 * WINDOW_WIDTH
            self.height = self.height/600 * WINDOW_HEIGHT

    def getCorner(self):
        dis = abs((WINDOW_WIDTH/2) - (self.x+self.width))/(WINDOW_WIDTH/2)

        dis = 0 if dis < 0.4 else dis-0.4

        return dis

    def getShootPosX(self):
        return self.x + self.width/2.0

    def getRect(self):
         # Rect(left, top, width, height) -> Rect
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def setPos(self, pos):
        self.x, self.y = pos

    def draw(self):
        if IMAGES:
            self.screen.blit(self.img, (self.x, self.y))
        else:
            pygame.draw.rect(self.screen, GREEN, self.getRect())

    def getState(self):
        return np.array([self.x/WINDOW_WIDTH*BULLET_FACTOR, (1-(self.x/WINDOW_WIDTH))*BULLET_FACTOR])


class Bullet:
    def __init__(self, screen, orientation="up", x=0, y=0):

        self.bulletImg = pygame.image.load('bullet.png')
        self.x = x
        self.y = y
        self.height = self.bulletImg.get_size()[0]/600 * WINDOW_HEIGHT
        self.width = self.bulletImg.get_size()[1]/800 * WINDOW_WIDTH

        self.show = False
        self.screen = screen
        self.orientation = orientation
        if(orientation == "down"):
            self.bulletImg = pygame.transform.flip(self.bulletImg, False, True)

    def draw(self):
        if(self.show):
            if(IMAGES):
                self.screen.blit(self.bulletImg, (self.x, self.y))
            else:
                pygame.draw.rect(self.screen, ROCKET, self.getRect())
                if(self.orientation == "down"):
                    pygame.draw.rect(self.screen, BLUE, self.getRect())

    def setPos(self, pos):
        self.x, self.y = pos

    def getRect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def getState(self):
        show = 1 if self.show else 0
        if(self.orientation == "up"):
            return np.array([show, self.x/WINDOW_WIDTH, self.y/WINDOW_HEIGHT])
        return np.array([show*BULLET_FACTOR, self.x/WINDOW_WIDTH*BULLET_FACTOR, self.y/WINDOW_HEIGHT*BULLET_FACTOR])


class Enemy:
    def __init__(self, screen, x, y, graphics=False):
        self.enemyImg = pygame.image.load('enemy.png')
        self.bulletImg = pygame.image.load('bullet.png')
        self.bulletImgXSize = self.bulletImg.get_size()[0]/2
        self.x = x
        self.y = y
        self.width = self.enemyImg.get_size()[0]
        self.height = self.enemyImg.get_size()[1]

        if(not graphics):
            self.width = self.width/800 * WINDOW_WIDTH
            self.height = self.height/600 * WINDOW_HEIGHT
        self.col = 0
        self.row = 0
        self.alive = True
        self.screen = screen
        self.draw()

    def getState(self):
        alive = 1 if self.alive else 0
        return np.array([alive, self.x/WINDOW_WIDTH, self.y/WINDOW_HEIGHT])

    def getRect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def collided(self, playerBulletRect):
        if(not self.alive):
            return False
        # check collision and kill enemy
        if self.getRect().colliderect(playerBulletRect):

            self.alive = False
            return True
        else:
            return False

    def draw(self):
        if(self.alive):
            if(IMAGES):
                self.screen.blit(self.enemyImg, (self.x, self.y))
            else:
                pygame.draw.rect(self.screen, RED, self.getRect())

    def getPos(self):
        return self.x, self.y


class EnemyBlock:
    def __init__(self, screen, num, x=0, y=0, maxX=600.0, maxY=400.0, graphics=False):
        self.enemyImg = pygame.image.load('enemy.png')
        self.enemyPointX = x
        self.enemyPointY = y
        self.alive = True
        self.screen = screen
        self.enemies = []
        self.num = num
        enemyImg = pygame.image.load('enemy.png')
        bulletImg = pygame.image.load('bullet.png')

        self.enemyXsize = enemyImg.get_size()[0]/800 * WINDOW_WIDTH
        self.enemyYsize = enemyImg.get_size()[1]/600 * WINDOW_HEIGHT

        self.enemyXpad = 0 + self.enemyXsize
        self.enemyYpad = 0 + self.enemyXsize
        self.numDead = 0
        self.blockStartX = 50/800 * WINDOW_WIDTH
        self.blockStartY = 50/600 * WINDOW_HEIGHT

        self.anchorX = self.blockStartX
        self.anchorY = self.blockStartY
        self.maxX = maxX/800 * WINDOW_WIDTH
        self.maxY = maxY/600 * WINDOW_HEIGHT

        self.moveXSpeed = ENEMYSPEED_X
        self.moveYSpeed = ENEMYSPEED_Y
        self.moveXVector = self.moveXSpeed
        self.moveYVector = self.moveYSpeed
        # enemy bullet
        self.enemyBullet = Bullet(self.screen, "down")
        self.enemyBulletSizeX = bulletImg.get_size()[1]
        self.enemyBulletSpeed = ENEMYBULLET_SPEED

        self.creatEnemies()

    def getDistanceFromEnd(self):
        mostLeftX, mostRightX, mostBottomY = self.getEdges()
        return (mostBottomY - self.blockStartY) / self.maxY

    def getState(self):
        state = np.array([])
        if(ST > 5):
            for i in range(self.num):
                state = np.append(state, self.enemies[i].getState())
        if(ST >= 5):
            state = np.append(state, self.getEdgesState())
        if(ST > 3):
            state = np.append(state, self.enemyBullet.getState())
        return state

    def shoot(self, player):
        # get bottom alive

        mostLeftX, mostRightX, mostBottomY = self.getEdges()
        bottomXs = []
        for i in range(self.numCols):
            mb = 0
            for j in range(self.numRows-1, -1, -1):

                enemy = self.enemies[j*self.numCols+i-1]
                if(enemy.alive and enemy.y > mb):
                    mb = enemy.y
                    bottomXs.append(
                        (enemy.x+self.enemyXsize/2, enemy.y+self.enemyYsize))

        if(len(bottomXs) == 0):
            return

        bulletSpawn = random.choice(bottomXs)

        enemyBulletY = mostBottomY + self.enemyYsize
        if(random.random() < 0):
            self.enemyBullet.x = player.x
        else:
            self.enemyBullet.x = bulletSpawn[0]
        # if(TARGET == "player"):
        #     self.enemyBullet.x = player.x
        # else:
        #     self.enemyBullet.x = bulletSpawn[0]
        self.enemyBullet.y = bulletSpawn[1]
        self.enemyBullet.show = True

    def getEdges(self):
        mostLeftX, mostRightX, mostBottomY = (WINDOW_WIDTH, 0, 0)
        for i in range(self.num):

            if(self.enemies[i].alive):
                if(self.enemies[i].x < mostLeftX):
                    mostLeftX = self.enemies[i].x
                if(self.enemies[i].x + self.enemyXsize > mostRightX):
                    mostRightX = self.enemies[i].x + self.enemyXsize
                if(self.enemies[i].x > mostBottomY):
                    mostBottomY = self.enemies[i].y

        return mostLeftX, mostRightX, mostBottomY

    def getEdgesState(self):
        mostLeftX, mostRightX, mostBottomY = self.getEdges()
        return np.array([mostLeftX/WINDOW_WIDTH, mostRightX/WINDOW_WIDTH])

    def playerShot(self, playerRect):
        if(playerRect.colliderect(self.enemyBullet.getRect())):
            if VERBOSE:
                print("mayday")
            return True
        return False

    def underBullet(self, playerRect):
        if(not self.enemyBullet.show):
            return False
        if(playerRect.colliderect(pygame.Rect(self.enemyBullet.x, self.enemyBullet.y, self.enemyBullet.width, WINDOW_HEIGHT))):

            return True
        return False

    def checkCollisions(self, playerBulletRect):
        collided = False
        for i in range(self.num):
            collided = self.enemies[i].collided(playerBulletRect)
            if(collided):
                self.numDead += 1
                break
        return collided

    def moveAnchor(self):
        # get limits
        mostLeftX, mostRightX, mostBottomY = self.getEdges()

        if(mostLeftX < 0):
            self.moveXVector = self.moveXSpeed
            self.anchorY += self.moveYVector
        if(mostRightX > WINDOW_WIDTH):
            self.moveXVector = -self.moveXSpeed
            self.anchorY += self.moveYVector
        self.anchorX += self.moveXVector

    def move(self, player):
        enemyPointX = 0
        enemyPointY = 0
        self.moveAnchor()
        for i in range(self.num):

            self.enemies[i].x = enemyPointX + self.anchorX
            self.enemies[i].y = enemyPointY + self.anchorY
            self.enemies[i].draw()

            enemyPointX += self.enemyXpad
            if(enemyPointX > self.maxX):
                enemyPointX = 0
                enemyPointY += self.enemyYpad

    def creatEnemies(self):
        self.numRows = 0
        self.numCols = 0
        col = 0
        row = 0
        for i in range(self.num):
            enemy = Enemy(self.screen, self.enemyPointX +
                          self.anchorX, self.enemyPointY+self.anchorY)
            enemy.col = col
            enemy.row = row
            col += 1
            self.enemies.append(enemy)
            self.enemyPointX += self.enemyXpad

            if(self.enemyPointX > self.maxX):
                col = 0
                row += 1
                self.enemyPointX = 0
                self.enemyPointY += self.enemyYpad
                self.numRows += 1
        self.numCols = math.ceil(self.num/self.numRows)

    def allDead(self):
        allDead = True
        for i in range(self.num):
            if(self.enemies[i].alive):
                allDead = False
                break
        return allDead

    def checkBottom(self, player):
        mostLeftX, mostRightX, mostBottomY = self.getEdges()
        if(player.x < mostLeftX or player.x > mostRightX):
            return False
        return True

    def enemyInvasion(self):
        mostLeftX, mostRightX, mostBottomY = self.getEdges()

        if(mostBottomY > self.maxY):
            self.moveXSpeed = 0
            self.moveYSpeed = 0
            return True
        return False


class GameEnv:

    def __init__(self, framerate=0, verbose=False, graphics=True):
        self.gWidth = WINDOW_WIDTH
        self.gHeight = WINDOW_HEIGHT
        self.graphics = graphics
        self.framerate = framerate
        self.verbose = verbose
        self.enemyXSpeed = 0
        self.observation_space = 89
        self.num_envs = 1
        self.action_space = spaces.Discrete(4)
    # The observation will be the coordinate of the agent
    # this can be described both by Discrete and Box space
        self.observation_space = spaces.Box(low=0, high=98,
                                            shape=(98,), dtype=np.float32)
        self.reward_range = (0, 1)
        self.metadata = []
        enemyImg = pygame.image.load('enemy.png')
        self.enemyXsize = enemyImg.get_size()[0]/2
        self.enemyYsize = enemyImg.get_size()[1]/2

        self.reset()
        # abe rewards
        self.stepReward = 0
        self.enemyMissedReward = 0
        self.playerShotReward = 0
        self.enemyShotReward = 0
        self.missedShotReward = 0
        self.allDeadReward = 0
        self.invasionReward = 0
        self.bottomReward = 0
        self.underReward = 0
        self.anchorReward = 0
        self.cornerReward = 0
        self.bulletDistanceReward = 1
        self.discount = 0

    def getImage(self):
        window_pixel_matrix = pygame.surfarray.array3d(self.screen)
        return window_pixel_matrix

    def getGameState(self):
        if(ST == 7):
            return self.getImage()
        state = np.array([])
        # enemy states
        enemyBlockState = self.enemyBlock.getState()

        state = np.append(state, enemyBlockState)
        state = np.append(
            state, [self.enemyBlock.underBullet(self.player.getRect())*1])

        # playerBullet
        bulletState = self.playerBullet.getState()
        state = np.append(state, bulletState)
        # add bullet distance state
        eb = self.enemyBlock.enemyBullet
        dis = 1
        if(eb.show):
            # bullet distance
            dis = abs(eb.x-self.player.x)/WINDOW_WIDTH*BULLET_FACTOR
        state = np.append(state, dis)
        # playerstates
        playerState = self.player.getState()
        state = np.append(state, playerState)

        return state

    def reset(self):
        pygame.init()

        self.steps = 0
        if(VERBOSE):
            print("game start")
        self.screen = pygame.display.set_mode(
            (int(self.gWidth), int(self.gHeight)))

        # self.ground
        self.background = pygame.image.load('background.png')
        # Caption and Icon
        pygame.display.set_caption("Space Invader")
        icon = pygame.image.load('ufo.png')
        pygame.display.set_icon(icon)

        self.font = pygame.font.Font('freesansbold.ttf', 32)

        # Game Over
        self.over_font = pygame.font.Font('freesansbold.ttf', 64)
        # Player
        self.player = Player(self.screen)
        self.playerXVector = 0
        self.playerXSpeed = PLAYERSPEED_X

        self.done = False
        self.enemyBlock = EnemyBlock(self.screen, num=NUM_ENEMIES, x=0, y=20)
        # self.bullets = NUM_ENEMIES
        self.bullets = 1000

        # Bullet
        self.playerBullet = Bullet(self.screen, y=480/600*WINDOW_HEIGHT, x=0)
        self.bulletXSpeed = 0
        self.bulletYSpeed = PLAYERBULLET_SPEED

        # Score
        self.score_value = 0
        self.totalReward = 0
        return self.getGameState()

    def player(self, x, y):
        self.screen.blit(self.playerImg, (x, y))

    def show_score(self, x, y):
        if(self.framerate != 0 and self.graphics):
            score = self.font.render(f"Score : {self.enemyBlock.numDead}",
                                     True, (255, 255, 255))
            self.screen.blit(score, (x, y))

    def playerShoot(self):

        self.playerBullet.show = True
        self.playerBullet.setPos(self.player)

    def loop(self):
        running = True
        action = 0
        totalReward = 0
        while running:

            if(self.done):
                running = False
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # if keystroke is pressed check whether its right or left
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        action = 1

                    if event.key == pygame.K_RIGHT:
                        action = 2
                    if event.key == pygame.K_SPACE:
                        action = 3

                if event.type == pygame.KEYUP:
                    # if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    action = 0

                if event.type == pygame.QUIT:
                    running = False
            # print("a", action)
            state, reward, done, win = self.step(action)
            #print(np.round(state, 2))
            totalReward += reward
        print(f"steps={self.steps} totalR={totalReward}", )
        # if(done):
        #     running = False

    def step(self, action, finishGame=False):
        # abcd
        reward = self.stepReward
        win = 0
        self.steps += 1
        pygame.event.pump()

        if action == 1:
            self.playerXVector = -self.playerXSpeed
        if action == 2:
            self.playerXVector = self.playerXSpeed
        if action == 3:
            if not self.playerBullet.show:
                # Get the current x cordinate of the spaceship

                if(self.bullets >= 0):
                    self.bullets -= 1

                    self.playerBullet.x = self.player.getShootPosX()
                    self.playerBullet.show = True

        if action == 0:
            self.playerXVector = 0

        self.screen.fill((0, 0, 0))
        # Background Image
        if(self.framerate != 0 and self.graphics):
            self.screen.blit(self.background, (0, 0))

        # if keystroke is pressed check whether its right or left

        self.player.x += self.playerXVector
        if self.player.x <= 0:
            self.player.x = 0
        elif self.player.x >= 736/800*WINDOW_WIDTH:
            self.player.x = 736/800*WINDOW_WIDTH

        # show player
        self.player.draw()
        self.playerBullet.draw()
        # enemyMovement
        self.enemyBlock.move(self.player)

        # enemy bullet movement
        # move bullet
        if(self.enemyBlock.enemyBullet.show):
            # moving bullet
            self.enemyBlock.enemyBullet.y += ENEMYBULLET_SPEED
            self.enemyBlock.enemyBullet.draw()
            # check collision with game boundary
            if(self.enemyBlock.enemyBullet.y > WINDOW_HEIGHT):
                self.enemyBlock.enemyBullet.show = False
                reward += self.enemyMissedReward
        else:
            # print("shoting")
            if(not self.enemyBlock.allDead()):
                self.enemyBlock.enemyBullet.show = True
                self.enemyBlock.shoot(self.player)
            else:
                if VERBOSE:
                    print("all dead")
        # check player collisions
        playerShot = self.enemyBlock.playerShot(self.player.getRect())
        eb = self.enemyBlock.enemyBullet
        if(eb.show):
            # bullet distance
            pass
        if(self.enemyBlock.underBullet(self.player.getRect())):
            # check under
            reward += self.underReward
            dis = abs(eb.x+eb.width-self.player.x +
                      self.player.width)/WINDOW_WIDTH
            dis = 1-dis
            # print("dis", dis)
            reward += -dis*self.bulletDistanceReward
        if(playerShot):
            # abcd
            reward += self.playerShotReward
            win = -2
            self.done = True
        # player bullet collision
        if(self.playerBullet.show):
            collision = self.enemyBlock.checkCollisions(
                self.playerBullet.getRect())
            if collision:
                # explosion# = mixer.Sound("explosion.wav")
                # explosionSound.play()
                self.playerBullet.y = self.player.y
                self.playerBullet.show = False
                # abcd
                reward += self.enemyShotReward
                self.score_value += 1

        # # Bullet Movement
        if self.playerBullet.y <= 0:
            self.playerBullet.y = 480/600*WINDOW_HEIGHT
            self.playerBullet.show = False
            # abcd
            reward += self.missedShotReward
        if self.playerBullet.show:
            self.playerBullet.y -= self.bulletYSpeed
        reward += (self.enemyBlock.anchorY -
                   self.enemyBlock.blockStartY)*self.anchorReward
        # gameover logic
        allDead = self.enemyBlock.allDead()
        invasion = False
        if(allDead):
            # abcd
            reward += self.allDeadReward * (self.discount**self.steps)
            running = False
            self.done = True
            win = 1
            if(self.verbose):
                print("gracefull win")
        else:
            invasion = self.enemyBlock.enemyInvasion()
            # at bottom reward

        if(invasion):
            # invaded
            running = False
            self.done = True
            win = -1
            if(self.verbose):
                print("gracefull lose")
            # abcd
            reward += self.invasionReward
        else:
            if(not self.enemyBlock.checkBottom(self.player)):
                reward += self.bottomReward
        self.show_score(50, 50)

        # cornerReward
        reward += self.player.getCorner() * self.cornerReward
        if(self.framerate != 0):
            time.sleep(self.framerate)
        pygame.display.update()

        self.totalReward += reward
        return self.getGameState(), reward, self.done, win

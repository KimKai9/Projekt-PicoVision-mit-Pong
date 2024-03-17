from micropython import const
from picovision import PicoVision, PEN_RGB555
from urandom import randrange
import gc
import machine
import utime

SCREEN_WIDTH = const(320)
SCREEN_HEIGHT = const(240)
COLLISION_TOLERANCE = const(3)
uart = machine.UART(0, baudrate=9600)

class Field:
    def __init__(self, screen):
        self._display = screen

    def draw(self, Spieler1: int, Spieler2: int) -> None:
        self._display.set_pen(WHITE)
        self._display.text(f'Spieler 1: {Spieler1}', 25, 15, scale=1)
        self._display.text(f'Spieler 2: {Spieler2}', 235, 15, scale=1)
        self._display.line(25, 25, SCREEN_WIDTH - 25, 25)
        self._display.line(25, SCREEN_HEIGHT - 25, SCREEN_WIDTH - 25, SCREEN_HEIGHT - 25)


class Paddle:
    PADDLE_SPEED = const(5)

    def __init__(self, screen, pos_x):
        self._display = screen
        self.width = 3
        self.height = 30
        self.pos_x = pos_x
        self.pos_y = SCREEN_HEIGHT // 2

    def handle_input(self):
  
      uart_data = uart.read(4) 
      if uart_data is not None: 
        for i in range(4):
          if uart_data[i] == 0: 
            if i == 0 and paddle2.pos_y > 30: 
              paddle2.pos_y -= Paddle.PADDLE_SPEED
            elif i == 1 and paddle2.pos_y < (SCREEN_HEIGHT - paddle2.height - 30):  
              paddle2.pos_y += Paddle.PADDLE_SPEED
            elif i == 2 and self.pos_y > 30:  
              self.pos_y -= Paddle.PADDLE_SPEED
            elif i == 3 and self.pos_y < (SCREEN_HEIGHT - self.height - 30):  
              self.pos_y += Paddle.PADDLE_SPEED
        

        self._display.set_pen(RED)
        self._display.rectangle(self.pos_x, self.pos_y, self.width, self.height)
        self._display.rectangle(paddle2.pos_x, paddle2.pos_y, paddle2.width, paddle2.height)


class Ball:
    def __init__(self, screen):
        self._display = screen
        self.radius = 2
        self.pos_x = None
        self.pos_y = None
        self.speed_x = None
        self.speed_y = None

    def reset(self) -> None:
        self.pos_x = SCREEN_WIDTH // 2
        self.pos_y = SCREEN_HEIGHT // 2
        self.speed_x = -1 if randrange(2) else 1
        self.speed_y = -1 if randrange(2) else 1

    def draw(self) -> None:
        self.pos_x += self.speed_x
        self.pos_y += self.speed_y

        self._display.set_pen(GREEN)
        self._display.circle(self.pos_x, self.pos_y, self.radius)


def check_collision(circle: list, rectangle: list) -> bool:
    circle_radius, circle_x, circle_y = circle
    rect_x, rect_y, rect_width, rect_height = rectangle

    closest_x = max(rect_x, min(circle_x, rect_x + rect_width))
    closest_y = max(rect_y, min(circle_y, rect_y + rect_height))

    distance = ((circle_x - closest_x) ** 2 + (circle_y - closest_y) ** 2) ** 0.5
    return distance <= (circle_radius + COLLISION_TOLERANCE)


display = PicoVision(PEN_RGB555, SCREEN_WIDTH, SCREEN_HEIGHT)
display.set_font("bitmap8")

BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(255, 0, 0)
GREEN = display.create_pen(0, 255, 0)

Spieler1_Punkt = 0
Spieler2_Punkt = 0
field = Field(screen=display)
paddle1 = Paddle(screen=display, pos_x=28)
paddle2 = Paddle(screen=display, pos_x=SCREEN_WIDTH - 33)
ball = Ball(screen=display)
ball.reset()

while True:
    display.set_pen(BLACK)
    display.clear()

    field.draw(Spieler1=Spieler1_Punkt, Spieler2=Spieler2_Punkt)
    paddle1.handle_input()
    paddle2.handle_input()

    
    if not (25 + ball.radius <= ball.pos_y <= SCREEN_HEIGHT - 25 - ball.radius):
        ball.speed_y *= -1
        
    if ball.pos_x <= 33:
        if check_collision(circle=[ball.radius, ball.pos_x, ball.pos_y],
                           rectangle=[paddle1.pos_x, paddle1.pos_y, paddle1.width, paddle1.height]):
            ball.speed_x *= -1

    if ball.pos_x - ball.radius < 25:
        Spieler2_Punkt += 1
        ball.reset()
    
    ball.draw()
    
    if ball.pos_x + ball.radius >= SCREEN_WIDTH - 34:
        if check_collision(circle=[ball.radius, ball.pos_x, ball.pos_y],
                           rectangle=[paddle2.pos_x, paddle2.pos_y, paddle2.width, paddle2.height]):
            ball.speed_x *= -1

    if ball.pos_x + ball.radius> SCREEN_WIDTH - 30:
        Spieler1_Punkt += 1
        ball.reset()
    
    ball.draw()

    display.update()
    gc.collect()
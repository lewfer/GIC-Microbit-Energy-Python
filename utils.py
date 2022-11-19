import pygame


red = (200,0,0)
green = (0,200,0)
blue = (0,0,200)
yellow = (255,215,0)

brown = (175,124,63)
white = (255,255,255)
grey = (200,200,200)
black = (0,0,0)


def map(n, a, b, c, d):
    return (n-a) * (d-c)/(b-a) + c

def text(screen, x,y,t,size=24,colour=black):
    font = pygame.font.Font('freesansbold.ttf',size)
    text = font.render(t, True, colour)
    text_rect = text.get_rect(center=(x, y))
    screen.blit(text, text_rect)

def textLeft(screen, x,y,t,size=24,colour=black):
    font = pygame.font.Font('freesansbold.ttf',size)
    text = font.render(t, True, colour)
    text_rect = text.get_rect(x=x, y=y)
    screen.blit(text, text_rect)    

class Button:
    def __init__(self,x,y,w,h, text):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text

    def draw(self, screen, isOn):
        if isOn:
            pygame.draw.rect(screen, green, (self.x,self.y,self.w,self.h))
        else:
            pygame.draw.rect(screen, red, (self.x,self.y,self.w,self.h))

        text(screen, self.x+self.w/2, self.y+self.h/2,self.text)
        """
        font = pygame.font.Font('freesansbold.ttf',24)
        font = pygame.font.Font(None, 25)
        text = font.render(self.text, True, black)
        text_rect = text.get_rect(center=(self.x+self.w/2, self.y+self.h/2))
        screen.blit(text, text_rect)"""


        # text = font.render("Press me", True, black)
        # screen.blit(text,
        #     (self.x , self.y ))
        #     #(self.x - text.get_width() // 2, self.y - text.get_height() // 2))

    def isOver(self):
         return self.x+self.w > mouse[0] > self.x and self.y+self.h > mouse[1] > self.y

    def clicked(self, mousepos):
        return self.x+self.w > mousepos[0] > self.x and self.y+self.h > mousepos[1] > self.y
         


class Graph():
    def __init__(self, x, y, w, h, screen):
        self.yaxisMargin = 30
        self.xaxisMargin = 10
        self.topMargin = 10
        self.rightMargin = 10
        self.showXAxis = False
        self.showYAxis = True
        self.rect = pygame.Rect(x,y,w,h)
        self.screen = screen

    # Set up axes with given x and y ranges
    def axes(self,x1,x2,y1,y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        pygame.draw.rect(self.screen, grey, self.rect, 2)
        if self.showXAxis:
            self.xAxis(x1,x2)
        if self.showYAxis:
            self.yAxis(y1,y2)

    def plot(self, data,color):
        #pygame.draw.rect(screen, black,self.rect,2)
        
        if len(data)>0:
            maxy = max(data)
            maxy = 100 if maxy < 100 else maxy
            for i,d in enumerate(data):
                x = map(i,self.x1, self.x2, self.yaxisMargin, self.rect.w-self.rightMargin) + self.rect.x
                y = map(d, self.y1, self.y2, self.rect.h-self.xaxisMargin, self.topMargin) + self.rect.y
                pygame.draw.circle(self.screen, color, (x, y), 1)
                if (i>0):
                    pygame.draw.line(self.screen, color, (px,py), (x,y)) 
                px = x
                py = y

    def xAxis(self,x1,x2):
        step = int((x2-x1)/10)   #max(int(count/10),1)
        for i in range(x1,x2,step):
            x = map(i,x1,x2, self.yaxisMargin, self.rect.w-self.rightMargin) + self.rect.x
            text(self.screen, x, self.rect.y+self.rect.h-self.xaxisMargin/2, str(i), size=8)

    def yAxis(self,y1,y2):
        step = int((y2-y1)/10)   #max(int(count/10),1)
        for i in range(y1,y2,step):
            y = map(i,y1,y2, self.rect.h-self.xaxisMargin, self.topMargin) + self.rect.y
            text(self.screen, self.rect.x+self.yaxisMargin/2, y, str(i), size=10)            

import tqdm
from PIL import Image,ImageTk
from numpy import complex,array
from PIL import ImageTk, Image
import math
import pygame
import os
from glob import glob
import cv2
import colorsys


Width = 1024
Height = int(Width / 2)
Center_Point = complex(0,0)
Start_Center_Point = Center_Point
resolution = 20
zoom = 0.007
Start_zoom = zoom
graph_stack = []
photo_Num = 0
video_Num = 0
Photoes_folder_Name = 'Photos'
path = '/Users/amit/Documents/python/Mandelbrot/'

pygame.init()
display = pygame.display.set_mode((Width,Height + 100))
crashed = False
vec = pygame.math.Vector2


class button():
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=None):
        if outline:
            pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont('comicsans', int(Width/20))
            text = font.render(self.text, 1, (0, 0, 0))
            win.blit(text, (
            self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False

def tryColorMake(i):
    color = 255 * array(colorsys.hsv_to_rgb(i / 255.0, 1.0, 0.5))
    return tuple(color.astype(int))

def ColorMake(i):
    if i == resolution:
        return (0, 0, 0)
    else:
        ex1 = (0.45*math.log(i+1.1))
        ex2 = (0.45 * math.log(i**0.8 + 1.1))
        ex3 = (0.45 * math.log(i**0.6 + 1.1)) - ex1 * 20
        return (int(ex1*255), int(ex2*255), int(ex3*255))

def mandelbrot(x, y ,c,bool):
    c0 = complex(x, y)
    for i in range(1, resolution):
        c = c * c + c0
        if abs(c) > 2:
            return ColorMake(i)
    return (0, 0, 0)


def mandelbrot_make(zoom,Center_Point,video):
    graph_img = Image.new('RGB', size=(Width, Height))
    graph_pixels = graph_img.load()
    real = Center_Point.real - Width/2 * zoom
    if not video:
        for x in tqdm.tqdm(range(Width)):
            img = zoom * Height/2 + Center_Point.imag
            for y in range(Height):
                graph_pixels[x,y] = mandelbrot(real,img,Center_Point,False)
                img -= zoom
            real += zoom
    else:
        for x in range(Width):
            img = zoom * Height/2 + Center_Point.imag
            for y in range(Height):
                graph_pixels[x,y] = mandelbrot(real,img,Center_Point,True)
                img -= zoom
            real += zoom

    return graph_img


def Save_Image(path,img):
    global photo_Num
    if not os.path.isdir(path + '/' + Photoes_folder_Name):
        os.makedirs(path + '/' + Photoes_folder_Name)
    elif(photo_Num == 0):
        files = []
        for f in os.listdir(path + '/' + Photoes_folder_Name):
            try:
                files.append(int(f))
            except:
                print('')
        if len(files)>0:
            files.sort()
            photo_Num = files[-1] + 1
    img.save(path + Photoes_folder_Name + '/' + str(photo_Num), 'jpeg')
    photo_Num+=1

def Save_Video(path,Start_Point,End_Point,sec,frames_sec):
    global video_Num
    zoom_Video = Start_zoom
    frames = sec * frames_sec
    C_Point = Start_Point
    real_Del = (Start_Point.real - End_Point.real) / frames
    img_Del = Start_Point.imag - End_Point.imag / frames
    folders_path = glob(path + '*/')
    folders_Num = []

    for folder_path in folders_path:
        folder_name = str(folder_path.split('/')[-2])
        try:
            folders_Num.append(int(folder_name))
        except:
            print('')

    if len(folders_Num) == 0:
        Frames_Folder = str(video_Num)
    else:
        num = biggestNum(folders_Num)
        Frames_Folder = str(num + 1)
        video_Num = num + 1

    os.makedirs(path + Frames_Folder)
    frames_array = []
    for frame in tqdm.tqdm(range(frames)):
        img = mandelbrot_make(zoom_Video,C_Point,True)
        C_Point = complex(C_Point.real-real_Del,C_Point.imag-img_Del)
        zoom_Video *= 0.99
        img.save(path + Frames_Folder + '/' + str(frame), 'jpeg')
        f = cv2.imread(path + Frames_Folder + '/' + str(frame))
        height, width, layers = f.shape
        frames_array.append(f)

    out = cv2.VideoWriter('./' + str(video_Num) +'/'+'Video '+str(video_Num)+'.avi' , cv2.VideoWriter_fourcc(*'DIVX'), frames_sec, (Width,Height))
    for i in range(len(frames_array)):
        out.write(frames_array[i])
    out.release()



def biggestNum(list):
    max = list[0]
    for num in list:
        if num > max:
            max = num
    return max

green = (0,255,0)

Save_img_button = button(green,0,Height+30,int(Width/4),int(Width/30),'Save Image')
Start_img_button = button(green,300,Height+30,int(Width/4),int(Width/30),'Start Image')
Save_Video_button = button(green,600,Height+30,int(Width/4),int(Width/30),'Save Video')


start_graph_img =  mandelbrot_make(zoom,Start_Center_Point,False)
graph_img = start_graph_img
graph = pygame.image.fromstring(start_graph_img.tobytes(),start_graph_img.size,start_graph_img.mode)
#Save_Video(path,complex(0,0), complex(0.5,0.34515j),40,30)

while not crashed:
    for event in pygame.event.get():
        Start_img_button.draw(display)
        Save_img_button.draw(display)
        Save_Video_button.draw(display)

        if event.type == pygame.QUIT:
            crashed = True

        if event.type == pygame.MOUSEBUTTONUP:
            Mouse_pos = pygame.mouse.get_pos()
            if Mouse_pos[1]<Height:
                real = (Center_Point.real - (Width / 2 * zoom)) + Mouse_pos[0] * zoom
                img = (Center_Point.imag + (Height / 2 * zoom)) - Mouse_pos[1] * zoom
                num = complex(real,img)
                Center_Point = num
                zoom = zoom * 0.95
                graph_img = mandelbrot_make(zoom, Center_Point,False)
                graph = pygame.image.fromstring(graph_img.tobytes(), graph_img.size, graph_img.mode)
                graph_stack.append([graph_img,Center_Point])
                print(num)
            elif Save_img_button.isOver(Mouse_pos):
                Save_Image(path,graph_img)
                print('Image saved')

            elif Start_img_button.isOver(Mouse_pos):
                data = [start_graph_img, Start_Center_Point]
                img, Center_Point = data[0], data[1]
                graph = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
                zoom = Start_zoom
                graph_stack.clear()

            elif Save_Video_button.isOver(Mouse_pos):
                Save_Video(path,complex(0.41141,0.34725500000000004), complex(0.41106000000000004,0.34592500000000004),20,30)




        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if len(graph_stack) > 0:
                    data = graph_stack.pop()
                    if data[1] == Center_Point:
                        try:
                            data = graph_stack.pop()
                        except:
                            data = [start_graph_img, Start_Center_Point]
                            img, Center_Point = data[0], data[1]
                            graph = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
                    img , Center_Point = data[0] , data[1]
                    graph = pygame.image.fromstring(img.tobytes(),img.size,img.mode)
                    zoom = zoom/0.8

                else:
                    data = [start_graph_img,Start_Center_Point]
                    img , Center_Point = data[0] , data[1]
                    graph = pygame.image.fromstring(img.tobytes(),img.size,img.mode)
                    zoom = Start_zoom


    display.blit(graph,(0,0))
    pygame.display.update()

pygame.quit()
quit()
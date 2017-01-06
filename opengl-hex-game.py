from OpenGL.GL import *
from OpenGL.GLU import *
import os, sys, math, random
import pygame
import time
from pygame.locals import *
if sys.platform == 'win32' or sys.platform == 'win64':
    os.environ['SDL_VIDEO_CENTERED'] = '1'
from World import World

KEY_MOVE_CONST = 0.006
ZOOM_SPEED_CONST = 0.3

SCREEN_SIZE_X = 800
SCREEN_SIZE_Y = 400

TAN_Y = math.tan(math.radians(45.0 / 2.0))
TAN_X = TAN_Y * float(SCREEN_SIZE_X) / float(SCREEN_SIZE_Y)

CameraPos = [0.0, 0.0, 50.0]

world = None

#----------------------------------- openGL -----------------------------------

def gl_resize((width, height)):
    if height==0:
        height=1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION) # Subsequent cmnds to projection matrix stack
    glLoadIdentity()    # Replace the current matrix with the identity matrix
    # Set Perspective projection (fov_y, aspect ratio, zNear, zFar)
    gluPerspective(45.0, float(width) / height, 1.0, 1000.0)
    glMatrixMode(GL_MODELVIEW) # Subsequent cmnds to modelview matrix stack
    glLoadIdentity()

def gl_init():
    glEnable(GL_BLEND)        # Blend incoming RGBA colr with values in colr buf
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # Texture env parameters (target, symbolic name, parameter)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    
    glShadeModel(GL_SMOOTH)

    glClearColor(0.0, 0.0, 0.0, 0.0)	# Defines values used to clear buffer
    glClearDepth(1.0)         # Value used when depth buffer is cleared
    glEnable(GL_DEPTH_TEST)   # Enable depth testing
    glEnable(GL_ALPHA_TEST)   # Do alpha testing
    glDepthFunc(GL_LEQUAL)    # Used for depth buffer comparison
    # Specify implementation-specifuc hints (target, mode)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    glAlphaFunc(GL_NOTEQUAL, 0.0) # Alpha test function

#    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)		# Set Line Antialiasing
#glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);	// Type Of Blending To Use

    ### Add lights ###
#    LightAmbient = [ 0.5, 0.5, 0.5, 1.0]
#    LightDiffuse = [ 1.0, 1.0, 1.0, 1.0]
#    LightIntensity = [ 50.0, 50.0, 50.0, 10.0]
#    LightPosition = [ 0, 0.0, 100.0, 1.0]

#    glLightfv(GL_LIGHT0, GL_AMBIENT, LightAmbient)
#    glLightfv(GL_LIGHT0, GL_DIFFUSE, LightDiffuse)
#    glLightfv(GL_LIGHT0, GL_POSITION, LightPosition)
#    glLightfv(GL_LIGHT0, GL_SPECULAR, LightIntensity)
#    glEnable(GL_LIGHT0)
#    glEnable(GL_LIGHTING)

def Draw():
    # Clear
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    # Move Camera
    glTranslatef(-CameraPos[0],-CameraPos[1],-CameraPos[2])
    # Paint World
    world.paint()
    # Flip Double Buffer
    pygame.display.flip()


#--------------------------------- Game Logic ---------------------------------

def handleMouseEvent(event):
    global CameraPos, TAN_Y, TAN_X
    mrel = pygame.mouse.get_rel()           # get mouse moved (in pixels)
    (mXpos, mYpos) = pygame.mouse.get_pos() # get mouse postion (in pixels)
    mpress = pygame.mouse.get_pressed()     # return (btn1, btn2, btn3)

    if (mrel[0] != 0 or mrel[1] != 0):      # Mouse moved
        world.highlightHex(
                CameraPos[0] + CameraPos[2] * TAN_X * 2 *
                float(mXpos - SCREEN_SIZE_X / 2) / SCREEN_SIZE_X,
                CameraPos[1] - CameraPos[2] * TAN_Y * 2 *
                float(mYpos - SCREEN_SIZE_Y / 2) / SCREEN_SIZE_Y)
        if mpress[2]:	                    # Right Button - Move Around
            CameraPos[0] -= CameraPos[2] * TAN_X * 2.0 * float(mrel[0]) / float(SCREEN_SIZE_X)
            CameraPos[1] += CameraPos[2] * TAN_Y * 2.0 * float(mrel[1]) / float(SCREEN_SIZE_Y)

    if mpress[0]:       # Left Mouse Button
        world.selectActiveHex()
        
    if event.type == MOUSEBUTTONDOWN:
        if event.button == 4:                   #Scroll In
            old_z = CameraPos[2]
            old_size = (old_z * TAN_X * 2.0, old_z * TAN_Y * 2.0)
            CameraPos[2] -= CameraPos[2] * ZOOM_SPEED_CONST
            if CameraPos[2] < 10:               # Limit zoom
                CameraPos[2] = 10

            new_z = CameraPos[2]
            new_size = (new_z * TAN_X * 2.0, new_z * TAN_Y * 2.0)
    
            xPer = float(mXpos - SCREEN_SIZE_X / 2) / SCREEN_SIZE_X
            yPer = float(mYpos - SCREEN_SIZE_Y / 2) / SCREEN_SIZE_Y

            mv_x = xPer * (old_size[0] - new_size[0])
            mv_y = yPer * (old_size[1] - new_size[1])
            CameraPos[0] += mv_x
            CameraPos[1] -= mv_y

        elif event.button == 5:                 #Scroll Out
            CameraPos[2] += CameraPos[2] * ZOOM_SPEED_CONST

def handleKeyEvent(event):
    """
        Function handling key events.
        Returns: True as default, False when a quit key has been pressed
    """
    global CameraPos

    keystate = pygame.key.get_pressed()

    if keystate[K_ESCAPE]:                          # ESC-key
        return False
    if keystate[K_v]:                               # "v"-key
         CameraPos = [40.0,50.0,50.0]
    if keystate[K_PLUS] or keystate[K_KP_PLUS]:     # "+"-key
            CameraPos[2] += CameraPos[2] * ZOOM_SPEED_CONST
    if keystate[K_MINUS] or keystate[K_KP_MINUS]:   # "-"-key
            CameraPos[2] -= CameraPos[2] * ZOOM_SPEED_CONST

    if CameraPos[2] < 10:                           # Limit zoom
        CameraPos[2] = 10

    return True

def tick():
    """
        Function handling periodic updates. Called by the 30Hz clock.
    """
    keystate = pygame.key.get_pressed()
    
    if keystate[K_UP]:                              # "up arrow"-key
         CameraPos[1] += CameraPos[2] * KEY_MOVE_CONST
    if keystate[K_DOWN]:                            # "down arrow"-key
         CameraPos[1] -= CameraPos[2] * KEY_MOVE_CONST
    if keystate[K_RIGHT]:                           # "right arrow"-key
         CameraPos[0] += CameraPos[2] * KEY_MOVE_CONST
    if keystate[K_LEFT]:                            # "left arrow"-key
         CameraPos[0] -= CameraPos[2] * KEY_MOVE_CONST
    

def main():
    global world

    pygame.init()

    Screen = (SCREEN_SIZE_X, SCREEN_SIZE_Y)
    icon = pygame.Surface((1,1))
    icon.set_alpha(0)
    pygame.display.set_icon(icon)
    pygame.display.set_caption('OpenGL Hex Game')
    pygame.display.set_mode(Screen, OPENGL|DOUBLEBUF)

    gl_resize(Screen)
    gl_init()

    world = World(40, 40)

    pygame.time.set_timer(USEREVENT, 40)   # 25 Hz timer

    frames = 0
    ticks = pygame.time.get_ticks()
    run = True
    while run: 
        events = [pygame.event.wait()]  # Wait for next event; user or timer
        if pygame.event.peek():
            events.extend(pygame.event.get())
        for event in events:
            if event.type == QUIT:
                run = False
                break 
            elif event.type == MOUSEBUTTONDOWN or event.type == MOUSEMOTION:
                handleMouseEvent(event)
            elif event.type == KEYDOWN:
                run = handleKeyEvent(event)   # Returns false on quit
            elif event.type == USEREVENT:
                tick()
                world.tick()

        Draw()
        frames = frames+1

    print "fps:  %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks))

    pygame.quit();

if __name__ == '__main__': main()


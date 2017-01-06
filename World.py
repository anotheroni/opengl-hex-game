from OpenGL.GL import *
from math import *
import os
import pygame
from Ship import Ship
from GLText import GLText

SQRT_3 = sqrt(3.0)
SQRT_3_2 = SQRT_3 * 2
HEX_M = 1 / SQRT_3

class World(object):
    """

      The world class represents and draws a Hexagon-Based Tile Map.
      Origo is bottom left.
      Hex Dimensions: s=2 h=1 r=sqrt(3) b=4 a=2*sqrt(3)

      Hex Sides:    _A
                  F/ \B
                  E\_/C
                    D
    """

    def __init__(self, x_size=40, y_size=40):

        global SQRT_3, SQRT_3_2, HEX_M

        self.textures = [0,0]

        self.textg24 = GLText(size=24, scale=0.05, color=(128,255,128))

        self.highlightDict = dict()
        self.activeHex = None    # Hex mouse pointer is in
        self.selectedHex = None  # Hex user left clicked in
        self.selectedShip = None # Ship that has been selected

        self.x = x_size
        self.y = y_size

        x_size /= 2     # To make it easier to draw the world
        y_size *= 2

        self.glLoadTextures()

        # Setup ships
        self.shipDict = dict()
        self.shipDict["one"] = Ship(10, 10, 0, 5, self.textures[0])
        self.shipDict["two"] = Ship(11, 10, 1, 5, self.textures[0])
        self.shipDict["tree"] = Ship(30, 12, 4, 8, self.textures[0])
        self.shipDict["four"] = Ship(32, 14, 4, 8, self.textures[0])

        #stringTex, w, h, tw, th = self.loadText("Cow!", color=(128,255,128))
        #self.stringDL = self.createTexDL(stringTex, tw, th)

        # Create Hex Field List
        self.dlHex = glGenLists(1)        # Get the next Display List ID
        glNewList(self.dlHex, GL_COMPILE) # Creates a display list (name, mode)

        glColor3f(0.7,0.7,0.7)
        yline = 0
        glTranslatef( 2.0, 0.0, 0.0)      # To get 0,0 as bottom left
        for y in xrange(y_size):
            yline += 1
            glTranslatef( 0.0, SQRT_3, 0.0)
            glPushMatrix()
            if yline % 2: glTranslatef(3.0, 0.0, 0.0)  # Indent
            else:                             # Side E on first column
                glBegin(GL_LINES)             # Start line
                glVertex3f(-1.0,-SQRT_3, 0.0)
                glVertex3f(-2.0, 0.0   , 0.0)
                glEnd()
            for x in xrange(x_size):
                glBegin(GL_LINES)
                glVertex3f(-2.0, 0.0   , 0.0) # Side F
                glVertex3f(-1.0, SQRT_3, 0.0)
                glVertex3f(-1.0, SQRT_3, 0.0) # Side A
                glVertex3f( 1.0, SQRT_3, 0.0)
                glVertex3f( 1.0, SQRT_3, 0.0) # Side B
                glVertex3f( 2.0, 0.0   , 0.0)
                glEnd()
                glTranslatef(6.0, 0.0, 0.0)
            if yline % 2:                     # Not indented
                glTranslatef(-6.0, 0.0, 0.0)
                glBegin(GL_LINES)             # End line
                glVertex3f( 2.0, 0.0   , 0.0) # Side C
                glVertex3f( 1.0,-SQRT_3, 0.0)
                glEnd()
            glPopMatrix()

        # Translate back to origo
        glTranslatef(0.0, -SQRT_3 * (y_size - 1), 0.0)
        glPushMatrix()
        glTranslatef(3.0, 0.0, 0.0)  # Indent
        for x in xrange(x_size):
            glBegin(GL_LINES)                 # Bottom lines
            glVertex3f( 2.0, 0.0   , 0.0)     # Side C
            glVertex3f( 1.0,-SQRT_3, 0.0)
            glVertex3f( 1.0,-SQRT_3, 0.0)     # Side D
            glVertex3f(-1.0,-SQRT_3, 0.0)
            glVertex3f(-1.0,-SQRT_3, 0.0)     # Side E
            glVertex3f(-2.0, 0.0   , 0.0)
            glEnd()
            glTranslatef(6.0, 0.0, 0.0)
        glPopMatrix()

        glPushMatrix()
        for x in xrange(x_size):
            glBegin(GL_LINES)
            glVertex3f(-1.0, 0.0, 0.0) # Side A
            glVertex3f( 1.0, 0.0, 0.0)
            glEnd()
            glTranslatef(6.0, 0.0, 0.0)
        glPopMatrix()
        glEndList()    # dlHex

        # Hight Light Hex polygon
        glLoadIdentity()
        self.dlHLHex = glGenLists(1)        # Get the next Display List ID
        glNewList(self.dlHLHex, GL_COMPILE) # Creates a display list(name, mode)
        glBegin(GL_POLYGON)
        glVertex3f(-1.0, SQRT_3, 0.0) # Side A
        glVertex3f( 1.0, SQRT_3, 0.0) # Side B
        glVertex3f( 2.0, 0.0   , 0.0) # Side C
        glVertex3f( 1.0,-SQRT_3, 0.0) # Side D
        glVertex3f(-1.0,-SQRT_3, 0.0) # Side E
        glVertex3f(-2.0, 0.0   , 0.0) # Side F
        glVertex3f(-1.0, SQRT_3, 0.0) # Side A
        glEnd()
        glEndList()    # dlHLHex

        # Selected Display List 
        glLoadIdentity()
        self.dlSelHex = glGenLists(1)        # Get the next Display List ID
        glNewList(self.dlSelHex, GL_COMPILE) # Creates a display list
        glBegin(GL_POLYGON)
        glVertex3f(-1.0, SQRT_3 + 0.1, 0.0) # Side A
        glVertex3f( 1.0, SQRT_3 + 0.1, 0.0) # Side B
        glVertex3f( 1.0, SQRT_3 - 0.1, 0.0) # Side B
        glVertex3f(-1.0, SQRT_3 - 0.1, 0.0) # Side A
        glEnd()
        glBegin(GL_POLYGON)
        glVertex3f( 1.0, SQRT_3 + 0.1, 0.0) # Side B
        glVertex3f( 2.1, 0.0   , 0.0) # Side C
        glVertex3f( 1.9, 0.0   , 0.0) # Side C
        glVertex3f( 1.0, SQRT_3 - 0.1, 0.0) # Side B
        glEnd()
        glBegin(GL_POLYGON)
        glVertex3f( 2.1, 0.0   , 0.0) # Side C
        glVertex3f( 1.0,-SQRT_3 - 0.1, 0.0) # Side D
        glVertex3f( 1.0,-SQRT_3 + 0.1, 0.0) # Side D
        glVertex3f( 1.9, 0.0   , 0.0) # Side C
        glEnd()
        glBegin(GL_POLYGON)
        glVertex3f( 1.0,-SQRT_3 - 0.1, 0.0) # Side D
        glVertex3f(-1.0,-SQRT_3 - 0.1, 0.0) # Side E
        glVertex3f(-1.0,-SQRT_3 + 0.1, 0.0) # Side E
        glVertex3f( 1.0,-SQRT_3 + 0.1, 0.0) # Side D
        glEnd()
        glBegin(GL_POLYGON)
        glVertex3f(-1.0,-SQRT_3 - 0.1, 0.0) # Side E
        glVertex3f(-2.1, 0.0   , 0.0) # Side F
        glVertex3f(-1.9, 0.0   , 0.0) # Side F
        glVertex3f(-1.0,-SQRT_3 + 0.1, 0.0) # Side E
        glEnd()
        glBegin(GL_POLYGON)
        glVertex3f(-2.1, 0.0   , 0.0) # Side F
        glVertex3f(-1.0, SQRT_3 + 0.1, 0.0) # Side A
        glVertex3f(-1.0, SQRT_3 - 0.1, 0.0) # Side A
        glVertex3f(-1.9, 0.0   , 0.0) # Side F
        glEnd()
        glEndList()    # dlHLHex

    def highlightHex(self, world_x, world_y):
        """
        Method that highlights a selected hex.
        Algorithm from http://www.gamedev.net/reference/articles/article1800.asp

        world_x: X-Coordinate of point in the hex to highlight
        world_y: Y-Coordinate of point in the hex to highlight
        """
        global SQRT_3, SQRT_3_2, HEX_M

        x_section = int(world_x / 3)
        y_section = int(world_y / SQRT_3_2)

        x_sectpxl = world_x - x_section * 3
        y_sectpxl = world_y - y_section * SQRT_3_2

        if x_section % 2:                               # Type A
            if x_sectpxl < (1 - y_sectpxl * HEX_M):     # Left Bottom
                hex = (x_section - 1, y_section - 1)
            elif x_sectpxl < (y_sectpxl * HEX_M - 1):   # Left Top
                hex = (x_section - 1, y_section)
            else:                                       # Right Area
                hex = (x_section, y_section)
        else:                                           # Type B
            if y_sectpxl >= SQRT_3:                     # Top Half
                if x_sectpxl < (2 - y_sectpxl * HEX_M):
                    hex = (x_section - 1, y_section)    # Top Left
                else:
                    hex = (x_section, y_section)        # Top Right
            else:                                       # Bottom Half
                if x_sectpxl < (y_sectpxl * HEX_M):
                    hex = (x_section - 1, y_section)    # Bottom Left
                else:
                    hex = (x_section, y_section - 1)    # Botom Right

        # Only highlight inside world
        if 0 <= hex[0] < self.x and 0 <= hex[1] < self.y:
            if not self.activeHex or hex != self.activeHex:
                self.highlightDict[hex] = 0.2
                self.activeHex = hex
        else:
            self.activeHex = None

    def selectActiveHex(self):
        """ Method called from Mouse handler when mouse button is pressed """
        if self.activeHex is None:
            self.selectedHex = None
            self.selectedShip = None
            return
        # Deselect if clicking a selected hex
        if self.activeHex == self.selectedHex:
            self.selectedHex = None
            self.selectedShip = None
        else:
            self.selectedHex = self.activeHex
            self.selectedShip = None
            for shipname, ship in self.shipDict.items():
                if ship.x == self.selectedHex[0] and \
                   ship.y == self.selectedHex[1]:
                    self.selectedShip = ship
            
    def glLoadTextures(self):
        """ Method loading textures """
        texturefile = os.path.join('data','nehe.bmp')
        textureSurface = pygame.image.load(texturefile)
        textureData = pygame.image.tostring(textureSurface, "RGBX", 1)

        glBindTexture(GL_TEXTURE_2D, self.textures[0])
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, textureSurface.get_width(),
                    textureSurface.get_height(), 0,
                    GL_RGBA, GL_UNSIGNED_BYTE, textureData )
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)


    def tick(self):
        """
          Updates time dependent states.
        """
        for hex, hv in self.highlightDict.items():
            if hex == self.activeHex:
                if hv < 0.7:
                    self.highlightDict[hex] += 0.036
            else:
                if hv < 0.1:
                    try:
                        del self.highlightDict[hex]
                    except KeyError: pass
                else:
                    self.highlightDict[hex] -= 0.024

    def paint(self):
        """
          Paints the world and the highlighted hexes
        """
        global SQRT_3, SQRT_3_2

        # Paint Hex-field
        glCallList(self.dlHex)

        # Paint all highlights
        for hex, hv in self.highlightDict.items():
            glPushMatrix()
            glColor3f(hv, hv, hv)
            if hex[0] % 2:
                glTranslatef(hex[0] * 3, hex[1] * SQRT_3_2, -0.05)
            else:
                glTranslatef(hex[0] * 3, SQRT_3 + hex[1] * SQRT_3_2, -0.05)
            glCallList(self.dlHLHex)
            glPopMatrix()

        # Paint selected hex
        if self.selectedHex:
            glPushMatrix()
            glColor3f(1, 1, 1)
            if self.selectedHex[0] % 2:
                glTranslatef(self.selectedHex[0] * 3, 
                    self.selectedHex[1] * SQRT_3_2, 0.05)
            else:
                glTranslatef(self.selectedHex[0] * 3,
                    SQRT_3 + self.selectedHex[1] * SQRT_3_2, 0.05)
            glCallList(self.dlSelHex)
            if self.selectedShip:
                self.textg24.glPrint(str(self.selectedShip.x))  
            glPopMatrix()

        # Paint Ships
        for name, ship in self.shipDict.items():
            ship.paint()


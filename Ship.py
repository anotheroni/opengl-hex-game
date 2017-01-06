from OpenGL.GL import *
from math import sqrt

SQRT_3 = sqrt(3.0)
SQRT_3_2 = SQRT_3 * 2

class Ship():

    x = 0
    y = 0
    a = 0

    mvpoints_total = 0
    mvpoints = 0

    weapons = {}
   
    def __init__(self, x, y, a, mp, texture):

        self.x = x
        self.y = y
        self.a = a

        self.mvpoints_total = mp

        # "Ship" Polygon
#        glLoadIdentity()
        self.dlist = glGenLists(1)         # Get the next Display List ID
        glNewList(self.dlist, GL_COMPILE) # Creates a display list(name, mode)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glNormal3f(0.0, 0.0, 1.0)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-1.5, -1.5, 0.1)
        glTexCoord2f(1.0, 0.0)
        glVertex3f( 1.5, -1.5, 0.1)
        glTexCoord2f(1.0, 1.0)
        glVertex3f( 1.5, 1.5, 0.1)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-1.5, 1.5, 0.1)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glEndList()    # dlist

    def newround(self):
        self.mvpoints = self.mvpoints_total

    def paint(self):
        glPushMatrix()
        if self.x % 2:
            glTranslatef(self.x * 3, self.y * SQRT_3_2, 0.0)
        else:
            glTranslatef(self.x * 3, SQRT_3 + self.y * SQRT_3_2, 0.0)
        glRotatef(-self.a * 60, 0.0, 0.0, 1.0)
        glCallList(self.dlist)
        glPopMatrix()

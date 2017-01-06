from OpenGL.GL import *
import pygame

class GLText(object):
    """ Only create one GLText object """

    def __init__(self, fontname=None, size=16, scale=0.1, color=(0,0,0),
            antialias=True):

        # Get font from pygame
        __fontObj = pygame.font.Font(fontname, size)

        # Allocate displays lists for the alphabet
        self.list_base = glGenLists (128)

        # Create each character display list.
        for i in xrange (32,128):
            #make_dlist (ft, i, self.m_list_base, self.textures);
            # Create a new Surface with the specified char rendered on it
            image = __fontObj.render(chr(i), antialias, color)
            height = image.get_height()
            width = image.get_width()
            # OpenGL requires textures to have a size that is a factor of 2
            h = 16
            while(h < height):
                h = h*2
            w = 16
            while(w < width):
                w = w*2
            # Setup texture parameters
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )

            # Create the texture itself
            emptyList = "\x00" * w*h*4
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0,
                    GL_RGBA, GL_UNSIGNED_BYTE, emptyList)
            textureData = pygame.image.tostring(image, "RGBA", 1)
            glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, width, height,
                    GL_RGBA, GL_UNSIGNED_BYTE, textureData)

            # Build the Display List
            glNewList(self.list_base + i, GL_COMPILE)

            # Special case for space, no need to paint a texture
            if i == ord(" "):
                glTranslatef(width * scale, 0, 0)
                glEndList()
            else:
                glBindTexture(GL_TEXTURE_2D, texture_id)
                # Account for the fact that textures are filled with empty
                # padding space. Calculate what portion of the texture is used
                # by the actual character. Only reference the parts of the
                # texture that contain the character itself in the quad.
                x = float(width) / float(w)
                y = float(height) / float(h)

                # Draw the texturemaped quad.
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0), glVertex2f(0, 0)
                glTexCoord2f(0, y), glVertex2f(0, height * scale)
                glTexCoord2f(x, y), glVertex2f(width * scale, height * scale)
                glTexCoord2f(x, 0), glVertex2f(width * scale, 0)
                glEnd()

                # Since rendering one char at a time the "pen" needs to be
                # andvanced. This is imperfect.
                glTranslatef((width + 0.75) * scale, 0, 0)
                glEndList()


    def glPrint(self, string):
        if string == None:
            return
        if string == "":
            return
        glListBase(self.list_base)
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        glCallLists(string)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
    

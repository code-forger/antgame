import os

import renderer
import engine
import brain
import gui
import pygame
import pygtk
pygtk.require('2.0')
import gobject
import gtk
import gtk.glade
print "imports done"

WINX = 400
WINY = 200


def window_main_destroy(widget, data=None):
	gtk.main_quit()

window_main_layout = "window.glade"
window_main_layout_tree = gtk.glade.XML(window_main_layout)
get_widget = window_main_layout_tree.get_widget

window_main = get_widget("window_main")
window_main.connect("destroy", window_main_destroy)


window_main.connect('delete-event', gtk.main_quit)
window_main.set_resizable(False)

get_widget("surface_pygame").set_app_paintable(True)
get_widget("surface_pygame").realize()
window_main.show_all()

# Force SDL to write on our drawing area
os.putenv('SDL_WINDOWID', str(get_widget("surface_pygame").window.xid))

# We need to flush the XLib event loop otherwise we can't
# access the XWindow which set_mode() requires
gtk.gdk.flush()

pygame.init()
pygame.display.set_mode((WINX, WINY), 0, 0)
screen = pygame.display.get_surface()

image_surface = pygame.surface.Surface((100,100));
image_surface.fill((255,0,0))
screen.blit(image_surface, (0, 0))

gobject.idle_add(pygame.display.update)



gtk.main()
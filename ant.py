import renderer
import engine
import brain
import gui
import pygame
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
print "imports done"

def window_main_destroy(widget, data=None):
	gtk.main_quit()

window_main_layout = "window.glade"
window_main_layout_tree = gtk.glade.XML(window_main_layout)
get_widget = window_main_layout_tree.get_widget

window_main = get_widget("window_main")
window_main.connect("destroy", window_main_destroy)

window_main.show()
gtk.main()
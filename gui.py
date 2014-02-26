import renderer
import runner
import engine
import brain
import gui
import pygame
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import glib
print "imports done"

class Gui:
	def __init__(self):
		gtk.threads_init()

		def window_main_destroy(widget, data=None):
			gtk.main_quit()

		def print_message(widget, data=None):
			print("message")

		def message_to_generate_world(widget, data=None):
			messages_to_engine.append(["generate world"])
			print messages_to_engine

		def message_to_load_world(widget, data=None):
			messages_to_engine.append(["load world", widget.get_filename()])

		def message_to_load_red_brain(widget, data=None):
			messages_to_engine.append(["load brain", widget.get_filename(), "red"])

		def message_to_load_black_brain(widget, data=None):
			messages_to_engine.append(["load brain", widget.get_filename(), "black"])

		def message_to_start_runner(widget, data=None):
			messages_to_runner.append(["run"])

		def message_to_stop_runner(widget, data=None):
			messages_to_runner.append(["stop"])

		def message_to_speed_runner(range, scroll, value, data=None):
			messages_to_runner.append(["speed", int(value)])
			print value

		def message_to_step_engine(widget, data=None):
			messages_to_engine.append(["step world"])


		window_main_layout = "window.glade"
		window_main_layout_tree = gtk.glade.XML(window_main_layout)
		get_widget = window_main_layout_tree.get_widget

		window_main = get_widget("window_main")
		window_main.connect("destroy", window_main_destroy)
		
		stat_controls = ["current_step_of_game",
					     "red_alive",
					     "black_alive",
					     "red_dead_redemption",
					     "black_dead",
					     "red_carrying",
					     "black_carrying",
					     "red_stored",
					     "black_stored"]

		stats = {}
		for name in stat_controls:
			stats[name] = get_widget("label_"+name)



		get_widget("button_generate_world").connect("clicked", message_to_generate_world)

		get_widget("file_chooser_load_world").connect("file-set", message_to_load_world)

		get_widget("file_chooser_red_brain").connect("file-set", message_to_load_red_brain)

		get_widget("file_chooser_black_brain").connect("file-set", message_to_load_black_brain)

		get_widget("button_start_game").connect("clicked", message_to_start_runner)

		get_widget("button_step_game").connect("clicked", message_to_step_engine)		

		get_widget("button_pause_game").connect("clicked", message_to_stop_runner)

		get_widget("slider_steps_per_sec").connect("change-value", message_to_speed_runner)



		self.label_details_of_world = get_widget("label_details_of_world")
		self.change_world_details("hello")
		# get_widget("file_chooser_load_world")

		# get_widget("button_generate_world")




		messages_to_engine = []
		messages_to_runner = []
		game_engine = engine.Engine(0,messages_to_engine, self)
		game_engine.start()

		runner_speed = 1
		engine_runner = runner.Runner(messages_to_runner, messages_to_engine)
		engine_runner.start()

		window_main.show()
		gtk.main()
		
	def change_world_details(self, message):
		gtk.idle_add(self.label_details_of_world.set_text, message)

	def change_brain_details(self, message, brain):
		exec("gtk.idle_add(self.label_details_of_" + brain + "brain.set_text, message)")

	def change_game_stats(self, stats):
		gtk.idle_add(self.stat_controls["current_step_of_game"].set_text, "step: " + stats["current_step_of_game"])
		for name in stat_controls.keys():
			if name == "current_step_of_game":
				continue
			gtk.idle_add(self.stat_controls["name"].set_text, stats["name"])


if __name__ == "__main__":
	gui = gui.Gui()
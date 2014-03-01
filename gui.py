import renderer
import runner
import engine
import brain
import gui
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import glib

class Gui:
	def __init__(self):
		gtk.threads_init()

		def window_main_destroy(widget, data=None):
			gtk.main_quit()

		def message_to_generate_world(widget, data=None):
			messages_to_engine.append(["generate world"])

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

		self._stats = {}
		for name in stat_controls:
			self._stats[name] = get_widget("label_"+name)



		get_widget("button_generate_world").connect("clicked", message_to_generate_world)

		get_widget("file_chooser_load_world").connect("file-set", message_to_load_world)

		get_widget("file_chooser_red_brain").connect("file-set", message_to_load_red_brain)

		get_widget("file_chooser_black_brain").connect("file-set", message_to_load_black_brain)

		get_widget("button_start_game").connect("clicked", message_to_start_runner)

		get_widget("button_step_game").connect("clicked", message_to_step_engine)		

		get_widget("button_pause_game").connect("clicked", message_to_stop_runner)

		get_widget("slider_steps_per_sec").connect("change-value", message_to_speed_runner)


		self.label_details_of_world = get_widget("label_details_of_world")

		self.label_details_of_red_brain = get_widget("label_details_of_red_brain")
		self.label_details_of_black_brain = get_widget("label_details_of_black_brain")

		messages_to_engine = []
		self._messages_to_runner = messages_to_runner = []
		messages_between_engine_and_renderer = []
		game_engine = engine.Engine(0,messages_to_engine, messages_between_engine_and_renderer, self)
		game_engine.start()

		world_renderer = renderer.Renderer(messages_between_engine_and_renderer)
		world_renderer.start()
		runner_speed = 1
		engine_runner = runner.Runner(messages_to_runner, messages_to_engine)
		engine_runner.start()

		messages_to_engine.append(["load world", "3.world"])
		messages_to_engine.append(["load brain", "cleverbrain1.brain", "red"])
		messages_to_engine.append(["load brain", "cleverbrain1.brain", "black"])

		window_main.show()

		window_main.set_keep_above(True)
		gtk.main()
		
	def change_world_details(self, message):
		gtk.idle_add(self.label_details_of_world.set_text, message)

	def change_brain_details(self, message, brain="red"):
		exec("gtk.idle_add(self.label_details_of_" + brain + "_brain.set_text, message)")

	def change_game_stats(self, stats):
		if stats["current_step_of_game"] == 30000:
			gtk.idle_add(self._stats["current_step_of_game"].set_text, "step: " + str(stats["current_step_of_game"]) + "! Game Over!")
			self._messages_to_runner.append(["stop"])
		else:
			gtk.idle_add(self._stats["current_step_of_game"].set_text, "step: " + str(stats["current_step_of_game"]))
		for name in self._stats.keys():
			if name == "current_step_of_game":
				continue
			gtk.idle_add(self._stats[name].set_text, str(stats[name]))


if __name__ == "__main__":
	gui = gui.Gui()
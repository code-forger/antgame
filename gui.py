import renderer
import runner
import engine
import brain
import tournament
import gui
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import glib

import math

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

		def message_to_load_theme(widget, data=None):
			print "THIS"
			messages_between_engine_and_renderer.append(["load theme", widget.get_filename()])


		self._num_of_worlds_remaining = 0
		self._num_of_players_remaining = 0



		def tournament_cancel_world(widget, data=None):
			world_num = int(widget.get_name().split("_")[-1])
			self._load_world_buttons[world_num].set_sensitive(True)
			self._generate_world_buttons[world_num].set_sensitive(True)
			self._num_of_worlds_remaining += 1
			tournament_setup_complete()

		def tournament_cancel_player(widget, data=None):
			world_num = int(widget.get_name().split("_")[-1])
			self._load_brain_buttons[world_num].set_sensitive(True)
			self._num_of_players_remaining += 1
			tournament_setup_complete()


		def tournament_message_to_generate_world(widget, data=None):
			widget.set_sensitive(False)
			self._num_of_worlds_remaining -= 1
			world_num = int(widget.get_name().split("_")[-1])
			self._load_world_buttons[world_num].set_sensitive(False)
			pairings = (self._num_of_players * (self._num_of_players-1)/2)

			offsett = world_num*pairings
			tournament_messages_to_engine.append(["generate world", str(offsett)])
			for x in range(pairings):
				tournament_messages_to_engine.append(["load world", "generated.world",str(offsett + x)])

			tournament_setup_complete()

		def tournament_message_to_load_world(widget, data=None):
			widget.set_sensitive(False)
			
			self._num_of_worlds_remaining -= 1
			world_num = int(widget.get_name().split("_")[-1])
			self._generate_world_buttons[world_num].set_sensitive(False)
			pairings = (self._num_of_players * (self._num_of_players-1)/2)

			offsett = world_num*pairings
			for x in range(pairings):
				tournament_messages_to_engine.append(["load world", widget.get_filename(), str(offsett + x)])
			tournament_setup_complete()

		def tournament_message_to_load_brain(widget, data=None):
			widget.set_sensitive(False)
			self._num_of_players_remaining -= 1
			player_num = int(widget.get_name().split("_")[-1]) + 1
			print "player_num ", player_num
			num_of_red_games = self._num_of_players - player_num
			pairings = (self._num_of_players * (self._num_of_players-1)/2)
			print pairings
			for x in range(self._num_of_worlds):
				offset = (pairings * x)
				for oponents in range(player_num-1):
					offset += self._num_of_players - (oponents + 1)
				for game in range(num_of_red_games):
					print "pushing red brain to game ", game + offset
					tournament_messages_to_engine.append(["load brain", widget.get_filename(), "red", str(game + offset)])

				num_of_black_games = (self._num_of_players - 1) - num_of_red_games
				offset = (pairings * x)
				for g in range(num_of_black_games):
					internal_offset = player_num - (2 + g)
					print "pushing black brain to game ", internal_offset, offset, internal_offset + offset
					tournament_messages_to_engine.append(["load brain", widget.get_filename(), "black", str(internal_offset + offset)])
					offset += (self._num_of_players - 1) - g
				tournament_setup_complete()


		def tournament_message_to_start_runner(widget, data=None):
			tournament_messages_to_runner.append(["run"])

		def tournament_message_to_stop_runner(widget, data=None):
			tournament_messages_to_runner.append(["stop"])

		def tournament_message_to_speed_runner(range, scroll, value, data=None):
			tournament_messages_to_runner.append(["speed", int(value)])

		def tournament_message_to_step_engine(widget, data=None):
			tournament_messages_to_engine.append(["step world"])

		tournament_messages_to_runner = []
		tournament_messages_to_engine = []
		self._num_of_players = 0
		self._num_of_worlds = 0
		self._generate_world_buttons = []
		self._load_world_buttons = []
		self._load_brain_buttons = []

		def tournament_setup_complete():
			if self._num_of_worlds_remaining == 0 and self._num_of_players_remaining == 0:
				get_tab_tournament_widget("button_start_game").set_sensitive(True)
				get_tab_tournament_widget("button_step_game").set_sensitive(True)
				get_tab_tournament_widget("button_pause_game").set_sensitive(True)
				get_tab_tournament_widget("slider_steps_per_sec").set_sensitive(True)
				get_tab_tournament_widget("spinner_select_tournament").set_sensitive(True)
			else:
				get_tab_tournament_widget("button_start_game").set_sensitive(False)
				get_tab_tournament_widget("button_step_game").set_sensitive(False)
				get_tab_tournament_widget("button_pause_game").set_sensitive(False)
				get_tab_tournament_widget("slider_steps_per_sec").set_sensitive(False)
				get_tab_tournament_widget("spinner_select_tournament").set_sensitive(False)

			if self._num_of_players_remaining == 0 and self._num_of_worlds_remaining == self._num_of_worlds:
				for x in self._load_world_buttons:
					print x
					x.set_sensitive(True)
				for x in self._generate_world_buttons:
					print x
					x.set_sensitive(True)


		def tournament_begin_setup(widget, data=None):
			get_tab_tournament_widget("button_begin_setup").set_sensitive(False)
			self._num_of_players = get_tab_tournament_widget("spinner_select_players").get_value_as_int()
			self._num_of_worlds = get_tab_tournament_widget("spinner_select_worlds").get_value_as_int()

			self._num_of_worlds_remaining = self._num_of_worlds
			self._num_of_players_remaining = self._num_of_players
			
			tournament_game = tournament.Tournament(tournament_messages_to_engine, messages_between_engine_and_renderer, self, self._num_of_worlds*((self._num_of_players-1)*(self._num_of_players)/2))
			tournament_game.start()
			tournament_runner = runner.Runner(tournament_messages_to_runner, tournament_messages_to_engine)
			tournament_runner.start()

			print len(tournament_messages_to_engine), self._num_of_worlds

			for w in range(self._num_of_worlds):
				layout_tree = gtk.glade.XML("world1.glade")
				get = layout_tree.get_widget
				t = get("top")
				get_tab_tournament_widget("worlds_box").pack_start(t)
				get("file_chooser_load_world").set_name("file_chooser_load_world_" + str(w))
				get("file_chooser_load_world").connect("file-set", tournament_message_to_load_world)
				get("file_chooser_load_world").set_sensitive(False)
				self._load_world_buttons.append(get("file_chooser_load_world"))

				get("button_generate_world").set_name("button_generate_world_" + str(w))
				get("button_generate_world").connect("clicked", tournament_message_to_generate_world)
				get("button_generate_world").set_sensitive(False)
				self._generate_world_buttons.append(get("button_generate_world"))

				get("button_cancel").set_name("button_cancel_" + str(w))
				get("button_cancel").connect("clicked", tournament_cancel_world)

			for w in range(self._num_of_players):
				layout_tree = gtk.glade.XML("players.glade")
				get = layout_tree.get_widget
				t = get("top")
				get_tab_tournament_widget("players_box").pack_start(t)

				x = get("file_chooser_player_brain")
				x.set_name("file_chooser_player_brain_" + str(w))
				x.connect("file-set", tournament_message_to_load_brain)

				get("player_label").set_text("Player " + str(w+1))
				get("button_cancel").set_name("button_cancel_" + str(w))
				get("button_cancel").connect("clicked", tournament_cancel_player)
				self._load_brain_buttons.append(x)

		def tournament_game_selected(widget, data=None):
			print "#" * 100
			if int(widget.get_value_as_int()) > (self._num_of_worlds*((self._num_of_players-1)*(self._num_of_players)/2)) - 1:
				widget.set_value((self._num_of_worlds*((self._num_of_players-1)*(self._num_of_players)/2)) - 1)
			messages_between_engine_and_renderer.append(("select_world" , str(widget.get_value_as_int())))
			tournament_messages_to_engine.append(("select_world" , str(widget.get_value_as_int())))




		window_main_layout = "window.glade"
		window_main_layout_tree = gtk.glade.XML(window_main_layout)
		get_widget = window_main_layout_tree.get_widget
		
		tab_1v1_main_layout = "1v1.glade"
		tab_1v1_main_layout_tree = gtk.glade.XML(tab_1v1_main_layout)
		get_tab_1v1_widget = tab_1v1_main_layout_tree.get_widget
		
		tab_tournament_main_layout = "tournament.glade"
		tab_tournament_main_layout_tree = gtk.glade.XML(tab_tournament_main_layout)
		get_tab_tournament_widget = tab_tournament_main_layout_tree.get_widget

		window_main = get_widget("window_main")
		window_main.connect("destroy", window_main_destroy)
		
		notepad = get_widget("tabs")
		
		notepad.append_page(get_tab_1v1_widget("top"), gtk.Label("Classic Mode"))
		notepad.append_page(get_tab_tournament_widget("top"), gtk.Label("Tournament Mode"))
	
		stat_controls = ["current_step_of_game",
					     "red_alive",
					     "black_alive",
					     "red_dead_redemption",
					     "black_dead",
					     "red_carrying",
					     "black_carrying",
					     "red_stored",
					     "black_stored"]	
		tournament_stat_controls = ["current_step_of_game",
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
			self._stats[name] = get_tab_1v1_widget("label_"+name)

		self._tournament_stats = {}
		for name in tournament_stat_controls:
			self._tournament_stats[name] = get_tab_tournament_widget("label_"+name)


		get_widget("theme_chooser").connect("file-set", message_to_load_theme)





		get_tab_1v1_widget("button_generate_world").connect("clicked", message_to_generate_world)
		get_tab_1v1_widget("file_chooser_load_world").connect("file-set", message_to_load_world)
		get_tab_1v1_widget("file_chooser_red_brain").connect("file-set", message_to_load_red_brain)
		get_tab_1v1_widget("file_chooser_black_brain").connect("file-set", message_to_load_black_brain)
		get_tab_1v1_widget("button_start_game").connect("clicked", message_to_start_runner)
		get_tab_1v1_widget("button_step_game").connect("clicked", message_to_step_engine)		
		get_tab_1v1_widget("button_pause_game").connect("clicked", message_to_stop_runner)
		get_tab_1v1_widget("slider_steps_per_sec").connect("change-value", message_to_speed_runner)

		get_tab_tournament_widget("button_start_game").connect("clicked", tournament_message_to_start_runner)
		get_tab_tournament_widget("button_step_game").connect("clicked", tournament_message_to_step_engine)		
		get_tab_tournament_widget("button_pause_game").connect("clicked", tournament_message_to_stop_runner)
		get_tab_tournament_widget("slider_steps_per_sec").connect("change-value", tournament_message_to_speed_runner)
		get_tab_tournament_widget("button_begin_setup").connect("clicked", tournament_begin_setup)
		get_tab_tournament_widget("spinner_select_tournament").connect("value-changed", tournament_game_selected)

		get_tab_tournament_widget("spinner_select_tournament").set_value(0)
		get_tab_tournament_widget("spinner_select_players").set_value(2)
		get_tab_tournament_widget("spinner_select_worlds").set_value(1)

		get_tab_tournament_widget("button_start_game").set_sensitive(False)
		get_tab_tournament_widget("button_step_game").set_sensitive(False)
		get_tab_tournament_widget("button_pause_game").set_sensitive(False)
		get_tab_tournament_widget("slider_steps_per_sec").set_sensitive(False)
		get_tab_tournament_widget("spinner_select_tournament").set_sensitive(False)



		self.label_details_of_world = get_tab_1v1_widget("label_details_of_world")

		self.label_details_of_red_brain = get_tab_1v1_widget("label_details_of_red_brain")
		self.label_details_of_black_brain = get_tab_1v1_widget("label_details_of_black_brain")

		messages_to_engine = []
		self._messages_to_runner = messages_to_runner = []
		messages_between_engine_and_renderer = []
		game_engine = engine.Engine(-1,messages_to_engine, messages_between_engine_and_renderer, self)
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
		if isinstance(stats, int):
			if stats == 30000:
				gtk.idle_add(self._stats["current_step_of_game"].set_text, "Step: " + str(stats) + "! Game Over!")
				self._messages_to_runner.append(["stop"])
			else:
				gtk.idle_add(self._stats["current_step_of_game"].set_text, "Step: " + str(stats))
		else:
			if stats["current_step_of_game"] == 30000:
				gtk.idle_add(self._stats["current_step_of_game"].set_text, "Step: " + str(stats["current_step_of_game"]) + "! Game Over!")
				self._messages_to_runner.append(["stop"])
			else:
				gtk.idle_add(self._stats["current_step_of_game"].set_text, "Step: " + str(stats["current_step_of_game"]))
			for name in self._stats.keys():
				if name == "current_step_of_game":
					continue
				gtk.idle_add(self._stats[name].set_text, str(stats[name]))

		if isinstance(stats, int):
			if stats == 30000:
				gtk.idle_add(self._tournament_stats["current_step_of_game"].set_text, "Step: " + str(stats) + "! Game Over!")
				self._messages_to_runner.append(["stop"])
			else:
				gtk.idle_add(self._tournament_stats["current_step_of_game"].set_text, "Step: " + str(stats))
		else:
			if stats["current_step_of_game"] == 30000:
				gtk.idle_add(self._tournament_stats["current_step_of_game"].set_text, "Step: " + str(stats["current_step_of_game"]) + "! Game Over!")
				self._messages_to_runner.append(["stop"])
			else:
				gtk.idle_add(self._tournament_stats["current_step_of_game"].set_text, "Step: " + str(stats["current_step_of_game"]))
			for name in self._tournament_stats.keys():
				if name == "current_step_of_game":
					continue
				gtk.idle_add(self._tournament_stats[name].set_text, str(stats[name]))


if __name__ == "__main__":
	print "this"
	gui = gui.Gui()
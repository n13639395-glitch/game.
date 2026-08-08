import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.filechooser import FileChooserIconView
from kivy.graphics import Color, Rectangle


class VerticalScoreboard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        # Background
        with self.canvas.before:
            Color(0.05, 0.05, 0.1, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        # Team names
        self.team1_name = TextInput(text="Team 1", font_size=30, size_hint=(1, 0.1))
        self.team2_name = TextInput(text="Team 2", font_size=30, size_hint=(1, 0.1))

        self.add_widget(self.team1_name)
        self.add_widget(self.team2_name)

        # Logos section
        logo_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.25))

        self.team1_logo = Image(source="", size_hint=(0.5, 1))
        self.team2_logo = Image(source="", size_hint=(0.5, 1))

        btn_logo1 = Button(text="Select Team 1 Logo", background_color=(0.2, 0.6, 1, 1))
        btn_logo2 = Button(text="Select Team 2 Logo", background_color=(1, 0.4, 0.2, 1))

        btn_logo1.bind(on_press=lambda x: self.pick_file_logo(self.team1_logo))
        btn_logo2.bind(on_press=lambda x: self.pick_file_logo(self.team2_logo))

        logo_box.add_widget(self.team1_logo)
        logo_box.add_widget(btn_logo1)
        logo_box.add_widget(self.team2_logo)
        logo_box.add_widget(btn_logo2)

        self.add_widget(logo_box)

        # SCORE (GOALS)
        score_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))

        self.team1_goals = 0
        self.team2_goals = 0

        self.score_label = Label(text="Score: 0 - 0", font_size=35, color=(1, 1, 1, 1))

        btn_goal1 = Button(text="Goal T1", background_color=(0.1, 0.7, 0.1, 1))
        btn_goal2 = Button(text="Goal T2", background_color=(0.7, 0.1, 0.1, 1))

        btn_goal1.bind(on_press=self.add_goal_team1)
        btn_goal2.bind(on_press=self.add_goal_team2)

        score_box.add_widget(self.score_label)
        score_box.add_widget(btn_goal1)
        score_box.add_widget(btn_goal2)

        self.add_widget(score_box)

        # Fouls section
        fouls_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))

        self.team1_fouls = 0
        self.team2_fouls = 0

        self.team1_fouls_label = Label(text="Team 1 Fouls: 0", font_size=25, color=(1, 1, 1, 1))
        self.team2_fouls_label = Label(text="Team 2 Fouls: 0", font_size=25, color=(1, 1, 1, 1))

        btn_foul1 = Button(text="Add Foul T1", background_color=(1, 0.2, 0.2, 1))
        btn_foul2 = Button(text="Add Foul T2", background_color=(0.2, 1, 0.2, 1))

        btn_foul1.bind(on_press=self.add_foul_team1)
        btn_foul2.bind(on_press=self.add_foul_team2)

        fouls_box.add_widget(self.team1_fouls_label)
        fouls_box.add_widget(btn_foul1)
        fouls_box.add_widget(self.team2_fouls_label)
        fouls_box.add_widget(btn_foul2)

        self.add_widget(fouls_box)

        # Timer settings
        self.first_half_duration = 5 * 60
        self.second_half_duration = 5 * 60

        self.extra_first = 0
        self.extra_second = 0

        self.current_time = 0
        self.running = False
        self.half = 1

        # Timer label
        self.timer_label = Label(text="00:00", font_size=50, size_hint=(1, 0.15))
        self.add_widget(self.timer_label)

        # Timer control buttons
        control_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))

        btn_start = Button(text="Start", background_color=(0.1, 0.7, 0.1, 1))
        btn_pause = Button(text="Pause", background_color=(0.9, 0.6, 0.1, 1))
        btn_reset = Button(text="Reset", background_color=(0.8, 0.1, 0.1, 1))

        btn_start.bind(on_press=self.start_timer)
        btn_pause.bind(on_press=self.pause_timer)
        btn_reset.bind(on_press=self.reset_timer)

        control_box.add_widget(btn_start)
        control_box.add_widget(btn_pause)
        control_box.add_widget(btn_reset)

        self.add_widget(control_box)

        # Extra time buttons
        extra_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))

        btn_extra1 = Button(text="Extra Time (1st Half)", background_color=(0.3, 0.3, 1, 1))
        btn_extra2 = Button(text="Extra Time (2nd Half)", background_color=(1, 0.3, 0.6, 1))

        btn_extra1.bind(on_press=self.add_extra_first)
        btn_extra2.bind(on_press=self.add_extra_second)

        extra_box.add_widget(btn_extra1)
        extra_box.add_widget(btn_extra2)

        self.add_widget(extra_box)

        # Timer update loop
        Clock.schedule_interval(self.update_timer, 1)

    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    # PICK LOGO FROM FILES
    def pick_file_logo(self, target_logo_widget):
        chooser = FileChooserIconView(path="/sdcard/")

        btn_ok = Button(text="OK", background_color=(0.2, 0.8, 0.2, 1))
        btn_cancel = Button(text="Cancel", background_color=(0.8, 0.2, 0.2, 1))

        btn_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))
        btn_box.add_widget(btn_ok)
        btn_box.add_widget(btn_cancel)

        popup_layout = BoxLayout(orientation='vertical')
        popup_layout.add_widget(chooser)
        popup_layout.add_widget(btn_box)

        popup = Popup(title="Select Logo File",
                      content=popup_layout,
                      size_hint=(0.9, 0.9))

        btn_cancel.bind(on_press=lambda x: popup.dismiss())

        def on_ok(instance):
            selection = chooser.selection
            if not selection:
                self.show_error("No file selected!")
                return

            file_path = selection[0]

            if not file_path.lower().endswith((".png", ".jpg", ".jpeg")):
                self.show_error("Selected file is NOT an image!")
                return

            target_logo_widget.source = file_path
            popup.dismiss()

        btn_ok.bind(on_press=on_ok)
        popup.open()

    # Error popup
    def show_error(self, msg):
        popup = Popup(title="Error",
                      content=Label(text=msg, font_size=20),
                      size_hint=(0.7, 0.3))
        popup.open()

    # GOALS
    def add_goal_team1(self, instance):
        self.team1_goals += 1
        self.update_score()

    def add_goal_team2(self, instance):
        self.team2_goals += 1
        self.update_score()

    def update_score(self):
        self.score_label.text = f"Score: {self.team1_goals} - {self.team2_goals}"

    # Fouls
    def add_foul_team1(self, instance):
        self.team1_fouls += 1
        self.team1_fouls_label.text = f"Team 1 Fouls: {self.team1_fouls}"

    def add_foul_team2(self, instance):
        self.team2_fouls += 1
        self.team2_fouls_label.text = f"Team 2 Fouls: {self.team2_fouls}"

    # Timer controls
    def start_timer(self, instance):
        self.running = True

    def pause_timer(self, instance):
        self.running = False

    def reset_timer(self, instance):
        self.running = False
        self.current_time = 0
        self.half = 1
        self.extra_first = 0
        self.extra_second = 0
        self.update_label()

    # Extra time
    def add_extra_first(self, instance):
        if self.half == 1:
            self.extra_first += 60

    def add_extra_second(self, instance):
        if self.half == 2:
            self.extra_second += 60

    # Timer update
    def update_timer(self, dt):
        if not self.running:
            return

        self.current_time += 1

        if self.half == 1:
            total = self.first_half_duration + self.extra_first
            if self.current_time >= total:
                self.running = False
                self.half = 2
                self.current_time = 0
        else:
            total = self.second_half_duration + self.extra_second
            if self.current_time >= total:
                self.running = False

        self.update_label()

    def update_label(self):
        m = self.current_time // 60
        s = self.current_time % 60
        self.timer_label.text = f"{m:02d}:{s:02d}"


class ScoreboardApp(App):
    def build(self):
        return VerticalScoreboard()


ScoreboardApp().run()

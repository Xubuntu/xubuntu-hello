#!/usr/bin/env python3

import locale
import gettext
import os
import json
import webbrowser
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class ManjaroHello(Gtk.Window):
    def __init__(self):
        # App vars
        self.app = "manjaro-hello"
        # Path vars
        config_path = os.path.expanduser("~") + "/.config/"
        #share_path = "/usr/share/"

        self.preferences_path = config_path + self.app +".json"
        self.desktop_path = os.getcwd() + "/" + self.app + ".desktop" # later use share_path
        self.autostart_path = config_path + "autostart/" + self.app + ".desktop"
        self.icon_path = self.app + ".png"

        # Languages vars
        self.language = locale.getlocale()[0][:2]
        self.default_language = "en"
        self.locale_dir = "locale"

        # Settings vars
        self.preferences = self.get_preferences()
        if not self.preferences:
            self.preferences = {"autostart": os.path.isfile(self.autostart_path)}
            self.save_preferences()

        self.infos = get_infos()

        # Social urls
        self.social_urls = {
            "google+": "https://plus.google.com/118244873957924966264",
            "facebook": "https://www.facebook.com/ManjaroLinux",
            "twitter": "https://twitter.com/ManjaroLinux",
            "reddit": "https://www.reddit.com/r/ManjaroLinux"
        }

        # Init language
        locale.setlocale(locale.LC_ALL, "")
        locale.bindtextdomain(self.app, self.locale_dir)
        gettext.bindtextdomain(self.app, self.locale_dir)
        gettext.textdomain(self.app)

        # Create window
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(self.app)
        self.builder.add_from_file("manjaro-hello.glade")
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("window")

        # Set window subtitle
        self.builder.get_object("headerbar").props.subtitle = self.infos["codename"] + " " + self.infos["release"] + " " + self.infos["arch"]

        # Initialize pages
        for page in ("readme", "release", "involved"):
            self.builder.get_object(page + "text").set_markup(self.read_page(page))

        # Set autostart switcher state
        self.builder.get_object("autostart").set_active(self.preferences["autostart"])

        self.window.show()

    def change_autostart(self, state):
        if state and not os.path.isfile(self.autostart_path):
            try:
                os.symlink(self.desktop_path, self.autostart_path)
            except OSError as e:
                print(e)
        elif not state and os.path.isfile(self.autostart_path):
            try:
                os.unlink(self.autostart_path)
            except OSError as e:
                print(e)
        self.preferences["autostart"] = state
        self.save_preferences()

    def save_preferences(self):
        try:
            with open(self.preferences_path, "w") as f:
                json.dump(self.preferences, f)
        except OSError as e:
            print(e)

    def get_preferences(self):
        try:
            with open(self.preferences_path, "r") as f:
                return json.load(f)
        except OSError as e:
            return None

    def read_page(self, name):
        filename = "pages/{}/{}".format(self.language, name)
        if not os.path.isfile(filename):
            filename = "pages/{}/{}".format(self.default_language, name)

        try:
            with open(filename, "r") as f:
                return f.read()
        except OSError as e:
            return None

    # Handlers
    def on_about_clicked(self, btn):
        dialog = self.builder.get_object("aboutdialog")
        dialog.set_transient_for(self.window)
        dialog.run()
        dialog.hide()

    def on_welcome_btn_clicked(self, btn):
        name = btn.get_name()
        if name == "readmebtn":
            self.builder.get_object("stack").set_visible_child(self.builder.get_object("documentation"))
            self.builder.get_object("documentation").set_current_page(0)
        elif name == "releasebtn":
            self.builder.get_object("stack").set_visible_child(self.builder.get_object("documentation"))
            self.builder.get_object("documentation").set_current_page(1)
        elif name == "involvedbtn":
            self.builder.get_object("stack").set_visible_child(self.builder.get_object("project"))
            self.builder.get_object("project").set_current_page(0)

    def on_social_pressed(self, eventbox, _):
        webbrowser.open_new_tab(self.social_urls[eventbox.get_name()])

    def on_autostart_switched(self, switch, _):
        autostart = True if switch.get_active() else False
        self.change_autostart(autostart)

    def on_delete_window(self, *args):
        Gtk.main_quit(*args)

def get_infos():
    lsb = get_lsb_information()
    infos = {}
    infos["codename"] = lsb.get("CODENAME", 0)
    infos["release"] = lsb.get("RELEASE", 0)
    infos["arch"] = "64-bit" if os.uname()[4] else "32-bit"
    infos["live"] = os.path.isfile("/bootmnt/manjaro") or os.path.isfile("/run/miso/bootmnt/manjaro")

    return infos

def get_lsb_information():
    lsb = {}
    try:
        with open("/etc/lsb-release") as lsb_file:
            for line in lsb_file:
                if "=" in line:
                    var, arg = line.rstrip().split("=")
                    if var.startswith("DISTRIB_"):
                        var = var[8:]
                    if arg.startswith("\"") and arg.endswith("\""):
                        arg = arg[1:-1]
                    if arg:
                        lsb[var] = arg
    except OSError as e:
        print(e)

    return lsb

win = ManjaroHello()
Gtk.main()

import os

from gi.repository import Gdk
import gi
gi.require_version("Gdk", "3.0")


def chkDesktop():
    if "wayland" in os.environ.get("XDG_SESSION_DESKTOP"):
        print("wayland")
        return False
    return True


def get_desktop_size(monitorIndex=-1):
    screen = Gdk.Display.get_default()
    if monitorIndex == -1:
        if screen:
            return (screen.get_default_screen().width(),
                    screen.get_default_screen().height())
    else:
        if screen:
            screen_rect = screen.get_monitor(monitorIndex).get_geometry()
            return (screen_rect.width, screen_rect.height)


def rewind_progress(instance, progress):
    if instance.get_progress() >= 1.0:
        instance.set_progress(0.0)
        instance.set_playing(True)

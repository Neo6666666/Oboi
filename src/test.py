import os, sys

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Gst", "1.0")
gi.require_version('GtkClutter', '1.0')
gi.require_version('ClutterGst', '3.0')
gi.require_version('Clutter', '1.0')

from gi.repository import Gtk, Gdk, GtkClutter, ClutterGst, Clutter, Gst, Gio

from utils import get_desktop_size
from video_wallpaper import VideoWallpaper
from shader_wallpaper import ShaderWallpaper

from OpenGL.GLUT import glutInit, glutMainLoop

if __name__ == '__main__':
    # app = App()
    # app.run(sys.argv)
    # chkDesktop()
    GtkClutter.init()
    ClutterGst.init()
    Gtk.init()
    Gst.init()
    # glutInit()
    size = get_desktop_size(0)
    window = VideoWallpaper(title="Test")
    # window = ShaderWallpaper(title="Test")
    window.move(1920, 0)
    window.set_actors_size(size)
    window.set_default_size(size[0], size[1])
    window.connect('destroy', Gtk.main_quit)
    window.show_all()

    # Clutter.main()
    Gtk.main()

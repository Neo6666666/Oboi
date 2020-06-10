from gi.repository import GtkClutter, ClutterGst, Gdk, Gtk, Clutter
from utils import rewind_progress
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")


class VideoWallpaper(Gtk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.embed = GtkClutter.Embed()
        self.mainActor = self.embed.get_stage()

        self.videoPlayback = ClutterGst.Playback()
        self.videoContent = ClutterGst.Content()
        self.videoPlayback.set_seek_flags(ClutterGst.SeekFlags.ACCURATE)

        self.videoContent.set_player(self.videoPlayback)
        self.videoPlayback.connect("notify::progress", rewind_progress)

        self.set_startup_id('Oboi')
        self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self.set_accept_focus(True)
        self.stick()
        self.set_resizable(False)
        self.set_keep_below(True)
        self.set_decorated(False)

        self.drag_dest_set(Gtk.DestDefaults.MOTION |
                           Gtk.DestDefaults.DROP,
                           None, Gdk.DragAction.MOVE)

        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.SMOOTH_SCROLL_MASK)

        self.mainActor.set_background_color(
            Clutter.color_from_string("#000")[1])
        self.wallpaperActor = Clutter.Actor()

        self.videoPath = "file:///home/qwerty/Downloads/videoplayback.mp4"
        self.videoPlayback.set_uri(self.videoPath)
        print("Video path:", self.videoPlayback.get_uri())
        self.videoPlayback.set_playing(True)
        print("Is paying:", self.videoPlayback.get_playing())
        self.wallpaperActor.set_content(self.videoContent)
        # size = get_desktop_size()

        self.wallpaperActor.set_pivot_point(0.5, 0.5)
        self.wallpaperActor.scale_y = 1
        self.wallpaperActor.scale_x = 1

        self.mainActor.add_child(self.wallpaperActor)
        self.add(self.embed)

    def set_actors_size(self, size: tuple):
        self.wallpaperActor.set_size(size[0], size[1])
        self.mainActor.set_size(size[0], size[1])

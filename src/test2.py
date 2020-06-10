import os
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, Gdk, AppIndicator3


class toolbarShit(Gtk.Application):
    def __init__(self):
        super().__init__()
        # self.builder = Gtk.Builder()
        # self.builder.add_from_file("window.glade")
        #self.builder.get_object("window1")
        self.createAssistant()

        icon = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'images', 'ip_white_1.png')
        self.app_id = 'ip-indicator'
        self.indicator = AppIndicator3.Indicator.new(
            self.app_id, icon, AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        # self.set_type_hint(Gdk.WindowTypeHint.DOCK)
        self.indicator.set_menu(self.build_menu())

    def build_menu(self):
        menu = Gtk.Menu()
        item_refresh = Gtk.MenuItem(label='Refresh')
        item_refresh.connect('activate', self.item_refresh)
        menu.append(item_refresh)
        item_quit = Gtk.MenuItem(label='Quit')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)
        menu.show_all()
        return menu

    def item_refresh(self, _):
        print(_)
        self.window.show_all()

    def quit(self, _):
        Gtk.main_quit()

    def createAssistant(self):
        num_monitors = Gdk.Display.get_n_monitors(Gdk.Display.get_default())
        self.window = Gtk.Assistant()
        self.window.set_default_size(400*num_monitors, 400)
        self.window.set_resizable(False)
        # Page 1
        grid = Gtk.Grid()
        grid.set_halign(Gtk.Align.CENTER)
        grid.set_column_spacing(400/num_monitors)
        main_monitor = Gtk.RadioButton(label='Monitor #1')
        grid.attach(main_monitor, 0, 0, 1, 1)


        print(num_monitors)
        if  num_monitors >= 2:
            for i in range(2, num_monitors+1):
                r = Gtk.RadioButton(label=f'Monitor #{i}', group=main_monitor)
                grid.attach(r, i, 0, i, 1)
        self.window.append_page(grid)
        self.window.set_page_complete(grid, True)

        # Page 2
        grid = Gtk.Grid()
        stack = Gtk.Stack()
        stack.set_vexpand(True)
        stack.set_hexpand(True)
        grid.attach(stack, 0, 1, 1, 1)

        buttonbox = Gtk.ButtonBox()
        buttonbox.set_layout(Gtk.ButtonBoxStyle.CENTER)
        grid.attach(buttonbox, 0, 0, 1, 1)

        stackswitcher = Gtk.StackSwitcher()
        stackswitcher.set_stack(stack)
        grid.attach(stackswitcher, 0, 0, 1, 1)

        label = Gtk.Label('Stack Content on Page')
        name = "label"
        stack.add_named(label, name)

        for page in range(1, 4):
            label = Gtk.Label("Stack Content on Page %i" % (page))
            name = "label%i" % page
            title = "Page %i" % page
            stack.add_titled(label, name, title)

        self.window.append_page(grid)
        self.window.set_page_complete(grid, True)






if __name__ == '__main__':
    Gtk.init()
    w = toolbarShit()
    # w.connect('destroy', Gtk.main_quit)
    # w.move(10, 10)
    # w.show_all()
    Gtk.main()

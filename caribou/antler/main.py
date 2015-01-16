from gi.repository import Caribou, GLib, GObject
from .window import AntlerWindowEntry
from .keyboard_view import AntlerKeyboardView
import sys

class AntlerKeyboardCommand(object):
    def run(self):
        pass

class AntlerKeyboardService(Caribou.KeyboardService, AntlerKeyboardCommand):
    def __init__(self, args=None):
        GObject.GObject.__init__(self)
        self.register_keyboard("Antler")
        self.window = AntlerWindowEntry(AntlerKeyboardView)

    def run(self):
        loop = GObject.MainLoop()
        loop.run()

    def do_show(self, timestamp):
        self.window.show_all()

    def do_hide(self, timestamp):
        self.window.hide()

    def do_set_cursor_location (self, x, y, w, h):
        self.window.set_cursor_location(x, y, w, h)

    def do_set_entry_location (self, x, y, w, h):
        self.window.set_entry_location(x, y, w, h)

    def do_name_lost (self, name):
        sys.stderr.write("Another service acquired %s, quitting..\n" % name)
        sys.exit(0)

if __name__ == "__main__":
    import argparse
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    GLib.set_prgname('antler-keyboard')

    parser = argparse.ArgumentParser(description='antler-keyboard')
    parser.add_argument('-c', '--command', type=str, default='service',
                        help='command (service or preview, default: service)')
    args = parser.parse_args()

    command = globals().get('AntlerKeyboard%s' % args.command.capitalize())
    if command:
        command(args).run()
    else:
        sys.stderr.write("Unknown command: %s\n" % args.command)
        sys.exit(1)

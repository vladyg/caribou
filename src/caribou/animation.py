import clutter, gtk

class AnimatedWindowBase(object):
    def __init__(self, ease=clutter.EASE_IN_QUAD):
        self._actor = clutter.Rectangle()
        self.ease = ease

    def _on_new_frame(self, timeline, timing):
        x, y = self._actor.get_position()
        self.move(int(x), int(y))

    def animated_move(self, x, y):
        orig_x, orig_y = self.get_position()
        self._actor.set_position(orig_x, orig_y)
        self._actor.set_size(self.allocation.width, self.allocation.height)
        animation = self._actor.animate(
            self.ease, 250, "x", x, "y", y)
        timeline = animation.get_timeline()
        timeline.connect('new-frame', self._on_new_frame)
        
        return animation
        
if __name__ == "__main__":
    class AnimatedWindow(gtk.Window, AnimatedWindowBase):
        def __init__(self):
            gtk.Window.__init__(self)
            AnimatedWindowBase.__init__(self)

    aw = AnimatedWindow()
    aw.show_all()
    aw.move(100, 100)
    aw.animated_move(200, 200)
    gtk.main()



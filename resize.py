from __future__ import division
import os
import sys
import PIL.Image
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import (NumericProperty, ReferenceListProperty,
                             ObjectProperty)
from kivy.uix.popup import Popup
from kivy.logger import Logger
try:
    import android
except ImportError:
    android = None

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Resizer(Widget):
    w = NumericProperty(0)
    h = NumericProperty(0)
    expo = ObjectProperty(None)

    def on_resize(self):
        if not hasattr(self, "filename") or not self.filename:
            Popup(title="No File Selected",
                  content=Label(text='Please load a file first.'),
                  size=(250,100), size_hint=(None,None)).open()
            return            
        scale_factor = 2 ** self.expo.value
        quality = int(self.quality.value)
        size = [int(dim * scale_factor) for dim in self.orig_img.size]
        img_resized = self.orig_img.resize(size, PIL.Image.ANTIALIAS)
        basename, ext = os.path.splitext(self.filename)
        savename_template = basename + "_rs%03d" + ext
        i = 1
        while os.path.exists(savename_template % i):
            i += 1
        savename = savename_template % i
        img_resized.save(savename, quality=quality)
        return savename

    def on_resize_and_send(self):
        if not android:
            Popup(title="Cannot Send",
                  content=Label(text='"Resize and Send" functionality not available.'),
                  size=(450,100), size_hint=(None,None)).open()
            return
        savename = self.on_resize()
        if savename:
            android.action_send("image/jpg", filename=savename, subject="Checkout this image", text="see attachment")

    def on_cancel(self):
        sys.exit(0)

    def dismiss_popup(self):
        self._popup.dismiss()

    def set_preset(self, preset):
        self.expo.value = preset

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filenames):
        filename = filenames[0]
        self.intro.text = os.path.normpath(os.path.basename(filename))
        self.filename = os.path.join(path, filename)
        self.orig_img = PIL.Image.open(self.filename)
        self.w, self.h = self.orig_img.size
        self.dismiss_popup()

class ResizeApp(App):
    def build(self):
        return Resizer()



if __name__ == '__main__':
    ResizeApp().run()
    

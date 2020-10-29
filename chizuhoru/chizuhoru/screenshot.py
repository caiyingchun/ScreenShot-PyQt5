import mss, mss.tools
from io import BytesIO


class ScreenshotCLI:

    def shot(self, mon=-1):
        sct = mss.mss()
        display = sct.monitors[mon+1]
        screenshot = sct.grab(display)
        raw_bytes = mss.tools.to_png(screenshot.rgb,
                                     screenshot.size)
        img = BytesIO(raw_bytes)
        return img

    def save(self, image: BytesIO, path: str):
        try:
            with open(path, 'wb') as file:
                file.write(image.getvalue())
        except PermissionError as e:
            print("Could not write to '%s': %s" % (path, e))
            return 1
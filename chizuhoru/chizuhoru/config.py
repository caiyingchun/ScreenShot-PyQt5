from os import path, environ
from os.path import join
import json


class Config:
    def __init__(self):
        _dirpath = path.dirname(path.realpath(__file__))
        self.config_path = join(_dirpath, '../config.json')

        if path.isfile(self.config_path):
            with open(self.config_path, 'r') as file:
                self.data = file.read()
                self.parse = json.loads(self.data)
        else:
            with open(self.config_path, 'w') as file:
                self.parse = {
                    "config":
                        {

                            "default_dir": f"/home/{environ['USER']}/Pictures/Screenshots/",
                            "filename_format": "%Y-%m-%d-%H-%M-%S",
                            "default_delay": 0.5,
                            "icon": "colored",

                            "canvas":
                                {
                                    "last_size": 6,
                                    "last_cap": "round",
                                    "last_joint": "round",
                                    "last_style": "solid",
                                    "last_pen_color": "",
                                    "last_brush_color": "",
                                    "pen_color": "196 31 31 255",
                                    "pen_hsv": "0 0 100",
                                    "pen_sel": "114 27",
                                    "brush_color": "0 0 0 0",
                                    "brush_hsv": "0 0 0",
                                    "brush_sel": "-5 135",
                                    "outline": 'disabled',
                                    "upload_service": "Imgur",
                                    "upload_confirmation": 0,
                                    "magnifier": 1,
                                    "save_action": "dir",
                                    "img_clip": 1
                                },
                            "upload":
                                {
                                    "clipboard_state": 0,
                                    "random_fname_state": 0,
                                    "last_service": "Imgur"
                                },
                            "imgur":
                                {
                                    "client_id": "25b4ba1ecc97502",
                                    "link": "https://api.imgur.com/3/image"
                                },
                            "palette":
                                {
                                    "red": "#C41F1F",
                                    "magenta": "#F230A5",
                                    "yellow": "#DBB126",
                                    "green": "#1DC129",
                                    "blue": "#2288E6",
                                    "white": "#FFFFFF",
                                    "black": "#000000"
                                },
                        },
                }
                file.write(str(json.dumps(self.parse, indent=4)))

    def change_config(self, section, undersection=None, value=None, save_changes=True):
        if undersection:
            self.parse["config"][section][undersection] = value
        else:
            self.parse["config"][section] = value
        if save_changes:
            with open(self.config_path, 'w') as file:
                new_config = str(json.dumps(self.parse, indent=4))
                file.write(new_config)

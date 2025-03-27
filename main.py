from Quartz import CGWindowListCopyWindowInfo, kCGNullWindowID, kCGWindowListOptionAll
import matplotlib.pyplot as plt
from PIL import Image
import os
from uuid import uuid4

gen_filename = lambda : str(uuid4())[-10:] + '.jpg'

def capture_window(window_name):
    window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
    for window in window_list:
        try:
            print(window['kCGWindowName'].lower())
            if window_name.lower() in window['kCGWindowName'].lower():
                filename = gen_filename()
                os.system('screencapture -l %s %s' %(window['kCGWindowNumber'], filename))
                os.remove(filename)
                break
        except:
            pass
    else:
        raise Exception('Window %s not found.'%window_name)

capture_window("рokeммo")
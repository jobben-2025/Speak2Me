import tkinter as tk
from tkinter import Tk
from PIL import Image, ImageTk
#from PIL.Image import Image as ImagePIL
#from PIL.ImageTk import PhotoImage
from pathlib import Path
from threading import Thread, Lock
from itertools import cycle
from typing import Iterable,Iterator
import time


ASSET_BACKGROUND = 'background'
ASSET_BACKGROUND_FRAMES = 'background_frames'

class Animation:
    def __init__(self,name, image_id, frames, fps=1/10):
        self.image_id = image_id
        self.name = name
        self.frames = frames
        self.frame_iterator = cycle(frames)
        self.fps = fps
        self.last_update = float()
        self.running = True
        
    def next_frame(self):
        return next(self.frame_iterator)
    
class AnimatedCanvas(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.animations:dict[int,Animation] = {}
        self.running = True
        self.exit = False
        self.fps = 1/10
        self.thread = Thread(target=self.update_background, daemon=True)
        self.lock = Lock()
        self.after_method = self.master.after_idle
    
    def create_animation(self,*args,image:Image.Image, name=None, fps=1/10, **kwargs):
        img_frames = []
        for i in range(getattr(image,'n_frames', 1)):
            image.seek(i)
            img_frames.append(ImageTk.PhotoImage(image.copy()))
            
        img_name = name or getattr(image,'filename', f'noname_{len(self.animations)+1}')
        img_id = super().create_image(*args, image=img_frames[0], **kwargs)
        ani = Animation(img_name, img_id, img_frames, fps=fps)
        with self.lock:
            self.animations[img_id] = ani
        return img_id, ani
    
    def start_animation(self):
        if not self.thread.is_alive():
            self.running = True
            self.exit = False
            self.thread.start()
    
    def stop_animation(self):
        self.running = False
        self.exit = True
        if self.thread.is_alive():
            self.thread.join(timeout=1)
    
    def pause_animation_toggle(self):
        self.running = not self.running
    
    def update_background(self):
        while not self.exit and self.winfo_exists():
            if self.running:
                #time.sleep(self.fps)
                now = time.time()
                next_frames = {}
                with self.lock:
                    for img_id,ani in self.animations.items():
                        if ani.running and now - ani.last_update >= ani.fps:
                            next_frames[img_id] = ani.next_frame()
                            ani.last_update = now
                            
                #self.master.after_idle(self.update_frames,next_frames)
                """
                """
                match self.after_method:
                    case self.master.after: 
                        self.master.after(0,self.update_frames,next_frames)               
                    case self.master.after_idle: 
                        self.master.after_idle(self.update_frames,next_frames)
            else:
                time.sleep(0.2)
                                    
    def update_frames(self,next_frames:dict):
        if self.running:
            for id,frame in next_frames.items():
                super().itemconfig(id,image=frame)
    
    
    #TESTING STANDALONE ANI UPDATE FROM EXTERNAL THREAD START - PART A
    def after_idle_update(self,img_id):
        while True:
            time.sleep(1/40)
            next_frame = self.animations[img_id].next_frame()
            self.master.after_idle(self.after_idle_update_set, img_id, next_frame)
    
    def after_idle_update_set(self, img_id, frame):
        self.itemconfig(img_id, image=frame)
  
class App:
    
    def __init__(self, root:Tk, asset_paths:dict):
        self.root:Tk = root
        self.asset_paths = asset_paths
        print(">>>>>>>>>>>>>>>>>>>>>>>>", Path.cwd())
        
        self.FB_IMAGE = Image.new('RGB',(500,500), color=(255,0,255))
        self.FB_IMAGE_TK = ImageTk.PhotoImage(self.FB_IMAGE)
 
        self.assets_raw = {
            ASSET_BACKGROUND : self.load_asset_image(ASSET_BACKGROUND)
        }
        
        self.assets_tk = {# IMPORTANT: tk is dumb and doesnt keep track of its own references so keep track here
            ASSET_BACKGROUND        : self.asset_to_TK_asset(ASSET_BACKGROUND),
            #ASSET_BACKGROUND_FRAMES : self.get_tk_frames(self.assets_raw.get(ASSET_BACKGROUND,self.FB_IMAGE))
        }
        
        self.bakani = AnimatedCanvas(self.root, width=800, height=500, bg='black')
        
        self.bakani_id,_ = self.bakani.create_animation(0, 0, anchor='nw', name='backani', fps=1/40,
                                                      image=self.assets_raw.get(ASSET_BACKGROUND, self.FB_IMAGE))
        self.bakani.pack()
        
        self.bakani.start_animation()
              
    def load_asset_image(self,asset) -> Image.Image :
        asset_path = self.asset_paths.get(asset)
        if asset_path == None: return self.FB_IMAGE
        else: 
            try: 
                return Image.open(asset_path)
            except Exception as e:
                print(f'FAIL_LOAD: RAW ASSET: {asset_path} \n {e}')
        return self.FB_IMAGE
    
    def asset_to_TK_asset(self,asset):
        asset_raw_object = None
        if asset not in self.assets_raw:
            print('No appropriate asset to convert')
            return asset_raw_object
        else:
            try: # TK ASSET CONVERSIONS
                asset_raw_object = self.assets_raw.get(asset)
                if isinstance(asset_raw_object, Image.Image): # Pillow Image to ImageTk
                    return ImageTk.PhotoImage(asset_raw_object)
                #... more conversions here 
            except Exception as e:
                print(f'FAIL_CONV: TK ASSET: {asset} \n {e}')
        print(f'Asset: {asset} of type {type(asset_raw_object)} \n has no TK conversion defined')
        return asset_raw_object
    

        
if __name__ == '__main__':
    
    app = App(root=tk.Tk(),
              asset_paths={
                  ASSET_BACKGROUND: Path.cwd() / "python_projects" / "Speak2Me" / 'assets' / 'chatbot_background.gif'
              })
    try:
        app.root.mainloop()
    except KeyboardInterrupt:
        print('bye')
        
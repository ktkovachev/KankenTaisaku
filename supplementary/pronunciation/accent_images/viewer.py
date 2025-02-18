import json
import tkinter
from PIL import Image
from PIL import ImageTk

with open("mappings.json") as f:
    data = json.load(f)

paths = list(data.keys())
# Uncomment to sort by pitch
# paths.sort(key=lambda d: data[d]["pitch"])
# Uncomment to sort by kana
# paths.sort(key=lambda d: data[d]["kana"])

i = 0

def left(*args):
    global i
    i = (i-1) % len(paths)
    update_image()
    print(i)

def right(*args):
    global i
    i = (i + 1) % len(paths)
    update_image()
    print(i)

images = {}
def update_image():
    if i not in images:
        imgfile = Image.open(paths[i])
        imgfile = imgfile.resize((320, 480), resample=Image.Resampling.NEAREST)
        images[i] = imgfile
    imgfile = images[i]
    global photo, kana_label, pitch_label, label
    for widget in root.winfo_children():
        widget.destroy()
    photo = ImageTk.PhotoImage(imgfile)
    kana = data[paths[i]]["kana"]
    pitch = data[paths[i]]["pitch"]
    label = tkinter.Label(root, image=photo)
    label.image = photo
    kana_label = tkinter.Label(root, text=kana, font=("TkDefaultFont", 44))
    pitch_label = tkinter.Label(root, text=pitch, font=("TkDefaultFont", 32))
    filename_text = tkinter.Text(root, height=1, borderwidth=0)
    filename_text.insert(1.0, paths[i])
    label.pack()
    kana_label.pack()
    pitch_label.pack()
    filename_text.pack()

    
root = tkinter.Tk()
root.geometry("600x700")
update_image()
root.bind("<Left>", left)
root.bind("<Right>", right)
root.focus_set()

root.mainloop()
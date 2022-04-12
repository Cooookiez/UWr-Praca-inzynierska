import tkinter as tk
import time
from PIL import ImageTk, Image

Tk = tk.Tk()

Tk.title("Face Recognition")

Tk.configure(
    background='#ff0000'
    )

a = input("Nowy kolor")
Tk.configure(
    background='#00ff00'
    )

a = input("Image is next")
image1 = Image.open("../../screen_images/Unknow person.png")
image2 = ImageTk.PhotoImage(image1)
image_label = tk.Label(Tk, image=image2)
image_label.place(x=0, y=0)

a = input("And add some text")
text = tk.Label(Tk, text="Hello World")
text.place(x=200, y=200)

a = input("FullScreen")
Tk.attributes("-fullscreen", True)

Tk.mainloop()
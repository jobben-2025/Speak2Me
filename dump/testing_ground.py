import tkinter as tk

root = tk.Tk()
#frame = tk.Frame(root)
##frame.pack()

#root.iconbitmap("pat(h .ico file")

#button_quit = Button(root, text="EXIT", command=root.quit)
#button_quit.pack()

#frame = LabelFrame(root, text="Chatbox", padx=5, pady=5)
#frame.pack(padx=10, pady=10)
#b = Button(frame, text="Send")
#b.pack()


#header_label = tk.Label(
#        root, text="Speak2Me Chatbot",
#        font=("Arial", 28, "bold"),
#        bg="#6200FF", fg="white", padx=10, pady=10
#        )
#header_label.pack()


#chat_frame = tk.Frame(root, bd=5, relief="raised")
#chat_frame.place(relwidth=1, relheight=0.3, rely=0.1)

#text_items = []
#y_offset = 10

canvas = tk.Canvas(root, bg="black", highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

e = tk.Entry(canvas, width=50)
e.pack()
e.get()

def myClick():
    myLabel = tk.Label(root, text="Your promt: " + e.get())
    myLabel.pack()

button_promt = tk.Button(root, text="Enter your promt", command=myClick)
button_promt.pack()

#user_input = tk.Entry(root, font=("Arial", 14))
#user_input.place(relwidth=1.0, relheight=0.07, rely=0.82, relx=0.02)
#def on_send(event=None):
#    ...
#user_input.bind("<Return>", on_send)

#send_btn = tk.Button(root, text="Send", font=("Arial", 14), command=on_send)
#send_btn.place(relx=0.85, rely=0.82, relwidth=0.12, relheight=0.07)



root.mainloop()
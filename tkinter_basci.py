import tkinter as tk
window=tk.Tk() # Create a window object

# Setup window
window.title("Dong dep trai") # Name
window.geometry("500x200") # Size start
window.resizable(width=False,height=False)  

container=tk.Frame()

# Parren
lable_username=tk.Label(container,text='username')
entry_username=tk.Entry(container)
btn_username=tk.Button(container,text='Login')

# Display method: pack(): Tự động căn giữa
lable_username.pack()
entry_username.pack()
btn_username.pack()
container.pack()

#Run the even loop
window.mainloop()

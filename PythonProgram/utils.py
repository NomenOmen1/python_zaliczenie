
#Pozycjonowanie okienek
# def place_window(window, x=300, y=200):
#     window.update_idletasks()
#     width = window.winfo_width()
#     height = window.winfo_height()
#     screen_width = window.winfo_screenwidth()
#     screen_height = window.winfo_screenheight()
#
#     x = (screen_width - width) // 2
#     y = (screen_height - height) // 3
#
#     window.geometry(f"{width}x{height}+{x}+{y}")

def place_window(window, width=600, height=400):

    window.geometry(f"{width}x{height}")

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 3

    window.geometry(f"{width}x{height}+{x}+{y}")


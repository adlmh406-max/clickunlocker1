# main.py - Click Unlocker Professional License System
import requests
import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import platform
import tempfile
import shutil
import threading
import time
import sys
import hashlib

# ============== الإعدادات ==============
SERVER_URL = "https://clickunlocker1.onrender.com/verify-key"
FILE_NAME = "clickunlocker.exe"

# إخفاء نافذة CMD
if platform.system() == "Windows":
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

# ============== دوال النظام ==============
def get_hwid():
    if platform.system() == "Windows":
        try:
            hwid = subprocess.check_output("wmic csproduct get UUID", shell=True).decode().split("\n")[1].strip()
            return hashlib.sha256(hwid.encode()).hexdigest()[:32]
        except:
            try:
                import uuid
                return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()[:32]
            except:
                return "UNKNOWN"
    return "OTHER"

def verify_key(key):
    hwid = get_hwid()
    try:
        response = requests.post(SERVER_URL, json={"key": key, "hwid": hwid}, timeout=10)
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": "Cannot connect to server"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def launch_file():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), FILE_NAME)
    if not os.path.exists(file_path):
        messagebox.showerror("Error", f"{FILE_NAME} not found!")
        return False
    try:
        temp_dir = tempfile.mkdtemp(prefix="cl_")
        temp_file = os.path.join(temp_dir, FILE_NAME)
        shutil.copy2(file_path, temp_file)
        
        if platform.system() == "Windows":
            os.startfile(temp_file)
        else:
            subprocess.Popen(["open", temp_file])
        
        def cleanup():
            time.sleep(5)
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
        
        threading.Thread(target=cleanup, daemon=True).start()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch: {str(e)}")
        return False

def activate():
    key = key_entry.get().strip()
    if not key:
        messagebox.showerror("Error", "Please enter your license key")
        return
    
    activate_btn.config(state="disabled", text="⏳ VERIFYING...")
    status_label.config(text="Connecting to server...", fg="#ffaa00")
    
    def check():
        result = verify_key(key)
        root.after(0, lambda: process_result(result))
    
    threading.Thread(target=check, daemon=True).start()

def process_result(result):
    status = result.get("status")
    
    if status == "valid":
        status_label.config(text="✓ LICENSE VERIFIED! Launching...", fg="#00ff00")
        root.update()
        if launch_file():
            messagebox.showinfo("Success", "Click Unlocker is starting!")
            root.destroy()
        else:
            status_label.config(text="✗ Failed to launch", fg="#ff0000")
            activate_btn.config(state="normal", text="ACTIVATE")
    elif status == "wrong_device":
        status_label.config(text="✗ License locked to another device", fg="#ff0000")
        messagebox.showerror("Error", "This key is already used on another device!")
        activate_btn.config(state="normal", text="ACTIVATE")
    elif status == "expired":
        status_label.config(text="✗ License expired", fg="#ff0000")
        messagebox.showerror("Error", "Your license has expired!")
        activate_btn.config(state="normal", text="ACTIVATE")
    elif status == "invalid":
        status_label.config(text="✗ Invalid license key", fg="#ff0000")
        messagebox.showerror("Error", "Invalid license key!")
        activate_btn.config(state="normal", text="ACTIVATE")
    else:
        status_label.config(text="⚠ Server error", fg="#ffaa00")
        messagebox.showerror("Error", "Cannot connect to license server!\nPlease check your internet connection.")
        activate_btn.config(state="normal", text="ACTIVATE")

def cancel():
    if messagebox.askyesno("Exit", "Exit Click Unlocker?"):
        root.destroy()

# ============== الواجهة الرئيسية ==============
root = tk.Tk()
root.title("Click Unlocker")
root.geometry("620x480")
root.configure(bg="#000000")
root.resizable(False, False)

# توسيط النافذة
root.update_idletasks()
x = (root.winfo_screenwidth() // 2) - 310
y = (root.winfo_screenheight() // 2) - 240
root.geometry(f"620x480+{x}+{y}")

# المحتوى الرئيسي
main_frame = tk.Frame(root, bg="#000000")
main_frame.pack(expand=True, fill="both", padx=0, pady=0)

# العنوان
title = tk.Label(
    main_frame,
    text="CLICK UNLOCKER",
    font=("Segoe UI", 36, "bold"),
    fg="#ff0000",
    bg="#000000"
)
title.pack(pady=(50, 5))

# خط أحمر
line = tk.Frame(main_frame, height=2, width=350, bg="#ff0000")
line.pack(pady=(0, 20))

# نص ثانوي
sub = tk.Label(
    main_frame,
    text="Professional License System",
    font=("Segoe UI", 11),
    fg="#888888",
    bg="#000000"
)
sub.pack(pady=(0, 40))

# تسمية الحقل
label = tk.Label(
    main_frame,
    text="ENTER YOUR LICENSE KEY",
    font=("Segoe UI", 10, "bold"),
    fg="#ff0000",
    bg="#000000"
)
label.pack(pady=(0, 10))

# حقل الإدخال
key_entry = tk.Entry(
    main_frame,
    font=("Consolas", 13),
    width=32,
    justify="center",
    bg="#111111",
    fg="#ffffff",
    insertbackground="#ff0000",
    relief="flat",
    bd=0,
    highlightthickness=0
)
key_entry.pack(ipady=10, pady=(0, 30))

# أزرار
buttons_frame = tk.Frame(main_frame, bg="#000000")
buttons_frame.pack(pady=(0, 30))

activate_btn = tk.Button(
    buttons_frame,
    text="ACTIVATE",
    font=("Segoe UI", 12, "bold"),
    bg="#ff0000",
    fg="#ffffff",
    activebackground="#cc0000",
    activeforeground="#ffffff",
    relief="flat",
    cursor="hand2",
    width=14,
    command=activate
)
activate_btn.pack(side="left", padx=10, ipady=8)

cancel_btn = tk.Button(
    buttons_frame,
    text="CANCEL",
    font=("Segoe UI", 12, "bold"),
    bg="#000000",
    fg="#ff0000",
    activebackground="#1a0000",
    activeforeground="#ff3333",
    relief="flat",
    cursor="hand2",
    width=14,
    command=cancel
)
cancel_btn.pack(side="left", padx=10, ipady=8)

# حالة التحقق
status_label = tk.Label(
    main_frame,
    text="",
    font=("Segoe UI", 10),
    fg="#ffaa00",
    bg="#000000"
)
status_label.pack(pady=(0, 20))

# تذييل
footer = tk.Label(
    main_frame,
    text="© 2026 Click Unlocker - All Rights Reserved",
    font=("Segoe UI", 8),
    fg="#444444",
    bg="#000000"
)
footer.pack(side="bottom", pady=20)

# ربط Enter
root.bind('<Return>', lambda e: activate())

# تأثيرات hover
def on_enter_activate(e):
    activate_btn.config(bg="#cc0000")

def on_leave_activate(e):
    activate_btn.config(bg="#ff0000")

def on_enter_cancel(e):
    cancel_btn.config(fg="#ff3333")

def on_leave_cancel(e):
    cancel_btn.config(fg="#ff0000")

activate_btn.bind("<Enter>", on_enter_activate)
activate_btn.bind("<Leave>", on_leave_activate)
cancel_btn.bind("<Enter>", on_enter_cancel)
cancel_btn.bind("<Leave>", on_leave_cancel)

# تشغيل التطبيق
root.mainloop()

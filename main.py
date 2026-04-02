# main.py - مع دعم ملف config خارجي
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
import json

FILE_NAME = "clickunlocker.exe"
CONFIG_FILE = "config.json"  # ملف الإعدادات الخارجي

def load_server_url():
    """تحميل رابط السيرفر من ملف خارجي"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                url = config.get('server_url')
                if url:
                    return url
    except:
        pass
    
    # الرابط الافتراضي (يتغير بعد الاستضافة)
    return "https://your-app.onrender.com/verify-key"

def save_server_url(url):
    """حفظ رابط السيرفر في ملف خارجي"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'server_url': url}, f, indent=4)
        return True
    except:
        return False

# تحميل الرابط
SERVER_URL = load_server_url()

# ============== باقي الكود كما هو ==============
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
    except:
        return {"status": "error"}

def launch_file():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), FILE_NAME)
    if not os.path.exists(file_path):
        messagebox.showerror("Error", f"{FILE_NAME} not found!")
        return False
    try:
        temp_dir = tempfile.mkdtemp(prefix="cl_")
        temp_file = os.path.join(temp_dir, FILE_NAME)
        shutil.copy2(file_path, temp_file)
        os.startfile(temp_file)
        threading.Thread(target=lambda: (time.sleep(5), shutil.rmtree(temp_dir, ignore_errors=True)), daemon=True).start()
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed: {str(e)}")
        return False

def open_settings():
    """نافذة إعدادات لتغيير رابط السيرفر"""
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("500x250")
    settings_window.configure(bg="#000000")
    settings_window.resizable(False, False)
    
    tk.Label(
        settings_window,
        text="Server URL",
        font=("Segoe UI", 12, "bold"),
        fg="#ff0000",
        bg="#000000"
    ).pack(pady=(20, 10))
    
    url_entry = tk.Entry(
        settings_window,
        font=("Consolas", 11),
        width=45,
        bg="#111111",
        fg="#ffffff",
        insertbackground="#ff0000",
        relief="flat"
    )
    url_entry.pack(pady=10, ipady=8)
    url_entry.insert(0, SERVER_URL)
    
    def save_settings():
        new_url = url_entry.get().strip()
        if save_server_url(new_url):
            messagebox.showinfo("Success", "Settings saved!\nPlease restart the application.")
            settings_window.destroy()
        else:
            messagebox.showerror("Error", "Failed to save settings")
    
    tk.Button(
        settings_window,
        text="SAVE",
        font=("Segoe UI", 11, "bold"),
        bg="#ff0000",
        fg="#ffffff",
        activebackground="#cc0000",
        relief="flat",
        cursor="hand2",
        command=save_settings
    ).pack(pady=20, ipady=5, ipadx=20)
    
    settings_window.transient(root)
    settings_window.grab_set()

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
        messagebox.showerror("Error", "Cannot connect to license server!\nCheck your settings.")
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

# المحتوى
main_frame = tk.Frame(root, bg="#000000")
main_frame.pack(expand=True, fill="both", padx=0, pady=0)

# عنوان
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

# زر الإعدادات (ترس)
settings_btn = tk.Button(
    main_frame,
    text="⚙️",
    font=("Segoe UI", 14),
    bg="#000000",
    fg="#ff0000",
    activebackground="#1a0000",
    relief="flat",
    cursor="hand2",
    command=open_settings
)
settings_btn.place(x=560, y=10)

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
activate_btn.bind("<Enter>", lambda e: activate_btn.config(bg="#cc0000"))
activate_btn.bind("<Leave>", lambda e: activate_btn.config(bg="#ff0000"))
cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(fg="#ff3333"))
cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(fg="#ff0000"))

root.mainloop()
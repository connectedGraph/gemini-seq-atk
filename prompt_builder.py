import tkinter as tk
from tkinter import messagebox, font
import ctypes
import pyperclip

def enable_high_dpi():
    """Enable Windows High DPI awareness to fix blurry UI."""
    try:
        # Query Windows version to use the correct API
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass # Non-Windows systems or older versions

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("U+035E Generator & Sandwich Builder")
        self.root.geometry("500x520")
        self.root.configure(bg="#f5f5f7") # Modern light gray background
        
        # Character definition
        self.special_char = "\u035E"
        
        # Set default font
        default_font = ("Segoe UI", 10)
        label_font = ("Segoe UI", 10, "bold")
        
        # --- UI Layout ---
        container = tk.Frame(root, bg="#f5f5f7", padx=30, pady=20)
        container.pack(expand=True, fill="both")

        # 1. Count Section
        tk.Label(container, text="Sequence Count / 序列个数", font=label_font, bg="#f5f5f7", fg="#333").pack(anchor="w")
        self.count_entry = tk.Entry(container, font=default_font, relief="flat", bd=1)
        self.count_entry.insert(0, "50")
        self.count_entry.pack(fill="x", pady=(5, 15), ipady=5)

        # 2. Prompt Section
        tk.Label(container, text="Attack Prompt / 攻击提示词", font=label_font, bg="#f5f5f7", fg="#333").pack(anchor="w")
        self.prompt_text = tk.Text(container, font=default_font, height=6, relief="flat", bd=1)
        self.prompt_text.pack(fill="x", pady=(5, 15))

        # 3. Mode Section
        self.sandwich_var = tk.BooleanVar(value=True)
        mode_frame = tk.Frame(container, bg="#f5f5f7")
        mode_frame.pack(fill="x", pady=5)
        
        tk.Checkbutton(
            mode_frame, 
            text="Sandwich Mode (Char + Prompt + Char)\n三明治模式 (字符+提示词+字符)", 
            variable=self.sandwich_var,
            font=default_font,
            bg="#f5f5f7",
            activebackground="#f5f5f7",
            justify="left"
        ).pack(anchor="w")

        # 4. Action Button
        self.copy_btn = tk.Button(
            container, 
            text="Generate & Copy / 生成并复制", 
            command=self.execute,
            font=("Segoe UI", 11, "bold"),
            bg="#007aff", # macOS/iOS style blue
            fg="white",
            activebackground="#005bb5",
            activeforeground="white",
            relief="flat",
            cursor="hand2"
        )
        self.copy_btn.pack(fill="x", pady=25, ipady=10)
        
        # Footer
        tk.Label(
            container, 
            text="Ready to inject U+035E sequence", 
            font=("Segoe UI", 8), 
            bg="#f5f5f7", 
            fg="#888"
        ).pack(side="bottom")

    def execute(self):
        try:
            count_str = self.count_entry.get().strip()
            if not count_str:
                raise ValueError("Empty count")
                
            count = int(count_str)
            prompt = self.prompt_text.get("1.0", tk.END).strip()
            
            sequence = self.special_char * count
            
            if self.sandwich_var.get():
                final_text = f"{sequence}{prompt}{sequence}"
            else:
                final_text = f"{sequence}{prompt}"

            pyperclip.copy(final_text)
            
            # Custom success feedback without blocking
            self.copy_btn.config(text="✓ Copied! / 已复制", bg="#34c759")
            self.root.after(2000, lambda: self.copy_btn.config(text="Generate & Copy / 生成并复制", bg="#007aff"))
            
        except ValueError:
            messagebox.showerror("Error / 错误", "Please enter a valid number.\n请输入有效的数字。")

if __name__ == "__main__":
    # Apply High DPI fix before creating root
    enable_high_dpi()
    
    root = tk.Tk()
    # Set icon if available, otherwise just window
    app = App(root)
    root.mainloop()
import tkinter as tk
from tkinter import messagebox
import random

# --- SOUND ENGINE ---
SOUND_ENABLED = True
try:
    import winsound
except Exception:
    winsound = None
    SOUND_ENABLED = False

# --- THEME ---
THEME = {
    "bg_main": "#1e1e1e",
    "bg_panel": "#252526",
    "fg_text": "#d4d4d4",
    "accent": "#007acc",
    "success": "#4ec9b0",
    "warning": "#ce9178",
    "highlight": "#dcdcaa",
    "inactive": "#3c3c3c",
    "font_main": ("Segoe UI", 10),
    "font_code": ("Consolas", 11),
    "font_bold": ("Segoe UI", 11, "bold")
}

# --- ALGORITHM LOGIC ---
PSEUDOCODE = """def binary_search(arr, target):
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = (low + high) // 2
        
        if arr[mid] == target:
            return mid  # Success
        
        elif arr[mid] < target:
            low = mid + 1
        
        else:
            high = mid - 1
            
    return -1  # Not Found"""

class SearchStep:
    def __init__(self, low, high, mid, msg, line_num, status="running", found_idx=None):
        self.low = low
        self.high = high
        self.mid = mid
        self.msg = msg
        self.line_num = line_num
        self.status = status
        self.found_idx = found_idx

class ProBinarySearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Binary Search Visualizer")
        self.root.geometry("1350x850")
        self.root.configure(bg=THEME["bg_main"])

        self.data = []
        self.target = 0
        self.steps = []
        self.current_step = -1
        self.is_playing = False

        self._build_ui()
        self.generate_data()

    def _build_ui(self):
        # === TOP HEADER ===
        header = tk.Frame(self.root, bg=THEME["bg_panel"], padx=10, pady=10)
        header.pack(fill=tk.X)

        tk.Label(header, text="Data Size:", bg=THEME["bg_panel"], fg=THEME["fg_text"]).pack(side=tk.LEFT)
        self.entry_size = tk.Scale(header, from_=5, to=40, orient=tk.HORIZONTAL, bg=THEME["bg_panel"],
                                   fg=THEME["fg_text"], highlightthickness=0)
        self.entry_size.set(15)
        self.entry_size.pack(side=tk.LEFT, padx=10)

        btn_style = {"bg": THEME["accent"], "fg": "white", "font": THEME["font_bold"], "relief": "flat", "padx": 15}
        tk.Button(header, text="🎲 Randomize", command=self.generate_data, **btn_style).pack(side=tk.LEFT, padx=5)

        tk.Label(header, text="Current List:", bg=THEME["bg_panel"], fg=THEME["fg_text"]).pack(side=tk.LEFT, padx=(20, 5))
        self.entry_custom = tk.Entry(header, width=35, bg="#3c3c3c", fg="white", insertbackground="white")
        self.entry_custom.pack(side=tk.LEFT)
        tk.Button(header, text="📥 Load", command=self.load_custom, **btn_style).pack(side=tk.LEFT, padx=5)

        tk.Label(header, text="Find:", bg=THEME["bg_panel"], fg=THEME["fg_text"], font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=(40, 5))
        self.entry_target = tk.Entry(header, width=8, font=("Arial", 12), bg="white", fg="black")
        self.entry_target.pack(side=tk.LEFT)

        self.btn_run = tk.Button(header, text="▶ START", command=self.init_search, bg=THEME["success"],
                                 fg="#1e1e1e", font=("Arial", 11, "bold"), padx=20)
        self.btn_run.pack(side=tk.LEFT, padx=20)

        # === MAIN WORKSPACE ===
        main_frame = tk.Frame(self.root, bg=THEME["bg_main"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # --- LEFT PANEL ---
        left_panel = tk.Frame(main_frame, bg=THEME["bg_main"])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Status Header
        var_frame = tk.Frame(left_panel, bg=THEME["bg_main"], pady=10)
        var_frame.pack(fill=tk.X)

        self.var_low = self._create_var_box(var_frame, "LOW (L)", "#4fc1ff")
        self.var_mid = self._create_var_box(var_frame, "MID (M)", "#dcdcaa")
        self.var_high = self._create_var_box(var_frame, "HIGH (H)", "#4fc1ff")

        self.lbl_top_status = tk.Label(var_frame, text="Ready.", bg=THEME["bg_main"], fg=THEME["fg_text"],
                                       font=("Consolas", 16, "bold"))
        self.lbl_top_status.pack(side=tk.RIGHT, padx=20)

        # Canvas
        self.canvas = tk.Canvas(left_panel, bg=THEME["bg_main"], highlightthickness=0, height=450)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=10)

        # Timeline Controls
        timeline_frame = tk.Frame(left_panel, bg=THEME["bg_panel"], pady=10, padx=10)
        timeline_frame.pack(fill=tk.X)

        self.btn_prev = tk.Button(timeline_frame, text="⏪ Step Back", command=self.step_back, bg="#444", fg="white",
                                  font=THEME["font_main"])
        self.btn_prev.pack(side=tk.LEFT, padx=5)

        self.btn_play = tk.Button(timeline_frame, text="▶ Play", command=self.toggle_play, bg=THEME["accent"],
                                  fg="white", font=THEME["font_bold"])
        self.btn_play.pack(side=tk.LEFT, padx=5)

        self.btn_next = tk.Button(timeline_frame, text="Step Fwd ⏩", command=self.step_fwd, bg="#444", fg="white",
                                  font=THEME["font_main"])
        self.btn_next.pack(side=tk.LEFT, padx=5)

        # SPEED CONTROLS
        speed_frame = tk.Frame(timeline_frame, bg=THEME["bg_panel"])
        speed_frame.pack(side=tk.RIGHT, padx=20)

        tk.Label(speed_frame, text="Fast", bg=THEME["bg_panel"], fg="white", font=("Arial", 8)).pack(side=tk.LEFT)
        self.speed_scale = tk.Scale(speed_frame, from_=0.05, to=1.0, resolution=0.05, orient=tk.HORIZONTAL,
                                    bg=THEME["bg_panel"], fg="white", highlightthickness=0, length=150, showvalue=0)
        self.speed_scale.set(0.5)
        self.speed_scale.pack(side=tk.LEFT, padx=5)
        tk.Label(speed_frame, text="Slow", bg=THEME["bg_panel"], fg="white", font=("Arial", 8)).pack(side=tk.LEFT)

        # --- RIGHT PANEL ---
        right_panel = tk.Frame(main_frame, bg=THEME["bg_panel"], width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0))
        right_panel.pack_propagate(False)

        tk.Label(right_panel, text="CODE EXECUTION", bg=THEME["bg_panel"], fg="#888", font=("Arial", 9, "bold")).pack(anchor="w", padx=10, pady=5)
        self.txt_code = tk.Text(right_panel, height=18, bg="#1e1e1e", fg=THEME["fg_text"], font=THEME["font_code"],
                                padx=10, pady=10, borderwidth=0)
        self.txt_code.pack(fill=tk.X, padx=5)
        self.txt_code.insert("1.0", PSEUDOCODE)
        self.txt_code.config(state="disabled")
        self.txt_code.tag_config("active_line", background="#264f78", foreground="white")

        tk.Label(right_panel, text="DEFINITION", bg=THEME["bg_panel"], fg="#888", font=("Arial", 9, "bold")).pack(anchor="w", padx=10, pady=(20, 5))
        def_text = ("Binary Search is an efficient algorithm that finds a target value in a SORTED array "
                    "by repeatedly dividing the search interval in half.")
        tk.Message(right_panel, text=def_text, bg=THEME["bg_panel"], fg="#cccccc", font=("Segoe UI", 10), width=330).pack(anchor="w", padx=5)

        tk.Label(right_panel, text="COMPLEXITY", bg=THEME["bg_panel"], fg="#888", font=("Arial", 9, "bold")).pack(anchor="w", padx=10, pady=(20, 5))
        self.lbl_complexity = tk.Label(right_panel, text="Time: O(log n)\nSpace: O(1)", justify="left", bg=THEME["bg_panel"], fg=THEME["fg_text"], font=("Consolas", 11))
        self.lbl_complexity.pack(anchor="w", padx=10)

    # --- HELPERS ---
    def _create_var_box(self, parent, title, color):
        frame = tk.Frame(parent, bg="#333", padx=10, pady=5)
        frame.pack(side=tk.LEFT, padx=10)
        tk.Label(frame, text=title, bg="#333", fg=color, font=("Arial", 8, "bold")).pack()
        lbl_val = tk.Label(frame, text="-", bg="#333", fg="white", font=("Consolas", 14, "bold"))
        lbl_val.pack()
        return lbl_val

    def play_sound(self, sound_type):
        """
        Use winsound if available; otherwise fall back to the system bell.
        Non-blocking and error-tolerant.
        """
        try:
            delay_sec = float(self.speed_scale.get())
            # duration in milliseconds, constrained to a small range
            duration = int(max(20, min(200, delay_sec * 1000 * 0.2)))

            if SOUND_ENABLED and winsound:
                if sound_type == "found":
                    winsound.Beep(1000, duration)
                    winsound.Beep(1500, min(duration * 2, 400))
                elif sound_type == "compare":
                    winsound.Beep(600, duration)
                elif sound_type == "eliminate":
                    winsound.Beep(250, duration)
            else:
                # fall back to a short bell (non-blocking)
                try:
                    self.root.bell()
                except Exception:
                    pass
        except Exception:
            # never raise sound errors
            pass

    # --- LOGIC ---
    def generate_data(self):
        try:
            sz = int(self.entry_size.get())
            self.data = sorted(random.sample(range(1, 150), sz))
            self.entry_custom.delete(0, tk.END)
            self.entry_custom.insert(0, ", ".join(map(str, self.data)))
            self.reset_ui()
            self.draw_bars()
            self.lbl_top_status.config(text=f"Generated {sz} numbers.", fg=THEME["fg_text"])
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_custom(self):
        try:
            txt = self.entry_custom.get()
            arr = [int(x.strip()) for x in txt.split(',') if x.strip() != ""]

            if arr != sorted(arr):
                messagebox.showerror("Invalid Input", "❌ Please enter a SORTED list!\n\nBinary Search requires the data to be in ascending order.")
                return

            self.data = arr
            self.entry_size.set(len(self.data))
            self.reset_ui()
            self.draw_bars()
            self.lbl_top_status.config(text="Custom sorted list loaded.", fg=THEME["fg_text"])
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers separated by commas.")

    def reset_ui(self):
        self.is_playing = False
        self.steps = []
        self.current_step = -1
        self.btn_play.config(text="▶ Play")
        self.var_low.config(text="-")
        self.var_mid.config(text="-")
        self.var_high.config(text="-")
        self.txt_code.tag_remove("active_line", "1.0", tk.END)

    def init_search(self):
        if not self.data:
            messagebox.showwarning("No Data", "Generate or load a list first.")
            return
        try:
            target_str = self.entry_target.get().strip()
            if not target_str:
                self.target = random.choice(self.data)
                self.entry_target.delete(0, tk.END)
                self.entry_target.insert(0, str(self.target))
            else:
                self.target = int(target_str)
        except Exception:
            messagebox.showerror("Error", "Invalid Target")
            return

        self.steps = []
        low = 0
        high = len(self.data) - 1

        # initial message
        self.steps.append(SearchStep(low, high, -1, f"Search Target: {self.target}", 2))

        # build steps
        while low <= high:
            mid = (low + high) // 2
            mid_val = self.data[mid]

            self.steps.append(SearchStep(low, high, mid, f"Midpoint is Index {mid} (Value: {mid_val})", 6))
            self.steps.append(SearchStep(low, high, mid, f"Comparing: Is {mid_val} == {self.target}?", 8))

            if mid_val == self.target:
                self.steps.append(SearchStep(low, high, mid, f"✅ Number {self.target} Found at Index {mid}!", 9, "found", mid))
                break
            elif mid_val < self.target:
                self.steps.append(SearchStep(low, high, mid, f"{mid_val} < {self.target}. Eliminate Left.", 11))
                low = mid + 1
            else:
                self.steps.append(SearchStep(low, high, mid, f"{mid_val} > {self.target}. Eliminate Right.", 14))
                high = mid - 1
        else:
            self.steps.append(SearchStep(-1, -1, -1, f"❌ Number {self.target} Not Found.", 17, "not_found"))

        self.current_step = 0
        self.is_playing = True
        self.btn_play.config(text="⏸ Pause")
        self.update_visuals()
        # start loop with a slight delay allowing UI to update
        self.root.after(150, self.loop)

    def update_visuals(self):
        if not self.steps or self.current_step < 0:
            return

        step = self.steps[self.current_step]

        self.var_low.config(text=str(step.low) if step.low != -1 else "-")
        self.var_mid.config(text=str(step.mid) if step.mid != -1 else "-")
        self.var_high.config(text=str(step.high) if step.high != -1 else "-")

        color = THEME["fg_text"]
        if step.status == "found":
            color = THEME["success"]
        elif step.status == "not_found":
            color = THEME["warning"]
        elif "Comparing" in step.msg:
            color = THEME["highlight"]

        self.lbl_top_status.config(text=step.msg, fg=color)

        self.txt_code.tag_remove("active_line", "1.0", tk.END)
        if step.line_num > 0:
            try:
                self.txt_code.tag_add("active_line", f"{step.line_num}.0", f"{step.line_num}.end")
            except Exception:
                pass

        if self.is_playing:
            if step.status == "found":
                self.play_sound("found")
            elif "Comparing" in step.msg:
                self.play_sound("compare")
            elif "Eliminate" in step.msg:
                self.play_sound("eliminate")

        self.draw_bars(step)

    def draw_bars(self, step=None):
        # ensure canvas geometry is updated before computing sizes
        self.root.update_idletasks()
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        if w < 100:
            w = 800
        h = 450
        baseline = h - 30
        n = len(self.data)
        if n == 0:
            return

        bar_w = w / (n + 1)
        max_val = max(self.data) if self.data else 1

        # --- MATH FIX ---
        base_height = 20
        max_bar_pixel_height = baseline - 130
        variable_height_range = max_bar_pixel_height - base_height

        for i, val in enumerate(self.data):
            variable_part = (val / max_val) * variable_height_range
            total_height = base_height + variable_part

            x0 = i * bar_w + 10
            y1 = baseline
            y0 = baseline - total_height
            x1 = (i + 1) * bar_w

            fill = THEME["accent"]

            if step:
                if step.found_idx == i:
                    fill = THEME["success"]
                elif i == step.mid:
                    fill = THEME["highlight"]
                elif step.low != -1 and step.high != -1:
                    if i < step.low or i > step.high:
                        fill = THEME["inactive"]

            self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="")

            # Value Text (Above bar)
            if n < 30:
                self.canvas.create_text((x0 + x1) / 2, y0 - 10, text=str(val), fill="white", font=("Arial", 9, "bold"))
            # Index Text (Below bar)
            self.canvas.create_text((x0 + x1) / 2, y1 + 15, text=str(i), fill="#666", font=("Arial", 8))

        # --- ARROW STACKING (Top Zone) ---
        if step and step.low != -1:
            pointer_counts = {}

            def get_stacked_y(idx):
                count = pointer_counts.get(idx, 0)
                pointer_counts[idx] = count + 1
                # Base Y is 90 (In the empty zone). Stack UP by 25px.
                return 90 - (count * 25)

            self._draw_pointer(step.low, "L", "#4fc1ff", bar_w, get_stacked_y(step.low))
            self._draw_pointer(step.mid, "M", "#dcdcaa", bar_w, get_stacked_y(step.mid))
            self._draw_pointer(step.high, "H", "#4fc1ff", bar_w, get_stacked_y(step.high))

    def _draw_pointer(self, idx, txt, color, width, y_pos):
        if idx < 0 or idx >= len(self.data):
            return
        x = idx * width + 10 + (width / 2) - 5
        self.canvas.create_text(x, y_pos, text=txt, fill=color, font=("Arial", 11, "bold"))

    def loop(self):
        if self.is_playing and self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_visuals()
            delay = int(self.speed_scale.get() * 1000)
            # minimum delay to keep UI readable
            delay = max(30, delay)
            self.root.after(delay, self.loop)
        elif self.current_step >= len(self.steps) - 1:
            self.is_playing = False
            self.btn_play.config(text="🔁 Reset")

    def toggle_play(self):
        # If ended, reset to start
        if self.current_step >= len(self.steps) - 1:
            self.current_step = 0
            self.update_visuals()

        self.is_playing = not self.is_playing
        self.btn_play.config(text="⏸ Pause" if self.is_playing else "▶ Play")
        if self.is_playing:
            self.loop()

    def step_fwd(self):
        self.is_playing = False
        self.btn_play.config(text="▶ Play")
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_visuals()

    def step_back(self):
        self.is_playing = False
        self.btn_play.config(text="▶ Play")
        if self.current_step > 0:
            self.current_step -= 1
            self.update_visuals()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProBinarySearchApp(root)
    root.mainloop()

# could use this for other projects

import tkinter as tk
import keyboard
import sys
from queue import Queue
import multiprocessing


class OnScreenKeyboard(tk.Toplevel):
    def __init__(self, master, command_queue):
        super().__init__(master)
        self.queue = command_queue
        self.configure(bg='gray15')
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        try:
            self.attributes('-toolwindow', True)
        except tk.TclError:
            print("INFO: '-toolwindow' attribute not supported on this OS.")
        self.shift_active = False
        self.caps_lock_active = False

        self.key_layout = [
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'BACKSPACE'],
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
            ['CAPS', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'ENTER'],
            ['SHIFT', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/'],
            ['SPACE'] #makes it easier for me to change stuff
        ]

        self.shift_map = {'`': '~', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*',
                          '9': '(', '0': ')', '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|', ';': ':', "'": '"',
                          ',': '<', '.': '>', '/': '?'}
        self.buttons = []
        self.build_keyboard()
        self.current_row, self.current_col = 0, 0
        self.withdraw()
        self.process_queue()

    def build_keyboard(self):
        for r, row_keys in enumerate(self.key_layout):
            row_frame = tk.Frame(self, bg='gray15')
            row_frame.grid(row=r, column=0, padx=5, pady=2)
            button_row = []
            for c, key_text in enumerate(row_keys):
                btn_props = {'text': key_text, 'width': 4, 'height': 2, 'bg': 'gray20', 'fg': 'white', 'relief': 'flat',
                             'highlightthickness': 0}

                # --- CHANGE 2: MAKE THE SPACEBAR WIDE ---
                if key_text in ['BACKSPACE', 'CAPS', 'ENTER', 'SHIFT']:
                    btn_props['width'] = 10
                elif key_text == 'SPACE':
                    btn_props['width'] = 50

                btn = tk.Button(row_frame, **btn_props)
                btn.grid(row=0, column=c, padx=2)
                button_row.append(btn)
            self.buttons.append(button_row)

    def update_key_visuals(self):
        for r, row_buttons in enumerate(self.buttons):
            for c, button in enumerate(row_buttons):
                base_char = self.key_layout[r][c]
                bg_color = 'gray20'
                if base_char == 'CAPS' and self.caps_lock_active: bg_color = 'gray40'
                if base_char == 'SHIFT' and self.shift_active: bg_color = 'gray40'
                button.config(bg=bg_color)
                button.config(text=self.get_display_char(base_char))

    def get_display_char(self, base_char):
        if base_char == 'SPACE': return 'Space'  # space bar thingy
        is_letter = len(base_char) == 1 and base_char.isalpha()
        if self.shift_active: return self.shift_map.get(base_char, base_char.upper())
        if self.caps_lock_active and is_letter: return base_char.upper()
        return base_char

    def center_window(self):
        self.update_idletasks()
        self.geometry(
            f'+{(self.winfo_screenwidth() - self.winfo_width()) // 2}+{(self.winfo_screenheight() - self.winfo_height()) // 2}')

    def highlight_current_key(self):
        self.update_key_visuals()
        self.buttons[self.current_row][self.current_col].config(bg='blue')

    def move(self, d_row, d_col):
        if not self.winfo_viewable(): return
        self.current_row = max(0, min(len(self.buttons) - 1, self.current_row + d_row))
        self.current_col = max(0, min(len(self.buttons[self.current_row]) - 1, self.current_col + d_col))
        self.highlight_current_key()

    def type_key(self):
        if not self.winfo_viewable(): return
        selected_key = self.key_layout[self.current_row][self.current_col]

        if selected_key == 'SPACE':
            keyboard.write(' ')
        elif selected_key == 'BACKSPACE':
            keyboard.press_and_release('backspace')
        elif selected_key == 'ENTER':
            keyboard.press_and_release('enter')
        elif selected_key == 'CAPS':
            self.caps_lock_active = not self.caps_lock_active
        elif selected_key == 'SHIFT':
            self.shift_active = not self.shift_active
        else:
            keyboard.write(self.get_display_char(selected_key))
            if self.shift_active: self.shift_active = False
        self.highlight_current_key()

    def _toggle_keyboard(self):
        if self.winfo_viewable():
            self.withdraw()
        else:
            self.center_window(); self.deiconify(); self.highlight_current_key()

    def process_queue(self):
        try:
            command = self.queue.get_nowait()
            is_physical_key = "_PHYSICAL" in command
            base_command = command.replace("_PHYSICAL", "")
            if base_command == "TOGGLE":
                self._toggle_keyboard()
            elif base_command == "UP":
                self.move(-1, 0)
            elif base_command == "DOWN":
                self.move(1, 0)
            elif base_command == "LEFT":
                self.move(0, -1)
            elif base_command == "RIGHT":
                self.move(0, 1)
            elif base_command == "INSERT":
                self.type_key()
            elif base_command == "SHUTDOWN":
                self.master.quit()
            if is_physical_key:
                keyboard.press_and_release('backspace')
        except Exception:
            pass
        finally:
            self.after(50, self.process_queue)


def _run_keyboard_gui(command_queue):
    root = tk.Tk()
    root.withdraw()
    app = OnScreenKeyboard(root, command_queue)
    action_map = {
        72: 'UP_PHYSICAL', 76: 'DOWN_PHYSICAL', 75: 'LEFT_PHYSICAL',
        77: 'RIGHT_PHYSICAL', 82: 'INSERT', 55: 'TOGGLE'
    }

    def master_event_handler(event):
        if event.event_type == keyboard.KEY_DOWN and event.scan_code in action_map:
            command_queue.put(action_map[event.scan_code])

    hook = keyboard.hook(master_event_handler)
    root.mainloop()
    keyboard.unhook(hook)


def start_keyboard_service():
    command_queue = multiprocessing.Queue()
    keyboard_process = multiprocessing.Process(target=_run_keyboard_gui, args=(command_queue,), daemon=True)
    keyboard_process.start()
    print("on screen keyboard started")

    return command_queue

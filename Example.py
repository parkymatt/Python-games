import keyboard
import time
import threading
import pyautogui

holding = False
spamming = False
clicking = False

# ---------- TOGGLE W ----------
def toggle_w():
    global holding
    if holding:
        keyboard.release("w")
        print("Released W")
        holding = False
    else:
        keyboard.press("w")
        print("Holding W...")
        holding = True

# ---------- SPAM SPACE ----------
def spam_space():
    global spamming
    if spamming:
        spamming = False
        print("Stopped spamming SPACE")
    else:
        spamming = True
        print("Started spamming SPACE")
        def loop():
            while spamming:
                keyboard.press_and_release("space")
                time.sleep(0.1)  # adjust spam speed
        threading.Thread(target=loop, daemon=True).start()

# ---------- MACRO (W + SPACE) ----------
def macro_jump_forward():
    print("Macro: Jump forward")
    keyboard.press("w")
    time.sleep(0.5)
    keyboard.press_and_release("space")
    time.sleep(0.2)
    keyboard.release("w")

# ---------- AUTO LEFT CLICK ----------
def toggle_click():
    global clicking
    if clicking:
        clicking = False
        print("Stopped auto-clicking")
    else:
        clicking = True
        print("Started auto-clicking")
        def loop():
            while clicking:
                pyautogui.click()
                time.sleep(0.05)  # adjust click speed
        threading.Thread(target=loop, daemon=True).start()

# ---------- HOTKEY BINDS ----------
keyboard.add_hotkey("F1", toggle_w)             # toggle hold W
keyboard.add_hotkey("F2", spam_space)           # toggle space spam
keyboard.add_hotkey("F3", macro_jump_forward)   # run W + Space macro
keyboard.add_hotkey("F4", toggle_click)         # toggle auto left-click

print("Controls:")
print(" F1 -> Toggle holding W")
print(" F2 -> Toggle spamming SPACE")
print(" F3 -> Run macro (W + Space)")
print(" F4 -> Toggle auto left-click")
print(" HOME -> Quit program")

keyboard.wait("home")

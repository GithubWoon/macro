import tkinter as tk
from pynput import keyboard
import time
import threading
import pickle

running = False
recording = False
key_log = {}
current_log = []
deleted_patterns = []

controller = keyboard.Controller()

delay_scaling_factor = 0.85  # 이 값을 조절하여 딜레이 시간을 조정

def on_press(key):
    if recording:
        current_log.append(('down', key, time.time()))

def on_release(key):
    if recording:
        current_log.append(('up', key, time.time()))

def press_key():
    global key_log, running
    try:
        interval_float = float(interval.get())
    except ValueError:
        print("Invalid interval value. Please enter a number.")
        return
    time.sleep(3)
    while running:
        prev_time = 0
        for action, key, cur_time in key_log[current_pattern.get()]:
            if not running:  # Stop 버튼이 눌렸다면, 즉시 중단
                break
            if prev_time != 0:
                time_diff = cur_time - prev_time
                scaled_time_diff = time_diff * delay_scaling_factor
                time.sleep(scaled_time_diff)
            prev_time = cur_time

            key = str(key).replace("'", "")
            if key.startswith("Key."):  # 특수 키 처리
                key = key.replace("Key.", "")
                if key == 'alt':  # 'alt' 키 처리
                    key = keyboard.Key.alt
                else:
                    key = getattr(keyboard.Key, key)
            else:
                key = key[1] if len(key) > 1 else key

            if action == 'down':
                controller.press(key)
            elif action == 'up':
                controller.release(key)
        time.sleep(interval_float)  # 패턴 사이의 딜레이를 추가

def start_thread():
    global running
    running = True
    threading.Thread(target=press_key).start()

def stop_thread():
    global running
    running = False

def start_recording():
    global recording, current_log
    recording = True
    current_log = []

def stop_recording():
    global recording, key_log
    recording = False
    pattern_name = 'Pattern ' + str(len(key_log) + 1)
    key_log[pattern_name] = current_log
    pattern_menu['menu'].add_command(label=pattern_name, command=tk._setit(current_pattern, pattern_name))

def delete_pattern():
    global key_log, deleted_patterns
    pattern = current_pattern.get()
    if pattern in key_log:
        # 삭제된 패턴을 저장
        deleted_patterns.append((pattern, key_log[pattern]))
        # 패턴 삭제
        del key_log[pattern]
        # 메뉴에서 패턴 제거
        pattern_menu['menu'].delete(pattern)
        # 현재 선택된 패턴 초기화
        current_pattern.set('')

# 복구 기능을 위한 새로운 함수를 정의합니다.
def restore_pattern():
    global key_log, deleted_patterns
    if deleted_patterns:
        pattern_name, pattern_data = deleted_patterns.pop()  # 가장 최근에 삭제된 패턴을 가져옴
        key_log[pattern_name] = pattern_data
        # 메뉴에 패턴을 다시 추가
        pattern_menu['menu'].add_command(label=pattern_name, command=tk._setit(current_pattern, pattern_name))
        current_pattern.set(pattern_name)  # 복구된 패턴을 현재 선택된 패턴으로 설정
    else:
        print("No patterns to restore.")

def save_patterns():
    global key_log
    with open('patterns.pkl', 'wb') as f:
        pickle.dump(key_log, f)

def load_patterns():
    global key_log
    try:
        with open('patterns.pkl', 'rb') as f:
            key_log = pickle.load(f)
    except FileNotFoundError:
        key_log = {}

root = tk.Tk()
root.title("Auto Key Presser")
root.geometry('600x300')

interval = tk.StringVar(root)
current_pattern = tk.StringVar(root)

interval_label = tk.Label(root, text="Interval (seconds)", font=("Helvetica", 16))
interval_label.grid(row=0, column=0)
interval_entry = tk.Entry(root, textvariable=interval, font=("Helvetica", 16))
interval_entry.grid(row=0, column=1)

start_button = tk.Button(root, text="Start", command=start_thread, font=("Helvetica", 16))
start_button.grid(row=1, column=0)
stop_button = tk.Button(root, text="Stop", command=stop_thread, font=("Helvetica", 16))
stop_button.grid(row=1, column=1)

start_recording_button = tk.Button(root, text="Start Recording", command=start_recording, font=("Helvetica", 16))
start_recording_button.grid(row=2, column=0)
stop_recording_button = tk.Button(root, text="Stop Recording", command=stop_recording, font=("Helvetica", 16))
stop_recording_button.grid(row=2, column=1)

delete_pattern_button = tk.Button(root, text="Delete Pattern", command=delete_pattern, font=("Helvetica", 16))
delete_pattern_button.grid(row=3, column=1)

pattern_menu = tk.OptionMenu(root, current_pattern, ())
pattern_menu.grid(row=3, column=0)

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# 프로그램 시작 시 패턴 불러오기
load_patterns()

# 패턴을 메뉴에 추가
for pattern_name in key_log.keys():
    pattern_menu['menu'].add_command(label=pattern_name, command=tk._setit(current_pattern, pattern_name))

# 프로그램 종료 시 패턴 저장하기
def on_closing():
    save_patterns()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)


# 패턴 이름을 입력하는 새로운 입력 필드 추가
pattern_name = tk.StringVar(root)
pattern_name_label = tk.Label(root, text="Pattern Name", font=("Helvetica", 16))
pattern_name_label.grid(row=4, column=0)
pattern_name_entry = tk.Entry(root, textvariable=pattern_name, font=("Helvetica", 16))
pattern_name_entry.grid(row=4, column=1)

# 패턴 저장 시 사용자가 입력한 패턴 이름을 사용하도록 수정
def stop_recording():
    global recording, key_log
    recording = False
    pattern_name = pattern_name_entry.get() if pattern_name_entry.get() != '' else 'Pattern ' + str(len(key_log) + 1)
    key_log[pattern_name] = current_log
    pattern_menu['menu'].add_command(label=pattern_name, command=tk._setit(current_pattern, pattern_name))

# 패턴 이름 수정 기능 추가
def rename_pattern():
    global key_log
    new_name = pattern_name_entry.get()
    if current_pattern.get() in key_log and new_name != '':
        key_log[new_name] = key_log[current_pattern.get()]
        del key_log[current_pattern.get()]
        pattern_menu['menu'].delete(current_pattern.get())
        pattern_menu['menu'].add_command(label=new_name, command=tk._setit(current_pattern, new_name))

rename_pattern_button = tk.Button(root, text="Rename Pattern", command=rename_pattern, font=("Helvetica", 16))
rename_pattern_button.grid(row=5, column=0)
# 기존의 rename_pattern 버튼 추가 코드 바로 아래에 복구 버튼 추가 코드를 삽입합니다.
restore_button = tk.Button(root, text="Restore Pattern", command=restore_pattern, font=("Helvetica", 16))
restore_button.grid(row=6, column=0)

root.mainloop()
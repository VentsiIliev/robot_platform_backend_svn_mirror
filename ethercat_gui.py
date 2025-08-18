import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import time

NUM_JOINTS = 6

def write_position(slave_id, pos):
    cmd = ["ethercat", "download", f"-p{slave_id}", "--type", "int32", "0x607A", "0", str(pos)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error writing position for slave {slave_id}: {result.stderr}")
    else:
        print(f"Position sent to slave {slave_id}: {pos}")


def read_position(slave_id):
    cmd = ["ethercat", "upload", f"-p{slave_id}", "--type", "int32", "0x6064", "0"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        val = result.stdout.strip().split()
        return int(val[1]) if len(val) == 2 else None
    except:
        return None

class EtherCATGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EtherCAT Joint Control")

        self.sliders = []
        self.labels = []

        for i in range(NUM_JOINTS):
            frame = ttk.Frame(root)
            frame.pack(pady=5)

            label = ttk.Label(frame, text=f"Joint {i+1}")
            label.pack(side=tk.LEFT)

            slider = ttk.Scale(frame, from_=-100000, to=100000, orient=tk.HORIZONTAL, length=300)
            slider.pack(side=tk.LEFT, padx=10)

            val_label = ttk.Label(frame, text="Actual: ???")
            val_label.pack(side=tk.LEFT)

            self.sliders.append(slider)
            self.labels.append(val_label)

        send_button = ttk.Button(root, text="Send All Positions", command=self.send_all)
        send_button.pack(pady=10)

        self.poll_thread = threading.Thread(target=self.poll_loop, daemon=True)
        self.poll_thread.start()

    def send_all(self):
        for i, slider in enumerate(self.sliders):
            pos = int(slider.get())
            write_position(i, pos)  # Shift slave IDs by +1

    def poll_loop(self):
        while True:
            for i in range(NUM_JOINTS):
                pos = read_position(i)  # Shift slave IDs by +1 here as well
                if pos is not None:
                    self.root.after(0, self.labels[i].config, {"text": f"Actual: {pos}"})
        time.sleep(0.1)

if __name__ == "__main__":
    root = tk.Tk()
    app = EtherCATGUI(root)
    root.mainloop()

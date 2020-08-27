from http.server import BaseHTTPRequestHandler, HTTPServer
import datetime
from functools import partial
import sys
import time
import tkinter as tk
import threading

MINUTE_MULTIPLIER = 60
WINDOW_HEIGHT = 150
WINDOW_WIDTH = 300
DEFAULT_MINUTES = 20


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("Received a GET request!")
        self.send_response(200)
        self.end_headers()
        timer = StandUpTimer.get()
        return_value = timer.get_string_time_remaining()
        self.wfile.write(str.encode(return_value))


def set_window_geometry(window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (WINDOW_WIDTH/2))
    y_cordinate = int((screen_height/2) - (WINDOW_HEIGHT/2))
    window.geometry("{}x{}+{}+{}".format(WINDOW_WIDTH, WINDOW_HEIGHT, x_cordinate, y_cordinate))


class StandUpTimer:
    TIMER = None

    def __init__(self, timer_minutes=DEFAULT_MINUTES):
        self.timer_minutes = timer_minutes
        self.window = None
        self.last_start = None
        self.window_thread = None
        self.snooze_5 = partial(self.start_timer, 5)
        self.snooze_10 = partial(self.start_timer, 10)
        self.reset = partial(self.start_timer, DEFAULT_MINUTES)
        StandUpTimer.TIMER = self

    @classmethod
    def get(cls):
        if not cls.TIMER:
            StandUpTimer()
        return cls.TIMER

    def get_string_time_remaining(self):
        time_remaining = self.last_start + (self.timer_minutes * MINUTE_MULTIPLIER) - time.time()
        delta = datetime.timedelta(seconds=time_remaining)
        return str(delta)

    def start_web_server(self):
        print("Starting server")
        httpd = HTTPServer(('localhost', 5001), Handler)
        httpd.serve_forever()

    def start_timer(self, timer_minutes):
        self.timer_minutes = timer_minutes
        if self.window is not None:
            self.window.destroy()
        self.window = None
        self.window_thread = None
        self.last_start = time.time()
        time.sleep(self.timer_minutes * MINUTE_MULTIPLIER)
        self.window_thread = threading.Thread(target=self.open_window, name="window_thread")
        self.window_thread.start()

    def start(self):
        self.web_server_thread = threading.Thread(target=self.start_web_server, name="web_server")
        self.web_server_thread.start()
        self.start_timer(self.timer_minutes)


    def open_window(self):
        window = tk.Tk()

        set_window_geometry(window)
        label = tk.Label(text="It's time to stand up!")

        button_reset = tk.Button(window, text="Reset ({})".format(DEFAULT_MINUTES), command=self.reset)
        button_5 = tk.Button(window, text="Snooze 5", command=self.snooze_5)
        button_10 = tk.Button(window, text="Snooze 10", command=self.snooze_10)

        label.pack()
        button_5.pack()
        button_10.pack()
        button_reset.pack()

        self.window = window
        window.mainloop()
    

def main():
    if len(sys.argv) > 1:
        minutes = int(sys.argv[1])
    else:
        minutes = DEFAULT_MINUTES
    timer = StandUpTimer(minutes)
    timer.start()


if __name__ == '__main__':
    main()


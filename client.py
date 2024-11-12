from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

import socket
import cv2

class StreamApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.streaming = False
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = 3030
        self.s = None
        self.cap = None

    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.status_label = Label(text="Press 'Start Stream' to begin", font_size=20)
        layout.add_widget(self.status_label)
        
        # Start/Stop button
        self.start_button = Button(text="Start Stream", font_size=24)
        self.start_button.bind(on_press=self.start_stream)
        layout.add_widget(self.start_button)

        return layout

    def start_stream(self, instance):
        if not self.streaming:
            self.status_label.text = "Connecting..."
            try:
                # Set up socket and camera
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect((self.ip, self.port))
                self.cap = cv2.VideoCapture(0)
                self.streaming = True
                self.status_label.text = "Streaming video..."
                self.start_button.text = "Stop Stream"
                
                # Schedule video sending every 0.05 seconds
                Clock.schedule_interval(self.send_frame, 0.05)
            except Exception as e:
                self.status_label.text = f"Error: {str(e)}"
        else:
            self.stop_stream()

    def send_frame(self, dt):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                try:
                    self.s.sendall(buffer.tobytes() + b'--end-of-frame--')
                except BrokenPipeError:
                    self.status_label.text = "Connection lost"
                    self.stop_stream()
            else:
                self.stop_stream()

    def stop_stream(self):
        self.streaming = False
        if self.cap:
            self.cap.release()
        if self.s:
            self.s.close()
        self.status_label.text = "Stream stopped"
        self.start_button.text = "Start Stream"
        Clock.unschedule(self.send_frame)

if __name__ == '__main__':
    StreamApp().run()

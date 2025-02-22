import sys
import subprocess
import ping3
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

class PingSpeedDisplay(QLabel):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set the window to be a tooltip and always on top
        self.setWindowFlags(Qt.ToolTip | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Set the font and size for the ping speed display
        self.setFont(QFont('Arial', 20))
        self.setStyleSheet("color: white;")

        # Position the label in the bottom right corner
        screen_geometry = QApplication.desktop().screenGeometry()
        self.move(screen_geometry.width() - 300, screen_geometry.height() - 50)

        # Start the timer to ping every 2 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ping_speed)
        self.timer.start(2000)  # 2000 milliseconds = 2 seconds

        # Initial ping
        self.update_ping_speed()

    def get_current_url(self):
        try:
            # Use xdotool to get the active window and check if it's Chrome
            active_window = subprocess.check_output(['xdotool', 'getactivewindow', 'getwindowname']).decode('utf-8').strip()
            if "Google Chrome" not in active_window:
                return None

            # Use DBus to get the current URL from Chrome
            dbus_command = [
                'dbus-send', '--session', '--dest=org.freedesktop.DBus',
                '--type=method_call', '--print-reply', '--reply-timeout=2000',
                '/org/freedesktop/DBus', 'org.freedesktop.DBus.ListNames'
            ]
            dbus_output = subprocess.check_output(dbus_command).decode('utf-8')
            if 'org.chromium.Chromium' not in dbus_output and 'org.google.Chrome' not in dbus_output:
                return None

            # Get the current URL from Chrome using DBus
            chrome_dbus_command = [
                'dbus-send', '--session', '--dest=org.chromium.Chromium',
                '/org/chromium/Chromium', 'org.freedesktop.DBus.Properties.Get',
                'string:org.chromium.Chromium', 'string:CurrentURL'
            ]
            chrome_output = subprocess.check_output(chrome_dbus_command).decode('utf-8')
            url = chrome_output.split('"')[1]  # Extract URL from DBus output
            if url and (url.startswith("http://") or url.startswith("https://")):
                return url
            else:
                return None
        except Exception as e:
            print(f"Error getting URL: {e}")
            return None

    def update_ping_speed(self):
        # Get the current URL
        url = self.get_current_url()
        if url:
            # Extract the hostname from the URL (remove "http://" or "https://")
            hostname = url.split("//")[-1].split("/")[0]
            # Ping the hostname
            ping_time = ping3.ping(hostname, unit='ms')
            if ping_time is not None:
                self.setText(f"Ping: {ping_time:.2f} ms")
            else:
                self.setText(f"Ping ({hostname}): Failed")
        else:
            self.setText("Ping: No URL found")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ping_display = PingSpeedDisplay()
    ping_display.show()
    sys.exit(app.exec_())

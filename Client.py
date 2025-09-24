import socket
import random, math
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from threading import Thread
from datetime import datetime, timedelta

PORT = 5055
HEADER = 64  # any data recieved by the server will be padded to be 64B
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "100.69.247.53"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

num = 0


#GUI Class:
class ClientGUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.status_label = Label(text="Connecting...", font_size='20sp')
        self.totp_label = Label(text="", font_size='40sp', bold=True)
        self.note_label = Label(text="", font_size='14sp', color=(1, 0, 0, 1))
        self.timer_label = Label(text="", font_size='16sp')
        
        self.add_widget(self.status_label)
        self.add_widget(self.totp_label)
        self.add_widget(self.note_label)
        self.add_widget(self.timer_label)

    def update_status(self, text):
        self.status_label.text = text

    def show_totp(self, totp):
        self.status_label.text = "Your One-Time Password:"
        self.totp_label.text = totp
        self.note_label.text = "Note: Please don't share this number with anyone"
        
        # Set expiration time (5 minutes from now)
        self.expiry_time = datetime.now() + timedelta(minutes=5)
        # Start the countdown timer
        Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        remaining = self.expiry_time - datetime.now()
        if remaining.total_seconds() > 0:
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            self.timer_label.text = f"This OTP is valid for: {mins:02d}:{secs:02d}"
        else:
            self.timer_label.text = "OTP has expired!"
            self.totp_label.color = (0.5, 0.5, 0.5, 1)  # Gray out expired OTP
            return False  # This stops the clock

#Client Application Class:
class ClientApp(App):
    def build(self):
        self.gui = ClientGUI()
        # Start the client operations in a separate thread
        Thread(target=self.run_client_operations, daemon=True).start()
        return self.gui

    def run_client_operations(self):
        # Your original client code with minor adjustments to update the GUI
        
        def is_prime(number):
            if number < 2:
                return False
            for i in range(2, number // 2 + 1):
                if number % i == 0:
                    return False
            return True

        def generate_prime(min_val, max_val):
            prime = random.randint(min_val, max_val)
            while not is_prime(prime):
                prime = generate_prime(min_val, max_val)
            return prime

        def mod_inverse(e, phi):
            for d in range(3, phi):
                if (d * e) % phi == 1:
                    return d
            raise ValueError("mod_inverse doesn't exsist")

        # Update GUI - generating keys
        Clock.schedule_once(lambda dt: self.gui.update_status("Connecting to the server..."))
        
        p, q = generate_prime(1000, 50000), generate_prime(1000, 50000)
        while p == q:
            q = generate_prime(1000, 50000)

        n = p * q
        phi_n = (p - 1) * (q - 1)

        e = random.randint(3, phi_n - 1)
        while math.gcd(e, phi_n) != 1:
            e = random.randint(3, phi_n - 1)

        d = mod_inverse(e, phi_n)

        print("PUBLIC KEY=", e)
        print("Private KEY=", d)
        print("n=", n)
        print("PHI=", phi_n)
        print("p:", p)
        print("q:", q)

        def receive_ack():
            """Helper function to receive server acknowledgments"""
            ack = client.recv(1024).decode(FORMAT)
            return ack.startswith("ACK:")

        def receive_message():
            """Properly receive framed messages"""
            header = client.recv(HEADER).decode(FORMAT).strip()
            if not header:
                return None
            msg_length = int(header)
            return client.recv(msg_length).decode(FORMAT)

        def send(msg, num):
            try:
                # Prepare message
                if num < 2:
                    msg = str(msg)

                message = msg.encode(FORMAT)
                msg_len = len(message)
                send_length = str(msg_len).encode(FORMAT)
                send_length += b' ' * (HEADER - len(send_length))

                # Send message
                client.send(send_length)
                client.send(message)

                # Update GUI - connecting to server
                Clock.schedule_once(lambda dt: self.gui.update_status("Your OTP is:"))

                # Handle special cases
                if num == 0:  # After sending 'e'
                    if not receive_ack():
                        raise ValueError("Server didn't acknowledge 'e'")
                elif num == 1:  # After sending 'n'
                    if not receive_ack():
                        raise ValueError("Server didn't acknowledge 'n'")
                elif num == 2:  # After "Get TOTP"
                    Clock.schedule_once(lambda dt: self.gui.update_status("Requesting One-Time Password..."))
                    response = receive_message()
                    if response:
                        ciphertxt = json.loads(response)
                        msg_decoded = [pow(ch, d, n) for ch in ciphertxt]
                        totp = "".join(chr(ch) for ch in msg_decoded)
                        print("Decrypted TOTP:", totp)
                        # Update GUI with TOTP
                        Clock.schedule_once(lambda dt: self.gui.show_totp(totp))
                    else:
                        print("No TOTP received")
                        Clock.schedule_once(lambda dt: self.gui.update_status("Failed to get OTP"))

                return True

            except Exception as e:
                print(f"Error in send: {str(e)}")
                Clock.schedule_once(lambda dt: self.gui.update_status(f"Error: {str(e)}"))
                return False

        send(e, 0)       # Send public key
        send(n, 1)       # Send modulus
        send("Get TOTP", 2)  # Request TOTP
        send(DISCONNECT_MESSAGE, 3)  # Disconnect

if __name__ == "__main__":
    ClientApp().run()
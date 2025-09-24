import socket
import threading  # Allows separating the code later on, so it doesn't wait for code thread to finish to run the other
import random
import json


PORT = 5055
HEADER = 64  # any data recieved by the server will be padded to be 64B
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
#if you want to connect external devices out of the LAN:
#SERVER = "192.168.153.1"  #Change this to your current local IP when you're trying again cause DHCP might have changed the ip it gave to your laptop
#Anyways the server IP will be printted in the terminal when the server runs
#Notice if the server is desired to be accessed globally you'll require to change this local IP to your global one
#Production scale this IP should be configured as Static IP


SERVER = socket.gethostbyname(socket.gethostname())  # Get ip addr by name of your laptop that is represented in nw automatically


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# AF_INET:what type of ips that we'll be using and here for ipv4
# socket.SOCK_STREAM:for streaming data via this socket

ADDR = (SERVER, PORT)  #Socket Pair of the server
server.bind(ADDR)



#This function will be running for each client
def handle_client(conn, addr):
    print(f"New connection from {addr}")
    num = 0
    e, n = None, None
    connected = True

    try:
        while connected:
            # Receive message length header
            msg_length = conn.recv(HEADER).decode(FORMAT).strip()
            if not msg_length:
                break

            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)

            if msg == DISCONNECT_MESSAGE:
                connected = False
                print(f"{addr} disconnected")
                break

            print(f"{addr}: {msg}")

            if num == 0:
                e = int(msg)
                num += 1
                # Send acknowledgment
                conn.send("ACK:e".encode(FORMAT))
            elif num == 1:
                n = int(msg)
                num += 1
                # Send acknowledgment
                conn.send("ACK:n".encode(FORMAT))
            elif num == 2 and msg == "Get TOTP":
                if e is None or n is None:
                    conn.send("ERROR:Missing keys".encode(FORMAT))
                    continue
                # Generate a single random 6-digit number (100000 to 999999)
                random_number = random.randint(100000, 999999)
                OTP=str(random_number)
                msg_encoded = [ord(ch) for ch in OTP]
                ciphertxt = [pow(ch, e, n) for ch in msg_encoded]

                # Send encrypted OTP with proper framing
                response = json.dumps(ciphertxt).encode(FORMAT)
                header = f"{len(response):<{HEADER}}".encode(FORMAT)
                conn.send(header)
                conn.send(response)

    except ConnectionResetError:
        print(f"{addr} forcibly closed the connection")
    finally:
        conn.close()
        print(f"Connection with {addr} closed")


# Handle the start of the connection
def start():
    server.listen()
    print(f"SERVER is listening on :{SERVER}")  #Print the IP the server which clients will connect on
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr)) #when a new connection starts pass it to handle_client to manage the session
        thread.start()
        print(f"Active connections : {threading.active_count() - 1}")


print("STARTING>>>..........")
start()


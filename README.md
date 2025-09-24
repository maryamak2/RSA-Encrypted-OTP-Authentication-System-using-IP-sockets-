A client–server OTP system that uses RSA encryption for secure delivery of one-time passwords.  
The server generates OTPs, encrypts them with the client’s public key, and sends them back.  
The client decrypts the OTP using its private key and displays it in a Kivy-based GUI with a countdown timer.

📂 Project Structure:
├── Server.py # Multi-client OTP server
├── Client.py # GUI-based OTP client
└── README.md # Documentation



⚙️ How It Works:

🔹 Server (`Server.py`)
- Accepts TCP connections from multiple clients (threaded).  
- Receives the client’s RSA public key (`e, n`).  
- Waits for `"Get TOTP"` request.  
- Generates a "6-digit OTP" (100000–999999).  
- Encrypts the OTP using RSA (`pow(m, e, n)`).  
- Sends back the **encrypted OTP**.  



🔹 Client (`Client.py`)
- Connects to the server.  
- Generates its own RSA key pair (`e, d, n`).  
- Sends public key (`e, n`) to server.  
- Requests OTP with `"Get TOTP"`.  
- Receives encrypted OTP, decrypts it using `d`.  
- Displays OTP in a GUI with Kivy:
  - ✅ OTP value (large font)  
  - ✅ Warning: "Do not share this number"  
  - ✅ Countdown timer (5-minute validity)
 

🚀 Running the Project:

1. Installing Requirements:
  >> pip install kivy
   
2. Run Server Code:
  >> python Server.py
  Now the Server is listening on Certain IP so make sure this IP is the same server IP in Client.py code
<img width="405" height="67" alt="image" src="https://github.com/user-attachments/assets/87dd09cb-faa1-460b-b8da-0aec86326a0b" />

   
3. Run Client code:
  >> python Client.py
✅The Client starts by generating keys and Connecting to the Server.
<img width="1000" height="790" alt="image" src="https://github.com/user-attachments/assets/875981f6-4583-402c-8827-b816ebb03127" />

✅After the Client recieves the OTP:
<img width="998" height="792" alt="Screenshot 2025-09-17 094533" src="https://github.com/user-attachments/assets/c9deb0e2-38d6-4def-ab9e-6ee845b53811" />

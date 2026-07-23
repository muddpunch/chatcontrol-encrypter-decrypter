
• # Anti Chat-Control Encrypter / Decrypter

  A collection of encrypted communication tools providing:

  - A manual message encrypter and decrypter.
  - A graphical encryption interface.
  - A direct peer-to-peer encrypted chat.
  - Terminal and Windows GUI modes.
  - Hamachi, Radmin VPN, LAN, and public Internet connectivity.

  ## Available Modes

   Mode                             Encryption                            Key management              Entry point
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━
   Terminal encrypter/decrypter     Fernet authenticated encryption       Shared key.txt              py main.py
  ───────────────────────────────  ────────────────────────────────────  ──────────────────────────  ─────────────────
   Graphical encrypter/decrypter    Fernet authenticated encryption       Shared key.txt              py ui.py
  ───────────────────────────────  ────────────────────────────────────  ──────────────────────────  ─────────────────
   Encrypted P2P chat               X25519 + HKDF-SHA256 + AES-256-GCM    Automatic per connection    py -m chat.main

  > The manual encrypter/decrypter and the P2P chat use separate encryption systems. The chat does not use key.txt.

  ## Project Structure

  .
  ├── main.py                 # Terminal menu
  ├── Key.py                  # Fernet key generator
  ├── saving.py               # Shared-key importer
  ├── szyfrowanie.py          # Terminal message encryption
  ├── odszyfrowanie.py        # Terminal message decryption
  ├── ui.py                   # Graphical encrypter/decrypter
  ├── key.txt                 # Local Fernet key
  └── chat/
      ├── main.py             # Chat entry point
      ├── ui.py               # Chat interface
      ├── connecting.py       # TCP and key exchange
      ├── encryption.py       # AES-GCM encryption
      └── decryption.py       # AES-GCM decryption

  ## Requirements

  - Windows 10 or Windows 11.
  - Python 3.10 or newer.
  - cryptography.
  - Hamachi or Radmin VPN when using a virtual network.

  ## Installation

  git clone <REPOSITORY_URL>
  cd chatcontrol-encrypter-decrypter

  py -m venv .venv
  .\.venv\Scripts\Activate.ps1
  py -m pip install --upgrade pip cryptography

  # Manual Encrypter / Decrypter

  The manual tools encrypt text into a portable Fernet token. The recipient must use the same shared key to decrypt it.

  ## Terminal Menu

  py main.py

  1. Generate a new key
  2. Encrypt a message
  3. Decrypt a message
  4. Open the graphical interface
  5. Paste or save an existing key
  0. Exit

  ## Shared-Key Workflow

  Sender                              Recipient
  ──────                              ─────────
  Generate key
       │
       ├──── Share key securely ─────► Save the same key
       │
  Encrypt message
       │
       └──── Send encrypted token ───► Decrypt token

  ### 1. Generate a Key

  Use option 1 from the terminal menu or run:

  py Key.py

  The generated key is saved to:

  key.txt

  Example key format:

  S0VZX0VYQU1QTEVfTk9UX0FfUkVBTF9LRVlfMTIzNDU2Nzg=

  > Generating a new key overwrites key.txt. Messages encrypted with the previous key cannot be decrypted unless the
  > previous key was backed up.

  ### 2. Share the Key

  Send the key to the recipient through a trusted channel. Do not publish it, commit it to Git, or send it together with
  the encrypted message.

  The recipient can import it through terminal option 5 or:

  py saving.py

  ### 3. Encrypt a Message

  Use terminal option 2 or run:

  py szyfrowanie.py

  Message: Secret message
  Encrypted message: gAAAAAB...

  Send only the generated encrypted token to the recipient.

  ### 4. Decrypt a Message

  Use terminal option 3 or run:

  py odszyfrowanie.py

  Encrypted message: gAAAAAB...
  Decrypted message: Secret message

  Decryption fails when:

  - The recipient has a different key.
  - The encrypted token was modified.
  - The encrypted token is incomplete.
  - key.txt is missing or invalid.

  ## Graphical Encrypter / Decrypter

  py ui.py

  The graphical interface supports:

  - Fernet key generation.
  - Importing an existing key.
  - Message encryption.
  - Message decryption.
  - Copying the output.
  - Unicode and emoji.

  Generate key → Enter text → Encrypt → Copy output
  Paste key   → Paste token → Decrypt

  # Encrypted P2P Chat

  The chat establishes a direct TCP connection between two users.

  Client ───── TCP connection ─────► Host
         X25519 key agreement
         HKDF-SHA256 key derivation
         AES-256-GCM encryption

  Each connection receives fresh session keys. The chat does not require users to exchange key.txt.

  ## Chat Features

  - Direct peer-to-peer communication.
  - X25519 ephemeral key agreement.
  - HKDF-SHA256 key derivation.
  - AES-256-GCM authenticated encryption.
  - Separate keys for each transmission direction.
  - Unique nonce for every message.
  - Connection fingerprint verification.
  - Unicode and emoji support.
  - No persistent chat history.
  - Maximum message size of approximately 1 MiB.

  ## Running the Chat

  py -m chat.main

  ## Connecting Through Hamachi

  Router port forwarding is not required when using Hamachi.

  1. Install Hamachi on both computers.
  2. Join the same Hamachi network.
  3. The host starts the application and clicks Host.
  4. The client enters the host's Hamachi IPv4 address.
  5. Both users keep port 5050.
  6. The client clicks Connect.

  Host:
  Port:   5050
  Action: Host

  Client:
  Address: <HOST_HAMACHI_IP>
  Port:    5050
  Action:  Connect

  > 127.0.0.1 points to the client's own computer. It cannot be used to connect to another user.

  ## Windows Firewall

  Run PowerShell as Administrator on the host computer:

  New-NetFirewallRule `
      -DisplayName "Encrypted Chat Hamachi" `
      -Direction Inbound `
      -Action Allow `
      -Protocol TCP `
      -LocalPort 5050 `
      -RemoteAddress 25.0.0.0/8 `
      -Profile Any

  This rule allows inbound TCP connections on port 5050 only from the Hamachi IPv4 range.

  ## Testing a Hamachi Connection

  Run this command on the client while the host is listening:

  Test-NetConnection <HOST_HAMACHI_IP> -Port 5050

  Expected result:

  TcpTestSucceeded : True

  If the result is False, verify that:

  - Both computers are online in the same Hamachi network.
  - The host clicked Host before running the test.
  - The client entered the host's Hamachi address.
  - Both applications use port 5050.
  - The Windows Firewall rule exists on the host computer.

  ## Local Network Connection

  When both computers use the same router, the client can connect directly to the host's LAN address:

  Example:
  192.168.1.20:5050

  The host's LAN address is displayed in the application.

  ## Public Internet Connection

  Without Hamachi or another VPN, the host's router must forward the TCP port:

  protocol: TCP
  external_port: 5050
  internal_ip: "<HOST_LAN_IP>"
  internal_port: 5050

  The client connects to the host's public IPv4 address.

  Direct hosting may not work behind CGNAT. Use Hamachi, Radmin VPN, or a public relay in that case.

  ## Building a Single Chat Executable

  Create chat_launcher.py in the project root:

  from chat.ui import ChatApp

  if __name__ == "__main__":
      ChatApp().run()

  Install PyInstaller and build the executable:

  py -m pip install --upgrade pyinstaller cryptography

  py -m PyInstaller `
      --noconfirm `
      --clean `
      --onefile `
      --windowed `
      --name EncryptedChat `
      chat_launcher.py

  Output:

  dist\EncryptedChat.exe

  Only EncryptedChat.exe must be sent to the other user. Python is not required on their computer, but Hamachi is still
  required when connecting through Hamachi.

  # Security

  ## Manual Encrypter / Decrypter

  Anyone with access to key.txt can decrypt messages encrypted with that key.

  Never commit key.txt
  Never publish the key
  Never send the key together with the encrypted token
  Keep a backup if old messages must remain decryptable

  ## P2P Chat

  After connecting, both applications display a fingerprint. Compare it through an independent trusted channel, such as
  a voice call:

  Host fingerprint == Client fingerprint

  Terminate the connection immediately if the fingerprints differ.

  This project has not undergone an independent security audit. Do not treat it as a replacement for professionally
  audited communication software.

  # Legal Notice

  This software is a general-purpose privacy and communication tool. Users are solely responsible for ensuring that
  their use complies with all applicable laws and regulations.

  The author does not endorse unlawful activity and, to the maximum extent permitted by applicable law, accepts no
  responsibility for illegal use, misuse, damages, claims, or other consequences arising from the use of this software.

  ## UI Preview

  **CHAT**<br>
  <img width="702" height="544" alt="image" src="https://github.com/user-attachments/assets/48153917-0d6c-4fe7-a0d2-db5698bec39f" /><br>
  **ENCRYPTER**<br>
  <img width="647" height="530" alt="{96C89EFF-DCC2-426F-9D2B-AAB07612E1C4}" src="https://github.com/user-attachments/assets/61ff9437-d381-4c97-b72f-c8f95234c364" />

  *README is ai generated :sob:*

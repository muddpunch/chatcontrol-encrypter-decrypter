# Anti Chat-Control Encrypter / Decrypter

Encrypted communication tools for manual message encryption and real-time
peer-to-peer chat. Run them from the terminal, use the desktop UI, or build the
chat as a standalone Windows executable.

## Features

- Manual Fernet message encryption and decryption.
- Terminal and graphical interfaces.
- Shared-key generation and import.
- Direct encrypted P2P chat.
- X25519, HKDF-SHA256, and AES-256-GCM chat encryption.
- LAN, Hamachi, Radmin VPN, and public Internet connectivity.
- Unicode and emoji support.
- No persistent chat history.

## Available Modes

| Mode | Encryption | Key management | Entry point |
| --- | --- | --- | --- |
| Terminal encrypter/decrypter | Fernet | Shared `key.txt` | `py main.py` |
| Graphical encrypter/decrypter | Fernet | Shared `key.txt` | `py ui.py` |
| Encrypted P2P chat | X25519, HKDF-SHA256, AES-256-GCM | Automatic per connection | `py -m chat.main` |

> [!IMPORTANT]
> The encrypter/decrypter and P2P chat use separate encryption systems. The
> chat does not use `key.txt`.

## Project Structure

```text
.
|-- main.py                 # Terminal menu
|-- Key.py                  # Fernet key generator
|-- saving.py               # Shared-key importer
|-- szyfrowanie.py          # Terminal message encryption
|-- odszyfrowanie.py        # Terminal message decryption
|-- ui.py                   # Graphical encrypter/decrypter
|-- key.txt                 # Local Fernet key
`-- chat/
    |-- main.py             # Chat entry point
    |-- ui.py               # Chat interface
    |-- connecting.py       # TCP transport and key exchange
    |-- encryption.py       # AES-GCM encryption
    `-- decryption.py       # AES-GCM decryption
```

## Requirements

- Windows 10 or Windows 11.
- Python 3.10 or newer.
- [`cryptography`](https://cryptography.io/).
- Hamachi or Radmin VPN when using a virtual network.

## Installation

```powershell
git clone <REPOSITORY_URL>
cd chatcontrol-encrypter-decrypter

py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip cryptography
```

# Manual Encrypter / Decrypter

The manual tools convert text into authenticated Fernet tokens. The sender and
recipient must use the same shared key.

## Terminal Menu

```powershell
py main.py
```

```text
1. Generate a new key
2. Encrypt a message
3. Decrypt a message
4. Open the graphical interface
5. Paste or save an existing key
0. Exit
```

## Shared-Key Workflow

```text
Sender                                 Recipient
  |                                        |
  |-- Share key through trusted channel ->|-- Save key
  |                                        |
  `-- Send encrypted token -------------->|-- Decrypt token
```

### Generate or Import a Key

```powershell
# Generate a new key and save it to key.txt:
py Key.py

# Validate and import an existing shared key:
py saving.py
```

> [!WARNING]
> Generating a new key overwrites the current key. Previous messages cannot be
> decrypted without a backup of the previous key. Never publish or commit
> `key.txt`.

### Encrypt a Message

```powershell
py szyfrowanie.py
```

```text
Message: Secret message
Encrypted message: gAAAAAB...
```

### Decrypt a Message

```powershell
py odszyfrowanie.py
```

```text
Encrypted message: gAAAAAB...
Decrypted message: Secret message
```

Decryption fails if the key is different, the token was modified, or the token
is incomplete.

## Graphical Encrypter / Decrypter

```powershell
py ui.py
```

The UI supports key generation and import, encryption, decryption, clipboard
copying, Unicode, and emoji.

```text
Generate key -> Enter text  -> Encrypt -> Copy output
Import key   -> Paste token -> Decrypt
```

# Encrypted P2P Chat

The chat establishes a direct TCP connection and negotiates fresh encryption
keys for every session.

```text
Client ---------------- TCP ----------------> Host
       X25519 key agreement
       HKDF-SHA256 key derivation
       AES-256-GCM message encryption
```

## Running the Chat

```powershell
py -m chat.main
```

One user clicks **Host**. The other enters the host address and clicks
**Connect**. Both users must use the same port; the default is `5050`.

## Connecting Through Hamachi

Hamachi avoids router port forwarding.

1. Install Hamachi on both computers.
2. Join the same Hamachi network.
3. Start the chat on the host and click **Host**.
4. Enter the host's Hamachi IPv4 address on the client.
5. Keep port `5050` on both computers.
6. Click **Connect** on the client.

```text
Host:
  Port:   5050
  Action: Host

Client:
  Address: <HOST_HAMACHI_IP>
  Port:    5050
  Action:  Connect
```

> [!NOTE]
> `127.0.0.1` points to the current computer. It cannot connect to another
> user.

## Windows Firewall

Run PowerShell as Administrator on the host computer:

```powershell
New-NetFirewallRule `
    -DisplayName 'Encrypted Chat Hamachi' `
    -Direction Inbound `
    -Action Allow `
    -Protocol TCP `
    -LocalPort 5050 `
    -RemoteAddress 25.0.0.0/8 `
    -Profile Any
```

This rule allows inbound TCP connections on port `5050` from the Hamachi IPv4
range.

## Testing a Hamachi Connection

Run this command on the client while the host is listening:

```powershell
Test-NetConnection <HOST_HAMACHI_IP> -Port 5050
```

Expected result:

```text
TcpTestSucceeded : True
```

## Other Connection Methods

| Method | Client address | Port forwarding |
| --- | --- | --- |
| Same LAN | Host LAN address, such as `192.168.1.20` | No |
| Hamachi | Host Hamachi address, such as `25.x.x.x` | No |
| Radmin VPN | Host Radmin address, such as `26.x.x.x` | No |
| Public Internet | Host public IPv4 address | Usually required |

For a direct public Internet connection, configure the host router:

```yaml
protocol: TCP
external_port: 5050
internal_ip: <HOST_LAN_IP>
internal_port: 5050
```

Direct hosting may not work behind CGNAT. Use Hamachi, Radmin VPN, or a public
relay in that case.

## Building a Standalone Chat Executable

Create `chat_launcher.py` in the project root:

```python
from chat.ui import ChatApp

if __name__ == '__main__':
    ChatApp().run()
```

Build the executable:

```powershell
py -m pip install --upgrade pyinstaller cryptography

py -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name EncryptedChat `
    chat_launcher.py
```

```text
Output: dist\EncryptedChat.exe
```

The recipient does not need Python. Hamachi is still required when connecting
through a Hamachi network.

# Security

## Manual Encrypter / Decrypter

- Anyone with `key.txt` can decrypt tokens created with that key.
- Never commit or publish `key.txt`.
- Do not send the key together with the encrypted token.
- Keep a secure backup if old tokens must remain decryptable.

## P2P Chat

Compare the displayed fingerprint through an independent trusted channel:

```text
Host fingerprint == Client fingerprint
```

Terminate the connection if the fingerprints differ.

> [!CAUTION]
> This project has not undergone an independent security audit. Do not treat it
> as a replacement for professionally audited communication software.

# Legal Notice

This software is a general-purpose privacy and communication tool. Users are
solely responsible for ensuring that their use complies with all applicable
laws and regulations.

The author does not endorse unlawful activity and, to the maximum extent
permitted by applicable law, accepts no responsibility for illegal use,
misuse, damages, claims, or other consequences arising from its use.

# License

Released under the [MIT License](https://github.com/muddpunch/chatcontrol-encrypter-decrypter/tree/main?tab=MIT-1-ov-file).

## UI Preview

**CHAT**<br>
<img width='702' height='544' alt='image' src='https://github.com/user-attachments/assets/48153917-0d6c-4fe7-a0d2-db5698bec39f' /><br>
**ENCRYPTER**<br>
<img width='647' height='530' alt='{96C89EFF-DCC2-426F-9D2B-AAB07612E1C4}' src='https://github.com/user-attachments/assets/61ff9437-d381-4c97-b72f-c8f95234c364' />

*README is ai generated :sob:*

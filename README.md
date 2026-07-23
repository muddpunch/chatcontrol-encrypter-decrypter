# 🔐 Encrypted Chat

  A lightweight peer-to-peer encrypted chat application. It does not require a central chat server: one user hosts the
  session and another connects through LAN, Hamachi, Radmin VPN, or a publicly reachable address.

  ## How It Works

  ```text
  Client ───── TCP connection ─────► Host
         X25519 key agreement
         HKDF-SHA256 key derivation
         AES-256-GCM encryption
  ```

  Every connection receives fresh session keys. Messages are encrypted before transmission and decrypted only by the
  connected peer.

  ## Features

  - Direct peer-to-peer communication.
  - AES-256-GCM authenticated encryption.
  - X25519 ephemeral key agreement.
  - Separate transmission keys for each direction.
  - Unique nonce for every message.
  - Connection fingerprint verification.
  - Unicode and emoji support.
  - No persistent chat history.
  - Single-file Windows executable support.

  ## Requirements

  - Windows 10 or Windows 11.
  - Python 3.10 or newer when running from source.
  - `cryptography`.
  - Hamachi or Radmin VPN when using a virtual network.

  ## Installation

  ```powershell
  git clone <REPOSITORY_URL>
  cd chatcontrol-encrypter-decrypter

  py -m venv .venv
  .\.venv\Scripts\Activate.ps1
  py -m pip install --upgrade pip cryptography
  ```

  ## Running From Source

  ```powershell
  py -m chat.main
  ```

  ## Connecting Through Hamachi

  Router port forwarding is not required when using Hamachi.

  1. Install Hamachi on both computers.
  2. Join the same Hamachi network.
  3. The host starts the application and clicks **Host**.
  4. The client enters the host's Hamachi IPv4 address.
  5. Both users keep port `5050`.
  6. The client clicks **Connect**.

  ```text
  Host:
  Port:   5050
  Action: Host

  Client:
  Address: <HOST_HAMACHI_IP>
  Port:    5050
  Action:  Connect
  ```

  > `127.0.0.1` always points to the client's own computer. It cannot be used to connect to another user.

  ## Windows Firewall

  Run PowerShell as Administrator on the host computer:

  ```powershell
  New-NetFirewallRule `
      -DisplayName "Encrypted Chat Hamachi" `
      -Direction Inbound `
      -Action Allow `
      -Protocol TCP `
      -LocalPort 5050 `
      -RemoteAddress 25.0.0.0/8 `
      -Profile Any
  ```

  This rule allows inbound TCP connections on port `5050` only from the Hamachi address range.

  ## Testing the Connection

  Run this command on the client while the host is listening:

  ```powershell
  Test-NetConnection <HOST_HAMACHI_IP> -Port 5050
  ```

  Expected result:

  ```text
  TcpTestSucceeded : True
  ```

  If the result is `False`, verify that:

  - Both computers are online in the same Hamachi network.
  - The host clicked **Host** before running the test.
  - The client entered the host's Hamachi address.
  - Both applications use port `5050`.
  - The firewall rule exists on the host computer.

  ## Local Network Connection

  When both computers use the same router, the client can connect directly to the host's LAN address:

  ```text
  Example:
  192.168.1.20:5050
  ```

  The host's LAN address is displayed in the application.

  ## Public Internet Connection

  Without Hamachi or another VPN, the host's router must forward the TCP port:

  ```yaml
  protocol: TCP
  external_port: 5050
  internal_ip: "<HOST_LAN_IP>"
  internal_port: 5050
  ```

  The client connects to the host's public IPv4 address. Direct hosting may not work behind CGNAT; use Hamachi, Radmin
  VPN, or a public relay in that case.

  ## Security

  After connecting, both applications display a fingerprint. Compare it through an independent trusted channel, such as
  a voice call:

  ```text
  Host fingerprint == Client fingerprint
  ```

  Terminate the connection immediately if the fingerprints differ.

  This project has not undergone an independent security audit. Do not treat it as a replacement for professionally
  audited communication software.

  ## Legal Notice

  This software is a general-purpose privacy and communication tool. Users are solely responsible for ensuring that
  their use complies with all applicable laws and regulations.

  The author does not endorse unlawful activity and, to the maximum extent permitted by applicable law, accepts no
  responsibility for illegal use, misuse, damages, claims, or other consequences arising from the use of this software.

  ## UI Preview

  **CHAT**
  <img width="702" height="544" alt="image" src="https://github.com/user-attachments/assets/48153917-0d6c-4fe7-a0d2-db5698bec39f" />
  **ENCRYPTER**
  <img width="647" height="530" alt="{96C89EFF-DCC2-426F-9D2B-AAB07612E1C4}" src="https://github.com/user-attachments/assets/61ff9437-d381-4c97-b72f-c8f95234c364" />


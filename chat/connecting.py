from __future__ import annotations
import hashlib
import socket
import struct
import threading
from dataclasses import dataclass, field

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from .decryption import decrypt_message
from .encryption import AAD, encrypt_message

MAGIC = b"CCHAT001"
MAX_FRAME_SIZE = 1024 * 1024
DEFAULT_PORT = 5050

def _recv_exact(sock: socket.socket, size: int) -> bytes:
    data = bytearray()
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Connection lost.")
        data.extend(chunk)
    return bytes(data)
def _send_frame(sock: socket.socket, payload: bytes) -> None:
    if len(payload) > MAX_FRAME_SIZE:
        raise ValueError("Protocol frame is too big.")
    sock.sendall(struct.pack("!I", len(payload)) + payload)
def _receive_frame(sock: socket.socket) -> bytes:
    size = struct.unpack("!I", _recv_exact(sock, 4))[0]
    if size < 28 or size > MAX_FRAME_SIZE:
        raise ValueError("Invalid frame size.")
    return _recv_exact(sock, size)
def _create_ciphers(
        sock: socket.socket,
        is_host: bool,
) -> tuple[AESGCM, AESGCM, str]:
    private_key = X25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    sock.sendall(MAGIC + public_key)
    peer_hello = _recv_exact(sock, len(MAGIC) + 32)

    if peer_hello[: len(MAGIC)] != MAGIC:
        raise ValueError("Unsupported version of protocol.")
    peer_public_bytes = peer_hello[len(MAGIC):]
    peer_public_key = X25519PublicKey.from_public_bytes(peer_public_bytes)
    shared_secret = private_key.exchange(peer_public_key)

    ordered_keys = sorted((public_key, peer_public_bytes))
    salt = hashlib.sha256(
        MAGIC + ordered_keys[0] + ordered_keys[1]
    ).digest()
    key_material = HKDF(
        algorithm=hashes.SHA256(),
        length=64,
        salt=salt,
        info=AAD,
    ).derive(shared_secret)

    host_key = key_material[:32]
    client_key = key_material[32:]
    tx_key, rx_key = (
        (host_key, client_key)
        if is_host
        else (client_key, host_key)
    )
    fingerprint = hashlib.sha256(
        b"fingerprint"
        + shared_secret
        + ordered_keys[0]
        + ordered_keys[1]
    ).hexdigest().upper()[:24]
    fingerprint = " ".join(
        fingerprint[index : index + 4]
        for index in range(0, len(fingerprint), 4)
    )
    return AESGCM(tx_key), AESGCM(rx_key), fingerprint
@dataclass(slots=True)
class SecureConnection:
    sock: socket.socket
    peer_ip: str
    tx_cipher: AESGCM
    rx_cipher: AESGCM
    fingerprint: str
    _send_lock: threading.Lock = field(
        default_factory=threading.Lock,
        repr=False
    )
    _close_lock: threading.Lock = field(
        default_factory=threading.Lock,
        repr=False,
    )
    _closed: bool = field(default=False, repr=False)

    def send(self, message: str) -> None:
        payload = encrypt_message(self.tx_cipher, message)
        with self._send_lock:
            if self._closed:
                raise ConnectionError("Connection got closed.")
            _send_frame(self.sock, payload)
    def receive(self) -> str:
        if self._closed:
            raise ConnectionError("Connection got closed.")
        return decrypt_message(
            self.rx_cipher,
            _receive_frame(self.sock),
        )
    def close(self) -> None:
        with self._close_lock:
            if self._closed:
                return
            self._closed = True
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.sock.close()
def _secure_connection(
        sock: socket.socket,
        is_host: bool,
) -> SecureConnection:
    sock.settimeout(None)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    tx_cipher, rx_cipher, fingerprint = _create_ciphers(
        sock,
        is_host,
    )
    return SecureConnection(
        sock=sock,
        peer_ip=sock.getpeername()[0],
        tx_cipher=tx_cipher,
        rx_cipher=rx_cipher,
        fingerprint=fingerprint,
    )
def connect_to_peer(
        host: str,
        port: int,
        timeout: float = 8.0,
) -> SecureConnection:
    sock = socket.create_connection((host, port), timeout=timeout)
    try:
        return _secure_connection(sock, is_host=False)
    except Exception:
        sock.close()
        raise
def wait_for_peer(
        port: int,
        stop_event: threading.Event,
) -> SecureConnection:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        listener.bind(("0.0.0.0", port))
        listener.listen(1)
        listener.settimeout(0.5)
        while not stop_event.is_set():
            try:
                sock, _ = listener.accept()
                break
            except socket.timeout:
                continue
        else:
            raise ConnectionAbortedError("Listening stopped.")
    finally:
        listener.close()
    try:
        return _secure_connection(sock, is_host=True)
    except Exception:
        sock.close()
        raise
def get_local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try: 
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()
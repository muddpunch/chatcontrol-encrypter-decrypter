import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from .connecting import (
    DEFAULT_PORT,
    SecureConnection,
    connect_to_peer,
    get_local_ip,
    wait_for_peer,
)

class ChatApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Encrypted Chat")
        self.root.geometry("700x500")
        self.connection: SecureConnection | None = None
        self.stop_event = threading.Event()
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.host = tk.StringVar(value="127.0.0.1")
        self.port = tk.StringVar(value=str(DEFAULT_PORT))
        self.status = tk.StringVar(value=f"Local IP: {get_local_ip()}")
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.after(100, self._process_events)
    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")
        ttk.Entry(top, textvariable=self.host).pack(side="left", expand=True, fill="x")
        ttk.Entry(top, textvariable=self.port, width=8).pack(side="left", padx="5")
        ttk.Button(top, text="Connect", command=self._connect).pack(side="left")
        ttk.Button(top, text="Host", command=self._host).pack(side="left", padx=5)
        self.messages = tk.Text(self.root, state="disabled", wrap="word")
        self.messages.pack(expand="True", fill="both", padx="10")
        bottom = ttk.Frame(self.root, padding=10)
        bottom.pack(fill="x")
        self.message = ttk.Entry(bottom)
        self.message.pack(side="left", expand="True", fill="x")
        self.message.bind("<Return>", lambda _: self._send())

        ttk.Button(bottom, text="send", command=self._send).pack(side="left", padx="5")
        ttk.Label(self.root, textvariable=self.status).pack(anchor="w", padx=10, pady="5")
    def _port(self) -> int:
        port = int(self.port.get())
        if not 1 <= port <= 65535:
            raise ValueError("Port must be between 1 and 65535.")
        return port
    def _connect(self) -> None:
        try:
            host, port = self.host.get().strip(), self._port()
        except ValueError as error:
            messagebox.showerror("Invalid address", str(error))
            return
        self.status.set("Connecting...")
        self._start_connection(lambda: connect_to_peer(host, port))
    def _host(self) -> None:
        try:
            port = self._port()
        except ValueError as error:
            messagebox.showerror("Invalid port", str(error))
            return
        self.status.set(f"Listening on {get_local_ip()}:{port}")
        self._start_connection(lambda: wait_for_peer(port, self.stop_event))
    def _start_connection(self, factory) -> None:
        if self.connection is not None:
            return
        self.stop_event.clear()
        threading.Thread(
            target=self._connection_worker,
            args=(factory,),
            daemon=True,
        ).start()
    def _connection_worker(self, factory) -> None:
        try:
            connection = factory()
            self.events.put(("connected", connection))
            while not self.stop_event.is_set():
                self.events.put(("message", connection.receive()))
        except Exception as error:
            if not self.stop_event.is_set():
                self.events.put(("error", error))
        finally:
            self.events.put(("disconnected", None))
    def _send(self) -> None:
        message = self.message.get().strip()
        if not message or self.connection is None:
            return
        try:
            self.connection.send(message)
        except Exception as error:
            messagebox.showerror("Send failed", str(error))
            return
        self.message.delete(0, tk.END)
        self._append(f"You: {message}")
    def _append(self, message: str) -> None:
        self.messages.configure(state="normal")
        self.messages.insert(tk.END, f"{message}\n")
        self.messages.configure(state="disabled")
        self.messages.see(tk.END)
    def _process_events(self) -> None:
        while not self.events.empty():
            event, value = self.events.get_nowait()
            if event == "connected":
                self.connection = value
                self.status.set(
                    f"Connected: {value.peer_ip} | Fingerprint: {value.fingerprint}"
                )
            elif event == "message":
                self._append(f"Peer: {value}")
            elif event == "error":
                messagebox.showerror("Connection error", str(value))
            elif event == "disconnected":
                self.connection = None
                self.status.set("Disconnected")
        self.root.after(100, self._process_events)
    def _close(self) -> None:
        self.stop_event.set()
        if self.connection is not None:
            self.connection.close()
        self.root.destroy()
    def run(self) -> None:
        self.root.mainloop()

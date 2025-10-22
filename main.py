#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FTP Honeypot (using pyftpdlib)

Features:
- Logs all connections, logins, and file uploads.
- Default user: ftpuser / 1234 (or set via environment variables).
- Admin console on stdin:
    - passwd NEWPASS  → change FTP password at runtime
    - quit / exit     → stop the server
- Uses port 21
- Logging saved to ftp_honeypot.log
"""

import os
import logging
import threading
import time
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Configuration (can override with environment variables)
FTP_DIRECTORY = os.environ.get("FTP_ROOT", "ftp_root")
LOG_FILE = os.environ.get("LOG_FILE", "ftp_honeypot.log")
BIND_IP = os.environ.get("BIND_IP", "0.0.0.0")
BIND_PORT = int(os.environ.get("PORT", "21"))
FTP_USER = os.environ.get("FTP_USER", "testftppno9")
INITIAL_PASS = os.environ.get("FTP_PASS", "test@pno9")

# Ensure FTP directory exists
os.makedirs(FTP_DIRECTORY, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
console_logger = logging.getLogger("console")
console_logger.setLevel(logging.INFO)

def build_authorizer(password):
    """Create an FTP authorizer with given password."""
    auth = DummyAuthorizer()
    auth.add_user(FTP_USER, password, FTP_DIRECTORY, perm="elradfmwMT")
    return auth

class HoneyHandler(FTPHandler):
    """Logs connection and file activity."""
    def on_connect(self):
        msg = f"[+] Connection from {self.remote_ip}:{self.remote_port}"
        print(msg); logging.info(msg)

    def on_disconnect(self):
        msg = f"[-] Disconnected {self.remote_ip}:{self.remote_port}"
        print(msg); logging.info(msg)

    def on_login(self, username):
        msg = f"[+] Login success: user={username} from {self.remote_ip}"
        print(msg); logging.info(msg)

    def on_login_failed(self, username, password):
        msg = f"[!] Login failed: user={username} pass={password} from {self.remote_ip}"
        print(msg); logging.info(msg)

    def on_file_received(self, filepath):
        msg = f"[+] File uploaded: {filepath} from {self.remote_ip}"
        print(msg); logging.info(msg)

def admin_console(authorizer, server):
    """Simple admin console for changing password or stopping the server."""
    prompt = "admin> "
    try:
        while True:
            cmd = input(prompt).strip()
            if not cmd:
                continue
            parts = cmd.split()
            if parts[0].lower() in ("quit", "exit"):
                print("Shutting down (admin requested)...")
                logging.info("Admin requested shutdown.")
                server.close_all()
                break
            elif parts[0].lower() == "passwd" and len(parts) == 2:
                newpw = parts[1]
                try:
                    authorizer.remove_user(FTP_USER)
                except Exception:
                    pass
                authorizer.add_user(FTP_USER, newpw, FTP_DIRECTORY, perm="elradfmwMT")
                msg = f"[+] Password changed for {FTP_USER}"
                print(msg); logging.info(msg)
            else:
                print("Commands: passwd NEWPASS  |  quit")
    except (EOFError, KeyboardInterrupt):
        print("\nAdmin console exiting.")
        logging.info("Admin console terminated by signal.")

def main():
    password = INITIAL_PASS
    authorizer = build_authorizer(password)
    handler = HoneyHandler
    handler.authorizer = authorizer
    handler.banner = "FTP Server"

    server = FTPServer((BIND_IP, BIND_PORT), handler)
    print(f"[*] FTP Honeypot running on {BIND_IP}:{BIND_PORT} (user: {FTP_USER})")
    logging.info(f"FTP Honeypot starting on {BIND_IP}:{BIND_PORT} user={FTP_USER}")

    # Start admin console thread
    t = threading.Thread(target=admin_console, args=(authorizer, server), daemon=True)
    t.start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Keyboard interrupt received, shutting down.")
    finally:
        server.close_all()
        logging.info("FTP Honeypot stopped.")
        print("Server stopped.")

if __name__ == "__main__":
    main()

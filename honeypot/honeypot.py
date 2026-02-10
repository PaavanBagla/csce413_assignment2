#!/usr/bin/env python3
"""Starter template for the honeypot assignment."""

import socket
import threading
import time
from logger import create_logger

HONEYPOT_PORT = 22
BANNER = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.7\r\n"

logger = create_logger()

def handle_client(conn, addr):
    ip, port = addr
    start_time = time.time()
    logger.info("New connection from %s:%s", ip, port)

    try:
        # Send fake SSH banner
        conn.sendall(BANNER.encode())

        # Simulate simple login prompt
        conn.sendall(b"login username: ")
        username = conn.recv(1024).decode(errors="ignore").strip()

        # Ignore SSH protocol negotiation pretending to be username
        if username.startswith("SSH-"):
            logger.info(
                "SSH handshake attempt from %s:%s (client banner captured: %s)",
                ip,
                port,
                username,
            )
            return  # stop handling this client

        conn.sendall(f"Password: ")
        password = conn.recv(1024).decode(errors="ignore").strip()

        # Log the attempted credentials
        logger.info(
            "Auth attempt from %s:%s -> username='%s', password='%s'",
            ip,
            port,
            username,
            password,
        )

        # Fake delay and close connection
        time.sleep(1)
        conn.sendall(b"Permission denied, please try again.\r\n")
    except Exception as e:
        logger.error("Error with connection %s:%s -> %s", ip, port, e)
    finally:
        conn.close()
        duration = time.time() - start_time
        logger.info("Connection from %s:%s closed (duration %.2f seconds)", ip, port, duration)

def run_honeypot():
    """Listen on port 22 and handle incoming connections."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", HONEYPOT_PORT))
    sock.listen(5)
    logger.info("Honeypot listening on port %s", HONEYPOT_PORT)

    while True:
        try:
            conn, addr = sock.accept()
            # Handle each client in a separate thread
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
        except KeyboardInterrupt:
            logger.info("Shutting down honeypot.")
            sock.close()
            break
        except Exception as e:
            logger.error("Error accepting connection: %s", e)


if __name__ == "__main__":
    run_honeypot()

#!/usr/bin/env python3
"""Starter template for the port knocking server."""

import argparse
import logging
import socket
import time
import subprocess
import select

DEFAULT_KNOCK_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_SEQUENCE_WINDOW = 10.0

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

def open_protected_port(protected_port):
    """Open the protected port using firewall rules."""
    logging.info(f"Opening firewall for port {protected_port}")
    # TODO: Use iptables/nftables to allow access to protected_port.
    subprocess.run(
        [
            "iptables",
            "-I", "INPUT",
            "-p", "tcp",
            "--dport", str(protected_port),
            "-j", "ACCEPT",
        ],
        check=False,
    )

def close_protected_port(protected_port):
    logging.info(f"Closing protected port {protected_port}")

    # Delete ACCEPT rule if exists, suppress errors
    subprocess.run(
        f"iptables -D INPUT -p tcp --dport {protected_port} -j ACCEPT",
        shell=True,
        check=False,
        stderr=subprocess.DEVNULL,  # <-- suppress "Bad rule"
    )

    # Add REJECT rule if not exists, suppress errors
    subprocess.run(
        f"iptables -C INPUT -p tcp --dport {protected_port} -j REJECT || iptables -A INPUT -p tcp --dport {protected_port} -j REJECT --reject-with tcp-reset",
        shell=True,
        check=False,
        stderr=subprocess.DEVNULL,
    )

def listen_for_knocks(sequence, window_seconds, protected_port):
    """Listen for knock sequence and open the protected port."""
    logger = logging.getLogger("KnockServer")
    logger.info("Listening for knocks: %s", sequence)
    logger.info("Protected port: %s", protected_port)

    # Ensure the protected port is CLOSED at startup
    close_protected_port(protected_port)

    # Create a non-blocking TCP socket for each knock port
    sockets = {}
    for port in sequence:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", port))
        s.listen()
        s.setblocking(False)
        sockets[port] = s

    # Track knock progress per IP address
    # Example:
    # progress["1.2.3.4"] = {"index": 1, "start": timestamp}
    progress = {}

    while True:
        # Wait for activity on any knock port
        readable, _, _ = select.select(sockets.values(), [], [], 1)

        for s in readable:
            conn, addr = s.accept()
            ip = addr[0]
            port = s.getsockname()[1]
            conn.close()

            now = time.time()

            # Initialize or retrieve progress for this IP
            state = progress.get(ip, {"index": 0, "start": now})

            # Enforce timing window
            if now - state["start"] > window_seconds:
                logger.info("Timing window expired for %s — resetting", ip)
                state = {"index": 0, "start": now}

            expected_port = sequence[state["index"]]

            if port == expected_port:
                state["index"] += 1
                progress[ip] = state
                logger.info(
                    "Correct knock %d/%d from %s",
                    state["index"],
                    len(sequence),
                    ip,
                )

                # Full sequence completed
                if state["index"] == len(sequence):
                    logger.info("Correct sequence completed by %s", ip)
                    open_protected_port(protected_port)
                    progress.pop(ip, None)

            else:
                # Wrong port → reset sequence
                logger.warning(
                    "Incorrect knock from %s on port %s — resetting",
                    ip,
                    port,
                )
                progress[ip] = {"index": 0, "start": now}

        time.sleep(0.1)

def parse_args():
    parser = argparse.ArgumentParser(description="Port knocking server starter")
    parser.add_argument(
        "--sequence",
        default=",".join(str(port) for port in DEFAULT_KNOCK_SEQUENCE),
        help="Comma-separated knock ports",
    )
    parser.add_argument(
        "--protected-port",
        type=int,
        default=DEFAULT_PROTECTED_PORT,
        help="Protected service port",
    )
    parser.add_argument(
        "--window",
        type=float,
        default=DEFAULT_SEQUENCE_WINDOW,
        help="Seconds allowed to complete the sequence",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging()

    try:
        sequence = [int(port) for port in args.sequence.split(",")]
    except ValueError:
        raise SystemExit("Invalid sequence. Use comma-separated integers.")

    listen_for_knocks(sequence, args.window, args.protected_port)


if __name__ == "__main__":
    main()
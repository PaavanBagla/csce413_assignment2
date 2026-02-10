## Port Knocking Starter Template

This directory contains my implementation of a simple port knocking system using Python and `iptables`.

The goal is to keep a protected port closed by default and only open it after a correct sequence of connection attempts (knocks) is received within a short time window.

---

### How it works

- The server listens on a predefined sequence of ports (default: `1234, 5678, 9012`).
- Each client connection attempt is treated as a “knock”.
- The server tracks knock progress per IP address and enforces a timing window.
- If the correct sequence is completed in order, the protected port (`2222`) is opened using `iptables`.
- Any incorrect knock or timeout resets the sequence.
- The port is closed again when the server restarts.

---

### Components

- **`knock_server.py`**
  - Listens on knock ports using non-blocking sockets.
  - Tracks knock order and timing per client IP.
  - Opens and closes the protected port using `iptables`.

- **`knock_client.py`**
  - Sends connection attempts to each knock port in order.
  - Optionally verifies access to the protected port after knocking.

- **`demo.sh`**
  - Demonstrates the full flow:
    1. Attempts to access the protected port before knocking (fails).
    2. Sends the knock sequence.
    3. Attempts to access the protected port again (succeeds).

---

### Running the demo

Run the demo script with root privileges:

```bash
sudo ./demo.sh

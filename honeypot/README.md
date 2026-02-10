# Honeypot Design Explanation

## Purpose
This honeypot simulates an SSH service to detect and log unauthorized access attempts. It is intentionally lightweight and does not provide real SSH access. Instead, it captures connection attempts, SSH handshakes, and login credentials for analysis.

# Design Overview
- The honeypot runs inside a Docker container.
- It listens on port 22 inside the container to mimic a real SSH service.
- Docker port forwarding exposes it on port 2222 on the host.
- Any incoming connection receives a fake SSH banner.
- Usernames and passwords are logged, but access is always denied.

# Key Features
- Fake SSH banner to appear legitimate
- Detection of SSH protocol handshakes
- Credential capture (username/password)
- File-based logging for later analysis

# Technologies Used
- Python (socket programming)
- Docker & Docker Compose
- TCP networking
- Logging module

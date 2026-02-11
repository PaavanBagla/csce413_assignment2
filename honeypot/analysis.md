### Honeypot Analysis

## Summary of Observed Attacks
During testing, the honeypot recorded multiple unauthorized connection attempts targeting the SSH service. Two main types of activity were observed:

# Attack 1: SSH Client Handshake
```bash
ssh testuser@localhost -p 2022
```
This simulates an attacker attempting to connect using a real SSH client.

# Results:
- The SSH handshake banner was captured
- The connection was immediately closed
- Logged as a protocol-level attack

# Attack 2: Manual Credential Attempt
```bash
nc localhost 2022
```
A fake username and password were entered manually.

# Results:
- Username and password were successfully logged
- Access was denied
- Connection closed after a delay

# Observations
- Real SSH clients do not reach the login stage
- Manual TCP clients expose credential attempts clearly
- The honeypot reliably logs attacker behavior without risk

## Notable Patterns
- SSH clients send an SSH-2.0-* banner before any authentication attempt.
- Manual TCP connections (e.g., using netcat) reach the login and password prompts.
- Attackers repeatedly attempt common or simple usernames and passwords.
- All connections were short-lived and terminated after authentication failure.
- No successful authentication attempts were observed.

These patterns are consistent with early-stage reconnaissance and brute-force behavior.

## Recommendations
- Deploy the honeypot on non-standard ports to reduce noise while still capturing attacks.
- Aggregate logs over time to identify repeated source IPs.
- Combine the honeypot with firewall rules or port knocking for layered defense.
- Extend logging to include timestamps and connection frequency for better analysis.

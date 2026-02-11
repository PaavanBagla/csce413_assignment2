#!/usr/bin/env python3
"""
Port Scanner - Starter Template for Students
Assignment 2: Network Security

This is a STARTER TEMPLATE to help you get started.
You should expand and improve upon this basic implementation.

TODO for students:
1. Implement multi-threading for faster scans
2. Add banner grabbing to detect services
3. Add support for CIDR notation (e.g., 192.168.1.0/24)
4. Add different scan types (SYN scan, UDP scan, etc.)
5. Add output formatting (JSON, CSV, etc.)
6. Implement timeout and error handling
7. Add progress indicators
8. Add service fingerprinting
"""

import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def grab_banner(sock):
    """
    Attempt to grab a service banner from an open socket.
    This helps identify what service is running on the port.
    """
    try:
        # Set a short timeout so we don't hang waiting for data
        sock.settimeout(1.0)

        # Try passive banner grab (many services send first)
        try:
            data = sock.recv(1024)
            if data:
                return data.decode(errors="ignore").strip()
        except socket.timeout:
            pass
        
        # If no banner, try HTTP probe
        http_request = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
        sock.sendall(http_request)

        data = sock.recv(1024)
        banner = data.decode(errors="ignore")

        # Return HTTP headers only
        headers = banner.split("\r\n\r\n")[0]
        return headers.strip()

    except Exception:
        return "Unknown"

def scan_port(target, port, timeout=0.2):
    """
    Scan a single port on the target host

    Args:
        target (str): IP address or hostname to scan
        port (int): Port number to scan
        timeout (float): Connection timeout in seconds

    Returns:
        state   : "open" or "closed"
        banner  : service banner if available
    """
    try:
        # TODO: Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # TODO: Set timeout
        sock.settimeout(timeout)
        # TODO: Try to connect to target:port
        result = sock.connect_ex((target, port))

        if result == 0:
            # If connection succeeds, the port is open
            banner = grab_banner(sock)
            sock.close()
            return "open", banner
        else:
            sock.close()
            return "closed", None

    except (socket.timeout, ConnectionRefusedError, OSError):
        # Handle common network-related errors safely
        return "closed", None

def scan_range(target, start_port, end_port, max_threads=200):
    """
    Scan a range of ports on the target host

    Args:
        target (str): IP address or hostname to scan
        start_port (int): Starting port number
        end_port (int): Ending port number

    Returns:
        list: List of open ports
    """
    open_ports = []
    total_ports = end_port - start_port + 1
    scanned = 0

    print(f"[*] Scanning {target} from port {start_port} to {end_port}")
    print(f"[*] This may take a while...")

    # TODO: Implement the scanning logic
    # Hint: Loop through port range and call scan_port()
    # Hint: Consider using threading for better performance
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {
            executor.submit(scan_port, target, port): port
            for port in range(start_port, end_port + 1)
        }
        for future in as_completed(futures):
            port = futures[future]
            scanned += 1

            try:
                state, banner = future.result()

                if state == "open":
                    print(f"\n[+] Port {port}/tcp OPEN")
                    if banner:
                        print(f"    Service: {banner}")
                    open_ports.append((port, banner))

            except KeyboardInterrupt:
                print("\n[!] Scan interrupted by user")
                break

            # Progress indicator
            percent = (scanned / total_ports) * 100
            print(f"\rProgress: {scanned}/{total_ports} ({percent:.1f}%)", end="")

    print()  # new line after progress bar
    return open_ports

def main():
    """Main function"""
    # Example usage (you should improve this):
    if len(sys.argv) < 2:
        print("Usage: python3 -m port_scanner --target <host> --ports <start-end>")
        print("Example: python3 -m port_scanner --target 172.20.0.0/24 --ports 1-10000")
        sys.exit(1)

    # TODO: Parse command-line arguments
    try:
        target = sys.argv[sys.argv.index("--target") + 1]
        port_range = sys.argv[sys.argv.index("--ports") + 1]
    except IndexError:
        print("[!] Missing argument value")
        sys.exit(1)

    start_port, end_port = map(int, port_range.split("-"))

    # Record the start time to measure scan duration
    start_time = time.time()

    open_ports = scan_range(target, start_port, end_port)

    print("\n==============================")
    print(f"[+] Scan complete for {target}")
    print(f"[+] Open ports found: {len(open_ports)}\n")

    for port, banner in open_ports:
        service = banner if banner else "Unknown"
        print(f"Port {port}/tcp - {service}")

    end_time = time.time()
    print(f"\n[+] Total scan time: {end_time - start_time:.2f} seconds")
    print("==============================")

if __name__ == "__main__":
    main()
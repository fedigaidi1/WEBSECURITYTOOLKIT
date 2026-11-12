import socket
import ssl
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# =====================================
# WEB & NETWORK SECURITY TOOLKIT
# =====================================

def banner():
    print("""
====================================================
          WEB & NETWORK SECURITY TOOLKIT
====================================================
       Python Ethical Hacking Learning Project
====================================================
    Coded by APACHE (https://github.com/fedigaidi1)
====================================================
""")

def get_domain():
    domain = input("Enter Domain or IP: ").strip()
    if not domain:
        raise ValueError("Domain cannot be empty")
    return domain.replace("https://", "").replace(
        "http://", ""
    ).split("/")[0].split(":")[0]

# =====================================
# A. DOMAIN RECONNAISSANCE
# =====================================

def dns_lookup():
    domain = get_domain()
    try:
        print(socket.getaddrinfo(domain, None))
    except Exception as e:
        print("Error:", e)

def http_headers():
    domain = get_domain()
    url = "https://" + domain

    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "SecurityToolkit/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            print("Status:", response.status)
            for key, value in response.headers.items():
                print(key, ":", value)
    except Exception as e:
        print("Error:", e)

def ssl_checker():
    domain = get_domain()

    try:
        context = ssl.create_default_context()

        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(
                sock, server_hostname=domain
            ) as secure:
                cert = secure.getpeercert()
                print("TLS:", secure.version())
                print("Certificate:", cert)

    except Exception as e:
        print("Error:", e)

def robots_checker():
    domain = get_domain()
    url = "https://" + domain + "/robots.txt"

    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            print(response.read(5000).decode(errors="replace"))
    except Exception as e:
        print("Error:", e)

def sitemap_checker():
    domain = get_domain()
    url = "https://" + domain + "/sitemap.xml"

    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            print(response.read(5000).decode(errors="replace"))
    except Exception as e:
        print("Error:", e)

# =====================================
# B. NETWORK SCANNING
# =====================================

def tcp_scanner():
    domain = get_domain()

    try:
        ip = socket.gethostbyname(domain)
        start = int(input("Start port: "))
        end = int(input("End port (max 1024 ports): "))

        if not (1 <= start <= end <= 65535 and end-start < 1024):
            print("Invalid port range.")
            return

        print("Scanning:", ip)

        for port in range(start, end + 1):
            with socket.socket() as s:
                s.settimeout(0.4)

                if s.connect_ex((ip, port)) == 0:
                    print("[OPEN]", port)

    except Exception as e:
        print("Error:", e)

def banner_grabber():
    domain = get_domain()

    try:
        port = int(input("Enter TCP port: "))
        ip = socket.gethostbyname(domain)

        with socket.create_connection((ip, port), timeout=3) as s:
            s.settimeout(2)

            if port in (80, 8080):
                s.sendall(
                    f"HEAD / HTTP/1.0\r\nHost: {domain}\r\n\r\n".encode()
                )

            try:
                print(s.recv(1024).decode(errors="replace"))
            except socket.timeout:
                print("No banner received.")

    except Exception as e:
        print("Error:", e)

def udp_checker():
    domain = get_domain()
    ip = socket.gethostbyname(domain)

    for port in [53, 123, 161, 500, 1900]:
        try:
            with socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM
            ) as s:
                s.settimeout(1)
                s.sendto(b"\x00", (ip, port))
                data, _ = s.recvfrom(512)
                print("[RESPONSE]", port, len(data))

        except socket.timeout:
            print("[NO RESPONSE / UNKNOWN]", port)
        except OSError as e:
            print("[ERROR]", port, e)

def multi_scanner():
    domain = get_domain()

    try:
        ip = socket.gethostbyname(domain)
        start = int(input("Start port: "))
        end = int(input("End port (max 1024 ports): "))

        if not (1 <= start <= end <= 65535 and end-start < 1024):
            print("Invalid range.")
            return

        def scan(port):
            with socket.socket() as s:
                s.settimeout(0.5)
                if s.connect_ex((ip, port)) == 0:
                    return port
            return None

        with ThreadPoolExecutor(max_workers=30) as executor:
            for result in executor.map(scan, range(start, end + 1)):
                if result:
                    print("[OPEN]", result)

    except Exception as e:
        print("Error:", e)

# =====================================
# C. WEB SECURITY
# =====================================

def security_headers():
    domain = get_domain()

    try:
        req = urllib.request.Request(
            "https://" + domain,
            headers={"User-Agent": "SecurityToolkit/1.0"}
        )

        with urllib.request.urlopen(req, timeout=5) as r:
            headers = {k.lower(): v for k, v in r.headers.items()}

        checks = [
            "strict-transport-security",
            "content-security-policy",
            "x-frame-options",
            "x-content-type-options",
            "referrer-policy",
            "permissions-policy"
        ]

        for item in checks:
            print(
                "[PRESENT]" if item in headers else "[MISSING]",
                item
            )

    except Exception as e:
        print("Error:", e)

def cors_checker():
    domain = get_domain()
    url = "https://" + domain

    try:
        req = urllib.request.Request(
            url,
            headers={"Origin": "https://example.invalid"},
            method="OPTIONS"
        )

        with urllib.request.urlopen(req, timeout=5) as r:
            for k, v in r.headers.items():
                if k.lower().startswith("access-control-"):
                    print(k, ":", v)

    except Exception as e:
        print("Error:", e)

def cookie_checker():
    domain = get_domain()
    url = "https://" + domain

    try:
        req = urllib.request.Request(url)

        with urllib.request.urlopen(req, timeout=5) as r:
            cookies = r.headers.get_all("Set-Cookie") or []

        for cookie in cookies:
            print(cookie)
            for flag in ["Secure", "HttpOnly", "SameSite"]:
                print(flag, ":", flag.lower() in cookie.lower())

    except Exception as e:
        print("Error:", e)

# =====================================
# D. WEB CRAWLING
# =====================================

def url_extractor():
    from html.parser import HTMLParser

    class Parser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.links = []

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                for key, value in attrs:
                    if key == "href":
                        self.links.append(value)

    domain = get_domain()
    url = "https://" + domain

    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            page = r.read(500000).decode(errors="replace")

        parser = Parser()
        parser.feed(page)

        for link in parser.links:
            print(link)

    except Exception as e:
        print("Error:", e)

# =====================================
# E. SECURITY LEARNING LABS
# =====================================

def xss_demo():
    import html

    text = input("Enter test text: ")

    print("Escaped HTML:")
    print(html.escape(text))

def sql_demo():
    import sqlite3

    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE users (username TEXT)")
    db.execute("INSERT INTO users VALUES (?)", ("alice",))

    username = input("Enter username: ")

    result = db.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchall()

    print(result)
    db.close()

def jwt_decoder():
    import base64

    token = input("Enter JWT: ")
    parts = token.split(".")

    if len(parts) != 3:
        print("Invalid JWT format")
        return

    try:
        for part in parts[:2]:
            part += "=" * (-len(part) % 4)
            decoded = base64.urlsafe_b64decode(part)
            print(json.dumps(json.loads(decoded), indent=4))

        print("WARNING: Signature NOT verified.")

    except Exception as e:
        print("Error:", e)

# =====================================
# MAIN MENU
# =====================================

TOOLS = {
    "1": ("DNS Lookup", dns_lookup),
    "2": ("HTTP Headers", http_headers),
    "3": ("SSL Checker", ssl_checker),
    "4": ("Robots.txt", robots_checker),
    "5": ("Sitemap", sitemap_checker),
    "6": ("TCP Port Scanner", tcp_scanner),
    "7": ("Banner Grabber", banner_grabber),
    "8": ("UDP Checker", udp_checker),
    "9": ("Multi-threaded Scanner", multi_scanner),
    "10": ("Security Headers", security_headers),
    "11": ("CORS Checker", cors_checker),
    "12": ("Cookie Checker", cookie_checker),
    "13": ("URL Extractor", url_extractor),
    "14": ("XSS Learning Demo", xss_demo),
    "15": ("SQL Learning Demo", sql_demo),
    "16": ("JWT Decoder", jwt_decoder),
}

def main():
    while True:
        print("""
========================================
       WEB SECURITY TOOLKIT
========================================

A. DOMAIN RECONNAISSANCE
1. DNS Lookup
2. HTTP Headers
3. SSL Checker
4. Robots.txt
5. Sitemap

B. NETWORK SCANNING
6. TCP Port Scanner
7. Banner Grabber
8. UDP Checker
9. Multi-threaded Scanner

C. WEB SECURITY
10. Security Headers
11. CORS Checker
12. Cookie Checker

D. WEB CRAWLING
13. URL Extractor

E. SECURITY LABS
14. XSS Learning Demo
15. SQL Learning Demo
16. JWT Decoder

0. Exit
========================================
""")

        choice = input("Choose tool: ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        if choice not in TOOLS:
            print("Invalid choice!")
            continue

        name, function = TOOLS[choice]

        print("\nStarting:", name)

        if choice not in ("14", "15", "16"):
            if input("Authorized target? (yes/no): ").lower() != "yes":
                print("Scan cancelled.")
                continue

        try:
            function()
        except KeyboardInterrupt:
            print("\nStopped.")
        except Exception as e:
            print("Error:", e)

        input("\nPress Enter to return to menu...")

if __name__ == "__main__":
    banner()
    main()
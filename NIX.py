# NIX

import socket, ipaddress, time, random
from concurrent.futures import ThreadPoolExecutor

default_timeout = 2.0
default_workers = 10

lower_port_limit = 1
upper_port_limit = 1024

common_ports = [21, 22, 23, 25, 53, 80, 443, 3306, 8080]
webserver_ports = [80, 8080, 443, 8443]

buffer_size = 4096

def scan_target(ip, port, show_closed_ports=False):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(default_timeout)
            s.connect((ip, port))
            print(f"[+] {ip}:{port} is open")

            if port in webserver_ports:
                check_web_server(s, ip, port)

    except (socket.timeout, socket.error) as e:
        if show_closed_ports:
            print(f"[-] {ip}:{port} is closed. reason: {type(e).__name__}: {e}")

def check_web_server(s, ip, port):
    try:
            s.sendall(b"HEAD / HTTP/1.1\r\nHost: example.com\r\n\r\n")
            response = s.recv(buffer_size)

            if b"200 OK" in response:
                print(f"[+] Web server is running on {ip}:{port}")
            else:
                print(f"[-] Web server on {ip}:{port} returned a non-success response: {response.decode('utf-8')}")

    except (socket.timeout, socket.error) as e:
        print(f"[-] Failed to connect to the web server at {ip}:{port}. Reason: {type(e).__name__}: {e}")

def scan(ip, ports, show_closed_ports=False, workers=default_workers):

    custom_delay = input("Do you want to set a custom delay? (yes/no): ").lower() == "yes"
    
    if custom_delay:
        try:
            min_delay = float(input("Enter the minimum delay in seconds: "))
            max_delay = float(input("Enter the maximum delay in seconds: "))
        except ValueError:
            print("Invalid input for delay. Please enter valid numeric values. ")
            return
    else:
        min_delay = 0.1
        max_delay = 0.5

    print(f"Scanning {ip}...")
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for port in ports:
            try:

                time.sleep(random.uniform(min_delay, max_delay))
                futures = executor.submit(scan_target, str(ip), port, show_closed_ports)
            except KeyboardInterrupt:
                print("\nScan interrupted by user. Exiting...")
                return

def main():

    try:
        print("NIX - Port Scanner")
        target_ip = input("Enter the target IP address: ")
        
    except KeyboardInterrupt:
        print("\nScan interrupted by user. Exiting...")
        return

    try:
        ipaddress.IPv4Address(target_ip)
    except ipaddress.AddressValueError:
        print("Invalid IP address. Exiting...")
        return
    
    print("Options for port range:")
    print("  - Enter a specific range like '1-1024'")
    print("  - Enter '-a' to scan all ports")
    print("  *-a* command takes considerable amount of time and resources ")
    print("  - Enter '-c' to scan common ports")
    print("  - Enter '-w' to scan web-server ports\n")

    try:
        ports_to_scan = input("Enter the range of ports to scan: ")

        if ports_to_scan.lower() == "-a":
            ports_to_scan = range(lower_port_limit, upper_port_limit + 1)
        elif ports_to_scan.lower() == "-c":
            ports_to_scan = common_ports
        elif ports_to_scan.lower() == "-w":
            ports_to_scan = webserver_ports
        else:
            try:
                start_port, end_port = map(int, ports_to_scan.split('-'))
                ports_to_scan = range(start_port, end_port + 1)
            except ValueError:
                print("Invalid port range. Exiting...")
                return
    except KeyboardInterrupt:
        print("\nScan interrupted by user. Exiting...")
        return
    
    try:
        timeout = float(input(f"Enter the timeout in seconds (default is {default_timeout}): ") or default_timeout)
        if timeout <= 0:
            print("Invalid input for timeout. Please enter a valid numeric value. Exiting...")
            return
        show_closed_ports = input("Do you want to show closed ports? (yes/no): ").lower() == "yes"

        scan(target_ip, ports_to_scan, show_closed_ports, timeout)
    except KeyboardInterrupt:
        print("\nScan interrupted by user. Exiting...")
        return

if __name__ == "__main__":
    main()

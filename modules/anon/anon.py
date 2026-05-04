import subprocess
import os
import random
import requests
import sys
from rich.console import Console

console = Console()

class GhostProtocol:
    def __init__(self, proxy_file="proxies.txt"):
        self.proxy_file = proxy_file
        self.proxies = []
        self._load_proxies()
        self.current_ip = self.get_my_ip()

    def get_my_ip(self):
        try:
            return requests.get("https://api.ipify.org", timeout=5).text
        except:
            return "UNKNOWN"

    def _load_proxies(self):
        """Handles both IP:PORT and IP:PORT:USER:PASS formats."""
        if os.path.exists(self.proxy_file):
            with open(self.proxy_file, "r") as f:
                for line in f:
                    parts = line.strip().split(":")
                    if len(parts) == 4: # Auth Proxy
                        ip, port, user, pw = parts
                        self.proxies.append(f"http://{user}:{pw}@{ip}:{port}")
                    elif len(parts) == 2: # Free/Simple Proxy
                        ip, port = parts
                        self.proxies.append(f"http://{ip}:{port}")

    def install_proton(self):
        """Executes the specific Debian installation path for ProtonVPN."""
        console.print("[bold yellow][*] ProtonVPN not found. Initiating Deployment...[/bold yellow]")
        deb_file = "protonvpn-stable-release_1.0.8_all.deb"
        checksum = "0b14e71586b22e498eb20926c48c7b434b751149b1f2af9902ef1cfe6b03e180"
        
        commands = [
            f"wget https://repo.protonvpn.com/debian/dists/stable/main/binary-all/{deb_file}",
            f"echo '{checksum} {deb_file}' | sha256sum --check -",
            f"sudo dpkg -i ./{deb_file}",
            "sudo apt update",
            "sudo apt install proton-vpn-gnome-desktop gnome-shell-extension-appindicator gnome-shell-extension-prefs proton-vpn-cli -y"
        ]
        
        for cmd in commands:
            console.print(f"[dim]Executing: {cmd}[/dim]")
            subprocess.run(cmd, shell=True, check=True)
        
        os.remove(deb_file)

    def check_tor(self):
        """Checks, Installs, Enables, and Activates Tor."""
        console.print("[bold cyan][*] Auditing Tor Service...[/bold cyan]")
        # Check if installed
        if subprocess.run("command -v tor", shell=True, capture_output=True).returncode != 0:
            console.print("[yellow][!] Tor missing. Installing...[/yellow]")
            subprocess.run("sudo apt update && sudo apt install tor -y", shell=True, check=True)

        # Ensure Enabled and Running
        subprocess.run("sudo systemctl enable tor", shell=True, capture_output=True)
        subprocess.run("sudo systemctl start tor", shell=True, capture_output=True)
        
        status = subprocess.run("systemctl is-active tor", shell=True, capture_output=True, text=True).stdout.strip()
        if status == "active":
            console.print("[bold green][+] Tor: ACTIVE & ENABLED[/bold green]")
            return True
        return False

    def connect_proton(self, country=None):
        """Connects to ProtonVPN. Defaults to fastest if no country specified."""
        if subprocess.run("command -v protonvpn", shell=True, capture_output=True).returncode != 0:
            self.install_proton()

        if country:
            console.print(f"[bold cyan][*] Routing Tunnel to: {country}[/bold cyan]")
            cmd = f"protonvpn connect --country {country}"
        else:
            console.print("[bold cyan][*] Routing Tunnel to Fastest Node...[/bold cyan]")
            cmd = "protonvpn connect"
            
        subprocess.run(cmd, shell=True, check=True)
        return self.check_proton_status()

    def check_proton_status(self):
        """Internal status check for logic flow."""
        res = subprocess.run("protonvpn status", shell=True, capture_output=True, text=True).stdout
        if "Status: Connected" in res:
            server = [line.strip() for line in res.split('\n') if "Server" in line]
            console.print(f"[bold green][+] ProtonVPN: {server[0] if server else 'CONNECTED'}[/bold green]")
            return True
        return False

    def get_verified_proxy(self):
        """Verification logic for rotated proxies."""
        if not self.proxies:
            return None
        console.print("[bold cyan][*] Rotating Shield Pool...[/bold cyan]")
        random.shuffle(self.proxies)
        for p in self.proxies[:10]:
            proxies = {"http": p, "https": p}
            try:
                r = requests.get("https://api.ipify.org", proxies=proxies, timeout=5)
                if r.status_code == 200 and r.text != self.current_ip:
                    console.print(f"[bold green][+] Proxy Verified: {r.text}[/bold green]")
                    return p
            except:
                console.print(f"[dim yellow][!] Proxy {p.split('@')[-1]} failed, cycling...[/dim yellow]")
        return None

    def setup_system_dns(self):
        """Verifies Quad9 lock."""
        res = subprocess.run("dig google.com", shell=True, capture_output=True, text=True).stdout
        if "9.9.9.9" in res:
            console.print("[bold green][+] DNS: HARDENED (Quad9)[/bold green]")
            return True
        console.print("[bold red][!] DNS LEAK DETECTED.[/bold red]")
        return False
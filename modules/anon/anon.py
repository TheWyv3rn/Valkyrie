import subprocess
import os
import random
from rich.console import Console

console = Console()

class GhostProtocol:
    def __init__(self, proxy_file="proxies.txt"):
        self.proxy_file = proxy_file
        self.proxies = []
        self._load_proxies()

    def _load_proxies(self):
        """Parses the ip:port:user:pass format into Python dicts."""
        if os.path.exists(self.proxy_file):
            with open(self.proxy_file, "r") as f:
                for line in f:
                    parts = line.strip().split(":")
                    if len(parts) == 4:
                        ip, port, user, pw = parts
                        proxy_url = f"http://{user}:{pw}@{ip}:{port}"
                        self.proxies.append(proxy_url)

    def get_random_proxy(self):
        return random.choice(self.proxies) if self.proxies else None

    def check_tor(self):
        """Checks if Tor is active; offers to install/fix if not."""
        console.print("[bold cyan][*] Auditing Tor Service...[/bold cyan]")
        status = subprocess.run("systemctl is-active tor", shell=True, capture_output=True, text=True).stdout.strip()
        
        if status != "active":
            console.print("[yellow][!] Tor is not active. Attempting to start/install...[/yellow]")
            subprocess.run("sudo apt update && sudo apt install tor -y", shell=True)
            subprocess.run("sudo systemctl enable --now tor", shell=True)
        else:
            console.print("[bold green][+] Tor: ONLINE[/bold green]")

    def check_proton(self):
        """Checks status of ProtonVPN CLI."""
        console.print("[bold cyan][*] Auditing ProtonVPN...[/bold cyan]")
        res = subprocess.run("protonvpn status", shell=True, capture_output=True, text=True).stdout
        if "Status: Connected" in res:
            console.print("[bold green][+] ProtonVPN: PROTECTED[/bold green]")
        else:
            console.print("[bold red][!] ProtonVPN: DISCONNECTED[/bold red]")
            # We won't auto-connect here to avoid leaking if they aren't signed in
            # but we can notify the user.

    def setup_system_dns(self):
        """Double check that the user didn't lose the Quad9 lock."""
        res = subprocess.run("dig google.com", shell=True, capture_output=True, text=True).stdout
        if "9.9.9.9" in res:
            console.print("[bold green][+] DNS: HARDENED (Quad9)[/bold green]")
        else:
            console.print("[bold yellow][!] DNS Warning: Quad9 not detected as primary.[/bold yellow]")

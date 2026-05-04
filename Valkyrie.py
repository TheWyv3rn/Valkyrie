import sys
from modules.anon.anon import GhostProtocol
from modules.recon.recon import Recon
from rich.console import Console

console = Console()

def main():
    if len(sys.argv) < 2:
        console.print("[bold red]Usage: python3 Valkyrie.py <target.com>[/bold red]")
        return

    target = sys.argv[1]
    
    # 1. Initialize Anonymity
    ghost = GhostProtocol()
    console.print("[bold magenta]=== VALKYRIE GHOST PROTOCOL INITIALIZING ===[/bold magenta]")
    ghost.check_tor()
    ghost.check_proton()
    ghost.setup_system_dns()

    # 2. Pick a proxy for this session
    session_proxy = ghost.get_random_proxy()
    if session_proxy:
        console.print(f"[bold cyan][*] Session Proxy Engaged: [white]{session_proxy.split('@')[1]}[/white][/bold cyan]")

    # 3. Hand over to Recon
    scanner = Recon(target, use_proxy=True)
    # Inject the specific proxy we picked
    if session_proxy:
        scanner.proxy_url = session_proxy

    scanner.run_sub_discovery()
    scanner.run_httpx()
    scanner.finalize_recon()

if __name__ == "__main__":
    main()

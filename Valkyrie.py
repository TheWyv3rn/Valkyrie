import sys
import argparse
import os
from modules.anon.anon import GhostProtocol
from modules.recon.recon import Recon
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.markup import escape

console = Console()

def print_banner():
    banner = r"""
____    ____      .__   __                  .__        
\   \ /   /____  |  | |  | _____.__._______|__| ____  
 \   Y   /\__  \ |  | |  |/ <   |  |\_  __ \  |/ __ \ 
  \     /  / __ \|  |_|    < \___  | |  | \/  \  ___/ 
   \___/  (____  /____/__|_ \/ ____| |__|  |__|\___  >
                \/          \/\/                    \/ 

[bold white]V A L H A L L A   S E C U R I T I T Y   L A B S[/bold white]
"""
    console.print(Align.center(Panel.fit(banner, border_style="bold cyan", padding=(0, 2))))

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="Valkyrie Recon Engine")
    parser.add_argument("-d", "--domain", help="Target domain")
    parser.add_argument("-a", "--all-anon", action="store_true", help="Enable All Anon")
    parser.add_argument("-p", "--proxy", action="store_true", help="Enable Proxies")
    parser.add_argument("-t", "--tor", action="store_true", help="Enable Tor")
    parser.add_argument("-v", "--vpn", action="store_true", help="Enable VPN")
    parser.add_argument("-vl", "--vpn-location", help="VPN Country Code")
    parser.add_argument("--recon-only", action="store_true", help="Skip Anon")

    args = parser.parse_args()

    if not args.domain:
        console.print("[bold red]ERROR:[/bold red] Domain required.")
        sys.exit(1)

    target = args.domain
    ghost = GhostProtocol()
    
    if not args.recon_only:
        console.print(Panel("[bold magenta]SHIELD INITIALIZATION[/bold magenta]", border_style="blue"))
        if args.all_anon or args.tor:
            if not ghost.check_tor(): sys.exit(1)
        if args.all_anon or args.vpn or args.vpn_location:
            if args.vpn_location or not ghost.check_proton_status():
                if not ghost.connect_proton(country=args.vpn_location): sys.exit(1)
        if args.all_anon:
            if not ghost.setup_system_dns(): sys.exit(1)

    use_proxy = False
    session_proxy = None
    if args.all_anon or args.proxy:
        session_proxy = ghost.get_verified_proxy()
        if session_proxy:
            use_proxy = True
            masked = session_proxy.split('@')[1] if '@' in session_proxy else session_proxy
            console.print(f"[bold cyan][*] SHIELD VERIFIED:[/bold cyan] {masked}")
        else:
            if not args.recon_only:
                choice = console.input("[yellow][!] Proxy dead. Proceed with VPN/Tor only? (y/n): [/yellow]")
                if choice.lower() != 'y': sys.exit(1)

    console.print(Panel(f"[bold green]ENGAGING TARGET: {target}[/bold green]", border_style="green"))
    
    scanner = Recon(target, use_proxy=use_proxy)
    if session_proxy: scanner.proxy_url = session_proxy

    try:
        # Full Phase Execution
        scanner.run_sub_discovery()
        scanner.run_httpx()
        scanner.finalize_recon()
        scanner.run_heavy_artillery() # Trigger the artillery
            
        console.print(Panel("[bold gold1]MISSION ACCOMPLISHED[/bold gold1]", border_style="yellow"))

    except Exception as e:
        console.print(Panel(f"[bold red]ERROR:[/bold red]\n{escape(str(e))}", border_style="red"))
        sys.exit(1)

if __name__ == "__main__":
    main()
import subprocess
import os
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class Recon:
    def __init__(self, target, use_proxy=False):
        self.target = target
        self.use_proxy = use_proxy
        self.proxy_url = "http://127.0.0.1:8080" # Example: Burp or Tor (127.0.0.1:9050)
        
        # File Manifest
        self.files = {
            "subfinder": f"{target}_subfinder.txt",
            "findomain": f"{target}_findomain.txt",
            "subs": f"{target}_subs.txt",
            "httpx": f"{target}_httpx.txt",
            "final": f"{target}_httpx_final.txt",
            "domains": f"{target}_confirmed_domains.txt"
        }

    def display_hud(self, task_name, status="EXECUTING"):
        panel = Panel(
            f"[bold cyan]TASK:[/bold cyan] [white]{task_name}[/white]\n"
            f"[bold cyan]STATUS:[/bold cyan] [bold green]{status}[/bold green]\n"
            f"[bold cyan]TARGET:[/bold cyan] [magenta]{self.target}[/magenta]",
            title="[bold red]VALKYRIE MK-1 HUD[/bold red]",
            border_style="blue"
        )
        console.print(panel)

    def run_command(self, cmd):
        # Inject Proxy if enabled
        env = os.environ.copy()
        if self.use_proxy:
            env["HTTP_PROXY"] = self.proxy_url
            env["HTTPS_PROXY"] = self.proxy_url
        
        subprocess.run(cmd, shell=True, check=True, env=env, capture_output=True)

    def run_sub_discovery(self):
        self.display_hud("SUBDOMAIN HARVESTING")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            progress.add_task(description="Querying Subfinder...", total=None)
            self.run_command(f"subfinder -d {self.target} -o {self.files['subfinder']}")
            
            progress.add_task(description="Querying Findomain...", total=None)
            self.run_command(f"findomain -t {self.target} -u {self.files['findomain']}")

        # Merge Logic
        all_subs = set()
        for key in ["subfinder", "findomain"]:
            if os.path.exists(self.files[key]):
                with open(self.files[key], "r") as f:
                    all_subs.update(f.read().splitlines())
                os.remove(self.files[key])

        with open(self.files["subs"], "w") as f:
            f.write("\n".join(sorted(all_subs)))
        
        console.print(f"[bold green]✔[/bold green] Collected {len(all_subs)} unique subdomains.")

    def run_httpx(self):
        self.display_hud("LIVE HOST ANALYSIS (HTTPX)")
        
        # The command for deep discovery
        cmd = f"httpx -l {self.files['subs']} -td -status-code -title -waf -o {self.files['httpx']}"
        
        with console.status("[bold neon_green]Probing technologies and WAFs..."):
            self.run_command(cmd)
        
        if os.path.exists(self.files["subs"]):
            os.remove(self.files["subs"])

    def finalize_recon(self):
        self.display_hud("RECON FINALIZATION", status="CLEANUP")
        
        table = Table(title=f"Results for {self.target}", show_header=True, header_style="bold magenta")
        table.add_column("URL", style="dim")
        table.add_column("Status", justify="right")
        table.add_column("Tech/Title")

        with open(self.files["httpx"], "r") as f, \
             open(self.files["final"], "w") as final, \
             open(self.files["domains"], "w") as domains:
            
            for line in f:
                parts = line.split()
                if not parts: continue
                
                url = parts[0]
                clean_domain = url.replace("http://", "").replace("https://", "").split(":")[0]
                
                final.write(line)
                domains.write(clean_domain + "\n")
                
                # Add to HUD Table
                table.add_row(url, "[green]SUCCESS[/green]", " ".join(parts[1:3]))
        
        console.print(table)
        os.remove(self.files["httpx"])
        console.print(f"[bold gold1]>> DATA SAVED TO {self.files['final']} AND {self.files['domains']}[/bold gold1]")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[red]Usage: python3 -m modules.recon.recon <target.com>[/red]")
        sys.exit(1)
    
    target_domain = sys.argv[1]
    scanner = Recon(target_domain, use_proxy=False) # Toggle proxy here
    scanner.run_sub_discovery()
    scanner.run_httpx()
    scanner.finalize_recon()

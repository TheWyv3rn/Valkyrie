import subprocess
import os
import sys
import re
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.markup import escape

console = Console()

class Recon:
    def __init__(self, target, use_proxy=False):
        self.target = target
        self.use_proxy = use_proxy
        self.proxy_url = "http://127.0.0.1:8080"
        
        self.files = {
            "subfinder": f"{target}_subfinder.txt",
            "findomain": f"{target}_findomain.txt",
            "subs": f"{target}_subs.txt",
            "httpx": f"{target}_httpx.txt",
            "final": f"{target}_httpx_final.txt",
            "domains": f"{target}_confirmed_domains.txt",
            "ips": f"{target}_confirmed_ips.txt",
            "urls": f"{target}_live_urls.txt",
            "naabu": f"{target}_naabu_ports.txt",
            "nmap": f"{target}_nmap_vuln.txt",
            "katana": f"{target}_katana_crawl.txt"
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
        env = os.environ.copy()
        home = os.path.expanduser("~")
        go_bin = os.path.join(home, "go", "bin")
        env["PATH"] = f"{env.get('PATH', '')}:{go_bin}:/usr/local/go/bin:/usr/sbin:/sbin"

        if self.use_proxy:
            env["HTTP_PROXY"] = self.proxy_url
            env["HTTPS_PROXY"] = self.proxy_url
            env["http_proxy"] = self.proxy_url
            env["https_proxy"] = self.proxy_url
        
        try:
            result = subprocess.run(cmd, shell=True, check=True, env=env, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            # Enhanced error reporting
            err_msg = e.stderr.strip() if e.stderr else e.stdout.strip()
            raise Exception(f"Error in {cmd.split()[0]}: {err_msg}")

    def run_sub_discovery(self):
        self.display_hud("SUBDOMAIN HARVESTING")
        with Progress(TextColumn("[bold blue]{task.description}"), BarColumn(bar_width=40, complete_style="cyan"), TimeElapsedColumn(), console=console) as progress:
            t1 = progress.add_task("Subfinder Scan", total=100)
            try:
                self.run_command(f"subfinder -d {self.target} -o {self.files['subfinder']}")
                progress.update(t1, completed=100)
            except Exception as e:
                console.print(f"[yellow][!] Subfinder fail: {escape(str(e))}[/yellow]")

            t2 = progress.add_task("Findomain Scan", total=100)
            try:
                self.run_command(f"findomain -t {self.target} -u {self.files['findomain']}")
                progress.update(t2, completed=100)
            except Exception as e:
                console.print(f"[yellow][!] Findomain fail: {escape(str(e))}[/yellow]")

        all_subs = set()
        for key in ["subfinder", "findomain"]:
            if os.path.exists(self.files[key]):
                with open(self.files[key], "r") as f:
                    all_subs.update(f.read().splitlines())
                os.remove(self.files[key])

        if not all_subs:
            raise Exception("Zero assets discovered in the void.")

        with open(self.files["subs"], "w") as f:
            f.write("\n".join(sorted(all_subs)))
        console.print(f"[bold green]✔[/bold green] Assets Discovered: {len(all_subs)}")

    def run_httpx(self):
        self.display_hud("LIVE HOST ANALYSIS")
        # Added -silent to keep output clean and -sc -ip for extraction
        cmd = f"httpx -l {self.files['subs']} -sc -ip -title -server -cdn -o {self.files['httpx']} -t 50 -timeout 15 -retries 2 -silent"
        
        with Progress(TextColumn("[bold neon_green]{task.description}"), BarColumn(bar_width=40, complete_style="green"), TimeElapsedColumn(), console=console) as progress:
            task = progress.add_task("HTTPX Probing...", total=None)
            self.run_command(cmd)
            progress.update(task, total=100, completed=100)
        
        if os.path.exists(self.files["subs"]):
            os.remove(self.files["subs"])

    def finalize_recon(self):
        self.display_hud("RECON FINALIZATION", status="EXTRACTION")
        
        # Regex to pull [1.2.3.4] from httpx output
        ip_pattern = re.compile(r"\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]")
        unique_ips = set()
        
        table = Table(title=f"LIVE ASSETS: {self.target}", show_header=True, header_style="bold magenta")
        table.add_column("URL", style="dim")
        table.add_column("IP Address", style="cyan")
        table.add_column("Details")

        if not os.path.exists(self.files["httpx"]):
            return

        with open(self.files["httpx"], "r") as f, \
             open(self.files["final"], "w") as final, \
             open(self.files["domains"], "w") as doms, \
             open(self.files["urls"], "w") as urls:
            
            for line in f:
                parts = line.split()
                if not parts: continue
                
                url = parts[0]
                ip_match = ip_pattern.search(line)
                ip_str = ip_match.group(1) if ip_match else "N/A"
                if ip_str != "N/A": unique_ips.add(ip_str)

                final.write(line)
                doms.write(url.split("://")[-1].split(":")[0] + "\n")
                urls.write(url + "\n")
                
                table.add_row(escape(url), ip_str, escape(" ".join(parts[1:3])[:30]))

        with open(self.files["ips"], "w") as f:
            f.write("\n".join(sorted(unique_ips)))

        console.print(table)
        os.remove(self.files["httpx"])
        console.print(f"[bold green]✔[/bold green] IPs Extracted: {len(unique_ips)}")

    def run_heavy_artillery(self):
        self.display_hud("DEEP ENUMERATION", status="ARTILLERY ENGAGED")
        
        with Progress(TextColumn("[bold red]{task.description}"), BarColumn(bar_width=40, complete_style="red"), TimeElapsedColumn(), console=console) as progress:
            
            # 1. Naabu: Use -s c (Connect Scan) for proxy compatibility and non-root
            if os.path.exists(self.files["domains"]):
                t1 = progress.add_task("Naabu Port Scan", total=100)
                # We use -tp top-100 for speed, change to -p 1-65535 for full
                naabu_cmd = f"naabu -l {self.files['domains']} -s c -p - -rate 1000 -passive -verify -o {self.files['naabu']} -silent"
                try:
                    self.run_command(naabu_cmd)
                    progress.update(t1, completed=100)
                except Exception as e:
                    progress.update(t1, description=f"Naabu [FAIL]", completed=100)
                    console.print(f"[dim red]Naabu Error: {escape(str(e))}[/dim red]")

            # 2. Nmap: Use -Pn to skip host discovery (often fails on proxies)
            if os.path.exists(self.files["ips"]):
                t2 = progress.add_task("Nmap Vuln Check", total=100)
                nmap_cmd = f"nmap -iL {self.files['ips']} -sV -Pn --script vuln -T4 -oN {self.files['nmap']}"
                try:
                    self.run_command(nmap_cmd)
                    progress.update(t2, completed=100)
                except Exception as e:
                    progress.update(t2, description=f"Nmap [FAIL]", completed=100)

            # 3. Katana
            if os.path.exists(self.files["urls"]):
                t3 = progress.add_task("Katana Crawl", total=100)
                katana_cmd = f"katana -list {self.files['urls']} -jc -d 2 -o {self.files['katana']} -silent"
                try:
                    self.run_command(katana_cmd)
                    progress.update(t3, completed=100)
                except Exception as e:
                    progress.update(t3, description=f"Katana [FAIL]", completed=100)

        console.print(Panel(f"[bold gold1]HEAVY ARTILLERY COMPLETE[/bold gold1]\nLog: {self.files['nmap']}", border_style="red"))
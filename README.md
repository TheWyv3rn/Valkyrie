# ⚔️ VALKYRIE v1.0 | Reconnaissance Engine
**Part of the Valhalla Security Labs Suite**

> "Choosing the slain on the digital battlefield."

Valkyrie is a high-speed, modular reconnaissance framework designed for bug bounty hunters and security auditors. It automates the transition from raw target discovery to actionable, confirmed infrastructure lists.

---

## ⚡ Core Capabilities
* **Multi-Source Harvesting**: Orchestrates `Subfinder` and `Findomain` for maximum coverage.
* **Intelligent Deduplication**: Merges and purges duplicate entries to ensure resource efficiency.
* **Tech-Stack Fingerprinting**: Leverages `HTTPX` to identify WAFs, CMS (WP/JS), and backend technologies.
* **Target Refinement**: Automates the cleanup of protocols and resolves live domains to confirmed IP assets.
* **Anonymity Ready**: Native support for proxy routing and hardened DNS configurations.

## 🛠 Project Architecture
```text
Valkyrie/
├── Valkyrie.py           # Master Orchestrator
├── modules/
│   └── recon/
│       └── recon.py      # The Heavy Lifter (Sub-discovery & Resolution)
└── logs/                 # Encrypted/Session Logs (Planned)  
proxies.txt               # Proxy Lists
```
  
## 🛠 Prerequisites & Installation  
  
Valkyrie requires a Linux environment (optimized for Debian) and the Go Programming Language.  
  
1. Install System Dependencies  
```
sudo apt update && sudo apt install -y python3-venv python3-pip nmap tor wget
```  
  
2. Install Go-Based Artillery  
Ensure your Go bin directory is in your `$PATH` (usually `~/go/bin`).  

```
# Core Discovery
go install -v [github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest](https://github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest)
go install -v [github.com/projectdiscovery/httpx/cmd/httpx@latest](https://github.com/projectdiscovery/httpx/cmd/httpx@latest)

# Port Scanning & Crawling
go install -v [github.com/projectdiscovery/naabu/v2/cmd/naabu@latest](https://github.com/projectdiscovery/naabu/v2/cmd/naabu@latest)
go install -v [github.com/projectdiscovery/katana/cmd/katana@latest](https://github.com/projectdiscovery/katana/cmd/katana@latest)

# Findomain (Rust)
wget [https://github.com/Findomain/Findomain/releases/latest/download/findomain-linux.zip](https://github.com/Findomain/Findomain/releases/latest/download/findomain-linux.zip)
unzip findomain-linux.zip && chmod +x findomain && mv findomain ~/go/bin/
```

3. Setup Valkyrie  
```
git clone [https://github.com/TheWyv3rn/Valkyrie.git](https://github.com/TheWyv3rn/Valkyrie.git)  
cd valkyrie  
python3 -m venv venv  
source venv/bin/activate  
pip install -r requirements.txt  
```  
  
## 🚀 Tactical Usage  
Valkyrie uses a flag-based system to control the "Ghost Protocol" (anonymity layers) and execution depth.  
  
**BASIC RECON** _Fast Discoveries_  
```
python3 Valkyrie.py -d target.com --recon-only
```
  
**Fully Cloaked Engagement** (`VPN` + `Tor` + `Proxy Rotation`)  
```
python3 Valkyrie.py -d target.com -a -vl JP
```  
  
**Flag Reference**  
|  FLAG  |  DESCRIPTION  |  
|  ---  |  ---  |  
|  `-d`  |  **Domain:** _The target asset (REQUIRED)_  |  
|  `-a`  |  **ALL Anon:** _Enables TOR, VPN, & PROXIES_  |  
|  `-v`  |  **VPN:** _Ensures ProtonVPN is active before scanning._ |  
|  `-vl`  |  **VPN Location:** _Specificy County (e.g., `-vl CA` for Canada)  |  
|  `-t`  |  **TOR:** _Routes tool traffic through the Tor Services.  |  
|  `-p`  |  **Proxy:** _Enalbes Verified rotation from `proxies.txt`.  |  
|  `--recon-only`  |  **HOT RUN:** _Skips all anonymous checks for local/internet testing_.  |  
  
## 📊 Output Manifest  
Valkyrie generates a structured intelligence folder for each target:  
* `target_subs.txt`: Every discovered unique subdomain.  
* `target_confirmed_ips.txt`: Resolved IPv4 addresses for the infrastructure.  
* `target_live_urls.txt`: Verified HTTP/HTTPS endpoints for crawling.  
* `target_nmap_vuln.txt`: Results from the Nmap Scripting Engine.  
* `target_katana_crawl.txt`: Deep-crawled parameters and JS files.  
  
# Made By:  
The `Valkyrie` tool is designed, developed, and deployed by;  
  
|  **NAME:**  |  **DESCRIPTION:**  |  **LINK:**  |  
|  ---  |  ---  |  ---  |  
| Brogan Cole Gallagher (**AKA** `TheWyv3rn`)  |  The Developer of Valkyrie  |  [Email](mailto:wyv3rn@valhallasecuritylabs.com)  |    
| Valhalla Security Labs  |  Senior Software Engineering meets Offensive Security.  |  [Website](https://valhallasecuritylabs.com)  |    


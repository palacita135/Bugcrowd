import os
import subprocess
import sys
import time
import shlex
import shutil
from datetime import datetime
from threading import Thread

def banner():
    print("""
 ██████████    ███             █████                █████████                   
░░███░░░░███  ░░░             ░░███                ███░░░░░███                  
 ░███   ░░███ ████  ████████  ███████   █████ ████░███    ░░░   ██████   ██████ 
 ░███    ░███░░███ ░░███░░███░░░███░   ░░███ ░███ ░░█████████  ███░░███ ███░░███
 ░███    ░███ ░███  ░███ ░░░   ░███     ░███ ░███  ░░░░░░░░███░███████ ░███ ░░░ 
 ░███    ███  ░███  ░███       ░███ ███ ░███ ░███  ███    ░███░███░░░  ░███  ███
 ██████████   █████ █████      ░░█████  ░░███████ ░░█████████ ░░██████ ░░██████ 
░░░░░░░░░░   ░░░░░ ░░░░░        ░░░░░    ░░░░░███  ░░░░░░░░░   ░░░░░░   ░░░░░░  
                                         ███ ░███                               
                                        ░░██████                                
                                         ░░░░░░                                 
                  Bug Hunting - DirtySec | v3.0 | Ultimate Recon Edition
    """)

def check_dependencies():
    tools = ["subfinder", "httprobe", "getallurls", "dnsx", "nmap"]
    for tool in tools:
        if not shutil.which(tool):
            print(f"[!] {tool} not found! Install it first.")
            sys.exit(1)

def get_target():
    return input("Enter the target domain (Do not include http/https): ").strip()

def create_target_folder(target):
    folder = f"results/{target}"
    os.makedirs(folder, exist_ok=True)
    return folder

def run_command(command, output_file, task_name):
    print(f"[+] Running: {task_name}")
    with open(output_file, "w") as f, open("error_log.txt", "a") as err:
        process = subprocess.run(command, shell=True, text=True, stdout=f, stderr=err)
        if process.returncode == 0:
            print(f"[✔] {task_name} Complete!")
        else:
            print(f"[!] Error in {task_name}. Check error_log.txt")
    return output_file

def recon(target, folder):
    print("[+] Running Recon...")
    tasks = {
        "Subdomains": f"subfinder -d {target}",
        "Live Hosts": f"cat {folder}/subdomains.txt | httprobe",
        "Wayback URLs": f"getallurls {target}",
        "DNS Enumeration": f"dnsx -d {target} -json -o {folder}/dns_records.json",
        "Port Scanning": f"nmap -p- {target} -oN {folder}/nmap_scan.txt"
    }
    files = {}
    threads = []
    
    for name, command in tasks.items():
        output_file = f"{folder}/{name.lower().replace(' ', '_')}.txt"
        thread = Thread(target=run_command, args=(command, output_file, name))
        threads.append(thread)
        thread.start()
        files[name] = output_file
    
    for thread in threads:
        thread.join()
    
    return files

def generate_report(target, folder, files):
    report_path = f"{folder}/summary_report.txt"
    with open(report_path, "w") as report:
        report.write(f"Bug Hunting Report for {target}\n")
        report.write(f"Generated on: {datetime.now()}\n\n")
        for name, file in files.items():
            report.write(f"## {name}\n")
            if os.path.exists(file):
                with open(file, "r") as f:
                    report.write(f.read())
            report.write("\n\n")
    print(f"[✔] REPORT SAVED: {report_path}")

def main():
    banner()
    check_dependencies()
    target = get_target()
    target_folder = create_target_folder(target)
    files = recon(target, target_folder)
    generate_report(target, target_folder, files)
    print("[✔] Recon Completed Successfully! Proceed with Manual Testing.")

if __name__ == "__main__":
    main()


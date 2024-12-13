import requests
import time
import os
import threading
from datetime import datetime
from colorama import init, Fore, Back, Style

init(autoreset=True)

def print_banner():
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════╗
║          BlockMesh Network AutoBot           ║
║     Github: https://github.com/IM-Hanzou     ║
║      Welcome and do with your own risk!      ║
╚══════════════════════════════════════════════╝
"""
    print(banner)

proxy_tokens = {}

print_banner()
print(f"{Fore.YELLOW}Please Login to your Blockmesh Account first.{Style.RESET_ALL}\n")
email_input = input(f"{Fore.LIGHTBLUE_EX}Enter Email: {Style.RESET_ALL}")
password_input = input(f"{Fore.LIGHTBLUE_EX}Enter Password: {Style.RESET_ALL}")

login_endpoint = "https://api.blockmesh.xyz/api/get_token"
report_endpoint = "https://app.blockmesh.xyz/api/report_uptime?email={email}&api_token={api_token}&ip={ip}"

login_headers = {
    "accept": "*/*",
    "content-type": "application/json",
    "origin": "https://app.blockmesh.xyz",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

report_headers = {
    "accept": "*/*",
    "content-type": "text/plain;charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

proxy_list_path = "proxies.txt"
proxies_list = []

if os.path.exists(proxy_list_path):
    with open(proxy_list_path, "r") as file:
        proxies_list = file.read().splitlines()
        print(f"{Fore.GREEN}[✓] Loaded {len(proxies_list)} proxies from proxies.txt")
else:
    print(f"{Fore.RED}[×] proxies.txt not found!")
    exit()

def format_proxy(proxy_string):
    proxy_type, address = proxy_string.split("://")
    
    if "@" in address:
        credentials, host_port = address.split("@")
        username, password = credentials.split(":")
        host, port = host_port.split(":")
        proxy_dict = {
            "http": f"{proxy_type}://{username}:{password}@{host}:{port}",
            "https": f"{proxy_type}://{username}:{password}@{host}:{port}"
        }
    else:
        host, port = address.split(":")
        proxy_dict = {
            "http": f"{proxy_type}://{host}:{port}",
            "https": f"{proxy_type}://{host}:{port}"
        }
        
    return proxy_dict, host

def authenticate(proxy):
    proxy_config, ip_address = format_proxy(proxy)
    
    if proxy in proxy_tokens:
        return proxy_tokens[proxy], ip_address
        
    login_data = {"email": email_input, "password": password_input}
    
    try:
        response = requests.post(login_endpoint, json=login_data, headers=login_headers, proxies=proxy_config)
        response.raise_for_status()
        auth_data = response.json()
        api_token = auth_data.get("api_token")
        
        proxy_tokens[proxy] = api_token
        
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.GREEN} Login successful {Fore.MAGENTA}|{Fore.LIGHTYELLOW_EX} {ip_address} {Style.RESET_ALL}")
        return api_token, ip_address
    except requests.RequestException as err:
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.RED} Login failed {Fore.MAGENTA}|{Fore.LIGHTYELLOW_EX} {ip_address}: {err}{Style.RESET_ALL}")
        return None, None

def send_uptime_report(api_token, ip_addr, proxy):
    proxy_config, _ = format_proxy(proxy)
    formatted_url = report_endpoint.format(email=email_input, api_token=api_token, ip=ip_addr)
    
    try:
        response = requests.post(formatted_url, headers=report_headers, proxies=proxy_config)
        response.raise_for_status()
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.LIGHTGREEN_EX} PING successfull {Fore.MAGENTA}|{Fore.LIGHTYELLOW_EX} {ip_addr} {Fore.MAGENTA}| {Fore.LIGHTWHITE_EX}{api_token} {Fore.MAGENTA}|{Fore.BLUE} Delay 5 minutes for next PING!{Style.RESET_ALL}")
    except requests.RequestException as err:
        if proxy in proxy_tokens:
            del proxy_tokens[proxy]
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.RED} Failed to PING {Fore.MAGENTA}|{Fore.LIGHTYELLOW_EX} {ip_addr}: {err}{Style.RESET_ALL}")

def process_proxy(proxy):
    first_run = True
    while True:
        if first_run or proxy not in proxy_tokens:
            api_token, ip_address = authenticate(proxy)
            first_run = False
        else:
            api_token = proxy_tokens[proxy]
            _, ip_address = format_proxy(proxy)
            
        if api_token:
            #print(f"{Fore.CYAN}[{datetime.now().strftime('%H:%M:%S')}] Delay 5 minutes before send PING | {ip_address}...")
            time.sleep(300)
            send_uptime_report(api_token, ip_address, proxy)
        time.sleep(2)

def main():
    print(f"\n{Style.BRIGHT}Starting ...")
    threads = []
    for proxy in proxies_list:
        thread = threading.Thread(target=process_proxy, args=(proxy,))
        thread.daemon = True
        threads.append(thread)
        thread.start()
        time.sleep(1)
    
    print(f"{Fore.CYAN}[✓] DONE! Delay 5 minutes before send PING for all proxies...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Stopping ...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {str(e)}")

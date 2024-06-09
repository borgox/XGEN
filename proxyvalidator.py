import requests
import concurrent.futures
import sys
import os
from pystyle import Colors, Colorate, Write
import ctypes
def change_title(title: str):
    """Change the console window title."""
    ctypes.windll.kernel32.SetConsoleTitleW(title)
def scrape_proxies():
    """Scrape free proxies from multiple sources and save them to proxies.txt."""
    sources = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies",
        "https://proxylist.geonode.com/api/proxy-list?protocols=http%2Chttps&limit=500&page=1&sort_by=lastChecked&sort_type=desc",
        "http://pubproxy.com/api/proxy?type=https&format=txt",
    ]

    fp = "proxies.txt"
    for url in sources:
        r = requests.get(url)
        if r.status_code == 200:
            with open(fp, "a", encoding="utf-8") as f:
                try:
                    content = r.content.decode()
                except:
                    content = r.content
                f.write(str(content))
            print(Colorate.Horizontal(Colors.green_to_yellow, "[!] Downloaded proxies."))
        else:
            print(Colorate.Horizontal(Colors.red_to_yellow, f"[!] Failed to download proxies. Status: {r.status_code}"))

def validate_proxy(proxy):
    """Validate a single proxy by attempting to connect to Google."""
    try:
        response = requests.get("http://www.google.com", proxies={"http": proxy, "https": proxy}, timeout=5)
        if response.status_code == 200:
            print(Colorate.Horizontal(Colors.green_to_yellow, f"[+] Valid {proxy}"))
            return True
    except requests.RequestException:
        pass
    print(Colorate.Horizontal(Colors.red_to_yellow, f"[!] Invalid {proxy}"))
    return False

def proxystart():
    """Load, validate, and save proxies from proxies.txt."""
    proxies_file = "proxies.txt"
    validated_proxies = []

    with open(proxies_file, "r", encoding="utf-8") as file:
        proxies = file.read().splitlines()

    print(Colorate.Horizontal(Colors.blue_to_red, f"Loaded {len(proxies)} proxies from {proxies_file}"))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(validate_proxy, proxies))

    validated_proxies = [proxy for proxy, result in zip(proxies, results) if result]

    print(Colorate.Horizontal(Colors.green_to_cyan, f"{len(validated_proxies)} Valid proxies"))
    print(Colorate.Horizontal(Colors.red_to_yellow, f"{(len(proxies) - len(validated_proxies))} Invalid proxies"))

    formatted_proxies = "\n".join(validated_proxies)
    with open(proxies_file, "w", encoding="utf-8") as file:
        file.write(formatted_proxies)
    main()

def main():
    """Main menu for scraping and validating proxies."""
    while True:
        change_title("Main Menu")
        print(Colorate.Diagonal(Colors.rainbow, """
    [1] Validate Proxies
    [2] Scrape Proxies
    [3] Exit
        """))
        choice = int(Write.Input("\n\nEnter option --> ", Colors.rainbow, interval=0.0025))

        if choice == 1:
            change_title("Validating Proxies")
            proxystart()
        elif choice == 2:
            change_title("Scraping Proxies")
            scrape_proxies()
        else:
            break
            sys.exit()

if __name__ == "__main__":
    main()

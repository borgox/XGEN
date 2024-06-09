import string
import random
import requests
import os
import time
import ctypes
import atexit
import signal
import datetime
import sys
import threading
from tqdm import tqdm
from pystyle import Colors, Colorate, Write

def times():
    """Return the current time as a string."""
    current_time = datetime.datetime.now()
    return f"{current_time.hour}:{current_time.minute}"

def sprint(prompt: str):
    """Print a message in red color."""
    print(Colors.red, prompt)

def exit_handler():
    """Handle program exit."""
    sprint(f"\n[{times()}] Exiting the program.{Colors.reset}")

def ctrl_c_handler(signum, frame):
    """Handle Ctrl+C signal."""
    sprint(f"Ctrl+C detected.")
    sys.exit(0)

# Register exit and signal handlers
atexit.register(exit_handler)
signal.signal(signal.SIGINT, ctrl_c_handler)

def change_title(title: str):
    """Change the console window title."""
    ctypes.windll.kernel32.SetConsoleTitleW(title)

class Generator:
    """Discord gift code generator and validator."""

    def __init__(self, amount: int = 100, proxies: bool = None):
        self.amount: int = amount
        self.baseurl: str = "https://discord.gift/"
        self.characters: str = string.ascii_letters + string.digits
        self.charamount = 16
        self.links = []
        self.valid_codes = []
        self.invalid_codes = []
        self.proxies = self.load_proxies() if proxies else None
        self.proxiest = proxies

    def change_title(self, title: str):
        """Change the console window title."""
        ctypes.windll.kernel32.SetConsoleTitleW(title)

    def load_proxies(self):
        """Load proxies from proxies.txt file."""
        try:
            with open("proxies.txt", "r") as file:
                proxies = file.read().splitlines()
            return proxies
        except FileNotFoundError:
            print(Colorate.Horizontal(Colors.red_to_yellow, "[-] Proxies file (proxies.txt) not found."))
            return []

    def validate_proxies(self):
        """Validate proxies by checking connectivity."""
        proxies = self.load_proxies()
        valid_proxies = []

        for proxy in proxies:
            try:
                requests.get("https://www.google.com", proxies={"http": proxy, "https": proxy}, timeout=5)
                valid_proxies.append(proxy)
            except (requests.RequestException, KeyboardInterrupt):
                print(Colorate.Horizontal(Colors.red_to_yellow, f"[-] Invalid proxy: {proxy}"))

        with open("proxies.txt", "w") as proxyfile:
            proxyfile.write("\n".join(valid_proxies))
        return valid_proxies

    def get_proxy(self):
        """Get a random proxy from the list."""
        return random.choice(self.proxies) if self.proxies else None

    def check_code(self, codex: str) -> bool:
        """Check if a generated Discord gift code is valid."""
        code = str(codex).split("/")[-1]
        url = f"https://discordapp.com/api/v6/entitlements/gift-codes/{code}?with_application=false&with_subscription_plan=true"

        try:
            proxy = self.get_proxy() if self.proxiest else None
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            response = requests.get(url, proxies=proxies)

            if response.status_code == 429:  # Rate limit
                retry_after = response.headers.get("Retry-After", 5)
                self.change_title(f"Rate Limit: {retry_after}")
                time.sleep(int(retry_after) + 1)
                return self.check_code(codex)

            return response.status_code == 200

        except (requests.RequestException, KeyboardInterrupt, AssertionError):
            return False

    def gen_code(self) -> str:
        """Generate a single Discord gift code."""
        chars = random.sample(self.characters, k=16)
        code = f"{self.baseurl}{''.join(chars)}"
        is_valid = self.check_code(code)

        if is_valid:
            with open("valid_codes.txt", "a") as file:
                file.write(f"{code}\n")
            self.valid_codes.append(code)
        else:
            self.invalid_codes.append(code)
        return code

    def generate_and_update_progress(self, pbar, pbar_lock):
        """Generate code and update progress bar."""
        self.gen_code()
        with pbar_lock:
            pbar.update(1)

    def gen_codes(self):
        """Generate multiple Discord gift codes."""
        start_time = time.time()
        try:
            pbar_lock = threading.Lock()
            threads = []
            with tqdm(total=self.amount, desc="Generating and checking codes", unit="code") as pbar:
                for _ in range(self.amount):
                    thread = threading.Thread(target=self.generate_and_update_progress, args=(pbar, pbar_lock))
                    thread.start()
                    threads.append(thread)

                for thread in threads:
                    thread.join()

        except KeyboardInterrupt:
            print(Colorate.Horizontal(Colors.red_to_yellow, "\n[!] Generation interrupted by user."))

        finally:
            end_time = time.time()
            elapsed_time = end_time - start_time
            time_unit = "seconds"
            if elapsed_time >= 60:
                elapsed_time /= 60
                time_unit = "minutes"
            if elapsed_time >= 60:
                elapsed_time /= 60
                time_unit = "hours"

            print(Colorate.Horizontal(Colors.purple_to_blue, f"\n[+] Generation finished in {elapsed_time:.2f} {time_unit}:\n"))
            print(Colorate.Horizontal(Colors.green_to_yellow, f"[+] Valid: {len(self.valid_codes)} {', '.join(self.valid_codes)}\n"))
            print(Colorate.Horizontal(Colors.red_to_yellow, f"[-] Invalid: {len(self.invalid_codes)}\n"))
            print(Colorate.Horizontal(Colors.purple_to_blue, f"[=] Total: {len(self.valid_codes) + len(self.invalid_codes)}"))
            input(Colorate.Horizontal(Colors.purple_to_blue, f"[=] Press ENTER to Continue: "))
            os.system("cls" if os.name == "nt" else "clear")

def main():
    """Main function to run the Discord gift code generator."""
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        change_title("XGEN - by borgo.xyz")
        ascii_art = """
    _  _______________   __
    | |/ / ____/ ____/ | / /
    |   / / __/ __/ /  |/ /                   [Made by borgo.xyz]  
    /   / /_/ / /___/ /|  /  
    /_/|_\\____/_____/_/ |_/   
    """
        print(Colorate.Horizontal(Colors.purple_to_blue, ascii_art))
        amount = Write.Input("\n\nEnter amount of codes to generate --> ", Colors.purple_to_blue, interval=0.0025)
        proxies = Write.Input("\n\n[1] Yes Proxies \n[2] No Proxies\n(program could be slow) ", Colors.purple_to_blue, interval=0.0025)
        use_proxies = True if proxies == "1" else False
        os.system("cls" if os.name == "nt" else "clear")

        generator = Generator(int(amount), use_proxies)
        generator.change_title("XGEN - by borgo.xyz")
        generator.gen_codes()

if __name__ == "__main__":
    main()

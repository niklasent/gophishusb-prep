import argparse
import ctypes
import platform
import os
import random
import requests
import shutil
import string
import subprocess
import sys
import time

GUSB_FLAG_PATH = os.path.join(os.path.dirname(__file__), "phish-files/nodata.gusb")
EXCEL_MACRO_PATH = os.path.join(os.path.dirname(__file__), "phish-files/invoice.xlsm")
EXECUTABLE_PATH = os.path.join(os.path.dirname(__file__), "phish-files/invoice.pdf.exe")
USB_LABEL = "USB-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def parse_args():
    parser = argparse.ArgumentParser(description="Gophish USB preparation tool")
    parser.add_argument("--drive", required=True, help="Drive (Linux/macOS: /dev/diskX, Windows: X:)")
    parser.add_argument("--apikey", required=True, help="Gophish USB API Key")
    parser.add_argument("--url", required=True, help="Gophish USB Admin URL")
    return parser.parse_args()

def run_command(command, shell=False):
    print(f"📄 Executing: {' '.join(command) if isinstance(command, list) else command}")
    result = subprocess.run(command, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr.strip()}")
        sys.exit(1)
    return result.stdout.strip()

def format_usb_windows(drive_letter):
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        sys.exit("❌ This script must be run as Administrator.")
    cmd = f'format {drive_letter} /FS:FAT32 /Q /Y /V:{USB_LABEL}'
    run_command(cmd, shell=True)

def format_usb_linux(device):
    if os.geteuid() != 0:
        sys.exit("❌ This script must be run as root.")
    run_command(["umount", device], shell=False)
    run_command(["mkfs.vfat", "-F", "32", "-n", USB_LABEL, device])

def format_usb_macos(device):
    run_command(["diskutil", "unmountDisk", device])
    run_command(["diskutil", "eraseDisk", "FAT32", USB_LABEL, "MBRFormat", device])

def mount_device_linux(device):
    mount_point = f"/mnt/{USB_LABEL}"
    os.makedirs(mount_point, exist_ok=True)
    run_command(["mount", device, mount_point])
    return mount_point

def mount_device_macos():
    return f"/Volumes/{USB_LABEL}"

def copy_files(dest_path):
    for file in [GUSB_FLAG_PATH, EXCEL_MACRO_PATH, EXECUTABLE_PATH]:
        if os.path.isfile(file):
            print(f"📁 Copy {file} to {dest_path}")
            shutil.copy(file, dest_path)
        else:
            print(f"⚠️ File not found: {file}")

def send_post_request(url, api_key, label):
    url = url + "/api/usbs/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": label
    }
    print(f"🌐 Registering USB device to {url}:")
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"🔁 Response: {response.status_code} - {response.text}")
        if not response.ok:
            sys.exit("❌ Error in USB registration.")
    except requests.RequestException as e:
        sys.exit(f"❌ Network error: {e}")


def main():
    args = parse_args()
    drive = args.drive
    api_key = args.apikey
    url = args.url

    os_type = platform.system()
    print(f"🖥️ Detected OS: {os_type}")

    confirm = input(f"⚠️ Drive {drive} will be formatted! Continue? (y/n): ")
    if confirm.lower() != "y":
        print("❌ Aborted.")
        sys.exit(0)

    if os_type == "Windows":
        format_usb_windows(drive)
        time.sleep(5)
        copy_files(drive)

    elif os_type == "Linux":
        format_usb_linux(drive)
        time.sleep(2)
        mount_point = mount_device_linux(drive)
        copy_files(mount_point)
        run_command(["umount", mount_point])

    elif os_type == "Darwin":  # macOS
        format_usb_macos(drive)
        time.sleep(5)
        mount_point = mount_device_macos()
        copy_files(mount_point)

    else:
        print(f"❌ Unsupported OS: {os_type}")
        sys.exit(1)

    send_post_request(url, api_key, USB_LABEL)

    print("✅ Done. Happy phishing!")

if __name__ == "__main__":
    main()

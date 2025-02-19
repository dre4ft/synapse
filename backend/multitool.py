import socket
import os

def can_route():
    try:
        # Attempt to connect to a well-known public DNS server (Google's DNS)
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

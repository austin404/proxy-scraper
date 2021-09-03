import socket


def check_connection(host: str, port: int, timeout: int = 20) -> bool:
    """Function to check if the proxy responds in given timeout

    Args:
        host (str): IP
        port (int): Port
        timeout (int, optional): timeout. Defaults to 20.

    Returns:
        bool: Returns True if connects in given time or False
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(timeout)
        s.connect((host, port))
        print(f"[+] {host}:{port} Connected")
        s.close()
        return True
    except ConnectionError:
        print(f"[-] Failed to connect to {host}:{port}")
    except TimeoutError:
        print(f"[-] Timeout while connecting to {host}:{port} {timeout=}")
    except Exception as e:
        print(f"[-] {e} {host}:{port}")
    s.close()

    return False

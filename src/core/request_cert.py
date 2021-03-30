import sys
import traceback
from typing import Dict
# from urllib.request import Request, urlopen , ssl, socket
import ssl
import socket
# from urllib.error import URLError, HTTPError
import json
import logging


def get_cert(base_url: str, port: str) -> Dict[str, str]:
    """
    :param base_url: e.g. sub.example.com
    :param port: e.g. 3141
    :return: bool if cert received
    """
    hostname = base_url
    context = ssl.create_default_context()

    print(hostname, port)

    try:
        with socket.create_connection((hostname, int(port)), timeout=2.0) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                ssock.setblocking(False)
                data = json.dumps(ssock.getpeercert())
                # print(ssock.getpeercert())

    except socket.gaierror as e:
        exception = sys.exc_info()[1]
        print(exception)
        logging.error(f"Got a SOCKET GAI ERROR during cert request for {base_url}:{port}:\n{traceback.format_exc()}")
        print(f"faulty domain input")
        return {}

    except ssl.SSLCertVerificationError as e:
        exception = sys.exc_info()[1]
        print(exception)
        logging.error(f"Got a SSL VERIFICATION error during cert request for {base_url}:{port}:\n{traceback.format_exc()}")
        print("cert verification failed")
        return {}

    except socket.timeout as e:
        exception = sys.exc_info()[1]
        print(exception)
        logging.error(f"Got a TIMEOUT during cert request for {base_url}:{port}:\n{traceback.format_exc()}")
        print("request timed out")
        return {}

    dc = json.loads(data)

    return dc


if __name__ == '__main__':
    # some site without http/https in the path
    base_url = 'christoph-geron.de'
    port = '443'
    get_cert(base_url, port)
    ts = "hi {}".format(2)
    print(ts)

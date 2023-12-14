# 2.6  client server October 2021
import os
from PIL import Image
from typing import List, Tuple
from alive_progress import alive_bar
import pickle
import base64
import socket
import sys
import traceback
from tcp_by_size import recv_by_size, send_with_size
from client_custom_exceptions import DisconnectErr, DisconnectRequest
import zlib

# from __ import * ruins LSP.
from client_handlers import *

import logging

logging.basicConfig(format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.propagate = True


def menu() -> Tuple[str, List[str], List[str]]:
    """
    show client menu and retrive the params they provided, both that need to go to server and to the client
    return: string with selection, arguments for the server and for the client both string arrays
    """
    options = [
        "ask for time",
        "ask for random",
        "ask for name",
        "notify exit",
        "request DIR",
        "execute a program",
        "copy a file on the remote pc",
        "delete a file",
        "screen shot",
        "fetch a file",
        # "Sign up for the chating service",
        # "Sign in to the chating service",
        # "Get unread messages",
        # "Send a message",
        "copy(with commpression per chunk) a file",
    ]

    for index, option in enumerate(options, start=1):
        print(f"\n  {index}. {option}")

    server_args = []
    client_args = []
    request = input(f"Input 1 - {len(options)} > ")

    count_args = {
        "5": [
            [
                1,
                [
                    "Any Sub directory? (. for current, ../ OR ./ works. may also specify dir name like: .git )"
                ],
            ],
            [0, []],
        ],
        "6": [[1, ["Program name / path to the .exe "]], [0, []]],
        "7": [[2, ["File to copy", "New file name to copy to"]], [0, []]],
        "8": [[1, ["File name to delete"]], [0, []]],
        "10": [[1, ["Remote file name"]], [1, ["local file name"]]],
        # "11": [[2, ["Username? ", " Password?"]], [0, []]],
        # "12": [[2, ["Username? ", " Password?"]], [0, []]],
        "11": [[1, ["Remote file name"]], [1, ["local file name"]]],
    }
    row = count_args.get(request, [[0, [""]], [0, [""]]])

    for i, req_row in enumerate(row):
        for j in range(req_row[0]):
            (server_args if i == 0 else client_args).append(input(req_row[1][j] + " "))
    return request, server_args, client_args


def main(ip: str) -> None:
    """
    main client - handle socket and main loop
    """
    connected = False
    global sock
    sock = socket.socket()
    port = 7777
    try:
        sock.connect((ip, port))
        print(f"Connect succeeded {ip}:{port}")
        connected = True
    except Exception:
        print(f"Error while trying to connect.  Check ip or port -- {ip}:{port}")

    while connected:
        from_user = menu()
        client_args = from_user[-1]
        to_send = protocol_build_request(from_user[:2])
        if to_send == "":
            print("Selection error try again")
            continue
        try:
            handle_msg(sock, to_send, client_args)
        except DisconnectRequest as e:
            break
        except socket.error as err:
            if err.errno == 10053:  # win err 10053: connection was aborted
                print("The server is now closed so cant connect to it")
            else:
                print(f"Got socket error: {err}")

            break
        except Exception as err:
            print(f"General error: {err}")
            print(traceback.format_exc())
            break

    print("Bye")
    sock.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main("127.0.0.1")

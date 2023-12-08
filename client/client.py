# 2.6  client server October 2021
from typing import List, Tuple
from alive_progress import alive_bar
import pickle
import base64
import socket
import sys
import traceback
from tcp_by_size import recv_by_size, send_with_size
from client_custom_exceptions import DisconnectErr, DisconnectRequest

# from __ import * ruins LSP.
from client_handlers import (
    handle_dir,
    handle_exec,
    handle_recived_chunk,
)
import logging

logging.basicConfig(format="%(asctime)s - %(message)s",
                    datefmt="%d-%b-%y %H:%M:%S")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.propagate = True
SCREEN_SHOT_OUTPUT_DIR = "SCREEN_SHOTS_OUTS"
FILE_MENU_LOCATION = "10"
GET_CHUNK_CONST = "1001"
USER_MENU_TO_CODE_DICT = {
    "1": "TIME",
    "2": "RAND",
    "3": "WHOU",
    "4": "EXIT",
    "5": "DIRR",
    "6": "EXEC",
    "7": "COPY",
    "8": "DELL",
    "9": "SCRS",
    FILE_MENU_LOCATION: "FILE",
    GET_CHUNK_CONST: "CHUK",
    "11": "REGI",
    "12": "LOGI"
}


def handle_file(fields, client_args):
    code, chunk_amount, file_name = fields
    with alive_bar(int(chunk_amount), bar="blocks", spinner="wait") as bar:
        for i in range(int(chunk_amount)):
            # print(f"Chunk: {i}")
            handle_msg(("CHUK~" + file_name).encode(), client_args)
            bar()
        # print("Finished writing the chunk")
    handle_msg("CLOS~" + file_name, [file_name])
    return ""


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
        "Sign up for the chating service",
        "Sign in to the chating service"
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
        "11": [[2, ["Username? ", " Password?"]], [0, []]],
        "12": [[2, ["Username? ", " Password?"]], [0, []]],

    }
    row = count_args.get(request, [[0, [""]], [0, [""]]])

    for i, req_row in enumerate(row):
        for j in range(req_row[0]):
            (server_args if i == 0 else client_args).append(
                input(req_row[1][j] + " "))
    return request, server_args, client_args


def protocol_build_request(from_user):
    """
    build the request according to user selection and protocol
    return: string - msg code
    """
    ret_str = (
        USER_MENU_TO_CODE_DICT.get(from_user[0], "")
        + ("~" if len(from_user[1]) > 0 else "")
        + "~".join(from_user[1])
    )
    return ret_str


def handle_screenshot(fileds, client_args):
    handle_msg(
        protocol_build_request(
            [FILE_MENU_LOCATION, [f"./{SCREEN_SHOT_OUTPUT_DIR}" + fileds[-1]]]),
        [input(" What name to give the screenshot? ")],
    )
    return f"Server took a screenshot named {fileds[-1]} sucsessfuly"


def handle_register_response(fields, client_args):

    return f"Register Request returned fields: {fields} "
    pass


def handle_signin_response(fields, client_args):
    return f"Signin Request returned fields: {fields}"
    pass


def protocol_parse_reply(reply, client_args):
    """
    parse the server reply and prepare it to user
    return: answer from server string
    """
    to_show = "Invalid reply from server"
    try:
        reply = reply.decode()
        fields = []
        if "~" in reply:
            fields = reply.split("~")

        code = reply[:4]
        if code == "EXTR":
            raise DisconnectRequest("disconnect request")
        special_handlers = {
            "DIRR": handle_dir,
            "SCTR": handle_screenshot,
            "EXER": handle_exec,
            "FILR": handle_file,
            "CHUR": handle_recived_chunk,
            "REGR": handle_register_response,
            "SIGR": handle_signin_response
        }
        if code in special_handlers.keys():
            return special_handlers[code](fields, client_args)

        to_show_dict = {
            "TIMR": "The Server time is: ",
            "RNDR": "Server draw the number: ",
            "WHOR": "Server name is: ",
            "ERRR": "Server returned an error: ",
            "EXTR": "Server Acknowleged the exit message ",
            "EXER": "Server Execution returrned: ",
            "SCTE": "Server screen shot err:",
            "COPR": " Server copied good",
            "OKAY": "",
        }

        to_show = to_show_dict.get(code, "Server sent an unknown code")
        for filed in fields[1:]:
            to_show += filed
    except DisconnectRequest as e:
        raise e
    except Exception as e:
        print("Error when parsing the reply")
        raise e
    return to_show


def handle_reply(reply, client_args):
    """
    get the tcp upcoming message and show reply information
    return: void
    """
    to_show = protocol_parse_reply(reply, client_args)

    if to_show != "":
        print("\n==========================================================")
        print(f"  SERVER Reply: {to_show}   |")
        print("==========================================================")


def handle_msg(to_send, client_args):
    global sock
    # send_with_size(sock,to_send,"",True)
    send_with_size(sock, to_send)
    byte_data = recv_by_size(sock, "", False)
    if byte_data == b"":
        print("Seems server disconnected abnormal")
        raise DisconnectRequest("Server dissconnected ")

    handle_reply(byte_data, client_args)


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
        print(
            f"Error while trying to connect.  Check ip or port -- {ip}:{port}")

    while connected:
        from_user = menu()
        client_args = from_user[-1]
        to_send = protocol_build_request(from_user[:2])
        if to_send == "":
            print("Selection error try again")
            continue
        try:
            handle_msg(to_send, client_args)
        except DisconnectRequest as e:
            # need to find a cleaner way to do this
            break
        except socket.error as err:
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

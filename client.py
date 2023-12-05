# 2.6  client server October 2021
import pickle
import base64
import socket
import sys
import traceback
from tcp_by_size import recv_by_size, send_with_size

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
    "10": "FILE",
    GET_CHUNK_CONST: "CHUK",
}


def logtcp(dir, byte_data):
    """
    log direction and all TCP byte array data
    return: void
    """
    if dir == "sent":
        print(f"C LOG:Sent     >>>{byte_data}")
    else:
        print(f"C LOG:Recieved <<<{byte_data}")


def send_data(sock, bdata):
    """
    send to client byte array data
    will add 8 bytes message length as first field
    e.g. from 'abcd' will send  b'00000004~abcd'
    return: void
    """
    # bytearray_data = str(len(bdata)).zfill(8).encode() + b'~' + bdata
    # sock.send(bytearray_data)
    send_with_size(sock, bdata)
    logtcp("sent", bdata)


def menu():
    """
    show client menu
    return: string with selection
    """
    print("\n  1. ask for time")
    print("\n  2. ask for random")
    print("\n  3. ask for name")
    print("\n  4. notify exit")
    print("\n  5. request DIR")
    print("\n  6. execute a program")
    print("\n  7. copy a file on the remote pc")
    print("\n  8. delete a file")
    print("\n  9. screen shot")
    print("\n  10. fetch a file")
    # print('\n  (5. some invalid data for testing)')
    args = []
    request = input("Input 1 - 4 > ")
    count_args = {"5": 1, "6": 1, "7": 2, "8": 1, "10": 1}
    for i in range(count_args.get(request, 0)):
        args.append(input("Insert Another paramater"))
    return request, args


def protocol_build_request(from_user):
    """
    build the request according to user selection and protocol
    return: string - msg code
    """
    # if from_user == '1':
    #     return 'TIME'
    # elif from_user == '2':
    #     return 'RAND'
    # elif from_user == '3':
    #     return 'WHOU'
    # elif from_user == '4':
    #     return 'EXIT'
    # #elif from_user == '5':
    # #    return input("enter free text data to send> ")
    # else:
    #     return ''
    #
    # from users is a tuple
    # index 0 is the CODE
    # index 1 is args
    print("The Args: ")
    print(from_user[1])
    ret_str = (
        USER_MENU_TO_CODE_DICT.get(from_user[0], "")
        + ("~" if len(from_user[1]) > 0 else "")
        + "~".join(from_user[1])
    )
    print(ret_str)
    return ret_str


def decode_from_pickle_and_from_base64(base):
    try:
        # Decode Base64 to get pickled data
        bytearr = base64.b64decode(base)
        # Deserialize the pickled data
        data = pickle.loads(bytearr)
        return data
    except Exception as e:
        print(f"Error2: {e}")
        return None


def handle_dir(fileds):
    all = fileds[1]  # 0 is the code
    decoded = decode_from_pickle_and_from_base64(all)
    return "Dirs: " + str(decoded)


def handle_screenshot(fileds):
    return f"Server took a screenshot named {fileds[-1]} sucsessfuly"


def handle_exec(fileds):
    code, ret_code, stdin, sterr = fileds
    return f"""return code: {ret_code} \n 
                stdout: {stdin} \n 
                stderr: {sterr}
"""


def get_file(file_name):
    print(f"Fetching: {file_name = } from the server")


def handle_file(fields):
    print("Handle File Paramas")
    print(fields)
    code, chunk_amount, file_name = fields
    for i in range(int(chunk_amount)):
        print(f"Chunk: {i}")
        handle_msg(("CHUK~" + file_name).encode())
        print("Finished writing the chunk")
    handle_msg("CLOS~" + file_name)
    return (
        "Server Says it will take: "
        + chunk_amount
        + " Chunks "
        + " To Fetch "
        + file_name
    )


def handle_recived_chunk(fields):
    print("Chur params: ")
    print(fields)
    code, remote_file_name, b64content = fields
    decoded_to_bin = base64.b64decode(b64content)
    out_filename = input("Enter the filename to save here ")
    with open(out_filename, "ab+") as f:
        f.write(decoded_to_bin)
    return ""


def protocol_parse_reply(reply):
    """
    parse the server reply and prepare it to user
    return: answer from server string
    """
    print("Full response from server: ")
    print(reply)
    to_show = "Invalid reply from server"
    try:
        reply = reply.decode()
        fields = []
        if "~" in reply:
            fields = reply.split("~")

        code = reply[:4]
        print("The Server send the code: " + code)
        if code == "EXTR":
            raise DisconnectRequest("dissconnect request")
        special_handlers = {
            "DIRR": handle_dir,
            "SCTR": handle_screenshot,
            "EXER": handle_exec,
            "FILR": handle_file,
            "CHUR": handle_recived_chunk,
        }
        if code in special_handlers.keys():
            return special_handlers[code](fields)
        to_show_dict = {
            "TIMR": "The Server time is: ",
            "RNDR": "Server draw the number: ",
            "WHOR": "Server name is: ",
            "ERRR": "Server returned an error: ",
            "EXTR": "Server Acknowleged the exit message ",
            "EXER": "Server Execution returrned: ",
            "SCTE": "Server screen shot err:",
            "COPR": " Server copied good",
            "OKAY": ""  # file handle closed alright left empty to not print
            # "FILR": "Server Says it will take  this much chunks: "
        }

        to_show = to_show_dict.get(code, "Server sent an unknown code")
        for filed in fields[1:]:
            to_show += filed
    except DisconnectRequest as e:
        raise e
    except Exception as e:
        # print('Server replay bad format')
        print("Error")
        raise e
    return to_show


def handle_reply(reply):
    """
    get the tcp upcoming message and show reply information
    return: void
    """
    to_show = protocol_parse_reply(reply)
    # if to_show:
    #     raise DisconnectRequest("Requested Dissconnect")
    if to_show != "":
        print("\n==========================================================")
        print(f"  SERVER Reply: {to_show}   |")
        print("==========================================================")


class DisconnectRequest(Exception):
    pass


class DisconnectErr(Exception):
    pass


connected = True  # gross solution dont have time to rewrite, future me problem


def handle_msg(to_send):
    global sock
    send_data(sock, to_send)  # .encode())
    # todo improve it to recv by message size
    byte_data = recv_by_size(sock)
    if byte_data == b"":
        print("Seems server disconnected abnormal")
        raise DisconnectRequest("Server dissconnected ")
    logtcp("recv", byte_data)
    # byte_data = byte_data[9:]  # remove length field
    handle_reply(byte_data)


def main(ip):
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
        to_send = protocol_build_request(from_user)
        if to_send == "":
            print("Selection error try again")
            continue
        try:
            handle_msg(to_send)
        except DisconnectRequest as e:
            print("Dissconnecting, i realy need to find a better way to handle")
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

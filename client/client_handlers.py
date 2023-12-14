import base64
import pickle
import zlib
from tcp_by_size import send_with_size, recv_by_size
from client_custom_exceptions import DisconnectRequest
from PIL import Image
from alive_progress import alive_bar

SCREEN_SHOT_OUTPUT_DIR = "srcshot"
FILE_MENU_LOCATION = "10"
ZIPED_FILE_MENU_LOCATION = "11"
GET_CHUNK_CONST = "1001"
GET_ZIPED_CHUNK_CONST = "10001"
TAKE_SCREENSHOT = "9"
USER_MENU_TO_CODE_DICT = {
    "1": "TIME",
    "2": "RAND",
    "3": "WHOU",
    "4": "EXIT",
    "5": "DIRR",
    "6": "EXEC",
    "7": "COPY",
    "8": "DELL",
    TAKE_SCREENSHOT: "SCRS",
    FILE_MENU_LOCATION: "FILE",
    GET_CHUNK_CONST: "CHUK",
    # "11": "REGI",
    # "12": "LOGI",
    # "13": "GETM",
    # "14": "ADDM",
    "11": "ZFIL",
    GET_ZIPED_CHUNK_CONST: "ZHUK",
}


def decode_from_pickle_and_from_base64(base):
    try:
        # Decode Base64 to get pickled data
        bytearr = base64.b64decode(base)
        # Deserialize the pickled data
        data = pickle.loads(bytearr)
        return data
    except Exception:
        return None


def handle_file(fields, client_args):
    code, chunk_amount, file_name = fields
    with alive_bar(int(chunk_amount), bar="blocks", spinner="wait") as bar:
        for i in range(int(chunk_amount)):
            # print(f"Chunk: {i}")

            # req_str = ("CHUK~" + file_name).encode()
            req_str = join_code_params("CHUK", file_name)  # protocol_build_request()
            handle_msg(to_send=req_str, client_args=client_args)
            bar()
        # print("Finished writing the chunk")
    close_str = join_code_params("CLOS", file_name)
    handle_msg(to_send=close_str, client_args=[file_name])
    return ""


def decompress_file(input_file, output_file):
    try:
        with open(input_file, "rb") as f_in:
            compressed_data = f_in.read()
            decompressed_data = zlib.decompress(compressed_data)
        with open(output_file, "wb") as f_out:
            f_out.write(decompressed_data)
    except Exception as e:
        print("Failed to decomp")


def handle_recived_zipped_file(fields, client_args):
    code, chunk_amount, compress_file_name = fields
    output_filename = client_args[0]
    client_args[0] = client_args[0] + ".gz"
    send_str = join_code_params("FILE", compress_file_name)
    handle_msg(to_send=send_str, client_args=client_args)
    # handle_file([code, chunk_amount, compress_file_name], client_args)
    print("Now Decomping")
    # print("Finished writing the chunk")
    decompress_file(client_args[0], output_filename)
    # os.remove(compress_file_name)
    return ""


def get_tree_structure(file_structure):
    directory_structure = {}

    for item in file_structure:
        parts = item.split("\\")
        current_dict = directory_structure

        for part in parts[:-1]:
            # The setdefault() method returns the value of the item with
            # the specified key.
            # If the key does not exist, insert the key, with the specified
            # value, see example below
            current_dict = current_dict.setdefault(part, {})

        current_dict[parts[-1]] = None

    def build_directory_structure(structure, indent=0):
        result = ""
        for key, value in structure.items():
            if value is None:
                result += "\t" * indent + key + "\n"
            else:
                result += "\t" * indent + key + ":\n"
                result += build_directory_structure(value, indent + 1)
        return result

    return build_directory_structure(directory_structure)


def handle_dir(fileds, client_args):
    all = fileds[1]  # 0 is the code
    decoded = decode_from_pickle_and_from_base64(all)
    return "\n Dirs: " + get_tree_structure(decoded)


def handle_exec(fileds, client_args):
    code, ret_code, stdin, sterr = fileds
    return f"""return code: {ret_code} \n
                stdout: {stdin} \n
                stderr: {sterr}
            """


def handle_recived_chunk(fields, client_args):
    # print("writing to: ")
    # print(client_args)
    code, remote_file_name, b64content = fields
    decoded_to_bin = base64.b64decode(b64content)
    # out_filename = input("enter the filename to save here ")
    with open(client_args[0], "ab+") as f:
        f.write(decoded_to_bin)
    return ""


def get_sock(sock):
    global sock_save
    if sock == None:
        # sock = sock_save
        return sock_save
    else:
        sock_save = sock
        return sock


def handle_msg(sock=None, to_send="", client_args=[]):
    # send_with_size(sock,to_send,"",True)
    soc = get_sock(
        sock
    )  # first time, its called from main. it is provided a socket and will save it
    # second time or when called from handlers it will returned the saved socket

    send_with_size(soc, to_send)
    byte_data = recv_by_size(soc, "", False)
    if byte_data == b"":
        print("Seems server disconnected abnormal")
        raise DisconnectRequest("Server dissconnected ")

    handle_reply(byte_data, client_args)


def handle_reply(reply, client_args):
    """
    get the tcp upcoming message and show reply information
    return: void
    """
    to_show = protocol_parse_reply(reply, client_args)

    if to_show != "":
        print("\n==========================================================")
        print(f"\t {to_show} \t")
        print("==========================================================")


def handle_screenshot(fields, client_args):
    out_name = input("What name to give the screenshot? ")
    remote_filename = f"./{SCREEN_SHOT_OUTPUT_DIR}/" + fields[-1]
    send_str = join_code_params(
        USER_MENU_TO_CODE_DICT[FILE_MENU_LOCATION], remote_filename
    )
    handle_msg(to_send=send_str, client_args=[out_name])
    img = Image.open(out_name)
    img.show()
    return ""  # f"Server took a screenshot named {fields[-1]} successfully"


#
# def handle_get_unread(fields, client_args):
#     print("Unread Messages: ")
#     print(fields)
#     pass
from client_custom_exceptions import DisconnectRequest
from client_handlers import *


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
            "ZFIR": handle_recived_zipped_file,
            # "REGR": handle_register_response,
            # "SIGR": handle_signin_response,
            # "GETM": handle_get_unread,
            # "ADDM": handle_add_message,
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
            "COPR": " Server Copy result: ",
            "OKAY": "",
            "DELR": "Server delete result: ",
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


def protocol_build_request(from_user):
    """
    build the request according to user selection and protocol
    return: string - msg code
    """
    print("From User: ")
    print(from_user)
    ret_str = join_code_params(
        USER_MENU_TO_CODE_DICT.get(from_user[0], ""), *from_user[1]
    )
    print("Ret Str: ")
    print(ret_str)
    return ret_str


def join_code_params(code, *params):
    built_str = code

    if params:
        # Add ~ because join doesn't put it at the start
        built_str = built_str + "~" + "~".join(params)

    return built_str

from db import get_received_messages_by_id, get_user_by_sessid, sign_in_to_db, sign_up_to_db, get_sent_messages_by_id
import shutil
import random
import os
import datetime
import subprocess
from typing import Tuple
import pyautogui
from PIL import Image
import pickle
import base64

HANDLE_TYPE = Tuple[(str | bytearray), bool]


def handle_error(args: str):
    return "ERRR~002~code not supported", True


def handle_time(args: str) -> HANDLE_TYPE:
    return "TIMR~" + datetime.datetime.now().strftime("%H:%M:%S:%f"), True


def handle_random(args: str) -> HANDLE_TYPE:
    return "RNDR~" + str(random.randint(1, 10)), True


def handle_who(args: str) -> HANDLE_TYPE:
    return "WHOR~" + os.environ["COMPUTERNAME"], True


def handle_exit(args: str) -> HANDLE_TYPE:
    return "EXTR", True


def handle_exec(args: str) -> HANDLE_TYPE:
    try:
        args_str = args.replace("~", "").replace("'", "")
        print("Args for subprocces: ", args_str)
        # , shell=True, check=True,
        res = subprocess.run(args_str, capture_output=True, text=True)
        #  capture_output=True, text=True)
        print(res.stdout)
        return "EXER~" + str(res.returncode) + "~" + res.stdout + "~" + res.stderr, True
    except subprocess.CalledProcessError as e:
        return f"Error during execution: {e}", True


def traverse(path="."):
    def sub_func(path):
        data = []
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            if os.path.isdir(full_path):
                # Recursive call for subdirectories
                data.extend(sub_func(full_path))
            else:
                data.append(full_path)  # Collect data (e.g., file names)
        return data

    return sub_func(path)


def base64_from_pickle(bytearr):
    try:
        # Deserialize the pickled data
        data = pickle.loads(bytearr)

        # Convert the pickled data to Base64
        base64_data = base64.b64encode(bytearr).decode("utf-8")

        return base64_data
    except Exception as e:
        print(f"Error: {e}")
        raise e
        return None


def handle_dir(args: str) -> HANDLE_TYPE:
    # params = args.split("~")[1:]
    data = traverse(args)  # params[0])
    return "DIRR~" + base64_from_pickle(pickle.dumps(data)), False


def handle_del(args: str) -> HANDLE_TYPE:
    print("Del Args: ", args)
    try:
        os.remove(args)
        return f"DELR~File '{args}' successfully deleted.", True
    except FileNotFoundError:
        return f"DELE~0010~Error: File '{args}' not found.", True
    except PermissionError:
        return f"DELE~0011: Permission denied. Unable to delete file '{args}'.", True
    except Exception as e:
        return (
            f"DELE~0012: An unexpected error occurred during file deletion: {e}",
            True,
        )

    # pass


def handle_copy(args: str) -> HANDLE_TYPE:
    print("Copying files: ")
    args_stringifyed = args
    print("Args: ", args)
    src, dest = args_stringifyed.split("~")
    print(f"{src = } { dest =}")
    shutil.copyfile(src, dest)
    return "COPR~Copy good", True
    # pass


def handle_screenshot(args: str) -> HANDLE_TYPE:
    filename = args
    if args == "" or args == b"":
        filename = (
            datetime.datetime.now().isoformat().replace(":", "_") + "_screenshot.png"
        )
    try:
        print(f"Saving {filename =}")
        pyautogui.screenshot("./srcshot/" + filename)
        return "SCTR~" + filename, True
    except Exception as e:
        print(e)
        return "SCTE~0100~" + "Cant save the screenshot", True
    pass


def get_file_size(file_path: str) -> int:
    try:
        size = os.path.getsize(file_path)
        return size
    except FileNotFoundError:
        return -1  # Or any other value indicating that the file was not found


SEND_SIZE = 4096


def handle_file(args: str, thread) -> HANDLE_TYPE:
    # the client needs to read chunked
    # find the file length
    # find the chunk numbers as file_length // chunk_size + 1 handle edge cases
    # send chuck by chunk
    # then send a final message

    file_name = args
    file_size = get_file_size(file_name)
    chunk_amount = file_size // SEND_SIZE + 1
    if file_size % SEND_SIZE == 0 and file_size > SEND_SIZE:
        chunk_amount -= 1  # no partial is needed
    thread.open_files[file_name] = open(file_name, "rb")
    return "FILR~" + str(chunk_amount) + "~" + file_name, True


def handle_chuk(args: str, thread):
    file_handle = thread.open_files[args]
    bin_data = file_handle.read(SEND_SIZE)

    # Convert binary data to base64-encoded string
    bin_data_b64 = base64.b64encode(bin_data).decode("utf-8")

    return "CHUR~" + args + "~" + bin_data_b64, True


def handle_close_file(args: str, thread):
    print("Requested Closed. ")
    thread.open_files[args].close()
    print("Closed: ", args)
    del thread.open_files[args]
    print("Closed sucsessfully")
    return "OKAY", True


def handle_register(args: str):
    print("Requested to register: ")
    username, password = args.split("~")
    sessid, errors = sign_up_to_db(username, password)
    print("Sign Up returned: ")
    print(f"{sessid =}")
    print(f"{errors =}")
    if len(errors) > 0:
        flattned = []
        for code, msg in errors:
            flattned.append(str(code))
            flattned.append(msg)
        return "REER~", "~".join(flattned)

    return f"REGR~{sessid}", True


def handle_signin(args: str):
    username, password = args.split("~")
    print(f"Sigin with: {username = } {password =}")
    sessid, errors = sign_in_to_db(username, password)
    print("Sign Up returned: ")
    print(f"{sessid =}")
    print(f"{errors =}")
    if len(errors) > 0:
        flattned = []
        for code, msg in errors:
            flattned.append(str(code))
            flattned.append(msg)
        return "REER~", "~".join(flattned)

    return f"REGR~{sessid}", True


def handle_get_inbox(args: str):
    sessid = args
    user = get_user_by_sessid(sessid)
    if user is None:
        return "INBE~Invalid Session Token~1001", True
    inbox = get_received_messages_by_id(user)[0]
    encoded = base64_from_pickle(pickle.dumps(inbox))
    return "BOXR~" + encoded, True


def handle_get_outbox(args: str):
    sessid = args
    user = get_user_by_sessid(sessid)
    if user is None:
        return "OUTE~Invalid Session Token~1001", True
    inbox = get_sent_messages_by_id(user)[0]
    encoded = base64_from_pickle(pickle.dumps(inbox))
    return "OUTR~" + encoded, True


def handle_get_unread(args):
    messages = get_unread_messages_from_sessid(args.split("~")[0])
    # Add rsa encoding
    encoded = base64_from_pickle(pickle.dumps(messages))
    return "UNRR~" + encoded, True


def handle_add_message(args):
    sessid, msg = args.split("~")
    succsess, error = add_message(sessid, msg)
    if error:
        return "ADME~"+error
    return "ADMR~" + succsess

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


def handle_error(args: bytearray):
    return "ERRR~002~code not supported", True


def handle_time(args: bytearray) -> HANDLE_TYPE:
    return "TIMR~" + datetime.datetime.now().strftime("%H:%M:%S:%f"), True


def handle_random(args: bytearray) -> HANDLE_TYPE:
    return "RNDR~" + str(random.randint(1, 10)), True


def handle_who(args: bytearray) -> HANDLE_TYPE:
    return "WHOR~" + os.environ["COMPUTERNAME"], True


def handle_exit(args: bytearray) -> HANDLE_TYPE:
    return "EXTR", True


def handle_exec(args: bytearray) -> HANDLE_TYPE:
    try:
        args_str = args.decode().replace("~", "").replace("'", "")
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


def handle_dir(args: bytearray) -> HANDLE_TYPE:
    # params = args.split("~")[1:]
    data = traverse()  # params[0])

    return "DIRR~" + base64_from_pickle(pickle.dumps(data)), False


def handle_del(args: bytearray) -> HANDLE_TYPE:
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


def handle_copy(args: bytearray) -> HANDLE_TYPE:
    print("Copying files: ")
    args_stringifyed = args.decode()
    print("Args: ", args)
    src, dest = args_stringifyed.split("~")
    print(f"{src = } { dest =}")
    shutil.copyfile(src, dest)
    return "COPR~Copy good", True
    # pass


def handle_screenshot(args: bytearray) -> HANDLE_TYPE:
    filename = args.decode()
    if args == "" or args == b"":
        filename = (
            datetime.datetime.now().isoformat().replace(":", "_") + "_screenshot.png"
        )
    try:
        print(f"Saving {filename =}")
        pyautogui.screenshot("./scrshot/" + filename)
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


SEND_SIZE = 2048


def handle_file(args: bytearray, thread) -> HANDLE_TYPE:
    # the client needs to read chunked
    # find the file length
    # find the chunk numbers as file_length // chunk_size + 1 handle edge cases
    # send chuck by chunk
    # then send a final message

    print("Args: ")
    print(args)
    file_name = args.decode()
    print("Requested filename: ", file_name)
    file_size = get_file_size(file_name)
    chunk_amount = file_size // SEND_SIZE + 1
    if file_size % SEND_SIZE == 0 and file_size > SEND_SIZE:
        chunk_amount -= 1  # no partial is needed
    print(f"Total Chunk amount: {chunk_amount}")
    thread.open_files[file_name] = open(file_name, "rb")
    return "FILR~" + str(chunk_amount) + "~" + file_name, True


def handle_chuk(args: bytearray, thread):
    file_handle = thread.open_files[args.decode()]
    bin_data = file_handle.read(SEND_SIZE)

    # Convert binary data to base64-encoded string
    bin_data_b64 = base64.b64encode(bin_data).decode("utf-8")

    return "CHUR~" + args.decode() + "~" + bin_data_b64, True


def handle_close_file(args: bytearray, thread):
    print("Requested Closed. ")
    thread.open_files[args.decode()].close()
    print("Closed: ", args.decode())
    del thread.open_files[args.decode()]
    print("Closed sucsessfully")
    return "OKAY", True

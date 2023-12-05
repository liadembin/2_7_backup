# from client import handle_msg
import base64
import pickle


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


def handle_dir(fileds, client_args):
    all = fileds[1]  # 0 is the code
    decoded = decode_from_pickle_and_from_base64(all)
    return "Dirs: " + str(decoded)


def handle_screenshot(fileds, client_args):
    return f"Server took a screenshot named {fileds[-1]} sucsessfuly"


def handle_exec(fileds, client_args):
    code, ret_code, stdin, sterr = fileds
    return f"""return code: {ret_code} \n 
                stdout: {stdin} \n 
                stderr: {sterr}
            """


def handle_recived_chunk(fields, client_args):
    # print("Writing to: ")
    # print(client_args)
    code, remote_file_name, b64content = fields
    decoded_to_bin = base64.b64decode(b64content)
    # out_filename = input("Enter the filename to save here ")
    with open(client_args[0], "ab+") as f:
        f.write(decoded_to_bin)
    return ""

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
    except Exception:
        return None


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
    # print("Writing to: ")
    # print(client_args)
    code, remote_file_name, b64content = fields
    decoded_to_bin = base64.b64decode(b64content)
    # out_filename = input("Enter the filename to save here ")
    with open(client_args[0], "ab+") as f:
        f.write(decoded_to_bin)
    return ""

import threading
import time
import socket
import traceback
from tcp_by_size import recv_by_size, send_with_size
from handlers import (
    handle_chuk,
    handle_close_file,
    handle_random,
    handle_error,
    handle_exit,
    handle_who,
    handle_time,
    handle_dir,
    handle_del,
    handle_exec,
    handle_copy,
    handle_file,
    handle_screenshot,
    handle_register,
    handle_signin
)
import os
SCREEN_SHOT_OUTPUT_DIR = "SCREEN_SHOTS_OUTS"


class CustomThread(threading.Thread):
    def __init__(self, cli_sock, addr, tid, tcp_debug=False):
        super(CustomThread, self).__init__()
        self.sock = cli_sock
        self.addr = addr
        self.tid = tid
        self.open_files = {}
        self.tcp_debug = tcp_debug
        if not os.path.isdir(SCREEN_SHOT_OUTPUT_DIR):
            os.makedirs(SCREEN_SHOT_OUTPUT_DIR)

    def handle_request(self, request):
        """
        Hadle client request
        tuple :return: return message to send to client and
        bool if to close the client self.socket
        """
        try:
            request_code = request[:4]
            to_send = self.dispatch_request(request)
            if request_code == b"EXIT":
                return to_send, True
        except Exception:
            print(traceback.format_exc())
            to_send = b"ERRR~001~General error"
        return to_send, False

    def run(self):
        print(f"New Client number {self.tid} from {self.addr}")

        while True:
            try:
                byte_data = recv_by_size(self.sock, self.tid, self.tcp_debug)
                if byte_data == b"":
                    print("Seems client disconnected")
                    break
                data_to_send, did_exit = self.handle_request(byte_data)
                self.send_data(data_to_send)
                if did_exit:
                    time.sleep(1)
                    break

            except socket.error as err:
                print(f"socket Error exit client loop: err:  {err}")
                break

            except Exception as err:
                print(f"General Error {err} exit client loop:")
                print(traceback.format_exc())
                break

    def send_data(self, bdata):
        """
        send to client byte array data
        will add 8 bytes message length as first field
        e.g. from 'abcd' will send  b'00000004~abcd'
        return: void
        """

        # logtcp("sent", bdata)
        send_with_size(self.sock, bdata, self.tid, self.tcp_debug)

    def dispatch_request(self, request):
        request_handlers = {
            "TIME": handle_time,
            "RAND": handle_random,
            "WHOU": handle_who,
            "EXIT": handle_exit,
            "EXEC": handle_exec,
            "DIRR": handle_dir,
            "DELL": handle_del,
            "COPY": handle_copy,
            "SCRS": handle_screenshot,
            "FILE": handle_file,
            "CHUK": handle_chuk,
            "CLOS": handle_close_file,
            "REGI": handle_register,
            "LOGI": handle_signin
        }
        request_code = request[:4].decode()
        # in this proto, the code is the client[:3] +"R", so can update this
        handler = request_handlers.get(request_code, handle_error)

        functions_that_require_this = ["CHUK", "FILE", "CLOS"]
        if request_code in functions_that_require_this:
            response = handler(request[5:].decode(), self)
        else:
            response = handler(request[5:].decode())  # 5 not 4 because of ~

        if len(response) == 1 or response[1]:
            res = response[0]
            return res.encode()
        return response[0]

import logging
import threading
import time
import socket
import traceback
from logger import log
# from rsa_client import RsaClient
from tcp_by_size import recv_by_size, send_with_size
from handlers import (
    handle_chuk,
    handle_close_file,
    handle_get_zipped_file,
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
    # handle_register,
    # handle_signin,
    # handle_get_unread,
    # handle_add_message,
    # handle_get_public_key,
    # handle_get_enc_key,
)
import os
from consts import SCREEN_SHOT_OUTPUT_DIR
import zlib


class CustomThread(threading.Thread):
    def __init__(self, cli_sock, addr, tid, tcp_debug=False):
        """
            input: socket, address of the client, and identifier and a flag on wheter to print debug info 
            output: returns a CustomThread Object 
            desc: the ctor of the class 
        """
        super(CustomThread, self).__init__()
        self.sock = cli_sock
        self.addr = addr
        self.tid = tid
        self.open_files = {}
        self.tcp_debug = tcp_debug
        self.save_screenshot_location = SCREEN_SHOT_OUTPUT_DIR + "/" + str(tid)
        if not os.path.isdir(self.save_screenshot_location):
            log("No Suitable screenshot directory, Creating",logging.INFO)
            os.makedirs(self.save_screenshot_location)

    def handle_request(self, request):
        """
        Handle client request
        tuple :return: return message to send to client and
        bool if to close the client self.socket
        """
        try:
            request_code = request[:4]
            to_send = self.dispatch_request(request)
            if request_code == b"EXIT":
                return to_send, True
        except Exception:
            #print(traceback.format_exc())
            log(traceback.format_exc(),"error")
            to_send = b"ERRR~001~General error"
        return to_send, False

    def run(self):
        """
            input: nothing
            output: nothing 
            desc: Runs the main function of the thread, it handles all its operations
        """
        log_msg=  f"New Client number {self.tid} from {self.addr}"
        log(log_msg,logging.INFO)
        while True:
            try:
                byte_data = recv_by_size(self.sock, self.tid, self.tcp_debug)
                if byte_data == b"":
                    #print("Seems client disconnected")
                    log("client dissconnect","info")
                    break
                data_to_send, did_exit = self.handle_request(byte_data)
                self.send_data(data_to_send)
                if did_exit:
                    time.sleep(1)
                    break
            except socket.error as err:
                log_msg= f"socket Error exit client loop: err:  {err}"
                log(log_msg,logging.ERROR)
                break

            except Exception as err:
                # print(f"General Error {err} exit client loop:")
                # print(traceback.format_exc())
                log(f"General Error {err} exit client loop:",logging.ERROR)
                log(traceback.format_exc(),logging.ERROR)
                break

    def send_data(self, bdata: bytearray) -> None:
        """
        send to client byte array data
        will add 10 bytes message length as first field
        e.g. from 'abcd' will send  b'0000000004~abcd'
        return: void
        """
        send_with_size(self.sock, bdata, self.tid, self.tcp_debug)

    def dispatch_request(self, request):
        """
        input:  request
        output:  the response to send 
        desc: Dispaches and calls the function that fits the request 
        """
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
            "ZFIL": handle_get_zipped_file,
            "CHUK": handle_chuk,
            "CLOS": handle_close_file,
            # "REGI": handle_register,
            # "LOGI": handle_signin,
            # "GETM": handle_get_unread,
            # "ADDM": handle_add_message,
            # "GETP": handle_get_public_key,
            # "GKEY": handle_get_enc_key,
        }
        request_code = request[:4].decode()
        handler = request_handlers.get(request_code, handle_error)
        functions_that_require_refrence_to_thread = [
            "CHUK",
            "FILE",
            "CLOS",
            "GETP",
            "GKEY",
            "ZFIL",
            "SCRS",
        ]
        if request_code in functions_that_require_refrence_to_thread:
            response = handler(request[5:].decode(), self)
        else:
            response = handler(request[5:].decode())  # 5 not 4 because of ~

        if (
            not (type(response) == tuple or type(response) == list) or response[1]
        ):  # to allow not returning True to not serialize
            res = response[0]
            return res.encode()
        return response[0]

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
)

# using from import * ruins the LSP(auto complete.)


def check_length(message):
    """
    check message length
    return: string - error message
    """
    size = len(message)
    if size < 13:  # 13 is min message size
        return b"ERRR~003~Bad Format message too short"
    if int(message[:8].decode()) != size - 9:
        return b"ERRR~003~Bad Format, incorrect message length"
    return b""


def protocol_build_reply(request):
    """
    Application Business Logic
    function despatcher ! for each code will get to some function that handle specific request
    Handle client request and prepare the reply info
    string:return: reply
    """


class CustomThread(threading.Thread):
    def __init__(self, cli_sock, addr, tid):
        super(CustomThread, self).__init__()
        self.sock = cli_sock
        self.addr = addr
        self.tid = tid
        self.open_files = {}

    def handle_request(self, request):
        """
        Hadle client request
        tuple :return: return message to send to client and bool if to close the client self.socket
        """
        try:
            request_code = request[:4]
            to_send = self.dispatch_request(request)
            if request_code == b"EXIT":
                return to_send, True
        except Exception as err:
            print(traceback.format_exc())
            to_send = b"ERRR~001~General error"
        return to_send, False

    def run(self):
        finish = False
        print(f"New Client number {self.tid} from {self.addr}")

        while not finish:
            try:
                # Improve by receiving data based on message size
                byte_data = recv_by_size(self.sock)

                if byte_data == b"":
                    print("Seems client disconnected")
                    break

                self.logtcp("recv", byte_data)
                data_to_send, did_err = self.handle_request(byte_data)
                # if to_send:
                self.send_data(data_to_send)

                if finish:
                    time.sleep(1)
                    break

            except socket.error as err:
                print(f"socket Error exit client loop: err:  {err}")
                break

            except Exception as err:
                print(f"General Error {err} exit client loop:")
                print(traceback.format_exc())
                break

    def logtcp(self, dir, byte_data):
        """
        log direction, self.tid and all TCP byte array data
        return: void
        """
        if dir == "sent":
            print(f"{self.tid} S LOG:Sent     >>> {byte_data}")
        else:
            print(f"{self.tid} S LOG:Recieved <<< {byte_data}")

    def send_data(self, bdata):
        """
        send to client byte array data
        will add 8 bytes message length as first field
        e.g. from 'abcd' will send  b'00000004~abcd'
        return: void
        """
        # bytearray_data = str(len(bdata)).zfill(8).encode() + b'~' + bdata
        # self.sock.send(bytearray_data)
        # self.logtcp('sent', bytearray_data)
        # print("")
        print("Sending back to the client the following data: ")
        print(bdata)
        send_with_size(self.sock, bdata)

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
        }
        request_code = request[:4].decode()
        # in this proto, the code is the client[:3] +"R", so can replace that and have
        handler = request_handlers.get(request_code, handle_error)
        # the function return norma, strings but this is more general
        if request_code == "CHUK" or request_code == "FILE" or request_code == "CLOS":
            response = handler(request[5:], self)
        else:
            response = handler(request[5:])  # 5 not 4 because of ~
        print("Response")
        print(response)
        if response[1]:
            res = response[0]
            return res.encode()
        return response[0]

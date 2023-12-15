import logging
from logger import log 
SIZE_HEADER_FORMAT = "000000000|"  # n digits for data size + one delimiter
size_header_size = len(SIZE_HEADER_FORMAT)
LEN_TO_PRINT = 90
PRINT_SEVERITY = logging.INFO

def recv_by_size(sock, tid="", TCP_DEBUG=False):
    size_header = b""
    data_len = 0
    while len(size_header) < size_header_size:
        _s = sock.recv(size_header_size - len(size_header))
        if _s == b"":
            size_header = b""
            break
        size_header += _s
    data = b""
    if size_header != b"":
        data_len = int(size_header[: size_header_size - 1])
        while len(data) < data_len:
            _d = sock.recv(data_len - len(data))
            if _d == b"":
                data = b""
                break
            data += _d

    if (TCP_DEBUG and size_header != b"") and (tid == "" or tid == -1): 
        print_msg = f" {tid} - Recived({size_header}) >>> {data[:min(LEN_TO_PRINT,len(data))]}"
        # logger.info(
        #     
        # )
        log(print_msg,PRINT_SEVERITY)
    elif TCP_DEBUG and size_header != b"":
        print_msg = f"Recived({size_header}) >>> {data[:min(LEN_TO_PRINT,len(data))]}"
        log(print_msg,PRINT_SEVERITY)
        
        # logger.info()
    return data if len(data) == data_len else b""


def send_with_size(sock, bdata, tid="", TCP_DEBUG=False):
    if type(bdata) == str:
        bdata = bdata.encode()
    len_data = len(bdata)
    header_data = str(len(bdata)).zfill(size_header_size - 1) + "~"

    bytea = bytearray(header_data, encoding="utf8") + bdata

    sock.send(bytea)
    if not (TCP_DEBUG and len_data > 0):
        return

    if tid != "" or tid == -1:
        print_msg= f" tid: {tid} -  Sent({len_data})>>> {bytea[:min(len(bytea),LEN_TO_PRINT)]}"
        log(print_msg,PRINT_SEVERITY)
        # logger.info(
            
        # )
    else:
        print_msg = f"  Sent({len_data})>>> {bytea[:min(len(bytea),LEN_TO_PRINT)]}"
        log(print_msg,PRINT_SEVERITY)

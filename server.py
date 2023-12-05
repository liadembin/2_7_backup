import socket

# import random
# import traceback
# import time
# import threading
# import os
# import datetime
from custom_thread import CustomThread

IP, PORT = ("127.0.0.1", 7777)


def main():
    global all_to_die
    """
        main server loop
        1. accept tcp connection
        2. create thread for each connected new client
        3. wait for all threads
        4. every X clients limit will exit
    """
    threads = []
    srv_sock = socket.socket()

    srv_sock.bind((IP, PORT))

    srv_sock.listen(20)

    # next line release the port
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    tid = 1
    while True:
        print("\nMain thread: before accepting ...")
        cli_sock, addr = srv_sock.accept()
        t = CustomThread(cli_sock, addr, tid, False)
        t.start()
        tid += 1
        break  # for testing, i use just one client for basic tests
    all_to_die = True
    print("Main thread: waiting to all clints to die")
    for t in threads:
        t.join()
    srv_sock.close()
    print("Bye ..")


if __name__ == "__main__":
    main()

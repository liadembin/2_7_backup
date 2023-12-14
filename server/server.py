# from rsa_client import RsaClient
import os
import pickle
import socket
from custom_thread import CustomThread
from dotenv import load_dotenv

IP, PORT = ("127.0.0.1", 7777)


def main():
    """
    main server loop
    1. accept tcp connection
    2. create thread for each connected new client
    3. wait for all threads
    4. every X clients limit will exit
    """
    # realy need to find better way to do this
    # client = RsaClient(17, 11)
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

        # t = CustomThread(cli_sock, client, addr, tid, True)
        t = CustomThread(cli_sock, addr, tid, True)
        t.start()
        tid += 1
        break  # for testing, i use just one client for basic tests
    print("Main thread: waiting to all clints to die")
    for t in threads:
        t.join()
    srv_sock.close()
    print("Bye ..")


if __name__ == "__main__":
    main()

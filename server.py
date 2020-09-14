import os
import socket
from threading import Thread

clients = []
block_size = 1024


# Thread to listen one particular client
class ClientListener(Thread):
    file = None

    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        while True:
            # try to read 1024 bytes from user
            # this is blocking call, thread will be paused here
            data = self.sock.recv(block_size)
            if data:
                # check if filename received
                if 'FILENAME#' in data.decode():
                    filename = data.decode().split('#')[1]
                    print("Received filename: %s" % filename)

                    # send ACK to client to start file upload procedure
                    self.sock.send("ACK".encode())
                    # check is file exists
                    if not is_file_exists(filename):
                        dir = os.path.split(filename)[1]  # file name at end of dir path
                        self.file = open(dir, 'xb')  #
                    else:
                        # generate new filename
                        dir = os.path.split(create_copy_name(filename))[1]  # file name at end of dir path
                        self.file = open(dir, 'xb')
                    while 1:
                        # receive data
                        data = self.sock.recv(block_size)
                        if not data:
                            break  # till closed on server side
                        self.file.write(data)
            else:
                self.file.close()
                self._close()
                # finish the thread
                return


def is_file_exists(filename):
    if os.path.isfile('./%s' % filename):
        return True
    else:
        return False


def create_copy_name(filename):
    for i in range(9999999):
        str = filename.split('.')
        if not is_file_exists(str[0] + ("_copy%d." % (i + 1)) + str[1]):  # expand test.txt to [test] and [txt]
            return str[0] + ("_copy%d." % (i + 1)) + str[1]
    return "What a hell are you uploading here?))"


def main():
    next_user = 1
    # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # listen to all interfaces at 8800 port
    sock.bind(('', 8800))
    sock.listen()
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        clients.append(con)
        name = 'user#' + str(next_user)
        next_user += 1
        print(str(addr) + ' connected as ' + name)
        # start new thread to deal with client
        ClientListener(name, con).start()


if __name__ == "__main__":
    main()

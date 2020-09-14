#!/usr/bin/env python3
import sys, os, time
from socket import *

block_size = 1024


# Print iterations progress
# https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def parse_commandline():
    args = sys.argv[1:]  # skip program name at front of args
    return {'file_name': args[0], 'host': args[1], 'port': args[2]}  # load parameters from commandline


def client(host, port, filename):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((host, port))

    # send filename
    sock.send(("FILENAME#" + filename).encode())

    # wait for ACK
    data = sock.recv(1024)
    if data and data.decode() == 'ACK':
        print("File name '%s' transmitted successfully, starting file transfer...\n" % filename)

        # start file transmitting
        try:
            file = open(filename, 'rb')  # open file
            total_sent = 0
            file_size = os.path.getsize(filename)
            printProgressBar(total_sent, file_size, prefix='Progress:', suffix='Complete',
                             length=50)  # init progress bar
            while True:
                bytes = file.read(block_size)  # read block_size at a time
                if not bytes:
                    break  # until file totally sent
                sent = sock.send(bytes)

                # update vars for progress bar
                total_sent += sent

                # update progress bar
                printProgressBar(total_sent, file_size, prefix='Progress:', suffix='Complete', length=50)

                # debug
                assert sent == len(bytes)
        except:
            print('Error occurred while downloading file on server:', filename)

    sock.close()


def main(args):
    # get params
    host = args.get('host')
    port = int(args.get('port'))
    file_name = args.get('file_name')
    client(host, port, file_name)


if __name__ == '__main__':
    args = parse_commandline()
    main(args)

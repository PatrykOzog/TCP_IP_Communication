import socket
import threading
import PIL
from PIL import Image

text_chars = ["@", "0", "#", "S", "%", "?", "*", "+", "=", ";", ":", "-", ",", "."]
received_file = "rf.jpg"


def gray_it_out(image):
    gray_image = image.convert("L")
    return gray_image


def resize_image(image, updated_width=100):
    width, height = image.size
    ratio = height / width * 0.5
    updated_height = int(updated_width * ratio)
    resized_image = image.resize((updated_width, updated_height))
    return resized_image


def pixels_to_text(image):
    pixels = image.getdata()
    characters = "".join([text_chars[pixel // 25] for pixel in pixels])
    return characters


def convert(client_socket, image, updated_width=100):
    new_data = pixels_to_text(gray_it_out(resize_image(image)))
    new_data_lines = [new_data[i:i + updated_width] for i in range(0, len(new_data), updated_width)]
    msg = "\n".join(new_data_lines) + "\n"

    while msg:
        sent = client_socket.send(msg.encode())
        msg = msg[sent:]


def send_msg(client_socket):
    while True:
        msg = input()
        if msg == "image":
            try:
                path = input("Enter a valid pathname to an image:\n")
                image = PIL.Image.open(path)
                convert(client_socket, image)
            except:
                print(f"{path} is invalid.\n")
        elif msg == "file":
            try:
                path = input("Enter a valid pathname to your file:\n")
                file = open(path, "rb")
                client_socket.send(received_file.encode())
                data = file.read()
                client_socket.sendall(data)
                client_socket.send(b" ")
                file.close()

            except:
                print(f"{path} is invalid.\n")
        else:
            client_socket.send(msg.encode())


def receive_msg(client_socket):
    buff_size = 1024
    while True:
        full_msg = ''
        while True:
            try:
                msg = client_socket.recv(buff_size).decode()
                if msg == received_file:
                    file = open(msg, "wb")
                    file_bytes = b""
                    done = False
                    data = client_socket.recv(buff_size)
                    while not done:
                        if len(data) == buff_size:
                            file_bytes += data
                            data = client_socket.recv(buff_size)
                        else:
                            file_bytes += data[:-1]
                            done = True

                    file.write(file_bytes)
                    file.close()
                elif len(msg) == buff_size:
                    full_msg += msg
                else:
                    full_msg += msg
                    print(full_msg)
                    full_msg = ''
            except:
                break


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 5555))

    send_thread = threading.Thread(target=send_msg, args=(client_socket,))
    receive_thread = threading.Thread(target=receive_msg, args=(client_socket,))

    send_thread.start()
    receive_thread.start()

    send_thread.join()
    receive_thread.join()

    client_socket.close()


start_client()
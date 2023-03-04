import socket
import threading
import PIL
from PIL import Image
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, \
    QTextEdit, QWidget

text_chars = ["@", "0", "#", "S", "%", "?", "*", "+", "=", ";", ":", "-", ",", "."]
received_file = "rf.jpg"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 5555))


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
    msg = input_box.text()
    if msg[:8] == "!sendart":
        try:
            path = msg[9:]
            image = PIL.Image.open(path)
            convert(client_socket, image)
        except:
            messages_box.append(f"###{path} is invalid.###\n")
    elif msg[:9] == "!sendfile":
        try:
            path = msg[10:]
            file = open(path, "rb")
            # dot_pos = msg.index(".")
            # received_file = path
            client_socket.send(received_file.encode())
            data = file.read()
            client_socket.sendall(data)
            client_socket.send(b" ")
            file.close()

        except:
            messages_box.append(f"###{path} is invalid.###\n")
    else:
        client_socket.send(msg.encode())


def receive_msg(client_socket):
    buff_size = 16
    #while True:
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
                messages_box.append(full_msg)
                full_msg = ''
        except:
            break


def handle_msg():
    send_thread = threading.Thread(target=send_msg, args=(client_socket,))
    send_thread.start()
    send_thread.join()
    input_box.clear()


receive_thread = threading.Thread(target=receive_msg, args=(client_socket,))
receive_thread.start()

# Ustawienia okna
app = QApplication([])
window = QMainWindow()
window.setWindowTitle("PySide6 Chat")
window.setGeometry(100, 100, 1000, 500)

# Tworzenie głównego widgetu
main_widget = QWidget()
window.setCentralWidget(main_widget)

# Układ głównego widgetu
main_layout = QVBoxLayout()
main_widget.setLayout(main_layout)

# Pole do wyświetlania wiadomości
messages_box = QTextEdit()
messages_box.setReadOnly(True)
font = QFont("Courier New", 10)
messages_box.setFont(font)
main_layout.addWidget(messages_box)

# Układ wiersza z polami tekstowymi i przyciskiem
input_layout = QHBoxLayout()
main_layout.addLayout(input_layout)

# Pole do wpisywania wiadomości
input_box = QLineEdit()
input_layout.addWidget(input_box)

# Przycisk do wysyłania wiadomości
send_button = QPushButton("Send")
send_button.clicked.connect(handle_msg)
input_layout.addWidget(send_button)

messages_box.append("### To send ASCII-ART write: !sendart yourimagename.jpg ###")
messages_box.append("### To send any file write: !sendfile yourfilename.extension ###")


window.show()
app.exec()
client_socket.close()

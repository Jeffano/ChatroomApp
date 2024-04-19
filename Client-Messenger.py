from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter

# Known authentication string
AUTHENTICATION_STRING = "TEAM10_VAILIDATION_STRING"

# get info from the server. used to get messages.
def receive():
    while True:
        try:
            msg = client_socket.recv(BUFFER_SIZE).decode("utf8")
            if not msg:  # If the message is empty, the server closed the connection
                break  # Exit the loop
            msg_list.insert(tkinter.END, msg)
            msg_list.see(tkinter.END)
        except OSError:
            break  # Exit the loop if there's an error with the socket


def send(event=None):  # binder passes event
    msg = my_msg.get()
    my_msg.set("")  # clear text field after sending a message
    global current_room
    if msg == "{quit}":  # check if the user decides to quit, if so, clean up
        msg_list.insert(tkinter.END, "Goodbye " + my_username.get())
        client_socket.send(bytes(my_username.get() + " left the chat", "utf8"))
        client_socket.close()  # closes client thread on server.
        rootWindow.quit()
        return
    client_socket.send(bytes(my_username.get() + ": " + msg, "utf8"))  # otherwise, send message to server, let
    # server handle our message.


# send quit message to the server.
def on_closing(event=None):
    # Send server quit message.
    my_msg.set("{quit}")
    send()
    # Close the client socket
    client_socket.close()
    rootWindow.quit()

def change_room():
    global current_room
    current_room = ((chatRoomSelected.get()).split(' '))[2]
    client_socket.send(bytes("/" + current_room, "utf8"))   # send msg to server to change our room
    msg_list.delete(0, tkinter.END)  # clear the chat
    msg_list.insert(tkinter.END, "Joining room " + str(current_room) + "...")  # tell user new room
    msg_list.see(tkinter.END)

# Global variables.
number_of_rooms = 0
current_room = 0

rootWindow = tkinter.Tk()
rootWindow.title("Chatroom Messenger")

messages_frame = tkinter.Frame(rootWindow)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("")  # set our globals. This sets the users msg and username values from text input
my_username = tkinter.StringVar()
my_username.set("")

# Socket with given AWS parameters.
HOST = "127.0.0.1"
PORT = 2008
BUFFER_SIZE = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)
client_socket.send(bytes(AUTHENTICATION_STRING, "utf8"))


# get number of rooms from the server and list them for the client
first_msg = client_socket.recv(BUFFER_SIZE).decode("utf8")
if first_msg:  # Check if the string is not empty
    try:
        number_of_rooms = int(first_msg)
    except ValueError:
        print("Received string cannot be converted to integer.")
else:
    print("Received string is empty.")
number_of_rooms = int(first_msg)
chatRoomSelected = tkinter.StringVar(rootWindow)
chatRoomSelected.set("Select Chat Room")
rooms_list = []
for i in range(number_of_rooms):
    rooms_list.append("Chat Room " + str(i + 1))

chat_rooms = tkinter.OptionMenu(rootWindow, chatRoomSelected, *rooms_list)
chat_rooms.pack()
change_button = tkinter.Button(rootWindow, text="Change Room", command=change_room)
change_button.pack()

receive_thread = Thread(target=receive)
receive_thread.start()
rootWindow.resizable(width=False, height=False)  # The client can't resize the window.

# Messages container.
msg_list = tkinter.Listbox(messages_frame, height=30, width=50, bg="light blue")
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

username_label = tkinter.Label(rootWindow, text="Enter username: ")
username_label.pack()
username_field = tkinter.Entry(rootWindow, textvariable=my_username)
username_field.pack()

message_label = tkinter.Label(rootWindow, text="Enter message: ")
message_label.pack()
entry_field = tkinter.Entry(rootWindow, textvariable=my_msg, width=50)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(rootWindow, text="Send", command=send)
send_button.pack()

rootWindow.protocol("WM_DELETE_WINDOW", on_closing)

tkinter.mainloop()
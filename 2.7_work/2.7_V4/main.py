import socket
import protocol

IP = "192.168.56.1"
PORT = 1234

CLIENT_IMAGE_PATH = r"C:\Users\user\Desktop\screenshot.png"


# Function to handle server responses, such as receiving a screenshot
def handle_server_response(my_socket, cmd):
    try:
        if cmd.startswith("SEND_PHOTO"):
            # Receive the length of the length of the image
            length_image = int(my_socket.recv(4).decode())

            # Receive the actual length of the image
            images_length = int(my_socket.recv(length_image).decode())

            # Open the file to write binary content
            with open(CLIENT_IMAGE_PATH, "wb") as image:
                image_content = my_socket.recv(images_length)  # Receive image content
                image.write(image_content)

            print(f"Screenshot received and saved to {CLIENT_IMAGE_PATH}")
        else:
            # Handle other responses
            response = my_socket.recv(1024).decode()
            print("Server response:", response)
    except Exception as e:
        print(f"Error in handle_server_response: {e}")
        return False  # Indicate an error occurred during response handling
    return True


# Function to send the username to the server
def sendname(my_socket):
    try:
        name = input("Enter username: ")
        my_socket.send(name.encode())
    except Exception as e:
        print(f"Error in sending name: {e}")


# Main function to manage the client-server communication
def main():
    try:
        # Open socket with the server
        my_socket = socket.socket()
        my_socket.connect((IP, PORT))

        sendname(my_socket)  # Send the username to the server

        # Print instructions for available commands
        print('Welcome to remote computer application. Available commands are:\n')
        print('TAKE_SCREENSHOT\nSEND_PHOTO\nDIR\nDELETE\nCOPY\nEXECUTE\nEXIT')

        # Loop until user requests to exit
        while True:
            cmd = input("Please enter command:\n")
            if protocol.check_cmd(cmd):
                packet = protocol.create_msg(cmd)
                my_socket.send(packet)  # Send the command packet to the server

                # Handle the server response based on the command
                if not handle_server_response(my_socket, cmd):
                    print("An error occurred while handling server response.")
                    break

                if cmd == 'EXIT':
                    print("Exiting the application...")
                    break
            else:
                print("Not a valid command, or missing parameters\n")
    except Exception as e:
        print(f"Error in main function: {e}")
    finally:
        # Ensure the socket is closed even if an error occurs
        my_socket.close()


if __name__ == '__main__':
    main()

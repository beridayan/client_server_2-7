import socket
import protocol
import glob
import os
import shutil
from PIL import ImageGrab  # pip install Pillow

IP = "0.0.0.0"
PORT = 1234


# Function to format and check the client's request
def format_and_check_client_request(cmd):
    try:
        # Split the command into its parts
        command_parts = cmd.split()
        command = command_parts[0]  # The first part is the command
        # The rest of the parts are parameters
        params = command_parts[1:] if len(command_parts) > 1 else []

        # Print the command and parameters for debugging
        print(f"{name}: {command_parts}")

        # Check if the command is valid using the protocol module
        if protocol.check_cmd(cmd):
            return True, command, params  # Return success and the command with parameters
        return False, None, None  # Return failure if the command is invalid
    except Exception as e:
        # If an error occurs, print the error and return failure
        print(f"Error formatting and checking client request: {e}")
        return False, None, None


# Function to handle the actual command sent by the client
def handle_client_request(command, params, client_socket):
    try:
        # Handle different commands sent by the client
        if command == "DIR":
            # List files matching the provided pattern
            files_list = glob.glob(params[0])
            return "\n".join(files_list)
        elif command == "DELETE":
            # Delete the specified file
            if os.path.isfile(params[0]):
                os.remove(params[0])  # Remove the file if it exists
            else:
                return f"File {params[0]} does not exist."  # Return an error if file doesn't exist
        elif command == "COPY":
            # Copy a file from source to destination
            if os.path.isfile(params[0]):
                shutil.copy(params[0], params[1])  # Copy the file
            else:
                return f"Source file {params[0]} does not exist."  # Error if source file doesn't exist
        elif command == "EXECUTE":
            # Execute the provided system command
            os.system(params[0])

        elif command == "SEND_PHOTO":
            # Send a photo from the server to the client
            if os.path.isfile(params[0]):
                # Open the image file in binary mode
                with open(params[0], "rb") as image:
                    image_content = image.read()

                    # Send the image size first (in case of large images)
                    image_length = str(len(image_content))
                    length_of_images_length = str(len(image_length)).zfill(4)

                    client_socket.send(length_of_images_length.encode())  # Send length of length
                    client_socket.send(image_length.encode())  # Send actual length
                    client_socket.send(image_content)  # Send the image content itself
            else:
                # Inform the client to take a screenshot first
                data_to_send = protocol.create_msg("Take a screenshot first.")
                client_socket.send(data_to_send)

        elif command == "TAKE_SCREENSHOT":
            # Take a screenshot of the entire screen
            screenshot = ImageGrab.grab()
            # Save the screenshot to a file specified by the client
            screenshot.save(params[0])

        # Return a success message after the command is executed
        return "Command executed successfully"
    except Exception as e:
        # If any error occurs while handling the request, print the error and return an error message
        print(f"Error handling client request '{command}': {e}")
        return f"Error executing {command} command."


# Main function to initialize the server and handle client connections
def main():
    try:
        # Open socket and bind it to the specified IP and port
        server_socket = socket.socket()
        server_socket.bind((IP, PORT))
        server_socket.listen()  # Start listening for incoming connections
        print("Server is listening...")

        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        global name
        # Receive the name of the client
        name = client_socket.recv(1024).decode()

        print(f"Connected to client at {client_address}")

        # Handle requests from the client
        while True:
            try:
                # Get the message from the client using the protocol
                valid_protocol, cmd = protocol.get_msg(client_socket)
                if valid_protocol:
                    # Format and check the client request
                    valid_cmd, command, params = format_and_check_client_request(cmd)

                    if valid_cmd:
                        # Handle the valid command and send the response back to the client
                        response = handle_client_request(command, params, client_socket)
                        packet = protocol.create_msg(response)
                        print(f"{name}: {packet}")  # Print the response in the server for debugging
                        client_socket.send(packet)
                        if command == 'EXIT':
                            break  # Exit the loop if the client sends 'EXIT'
                    else:
                        # If the command or parameters are invalid, inform the client
                        response = 'Bad command or parameters'
                        client_socket.send(protocol.create_msg(response))
                else:
                    # If the protocol is invalid, inform the client
                    response = 'Packet not according to protocol'
                    client_socket.send(protocol.create_msg(response))
                    client_socket.recv(1024)  # Clean up socket
            except Exception as e:
                # If an error occurs while handling client requests, print the error and send an error message
                print(f"Error handling client request: {e}")
                client_socket.send(protocol.create_msg("Internal server error"))
                client_socket.recv(1024)  # Clean up socket

        # Close the connection once the loop is broken (i.e., client sends 'EXIT')
        print("Closing connection")
        client_socket.close()
        server_socket.close()

    except Exception as e:
        # If any error occurs during the main server operation, print the error and clean up sockets
        print(f"Error in main server loop: {e}")
        if 'client_socket' in locals():
            client_socket.close()
        if 'server_socket' in locals():
            server_socket.close()


# Entry point for the program
if __name__ == '__main__':
    main()

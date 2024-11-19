LENGTH_FIELD_SIZE = 4  # The size of the length field used to indicate the size of the message
PORT = 8820  # Port number for the server to listen on


# Function to check if a command is valid based on the expected parameters
def check_cmd(data):
    try:
        check = False

        # Dictionary mapping commands to the number of expected parameters
        commands = {
            "DIR": 1, "DELETE": 1, "COPY": 2, "EXECUTE": 1, "TAKE_SCREENSHOT": 1, "SEND_PHOTO": 1, "EXIT": 0
        }

        # Split the input data into command and parameters
        command_parts = data.split()
        command = command_parts[0]  # The first part is the command

        # Check if the number of parameters matches the expected number for the command
        if len(command_parts) - 1 == commands[command]:
            check = True  # Set check to True if the number of parameters is correct

        # Return True if the command is valid and the parameter count matches, else False
        if check:
            return command in commands
        return False
    except Exception as e:
        # Catch any exceptions and print the error message
        print(f"Error in check_cmd function: {e}")
        return False


# Function to create a message to be sent to the client
def create_msg(data):
    try:
        # Calculate the length of the data and pad it to fit the length field size
        data_length = str(len(data)).zfill(LENGTH_FIELD_SIZE)
        # Concatenate the length and data, then encode it into bytes
        return (data_length + data).encode()
    except Exception as e:
        # Catch any exceptions and print the error message
        print(f"Error in create_msg function: {e}")
        return None


# Function to receive a message from a socket, with length checking
def get_msg(my_socket):
    try:
        # Receive the length of the incoming message (in bytes) from the socket
        length_data = my_socket.recv(LENGTH_FIELD_SIZE).decode()

        # Check if the received length data is a valid digit
        if not length_data.isdigit():
            raise ValueError("Received length data is not a valid digit")  # Raise an error if it's not a valid number

        length = int(length_data)  # Convert the length data to an integer
        # Receive the actual message from the socket based on the specified length
        message = my_socket.recv(length).decode()

        # Return True indicating the message is received successfully, along with the message itself
        return True, message
    except ValueError as ve:
        # Catch specific ValueError and handle invalid length data
        print(f"Error: {ve}")
        return False, "Error: Invalid length data"
    except Exception as e:
        # Catch any other exceptions and print the error message
        print(f"Error in get_msg function: {e}")
        return False, "Error: Exception occurred while receiving message"

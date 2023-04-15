import socket
import ssl

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Storing users and fuel costs

users = {'client1': 'password123', 'client2': 'password456'}

fuel_price = {'95 Benzin': 610,'Prémium Diesel': 640,
              'Diesel': 585,'Prémium Benzin': 647 }

# Generate and import key pair

key = RSA.generate(2048)

public_key = key.publickey().export_key()

private_key = key.export_key()

 
# Set up SSL/TLS server

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

context.load_cert_chain('server.crt', 'server.key')

context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

# Start server and listen for client connection

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    
    sock.bind(('localhost', 8000))
    
    sock.listen(5)
    
    print("Listening on port 8000")
    
    while True:
        
     try:
         
         conn, addr = sock.accept()
         
         with context.wrap_socket(conn, server_side=True) as ssock:
                    
             # Send public key to client
             
             ssock.sendall(public_key)
             
             # Prompt for login credentials
             
             print("Waiting for credentials")
             
             cipher = PKCS1_OAEP.new(key)
             
             ssock.send('Enter your username: '.encode())
             
             encrypted_username = ssock.recv(1024)
             
             decrypted_username = cipher.decrypt(encrypted_username).decode("utf-8")             
             
             ssock.send('Please enter your password: '.encode())
             
             encrypted_password = ssock.recv(1024)
                       
             decrypted_password = cipher.decrypt(encrypted_password).decode("utf-8")          
             
             # Verify the credentials against the stored values
             
             if decrypted_username in users and users[decrypted_username] == decrypted_password:
                 
                 ssock.send('Login successful!'.encode())
                 
             else:
                 
                 ssock.send('Error: Incorrect username or password.'.encode())
                 
             # Recive the fuel data, calculate cost and send it back to client
             
             encrypted_fuel_amount = ssock.recv(1024)
             
             decrypted_amount_bytes = cipher.decrypt(encrypted_fuel_amount)
             
             decrypted_fuel_amount = int.from_bytes(decrypted_amount_bytes, byteorder='big')
             
             encrypted_fuel_type = ssock.recv(1024)
                        
             decrypted_type_bytes = cipher.decrypt(encrypted_fuel_type)
             
             decrypted_fuel_type = int.from_bytes(decrypted_type_bytes, byteorder='big')
             
             
             type_dict = {
                 1:"95 Benzin",
                 2:"Diesel",
                 3:"Prémium Benzin",
                 4:"Prémium Diesel",
                 5:"Autógáz"
             }
             
             fuel_type_str = type_dict.get(decrypted_fuel_type, "Invalid number")
             
             fuel_price = fuel_price[fuel_type_str]
             
             final_price = fuel_price * decrypted_fuel_amount
             
             # print(final_price)
             
             # ssock.send(final_price)
             
     except BlockingIOError:
         pass  # no client connection yet, keep waiting
import socket
import ssl
# import hashlib

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Storing users

users = {'client1': 'password123', 'client2': 'password456'}

# Generate and import key pair

key = RSA.generate(2048)

public_key = key.publickey().export_key()

private_key = key.export_key()

 
# Set up SSL/TLS server

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

context.load_cert_chain('server.crt', 'server.key')

context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

print('SSL set up')


# Start server and listen for client connection

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    
    sock.bind(('localhost', 8000))
    
    sock.listen(5)
    
    print('Started server')
    
    while True:
        
     try:
         
         conn, addr = sock.accept()
         
         with context.wrap_socket(conn, server_side=True) as ssock:
             
             
             # Send public key to client
             
             ssock.sendall(public_key)
             
             print('Public key sent to client.')
             
             # Prompt for login credentials
             
             print("Waiting for credentials")
             
             cipher = PKCS1_OAEP.new(key)
             
             ssock.send('Enter your username: '.encode())
             encrypted_username = ssock.recv(1024)
             
             decrypted_username = cipher.decrypt(encrypted_username).decode("utf-8")
             print(decrypted_username)
             
             ssock.send('Please enter your password: '.encode())
             encrypted_password = ssock.recv(1024)
                       
             decrypted_password = cipher.decrypt(encrypted_password).decode("utf-8")
             print(decrypted_password)
             
             
             # Verify the credentials against the stored values
             
             if decrypted_username in users and users[decrypted_username] == decrypted_password:
                 
                 ssock.send('Login successful!'.encode())
                 
             else:
                 ssock.send('Error: Incorrect username or password.'.encode())
             
             
             # Receive encrypted message from client
             
             encrypted_message = ssock.recv(1024)
             
             print('Encrypted message received:', encrypted_message)
             

             # Decrypt message with private key
             
             cipher = PKCS1_OAEP.new(key)
             
             decrypted_message = cipher.decrypt(encrypted_message)
             
             print('Decrypted message:', decrypted_message.decode())
             
             

             
     except BlockingIOError:
         pass  # no client connection yet, keep waiting
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

import socket
import ssl


context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

context.load_verify_locations('server.crt')


# Connect to server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    
    with context.wrap_socket(sock, server_hostname='localhost') as ssock:
        
        ssock.connect(('localhost', 8000))
        
        
        # Receive public key from server
        
        public_key = ssock.recv(1024)
        
        print('Public key received from server.')
        
        while True:
            
            response = ssock.recv(1024).decode()
            
            cipher = PKCS1_OAEP.new(RSA.import_key(public_key))
            
            if 'username' in response.lower():
                
                username = input(response)
            
                encrypted_username = cipher.encrypt(username.encode())

                ssock.send(encrypted_username)
                
            elif 'password' in response.lower():
                
                password = input(response)
                
                encrypted_password = cipher.encrypt(password.encode())
                
                ssock.send(encrypted_password)
                
            else:
                
                print(response)
                
            if response.startswith('Login successful'):
                
                break
            
            elif response.startswith('Error'):
                
                print('Incorrect credentials')

                break
        
        
        # Encrypt message with public key
        
        cipher = PKCS1_OAEP.new(RSA.import_key(public_key))
        
        message = 'Hello, server!'
        
        encrypted_message = cipher.encrypt(message.encode())
        
        
        # Send encrypted message to server
        
        ssock.sendall(encrypted_message)
        
        print('Encrypted message sent to server.')
        
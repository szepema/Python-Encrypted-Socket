import socket
import ssl
import random

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

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
                
        # Determine fuel type and amount
             
        fuel_amount = random.randint(10, 75)
        
        fuel_type = random.randint(1, 4)
        
        type_dict = {
            1:"95 Benzin",
            2:"Diesel",
            3:"Prémium Benzin",
            4:"Prémium Diesel",
        }
        
        fuel_type_str = type_dict.get(fuel_type, "Invalid number")
        
        print('Tankolásnál összesen {} litert tankoltál.'
        ' Üzemanyag típusa: {}'.format(fuel_amount, fuel_type_str)) 
        
        # Encrypting and sending fueling data
        
        amount_bytes = fuel_amount.to_bytes((fuel_amount.bit_length() + 7) // 8, byteorder='big')
        
        encrypted_fuel_amount = cipher.encrypt(amount_bytes)  
        
        ssock.send(encrypted_fuel_amount)
        
        type_bytes = fuel_type.to_bytes((fuel_type.bit_length() + 7) // 8, byteorder='big')  
       
        encrypted_fuel_type = cipher.encrypt(type_bytes)  
        
        ssock.send(encrypted_fuel_type)  
        
        # Receving and decrypting the price

        # fuel_price = ssock.recv(1024)            
        
        # print(fuel_price)
        
        
            
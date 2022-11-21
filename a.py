import rsa

# Use at least 2048 bit keys nowadays, see e.g. https://www.keylength.com/en/4/
publicKey, privateKey = rsa.newkeys(1024) 
A=open("a.txt",'w')
B=open("b.txt",'w')
# Export public key in PKCS#1 format, PEM encoded 
publicKeyPkcs1PEM = publicKey.save_pkcs1().decode()
print(publicKeyPkcs1PEM)
# Export private key in PKCS#1 format, PEM encoded 
privateKeyPkcs1PEM = privateKey.save_pkcs1().decode()
print(privateKeyPkcs1PEM)
A.write(publicKeyPkcs1PEM)
B.write(privateKeyPkcs1PEM)
# Save and load the PEM encoded keys as you like
A.close()
B.close()
C=open("a.txt","r")
D=open("b.txt","r")
# Import public key in PKCS#1 format, PEM encoded 
publicKeyReloaded = rsa.PublicKey.load_pkcs1(C.read().encode()) 
# Import private key in PKCS#1 format, PEM encoded 
privateKeyReloaded = rsa.PrivateKey.load_pkcs1(D.read().encode()) 

plaintext = "hii".encode('utf8')
print("Plaintext: ", plaintext)

ciphertext = rsa.encrypt(plaintext, publicKey)
print("Ciphertext: ", ciphertext)
 
decryptedMessage = rsa.decrypt(ciphertext, privateKeyReloaded)
print("Decrypted message: ", decryptedMessage)

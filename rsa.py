import rsa
import csv
# Use at least 2048 bit keys nowadays, see e.g. https://www.keylength.com/en/4/
publicKey, privateKey = rsa.newkeys(1024) 
#A=open("a.txt",'w')
#B=open("b.txt",'w')
# Export public key in PKCS#1 format, PEM encoded 
publicKeyPkcs1PEM = publicKey.save_pkcs1().decode()
#print(publicKeyPkcs1PEM)
# Export private key in PKCS#1 format, PEM encoded 
privateKeyPkcs1PEM = privateKey.save_pkcs1().decode()
#print(privateKeyPkcs1PEM)
#A.write(publicKeyPkcs1PEM)
#B.write(privateKeyPkcs1PEM)
filename="xyz.csv"
with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([publicKeyPkcs1PEM])
        writer.writerow([privateKeyPkcs1PEM])
# Save and load the PEM encoded keys as you like
#A.close()
#B.close()
#C=open("a.txt","r")
#D=open("b.txt","r")

with open(filename, 'r') as file:
        csvreader = csv.reader(file)
        i=0
        for row in csvreader:
            if i==0:
                x=(row[0])
            if i==1:
                y=row[0]
            i=i+1
#print(x,y)
# Import public key in PKCS#1 format, PEM encoded 
publicKeyReloaded = rsa.PublicKey.load_pkcs1(x.encode()) 
# Import private key in PKCS#1 format, PEM encoded 
privateKeyReloaded = rsa.PrivateKey.load_pkcs1(y.encode()) 
msg="ty wekl"
print("Input:",msg)
plaintext = msg.encode('utf8')
#print("Plaintext: ", plaintext)

ciphertext = rsa.encrypt(plaintext, publicKey)
#print("Ciphertext: ", ciphertext)
 
decryptedMessage = rsa.decrypt(ciphertext, privateKeyReloaded)
print("Decrypted message: ", decryptedMessage.decode("utf-8"))
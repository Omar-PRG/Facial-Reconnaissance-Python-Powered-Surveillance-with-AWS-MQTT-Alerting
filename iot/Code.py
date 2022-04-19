import cv2
import face_recognition
import os
import numpy as np
import time 
import csv
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import sys
import requests

r=requests.get('https://get.geojs.io/')
ip_request=requests.get('https://get.geojs.io/v1/ip.json')
ipAdd=ip_request.json()['ip']
#print(ipAdd)

url='https://get.geojs.io/v1/ip/geo/'+ipAdd+'.json'
geo_request=requests.get(url)
geo_data=geo_request.json()
#print(geo_data)
data=str(geo_data["city"])
long=str(geo_data["longitude"])
lat=str(geo_data["latitude"])
region=str(geo_data["region"])
ip=str(ipAdd)
#Track=ip+'/'+data+'/'+region+'/'+long+'/'+lat
Track=("77.220.30.5/Paris/Ile-de-france/2.2245/49.4585")
print(Track)

topic="testing"
face_cascade=cv2.CascadeClassifier('C:/Users/123/Desktop/iot/data/haarcascade_frontalface_alt2.xml')
myMQTTClient= AWSIoTMQTTClient("DATA")
myMQTTClient.configureEndpoint("a3p29hlyue36he-ats.iot.us-east-1.amazonaws.com",8883)
myMQTTClient.configureCredentials("./AmazonRootCA1.pem  ","./0acacdb93a6a456b284adcff33fa1b92fdfebb4e351bf9d6ef870afb3178b240-private.pem.key" ,"./0acacdb93a6a456b284adcff33fa1b92fdfebb4e351bf9d6ef870afb3178b240-certificate.pem.crt")



#encoding part
#######################
path = 'criminels'
images = []
personNames = []
myList = os.listdir(path)
#print(myList)
for cu_img in myList:
    current_Img = cv2.imread(f'{path}/{cu_img}')
    images.append(current_Img)
    personNames.append(os.path.splitext(cu_img)[0])
#print(personNames)

####saving pictures in a list and noting their name 
n=0;

def faceEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
class Crim:
    crimList=list()
    def __init__(self,crimid,crimnom,crimprenom,naissance,commentaire):
        self.crimid, self.crimnom,self.crimprenom,self.naissance,self.commentaire=crimid,crimnom,crimprenom,naissance,commentaire
    def addnewcrim(self):
        Crim.crimList.append(self)
    def getcrimList(self):
        return Crim.crimList
    def getcriminfo(self,crimnom):
        for a in Crim.crimList:
            if(a.getcrimnom() == crimnom):
                return a
        return False
    def updatecriminfo(self,crimid,crimnom,crimprenom,naissance,commentaire):
        for x in Crim.crimList:
            if(x.crimnom==crimnom):
                x.id,x.crimnom,x.crimprenom,x.naissance,x.commentaire=crimid,crimnom,crimprenom,naissance,commentaire
                return True
        return False
    def removecrim(self,crimnom):
        for x in Crim.crimList:
            if(x.crimnom == crimnom):
                Crim.crimList.remove(x)
                return True
        return False
    def setcrimid(self,crimid):
        self.crimid = crimid
    def setcrimnom(self,crimnom):
        self.crimnom = crimnom
    def setcrimprenom(self,crimprenom):
        self.crimprenom = crimprenom
    def setnaissance(self,naissance):
        self.naissance=naissance
    def setcommentaire(self,commentaire):
        self.commentaire = commentaire
    def getcrimid(self):
        return self.crimid
    def getcrimnom(self):
        return self.crimnom
    def getcrimprenom(self):
        return self.crimprenom
    def getnaissance(self):
        return self.naissance
    def getcommentaire(self):
        return self.commentaire
    def __str__(self):
        return "%d %s %s %s %s"%(self.crimid, self.crimnom,self.crimprenom,self.naissance,self.commentaire)

uncrim = Crim(0,"","","","")

with open('Database.txt','r',newline='\n') as csv_file:
    csv_reader=csv.reader(csv_file,delimiter=' ')
   
    for line in csv_reader:
        
        if not line[0]:
            break
        crimid=int(line[0])
        crimnom=line[1]
        crimprenom=line[2]
        naissance=int(line[3])
        commentaire=line[4]
        crimo =Crim(crimid,crimnom,crimprenom,naissance,commentaire)
        crimo.addnewcrim()
        #print(crimo)
'''
for crimo in uncrim.getcrimList():
    print(crimo) 
'''
print("Scanning test Started, Please press 'esc' to open UserMode or 'Space' to add a criminel")

cam = cv2.VideoCapture(0)
cv2.namedWindow("test")
encodeListKnown = faceEncodings(images)
print('All Encodings Complete!!!')
while True:
   ret, frame = cam.read()
   faces = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
   faces = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)

   facesCurrentFrame = face_recognition.face_locations(faces)
   encodesCurrentFrame = face_recognition.face_encodings(faces, facesCurrentFrame)
   facesCurrentFrame = face_recognition.face_locations(faces)
   encodesCurrentFrame = face_recognition.face_encodings(faces, facesCurrentFrame)

   for encodeFace, faceLoc in zip(encodesCurrentFrame, facesCurrentFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print(faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            n=1
            name = personNames[matchIndex].lower()
            print("The guy is a criminel")
            #print(name)
            x= uncrim.getcriminfo(name)
            print(x)
            print(Track)
            msg=str(x)+Track
            myMQTTClient.connect(keepAliveIntervalSecond=600)
            myMQTTClient.publish(topic,msg,0)
            myMQTTClient.disconnect() 
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            continue
        
   cv2.imshow("test", frame)
   k = cv2.waitKey(1)
   if k%256 == 27: 
       print("(1) Press 1 to print images list")
       print("(2) Press 2 to print criminels list")
       print("(3) Press 3 to Remove a criminel from the list")
       print("(4) Press 4 to search for a criminel")
       print("(5) Press 5 to edit a criminels information")
       print("(6) Press 6 to come back to scanning mode")
       print("(7) Press 7 to close the program")
      
       
       Choicee=int(input("Please choose one of the options : "))
       
       if Choicee==1:
           print("(1) Press 1 to print images list")
           myList = os.listdir(path)
           print(myList)
           continue
       elif Choicee==2:
           print("Press 2 to print criminels list")
           for crimo in uncrim.getcrimList():
               print(crimo) 
           continue
           
       elif (Choicee==3):
           print("(1) Press 3 to delete a criminel")
           answer=input("Do you want to Free a criminel from a list? Y/N")
           if (answer =='Y' or answer =='y'):
               crr=input('enter the criminel name')
               cr= uncrim.getcriminfo(crr)
               if (cr==False):
                   print('Criminel not found')
               else:
                   #print(cr)
                   uncrim.removecrim(crr)
                   PATH='C:/Users/123/Desktop/iot/criminels'
                   z='.png'
                   crr+=z
                   os.remove( PATH + '/' + crr)
                   path = 'criminels'
                   images = []
                   personNames = []
                   myList = os.listdir(path)
                   print(myList)
                   for cu_img in myList:
                       current_Img = cv2.imread(f'{path}/{cu_img}')
                       images.append(current_Img)
                       personNames.append(os.path.splitext(cu_img)[0])
                   print(personNames)
                   encodeListKnown = faceEncodings(images)
                   print('All Encodings updated!!!') 
                   with open('Database.txt','w') as f:
                       writer=csv.writer(f)
                       for x in Crim.crimList:
                          writer.writerow([x])
                          print(x)
               continue
      
       elif Choicee==4:
            answer=input("Are you Looking for a crim? Y/N")
            if (answer =='Y' or answer =='y'):
                crimn=input('enter the criminel name')
                cri= uncrim.getcriminfo(crimn)
                if (cri==False):
                    print('Criminel not found')
                else:
                    print(cri)
                    pass
            
            else: 
                print('Quit')
            continue
       elif Choicee==5:
            
            print("Your pressed 6")
            answer=input("Do you want to update a criminel info? Y/N")
            if (answer =='Y' or answer =='y'):
                crimn=input('enter the criminel name')
                cri= uncrim.getcriminfo(crimn)
                if (cri==False):
                    print('Criminel not found')
                else:
                    print(cri)
                    crimid=int(input("Please write the new criminel id"))
                    crimnom=crimn
                    crimprenom=input("please write the new criminel surname")
                    naissance=input("please write the criminel birth date")
                    commentaire=input("Give some comments")
                    crc=uncrim.updatecriminfo(crimid,crimnom,crimprenom,naissance,commentaire)
                    if(crc==False):
                        print("\n Update failed. Unable to find ",crimnom)
                    else:
                        print("Successfully updated")
                        print(crc)
                    with open('Database.txt','w') as f:
                           writer=csv.writer(f)
                           for x in Crim.crimList:
                              writer.writerow([x])
                              print(x)
            continue
       elif Choicee==6:
            print("Coming Back to scanning mode")
            continue
       elif Choicee==7:
            cam.release()
            cv2.destroyAllWindows()
            break
       else:
            print("You didn't enter a valid choice please try again")
            continue
      
   elif k%256==32:
           
        x=input("Please enter a name : ")
        z='.png'
        img_name=x+z
        path='C:/Users/123/Desktop/iot/criminels'
        cv2.imwrite(os.path.join(path,img_name), frame)
        print("{} written!".format(img_name))
        
        #uncrim = Crim(0,"","","","")
        crimid=int(input("veuillez saisir l'id du criminel"))
        crimnom=x
        crimprenom=input("veuillez saisir le prenom du criminel")
        naissance=input("veuillez saisir sa date de naissance")
        commentaire=input("veuillez saisir des commentaires sur son dossier")
        crimo = Crim(crimid,crimnom,crimprenom,naissance,commentaire)
        crimo.addnewcrim()
        path = 'criminels'
        images = []
        personNames = []
        myList = os.listdir(path)
        print(myList)
        for cu_img in myList:
            current_Img = cv2.imread(f'{path}/{cu_img}')
            images.append(current_Img)
            personNames.append(os.path.splitext(cu_img)[0])
        print(personNames)
        encodeListKnown = faceEncodings(images)
        print('All Encodings updated!!!') 
        #for crimo in uncrim.getcrimList():
            #print(crimo) 
        with open('Database.txt','w') as f:
            writer=csv.writer(f)
            for x in Crim.crimList:
               writer.writerow([x])
               print(x)
        continue
      
     
    

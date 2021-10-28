import glob, os, AESstuff, MP3stuff 
os.chdir("FTP/")
files = sorted(glob.glob("*.enc"))
count=0
for file in  files :
    os.chdir("..")
    parameters=file.split("_")  
    AESstuff.decryptFile("FTP/"+file,"password")
    os.chdir("FTP/")
    if parameters[2]=="acc":
        acc=MP3stuff.decompress("output.mp3","values.txt")*float(parameters[3])
    elif parameters[2]=="axes":
        axes=MP3stuff.decompress("output.mp3","values.txt")*float(parameters[3])
    elif parameters[2]=="gyro":
        gyro=MP3stuff.decompress("output.mp3","values.txt")*float(parameters[3])
    count+=1
    if count%3==0:
        import csv

        with open(parameters[0]+"_"+parameters[1]+'.csv', 'w') as csvfile:
            fieldnames = ['pitch', 'roll','yaw','Ax','Ay','Az','Gx','Gy','Gz']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            numValues=int(len(acc)/3)
            for i in range(numValues):
                writer.writerow({'pitch':axes[i], 'roll':axes[i+numValues],'yaw':axes[i+2*numValues],'Ax': acc[i],'Ay':acc[i+numValues],'Az':acc[i+2*numValues],'Gx': gyro[i],'Gy':gyro[i+numValues],'Gz':gyro[i+2*numValues]})



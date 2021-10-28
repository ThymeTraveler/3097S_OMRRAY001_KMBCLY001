import ftplib
import getpass

def send(inputFile):
   # password = getpass.getpass('FTP Password:')
    session = ftplib.FTP('192.168.0.200','rayhaan2120@gmail.com',"password")
    file = open(inputFile,'rb')                  # file to send
    session.storbinary('STOR '+inputFile, file)     # send the file
    file.close()                                    # close file and FTP
    session.quit()
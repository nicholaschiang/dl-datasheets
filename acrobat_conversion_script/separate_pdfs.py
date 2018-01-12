import os
import shutil

source = "C:/Users/Administrator/Desktop/op_amp_pdf"

for path,dirlist,filelist in os.walk(source):
    num = len(filelist)/100
    for i in range(num):
	foldername = source+"/folder"+str(i)
	if not os.path.exists(foldername):
	    os.makedirs(foldername)
	for j in range(i*100,(i+1)*100):
	    shutil.move(source+"/"+filelist[j],foldername)

    #move remainder
    foldername = source+"/folder"+str(num)
    if not os.path.exists(foldername):
    	os.makedirs(foldername)
    for j in range(num*100,len(filelist)):
	shutil.move(source+"/"+filelist[j],foldername)
     
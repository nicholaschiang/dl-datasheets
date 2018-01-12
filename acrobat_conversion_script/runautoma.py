from automa.api import *
import time

#if Acrobat is already open
#switch_to("Adobe Acrobat Pro DC")

i = 0
while i < 25: #Replace with number of folders
    try:
    	#open Acrobat
    	acrobat = start("C:\Program Files (x86)\Adobe\Acrobat 2015\Acrobat\Acrobat.exe")
    	click("View","Tools","Action Wizard","Open")
    	click("sanitize-to-html")

    	centerval = Window("Adobe Acrobat Pro DC").center

    	#first save
    	click(Point(400+centerval.x,centerval.y-50),"Save to Local Folder")
    	write("sanitized_pdf", into="Folder:")
    	press(ENTER)

    	#second save
    	click(Point(400+centerval.x,centerval.y-20),"Save to Local Folder")
    	write("html", into="Folder:")
    	press(ENTER)

    	#Add Folder
    	click(Point(400+centerval.x,centerval.y-230))    
    	write("folder"+str(i), into="Folder:")
    	press(ENTER)

    	#Press Start
    	click(Point(400+centerval.x,centerval.y-110))

    except Exception as e:
	    print i, ":", str(e)

    print "Entering sleep loop"
    while True:
	    time.sleep(120) #check every two minutes

	    try:
    	    popup = find_all(Button("OK"))
    	    if len(popup) > 0:
	    	click(Button("OK"))
	    except:
	        pass
	
	    try:	
	        completed_button = find_all(Image("C:\Users\Administrator\Desktop\completed_button.png"))
      	    if len(completed_button) > 0:
	    	break
	    except:
	        pass

    print "Finished",i
    kill(acrobat)
    i += 1

To make this module work it is necessary to create a file called "user.ini" in the folder "model2xml".
This file must have as content the lines between "---------":

---------------------------------------------------------------
[URL]
url = http://landportal.info/receiver
[USER]
login = XXXXX
api_key = YYYYYYYYYYYY
---------------------------------------------------------------


You must substitute "XXX" by your user login in ckan, and "YYY" by your own api_key associated to that user.
The url used in the example could change, but it is suppoused to be valid.
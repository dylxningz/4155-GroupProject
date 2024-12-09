ITIS-4155 Team 7

NinerBuys - Dylan, Henry, Somot, Jack

A web application developed in python and flask library. 
We aim to create a safe second hand selling platorm for UNCC. 

Youtube video for troubleshooting if you cannot get it to work!!!
https://youtu.be/_2148i91dNo


To run our website complete the following task

On windows computer 
Install Visual Studio Code and make sure in the extensions within visual studio code to install Python

https://code.visualstudio.com/download

Download the python library and install
IMPORTANT!!! Make sure you check the box near the bottom that sets python as a PATH
https://www.python.org/downloads/

Download the Zipped repo and unzip it somewhere on your pc as you will access this with visual studio code.
https://github.com/dylxningz/4155-GroupProject

Once in the terminal within Visual studio code after python has been downloaded and installed please run these commands 

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

Then if all is successful run the final command 

python app.py

After these steps you should see in the terminal the website configuration being set and the database being loaded.

To access the website go to your browser and go to 

localhost:5000

To access the FastAPI routes to just see what we used go to 

localhost:8000/docs


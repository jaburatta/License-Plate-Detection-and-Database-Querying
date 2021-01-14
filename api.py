from fastapi import FastAPI, File, UploadFile
import uvicorn
import requests
import json
import re
import os
import mysql.connector
import pandas as pd

user_name = os.environ.get('DB_USER')
password = os.environ.get('DB_PASS')

connection = mysql.connector.connect(
    host = 'localhost', 
    user = user_name,
    passwd = password,
    db = 'registration'
)

app = FastAPI()

def user_data(data):
    '''
    This function takes in input variable or value and
    returns the corresponding data from the db
    
    cur.description was also needed to get the columns for the dataframe
    '''

    cur = connection.cursor()
    try:
        cur.execute("SELECT * FROM registration WHERE Plate_number = %s", (data,))
        res = cur.fetchall()
        if res:
            data = pd.DataFrame(data = res, columns=[x[0] for x in cur.description])
            return data
        else:
            return ('No Record Found')
    except Exception:
        print('Exception Found')

@app.get('/')
async def index():
    return{'Run your License Plate'}

@app.post('/user')

async def Run_Plate(file: UploadFile = File(...)):

    
    img_path = file

    url = 'https://handwriting-extraction.herokuapp.com/predict handwriting local images'

    image_file_descriptor = open(img_path, 'rb')
    # Requests makes it simple to upload Multipart-encoded files
    header={'content_type':'multipart/form-data', 'accept': 'application/json'}
    files = {'Image': image_file_descriptor}

    s= requests.post(url, files=files)
    try:
        data = s.json()    
        print(data, '\n')                
    except requests.exceptions.RequestException:
        print(s.status_code, '\n')
        
    print(s)
    image_file_descriptor.close()

    h = ' '.join(data)

    # This works for the standard nigeria plates 
    l = re.search(r'[a-zA-Z]+[-. ]*[0-9]+[- ]*[a-zA-Z]+', h)

    # This works for both standard and customized plates only if value read is the license plate value
    # l = re.search(r'[-a-zA-Z0-9: ]*', h)
    dt = l.group()

    unwanted = ['-', '.', ' ']
    for i in unwanted:
        dt = dt.replace(i, '')
    print(dt)        

    result = user_data(dt)

    return {'result': result}
    



if __name__ == '__main__':
    uvicorn.run(app, host = '127.0.0.1', port = 8000)

#uvicorn api:app --reload
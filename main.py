from api import apikey
from flask import Flask, request, jsonify
import pandas as pd
from csv import writer

import os
import time
from openai import OpenAI
import json
import jsonpickle
from langchain.document_loaders import PyPDFLoader
# from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
apikeys = apikey

app = Flask(__name__)
client = OpenAI(api_key=apikeys)

############## GPT PROMPT ####################
def gpt(inp,prompt):
    
    systems = {"role":"system","content":"""
    You are an AI Visa consultation Agent for USA and CANADA.
               you're main job is Eligibility Checking and Recommendation:
    your job is to ask all questions from user that is needed for job application for USA and CANADA.
               first confirm the Country they want to travel.
               then after complete assesment you have to tell them if they've all the required stuff and they are Eligible for the VISA or not.
               ask question one by one and give the options as well. 
               IMPORTNAT: Keep your answers short and ask only one question at a time
"""}
    new_inp = inp
    new_inp.insert(0,systems)
    print("inp : \n ",new_inp)
#    openai.api_key = apikeys
    print('&&&&&&&&&&&&^^^^^^^^^^^^%$######################$%^&*((((((((((((((()))))))))))))))')
    completion = client.chat.completions.create(
    model="gpt-4o", 
    messages=new_inp
    )
    return completion.choices[0].message.content

############    GET CHATS BY USER ID ##################
def get_chats(id):
    path = id
    isexist = os.path.exists(path)
    if isexist:
        data = pd.read_json(path)
        chats = data.chat
        return  list(chats)
    else:
        return "No Chat found on this User ID."





############### APPEND NEW CHAT TO USER ID JSON FILE #################
def write_chat(new_data, id):
    with open(id,'r+') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["chat"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)



################################ CHECK IF USER IS ALREADY EXIST IF NOT CREATE ONE ELSE RETURN GPT REPLY ##################
@app.route('/api', methods=['POST'])
def check_user():
    
    ids = request.json['user_id']
    prompt = request.json['prompt']
    # status = request.json['status']
    print("asd")
    path = str(os.getcwd())+'//chats//'+ids+'.json'
    # path = str(os.getcwd())+'\\'+"5467484.json"
    isexist = os.path.exists(path)
    if isexist:
        # try:
        print(path," found!")
        write_chat({"role":"user","content":prompt},path)
        # print()
        chats = get_chats(path)
        print(chats)
        send = gpt(chats,prompt)
        reply = send
        print("reply    ",reply)
        write_chat({"role":"assistant","content":reply},path)
        return {"message":reply,"status":"OK"}
        # except:
        #     return {"message":"something went wrong!","status":"404"}

    else:
        print(path," Not found!")
        dictionary = {
        "user_id":ids,
        "chat":[]


        }
        
        # Serializing json
        json_object = json.dumps(dictionary, indent=4)
        
        # Writing to sample.json
        with open(path, "w") as outfile:
            outfile.write(json_object)
        reply = check_user()
        return reply

####################   NEW ENPOINT GET CHAT ##############################
@app.route('/get_chats', methods=['POST'])
def get_chatss():
    ids = request.json['user_id']
    return jsonpickle.encode(get_chats(ids))





if __name__ == '__main__':
    app.run(port=5002,host='0.0.0.0')
    

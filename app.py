from flask import Flask, render_template, request,redirect, url_for, jsonify, Response
import subprocess
import numpy as np
import cv2
import os
import uuid
import json
import requests

app = Flask(__name__)
camera=cv2.VideoCapture(0)

def generate_frames():
    while True:
            
        ## read the camera frame
        success,frame=camera.read()
        if not success:
            break
        else:
            #ret,buffer=cv2.imencode('.jpg',frame)
            #frame=buffer.tobytes()
            detector = cv2.CascadeClassifier('Haarcascades/haarcascade_frontalface_default.xml')
            eye_cascade = cv2.CascadeClassifier('Haarcascades/haarcascade_eye.xml')
            faces = detector.detectMultiScale(frame, 1.1, 7)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Draw the rectangle around each face
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = frame[y:y + h, x:x + w]
                eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')




@app.route('/', methods=['GET', 'POST'])
def ajax():
    return render_template("inde.html")

@app.route("/output", methods=['GET','POST'])
def output():
    cmd = request.json['user_input']
    if("logins" in  cmd):
        return render_template("mymenu.html", data= subprocess.getoutput("az login"))
    elif("Virtual Machine help" in cmd):
        return render_template("mymenu.html", data=subprocess.getoutput("az vm --help"))
    elif("machine learning help" in cmd):
        return render_template("mymenu.html",data=subprocess.getoutput("az ml --help"))
    elif("Face" in cmd):
	    return render_template("index.html")
    elif("Translate" in cmd):
        return render_template("Translator.html")
    elif("create a resource group" in  cmd):
        return render_template("mymenu.html", data=subprocess.getoutput("az group create -l eastus -n MyResourceGroup"))
    elif("create a virtual machine" in cmd):
        return render_template("mymenu.html", data=subprocess.getoutput("az vm create \
    --resource-group myResourceGroup \
    --name myVM \
    --image UbuntuLTS \
    --admin-username azureuser"))
    else:
        return render_template("mymenu.html", data=subprocess.getoutput(cmd))


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/update_decimal', methods=['POST'])
def updatedecimal():
    random_decimal = np.random.rand()
    return jsonify('', render_template('random_decimal_model.html', x=random_decimal))


@app.route("/menu", methods=["GET"])
def myform():
    name = request.args.get("x")
    if(("start computer" in name) or (name == "start instance") or (name == "launce instance") or (name == "create instance")):
        subprocess.getoutput("az login")
        return render_template("test.html")
    else:
        cmd = "wrong command"
    return render_template("mymenu.html", myname=cmd, cname="IIEC")

@app.route('/test', methods = ["GET"])
def myMenu():
    return render_template("Assistant.html")

@app.route("/yourVM", methods=["GET"])
def myVM():
    cmd = request.args.get("OS_name")
    if(("group" in cmd) or ("resource group name" in cmd) or ("group name" in cmd) or ("Resource name" in cmd) or ("resource group name" in cmd)):
        operation = " az vm create - n " + cmd
        print(operation)
        return render_template("mymenu.html",myOPS = operation)

@app.route('/Translate', methods=['GET'])
def index():
    return render_template('Translator.html')


@app.route('/Translate', methods=['POST'])
def index_post():
    # Read the values from the form
    original_text = request.form['text']
    target_language = request.form['language']

    # Load the values from .env
    key = "07c23a6fc8d9465594e7832b31e4688f"
    endpoint = "https://api.cognitive.microsofttranslator.com"
    location = "eastus2"

    # Indicate that we want to translate and the API
    # version (3.0) and the target language
    path = '/translate?api-version=3.0'

    # Add the target language parameter
    target_language_parameter = '&to=' + target_language

    # Create the full URL
    constructed_url = endpoint + path + target_language_parameter

    # Set up the header information, which includes our
    # subscription key
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # Create the body of the request with the text to be
    # translated
    body = [{'text': original_text}]

    # Make the call using post
    translator_request = requests.post(
        constructed_url, headers=headers, json=body)

    # Retrieve the JSON response
    translator_response = translator_request.json()

    # Retrieve the translation
    translated_text = translator_response[0]['translations'][0]['text']

    # Call render template, passing the translated text,
    # original text, and target language to the template
    return render_template(
        'results.html',
        translated_text=translated_text,
        original_text=original_text,
        target_language=target_language
    )


if __name__ == '__main__':
    app.run(debug = True)

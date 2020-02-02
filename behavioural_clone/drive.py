import base64
import numpy as np
from io import BytesIO
import socketio
import eventlet
from flask import Flask
from keras.models import load_model
from PIL import Image
import cv2

sio = socketio.Server()

app = Flask(__name__) # '__main__'
speed_limit = 30

@sio.on('telemetry')
def telemetry(sid, data):
    speed = float(data['speed'])
    image = Image.open(BytesIO(base64.b64decode(data['image'])))
    image = np.asarray(image)
    image = img_preprocess(image)
    image = np.array([image])
    steering_angle = float(model.predict(image))
    throttle = 1.0 - speed/speed_limit
    print('{} --> throttle : {} --> speed : {}'.format(steering_angle, throttle, speed))
    send_control(steering_angle, throttle)

@sio.on('connect')
def connect(sid, environ):
    print('Connected')
    send_control(0, 1)

def send_control(steering_angle, throttle):
    sio.emit('steer', data = {
        'steering_angle': steering_angle.__str__(),
        'throttle': throttle.__str__()
    })

def img_preprocess(img):
  img = img[60:135, :, :  ] # Height (To Be Edited), Width, Channel_Index
  img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV) # YUV =>  Luminance (Y), blue–luminance (U), red–luminance (V) || (SECAM and PAL color spaces)
  img = cv2.GaussianBlur(img,(3,3), 0) # Applies Gaussian Kernal Convolution On the image which help smoothens the image 
  img = cv2.resize(img, (200, 66))
  img = img / 255
  return img

if __name__ == '__main__':
    model = load_model('new_model.h5')
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)

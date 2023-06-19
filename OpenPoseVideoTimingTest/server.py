from base64 import decode
import os
from flask import Flask, request
from PIL import Image
from base64 import b64decode, b64encode
from waitress import serve
from controlnet_aux import OpenposeDetector
from flask_socketio import SocketIO
import random
import cv2
import numpy as np

# Run pip install flask_socketIO
app = Flask(__name__)
socketio = SocketIO(app)

class ProgressHandler():
    
    def __init__(self, maxFrames):
        self.frames_processed = 0
        self.NUM_FRAMES = maxFrames
        self.socketpath = "progress"
    
    def getPercent(self):
        return self.frames_processed / self.NUM_FRAMES
    
    def updateProgress(self):
        '''
            Increases frame count by one and updates socket accordingly
        '''
        self.prev_percent = self.getPercent()
        self.frames_processed += 1
        if (self.getPercent() * 10 // 1 != self.prev_percent * 10 // 1):
            socketio.emit(self.socketpath, self.getPercent())
        
        

def applyPoseDetection(filepath, content, extension):
    unprocessed_image = Image.open(filepath, "r")
    
    #TODO: Take image, apply OpenPose algorithm, save image locally, and return image filepath

    model = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")
    processed_image = model(unprocessed_image)
    processed_filepath = f"processed_image_{content}.{extension}"
    processed_image.save(processed_filepath)
    return processed_filepath

@app.route("/video", methods = ['POST'])
def processVideo():
    '''
        Data passed in this format:
        {
            "b64_encoded_video": Base64 Encoded Image
            "extension": extension of video e.g. .mp4
        }
    '''
    print("reached")
    data = request.get_json()
    encoded_video = data["b64_encoded_video"]
    extension = data["extension"]
    model = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")
    video_data = b64decode(encoded_video)
    inputPath = f"input.{extension}"
    with open(inputPath, "wb") as file:
        file.write(video_data)

    input_video = cv2.VideoCapture(inputPath)
    width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    codec = int(input_video.get(cv2.CAP_PROP_FOURCC))
    fps = input_video.get(cv2.CAP_PROP_FPS) 
    num_frames = int(input_video.get(cv2.CAP_PROP_FRAME_COUNT))
        
    output_file_path = f"transformed_output.{extension}"
    video_writer = cv2.VideoWriter(output_file_path, codec, fps, (width, height))
    progress = ProgressHandler(num_frames)
    while input_video.isOpened():
        res, frame = input_video.read()
        if not res:
            break
        image = Image.fromarray(frame)

        transformed = model(image)
        resized_transformed = transformed.resize((width, height))
        transformed_array = np.array(resized_transformed)

        video_writer.write(transformed_array)
        progress.updateProgress()
    
    video_writer.release()
    input_video.release()

    with open(output_file_path, 'rb') as file:
        transformed_data = file.read()
    
    encoded_transformed = b64encode(transformed_data).decode('utf-8')
    try:
        os.remove(inputPath)
        os.remove(output_file_path)
    except FileNotFoundError as e:
        print(e.strerror)
    return encoded_transformed



@app.route("/image", methods = ['POST'])
def processImage():
    '''
        Data passed in this format:
        {
            "b64_encoded_image": Base64 Encoded Image
            "extension": Supports jpg, png, and jpeg
        }
    '''
    data = request.get_json()
    encoded_image = data["b64_encoded_image"]
    extension = data["extension"]
    
    #Content => {"b64_encoded_image": encoded string, "extension": file extension type (string)}
    seven_digits = str(random.randint(1000000, 9999999))
    unprocessed_image_filepath = f"unprocessed_image_{seven_digits}.{extension}"
    unprocessed_image = open(unprocessed_image_filepath, "wb")
    decoded = b64decode(encoded_image)
    unprocessed_image.write(decoded)
    unprocessed_image.close()
    
    processed_image_filepath = applyPoseDetection(unprocessed_image_filepath, seven_digits, extension)
    
    processed_image = open(processed_image_filepath, "rb")
    processed_image_base64 = b64encode(processed_image.read())
    processed_image.close()

    try:
        os.remove(unprocessed_image_filepath)
        os.remove(processed_image_filepath)
    except FileNotFoundError as e:
        print(e.strerror)
    return processed_image_base64
        
        
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=14366)
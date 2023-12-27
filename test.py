import io
import sys
import math
from flask import Flask
from flask import send_file
from PIL import Image, ImageDraw, ImageFont

debug = False
#####
# Hosted at theoneandonly2.pythonanywhere.com
#####

GifHeight = 125
GifWidth = 200
FontSize = 50
SmallFont = FontSize / 3

TimeFont = {}
TextFont = {}
RoundFont = {}
TimeSize = ()
WorkoutSize = ()
RestSize = ()
RoundSize = ()
RestColor = (204,0,0)
WorkoutColor = (42,128,0)
TimeColor = (0,0,0)
RoundColor = (0,0,0)

def createImage(wordText, timeText, active, round):

    img = Image.new('RGB', (GifWidth, GifHeight), (255,255,255))
    draw = ImageDraw.Draw(img)

    # Draw the instructions string
    if active:
        draw.text((GifWidth/2 - WorkoutSize[0]/2, GifHeight/2 - WorkoutSize[1]+5), wordText, WorkoutColor, font=TextFont)
    else:
        draw.text((GifWidth/2 - RestSize[0]/2, GifHeight/2 - RestSize[1]+5), wordText, RestColor, font=TextFont)

    if round > 0:
        draw.text((GifWidth - RoundSize[0] - 5, 5), "Round " + str(round), RoundColor, font=RoundFont)

    # Draw the time string
    draw.text((GifWidth/2 - TimeSize[0]/2, GifHeight/2 + 15), timeText, TimeColor, font=TimeFont)

    return img

def generateFrames(instructions, seconds, active, round, countDown):
    frames = []

    if countDown:
        originalSeconds = seconds
        minutes = math.floor(seconds / 60)
        seconds = seconds % 60

        for i in range(originalSeconds+1):
            frames.append(createImage(instructions, str(minutes).zfill(2)+":"+str(seconds).zfill(2), active, round))

            if (seconds == 0) and (minutes == 0):
                break
            elif seconds == 0:
                minutes -= 1
                seconds = 59
            else:
                seconds -= 1    
    else:
        originalSeconds = seconds
        minutes = 0
        seconds = 0

        for i in range(originalSeconds + 1):
            frames.append(createImage(instructions, str(minutes).zfill(2)+":"+str(seconds).zfill(2), active, round))

            if seconds == 59:
                minutes += 1
                seconds = 0
            else:
                seconds += 1

    return frames

def createGif(workoutSeconds, restSeconds, setCount, countDown=True):

    global TimeFont
    global TimeSize
    global TextFont
    global WorkoutSize
    global RestSize
    global RoundFont
    global RoundSize

    #    TimeFont = ImageFont.truetype(".\\fonts\\Digital dream Fat Narrow.ttf", FontSize)
    TimeFont = ImageFont.truetype("./fonts/CollegiateBlackFLF.ttf", FontSize)
    TimeSize = TimeFont.getsize("00:00")
    #    TextFont = ImageFont.truetype(".\\fonts\\Bohemian typewriter.ttf", FontSize)
    TextFont = ImageFont.truetype("./fonts/CollegiateBlackFLF.ttf", FontSize)
    RoundFont = ImageFont.truetype("./fonts/CollegiateBlackFLF.ttf", int(SmallFont))

    RoundSize = RoundFont.getsize("Round 0")
    WorkoutSize = TextFont.getsize("Go!")
    RestSize = TextFont.getsize("Rest")

    frames = []

    if setCount > 1:
        for i in range(setCount):
            frames += generateFrames("Go!", workoutSeconds, True, i+1)
            frames += generateFrames("Rest", restSeconds, False, i+1)
    else:
        frames += generateFrames("Go!", workoutSeconds, True, 0, countDown)


    fileBytes = io.BytesIO()

    #writer = io.BufferedWriter(fileBytes)

    frames[0].save(fileBytes, format='GIF', append_images=frames[1:], save_all=True, duration=1000)

    fileBytes.seek(0)

    return fileBytes

app = Flask(__name__)

@app.route('/')
def index():
        return "Hello, World!"

@app.route('/timer/interval/<int:work>/<int:rest>/<int:rounds>')
def getIntervalTimer(work, rest, rounds):
    fileIO = createGif(work, rest, rounds)

    fileBytes = fileIO.read()

    response = app.make_response(fileBytes)
    response.headers.set('Content-Length', len(fileBytes))
    response.headers.set('Cache-Control', 'public, max-age=31536000')
    response.headers.set('Content-Type', 'image/gif')

    return response

@app.route('/timer/countdown/<int:work>')
def getCountdownTimer(work):
    fileIO = createGif(work, 0, 0)

    fileBytes = fileIO.read()

    response = app.make_response(fileBytes)
    response.headers.set('Content-Length', len(fileBytes))
    response.headers.set('Cache-Control', 'public, max-age=31536000')
    response.headers.set('Content-Type', 'image/gif')

    return response    

@app.route('/timer/countup/<int:work>')
def getCountupTimer(work):
    fileIO = createGif(work, 0, 0, False)

    fileBytes = fileIO.read()

    response = app.make_response(fileBytes)
    response.headers.set('Content-Length', len(fileBytes))
    response.headers.set('Cache-Control', 'public, max-age=31536000')
    response.headers.set('Content-Type', 'image/gif')

    return response    

if __name__ == "__main__":
    
    if debug:
        fileName = sys.argv[1]
        print(fileName)
        fileBytes = createGif(10, 0, 0, False)

        f = open(fileName, 'w+b')
        f.write(bytearray(fileBytes.read()))
        f.close()
    else:
        app.run()

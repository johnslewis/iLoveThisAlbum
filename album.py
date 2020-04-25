from PIL import Image
from flask import send_file
from flask import Flask
from flask import request, render_template, Response
from io import StringIO
from io import BytesIO
import json

import requests
app = Flask(__name__)



@app.route('/')
def index():
  return render_template("home.html")


@app.route('/get_image')
def get_image(methods=['GET']):
  artist = request.args.get('artist', default = "", type = str)
  album = request.args.get('album', default = "", type = str)

  background = Image.open("scene.png")
  url = getAlbum(artist, album)
  if url == -1:
    urlImage = "notFoundText.png"
    album = Image.open(urlImage).convert('RGBA')
  else:
    urlImage = requests.get(url)
    album = Image.open(BytesIO(urlImage.content)).convert('RGBA')
  
  album = album.rotate(20, expand = True)
  background.paste(album, (400, 250), album)

  return serve_pil_image(background)

# return image without actually saving, https://stackoverflow.com/questions/7877282/how-to-send-image-generated-by-pil-to-browser
# https://www.pythonanywhere.com/forums/topic/13570/ pythonanywhere doesnt like send file
def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img = pil_img = pil_img.convert("RGB")
    pil_img.save(img_io, 'JPEG', quality=100)
    img_io.seek(0)
    return Response(img_io, mimetype='image/jpeg', direct_passthrough=True)
    # return send_file(img_io, mimetype='image/jpeg')

def getAlbum(artist, album):

  api_key = ""
  with open('settings.json') as json_file:
    data = json.load(json_file)

    api_key = data["apiKey"]




  print(api_key)
  headers = {
      # 'user-agent': ""
  }

  payload = {
      'api_key': api_key,
      'method': 'album.getinfo',
      'format': 'json',
      'artist': artist,
      'album': album

  }

  r = requests.get('http://ws.audioscrobbler.com/2.0/', headers=headers, params=payload)
  r.status_code
  rJson = r.json()



  if r.status_code == 200:
    print(json.dumps(rJson, sort_keys=True, indent=4))
    if("error" in rJson):
      return -1
    for x in range(0, len(rJson["album"]["image"])):
      if rJson["album"]["image"][x]["size"] == "mega":
        if rJson["album"]["image"][x]["#text"] != "":
          return rJson["album"]["image"][x]["#text"]

  return -1






if __name__ == "__main__":
  app.run(host='0.0.0.0')
  #app.run(debug=True)




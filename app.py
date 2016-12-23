from PIL import Image, ImageChops, ImageEnhance
import requests
import os
from flask import Flask, redirect, jsonify, render_template, request, send_file
import werkzeug
import datetime
import uuid

app = Flask(__name__)

ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def process_image(img):
  #open up the mask
  mask = Image.open('mask.png')
  mask = mask.convert('RGBA')
  mask = mask.resize(img.size)

  img.paste(mask, (0,0), mask)
  newdata = img.getdata()

  '''

  #make sure it matches the size of the image
  mask = mask.resize(img.size)
  #enhance it by raising its saturation
  #converter = ImageEnhance.Color(mask)
  #mask = converter.enhance(2.0)
  #get mutable data
  mdata = mask.getdata()
  #make sure our image has alpha channel
  img = img.convert('RGBA')
  #dummy convert does nothing but available for saturation tweaking
  converter = ImageEnhance.Color(img)
  img = converter.enhance(1.0)
  #get mutable data
  idata = img.getdata()

  #create output data
  newdata = []
  #loop through our mask and image pixels
  for iitem, mitem in zip(idata, mdata):
    #ratio of each pixel is 1:2 (image:mask)
    #tweak this for different colorings
    r1 = iitem[0]
    r2 = mitem[0]
    g1 = iitem[1]
    g2 = mitem[1]
    b1 = iitem[2]
    b2 = mitem[2]

    #mm = 2.0
    #the higher b, the higher the brightness
    #b = .3
    #create RGBs
    r = r1
    g =
    b =
    a = 255
    #add it to our output
    newdata.append((r, g, b, a))

  '''

  #create an image from our new combined data
  img.putdata(newdata)
  #unique name
  filename = uuid.uuid4().hex + '.png'
  filename = os.path.join('/tmp', filename)
  img.save(filename, 'PNG')
  #send it back
  return filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questify', methods=['POST'])
def classify_upload():
  try:
    #get the image from the request
    imagefile = request.files['imagefile']
    filename_ = str(datetime.datetime.now()).replace(' ', '_') + \
            werkzeug.secure_filename(imagefile.filename)
    filename = os.path.join('/tmp', filename_)

    #make sure it has the correct file type
    b = False
    for ext in ALLOWED_IMAGE_EXTENSIONS:
      if ext in filename:
        b = True
    if not b:
      return 'Invalid filetype.'

    #save the file to /tmp
    imagefile.save(filename)
    #open the image for Pillow
    image = Image.open(filename)
  except Exception as err:
    #uh oh. Something went wrong.
    print ('Uploaded image open error: ' + err)
    return 'Error: ' + err

  #process the image
  resultFilename = process_image(image)
  #send it back
  return send_file(resultFilename)

@app.route('/login')
def login():
    callback = url_for(
        'facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True
    )
    return facebook.authorize(callback=callback)


@app.route('/login/authorized')
def facebook_authorized():
    resp = facebook.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    if isinstance(resp, OAuthException):
        return 'Access denied: %s' % resp.message

    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    return 'Logged in as id=%s name=%s redirect=%s' % \
        (me.data['id'], me.data['name'], request.args.get('next'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')



if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
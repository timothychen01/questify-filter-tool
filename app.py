from PIL import Image, ImageChops, ImageEnhance
import requests
import os
from flask import Flask, redirect, jsonify, render_template, request, send_file, send_from_directory, url_for, session
import werkzeug
import datetime
import uuid
from flask_oauthlib.client import OAuth, OAuthException

# Binary response content parsing
from PIL import Image
from io import BytesIO


FACEBOOK_APP_ID = '1813961962211551'
FACEBOOK_APP_SECRET = '1d4efe2619879a1cd22e39e30767e4fb'


app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

facebook = oauth.remote_app(
    'facebook',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    access_token_method='GET',
    authorize_url='https://www.facebook.com/dialog/oauth'
)


ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def process_image(img):
  #open up the mask
  mask = Image.open('static/images/mask.png')
  mask = mask.convert('RGBA')
  mask = mask.resize(img.size)

  img.paste(mask, (0,0), mask)
  newdata = img.getdata()

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
    # return 'Logged in as id=%s name=%s redirect=%s' % \
    #     (me.data['id'], me.data['name'], request.args.get('next'))
    payload = {'type':'large','redirect':'true','width':'500','height':'500'}
    r = requests.get("http://graph.facebook.com/" + me.data['id'] + "/picture", params=payload)
    img = Image.open(BytesIO(r.content))

    #process the image
    resultFilename = process_image(img)
    #send it back
    return send_file(resultFilename)

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')



if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
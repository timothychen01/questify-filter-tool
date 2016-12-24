# QUESTify Filter Tool

Based off of cnexus's filter app for AKPsi and AlexEKoren's filter app for [Technica](https://gotechnica.org)

Here's a [demo](http://questify-umd.herokuapp.com)

## Setup
```
pip install -r requirements.txt
```

## Configuration

You'll need to create a Facebook app and publish it (get it out of developer mode). Update the `FACEBOOK_APP_ID` and `FACEBOOK_APP_SECRET` in `app.py`

To change the filter mask, switch out the `mask.png` in `/static/images`

## Running the app
```
python app.py
```
Runs on [http://localhost:5000](http://localhost:5000) by default.

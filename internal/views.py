import os
import jinja2
import json
import requests

from flask import Flask, request, redirect, render_template, url_for, session, flash, abort, current_app
from flask_oauthlib.client import OAuth, OAuthException
from localgov import app, oauth, forms

registry = oauth.remote_app(
    'registry',
    consumer_key=app.config['REGISTRY_CONSUMER_KEY'],
    consumer_secret=app.config['REGISTRY_CONSUMER_SECRET'],
    request_token_params={'scope': 'vehicle:view address:view'},
    base_url=app.config['REGISTRY_BASE_URL'],
    request_token_url=None,
    access_token_method='POST',
    access_token_url='%s/oauth/token' % app.config['REGISTRY_BASE_URL'],
    authorize_url='%s/oauth/authorize' % app.config['REGISTRY_BASE_URL']
)

#auth helper
@registry.tokengetter
def get_registry_oauth_token():
    return session.get('registry_token')

#views
@app.route("/")
def index():
    notices = _get_notices(max=3)
    return render_template('index.html', fullscreen=True, notices=notices)

@app.route("/parking-permit")
def parking_permit_start():
    session.clear()
    return render_template('parking-permit-start.html')

@app.route("/parking-permit/information")
def parking_permit_information():
    if not session.get('registry_token', False):
        session['resume_url'] = 'parking_permit_information'
        return redirect(url_for('verify'))
    return render_template('parking-permit-information.html')

@app.route("/parking-permit/done")
def parking_permit_done():
    session.clear()
    return render_template('parking-permit-done.html')


@app.route('/verify')
def verify():
    _scheme = 'https'
    if os.environ.get('OAUTHLIB_INSECURE_TRANSPORT', False) == 'true':
        _scheme = 'http'
    return registry.authorize(callback=url_for('verified', _scheme=_scheme, _external=True))


@app.route('/verified')
def verified():
    resp = registry.authorized_response()

    if resp is None or isinstance(resp, OAuthException):
        return 'Access denied: reason=%s error=%s' % (
        request.args['error_reason'],
        request.args['error_description']
        )

    session['registry_token'] = (resp['access_token'], '')
    if session.get('resume_url'):
        return redirect(url_for(session.get('resume_url')))
    else:
        return redirect(url_for('index'))


@app.route("/notices")
def notices():
    # go via request for notices rather than registry as they're totally
    # public i think?
    # also should filter for notices issued by this council
    notices = _get_notices()
    return render_template('notices.html', notices=notices)



def _get_notices(max=None):
    notices = []
    url = '%s/notices' % current_app.config['REGISTRY_BASE_URL']
    if max:
        url = "%s?max=%d" % (url, max)

    response = requests.get(url)
    if response.status_code == 200:
        notices = response.json()
    return notices


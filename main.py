# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_app]
# [START gae_python3_app]
from flask import Flask
from flask import render_template
from flask import request

from app.discovery_doc_parser import DiscoveryDocParser


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


@app.route('/')
def index():
  return 'Welcome'


@app.route('/disdoc')
def disdoc():
  dis_doc_url = request.args.get('url', type = str)
  return render_template('disdoc.html', dis_doc_url=dis_doc_url)


@app.route('/toc')
def toc():
  dis_doc_url = request.args.get('url', type = str)
  disdoc = DiscoveryDocParser()
  toc = disdoc.get_toc(dis_doc_url)
  return toc

@app.errorhandler(404)
def page_not_found(e):
  return 'Sorry, did not find the page. <br/> - Discovery Doc Parser'


if __name__ == '__main__':
  # This is used when running locally only. When deploying to Google App
  # Engine, a webserver process such as Gunicorn will serve the app. This
  # can be configured by adding an `entrypoint` to app.yaml.
  app.run(host='127.0.0.1', port=8080, debug=True)

# [END gae_python3_app]
# [END gae_python38_app]

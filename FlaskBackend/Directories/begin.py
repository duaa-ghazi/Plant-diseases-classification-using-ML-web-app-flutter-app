from flask import Flask

app = Flask(__name__)
print("model loading .... plaese wait this might take a while")

app.secret_key ='1234'
from Directories import Backend,api
from Directories.Backend.routes import mod
from Directories.api.routes import mod




app.register_blueprint(Backend.routes.mod)
app.register_blueprint(api.routes.mod, url_prefix='/api')

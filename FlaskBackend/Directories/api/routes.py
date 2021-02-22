from flask import Blueprint
mod = Blueprint('api',__name__,template_folder='templates')
from Directories.Database import collection as db
from bson.json_util import dumps
from flask import Flask,Blueprint,request,render_template,jsonify

@mod.route('/',methods=['POST'])

def api():

    json_data = request.get_json()
    user_uid = json_data['user_uid']
    #print(user_uid)
   # print(db.getAllImages(user_uid))
    return dumps(db.getAllImages(user_uid))
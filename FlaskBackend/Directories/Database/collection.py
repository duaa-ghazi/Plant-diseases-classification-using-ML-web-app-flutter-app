from pymongo import MongoClient
from bson import ObjectId


# Here we made connection with local mongoDB database by passing  the url of it which called client
client = MongoClient("mongodb://127.0.0.1:27017")  # host uri
# Create database with name predicted_images then select it
db = client.predicted_images  # Select the database  predicted_image as db
image_collection = db.image_info  # Create collection called image_info and access it as image_collection


# define function called addNewImage to insert new image with specific data fields
# (insert new document in image_info collection)
def addNewImage(user_uid, image_name, prediction, conf, model_name, time, url,information):
    image_collection.insert({
        "user_uid":user_uid,
        "file_name": image_name,
        "prediction": prediction,
        "confidence": conf,
        "model_name":model_name,
        "upload_time": time,
        "url": url,
        "information": information
    })
def getAllImages(user_uid):
    print (user_uid)
    data = image_collection.find({"user_uid": user_uid})
    print(data)
    return data

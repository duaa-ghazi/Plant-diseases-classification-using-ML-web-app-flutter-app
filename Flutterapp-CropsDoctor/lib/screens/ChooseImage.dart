//import 'dart:html';

import 'package:async/async.dart';
import 'package:flutter/material.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:path/path.dart';
import 'dart:convert';
import 'dart:async';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

final _firestore = Firestore.instance;
User loggedInUser;

class ChooseImage extends StatefulWidget {
  @override
  _ChooseImageState createState() => _ChooseImageState();
}

enum PhotoDialogAnswers { CAMERA, STORAGE }

class _ChooseImageState extends State<ChooseImage> {
  File image_path;
  String prediction;
  String confidence;
  String model_name;
  String information;

  final _auth = FirebaseAuth.instance;

  @override
  void initState() {
    super.initState();

    getCurrentUser();
  }

  void getCurrentUser() async {
    try {
      final User user = await _auth.currentUser;
      if (user != null) {
        loggedInUser = user;
      }
    } catch (e) {
      print(e);
    }
  }

  @override
  Widget build(BuildContext context) {
    // TODO: implement build
    return Scaffold(
      backgroundColor: Colors.grey[500],
      appBar: AppBar(
        title: Text(
          "Choose Image",
          textAlign: TextAlign.center,
          style: TextStyle(
            color: Colors.white70,
          ),
        ),
        backgroundColor: Colors.green[400],
      ),
      body: Container(
          child: Center(
        child: Column(
          children: <Widget>[
            SizedBox(height: 50),
            image_path != null
                ? new Image.file(image_path, height: 300, width: 400)
                : new Text(
                    "Choose an image to classify",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 20,
                      color: Colors.brown[800],
                    ),
                  ),
            SizedBox(height: 20),
            prediction != null
                ? new Text(
                    "Prediction : " + prediction + "%",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: Colors.brown[800],
                    ),
                  )
                : new Text(
                    "Prediction :-%",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: Colors.brown[800],
                    ),
                  ),
            SizedBox(height: 20),
            confidence != null
                ? new Text(
                    "Result  : " + confidence,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                      color: Colors.brown[800],
                    ),
                  )
                : new Text(
                    "Result  : -",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: Colors.brown[800],
                    ),
                  ),
            SizedBox(height: 20),
            model_name != null
                ? new Text(
                    "model_name  : " + model_name,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: Colors.brown[800],
                    ),
                  )
                : new Text(
                    "model_name : -",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: Colors.brown[800],
                    ),
                  ),
            SizedBox(height: 20),
            model_name != null
                ? FlatButton(
                    padding: EdgeInsets.fromLTRB(20.0, 10.0, 20.0, 10.0),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8.0)),
                    color: Colors.green,
                    textColor: Colors.white,
                    onPressed: () {
                      createAlertDialog(context);
                    },
                    child: Text(
                      "More info",
                      style: TextStyle(
                        fontSize: 20.0,
                        color: Colors.brown[800],
                      ),
                    ))
                : new Text(
                    "",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: Colors.brown[800],
                    ),
                  ),
          ],
        ),
      )),
      floatingActionButton: FloatingActionButton(
        child: Icon(Icons.cloud_upload,
            color: Colors.lightGreen.shade400, size: 18.0),
        onPressed: _addPhoto,
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
    );
  }

  Future _addPhoto() async {
    switch (await showDialog(
        context: this.context,
        builder: (BuildContext context) {
          return SimpleDialog(
            title: Text(
              'Add photo from:',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.brown[800],
              ),
            ),
            children: <Widget>[
              SimpleDialogOption(
                child: ListTile(
                  title: Text(
                    'Camera',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.brown[800],
                    ),
                  ),
                  leading: Icon(
                    Icons.camera,
                    color: Colors.lime[800],
                  ),
                ),
                onPressed: () =>
                    Navigator.pop(context, PhotoDialogAnswers.CAMERA),
              ),
              SimpleDialogOption(
                child: ListTile(
                    title: Text(
                      'Gallery',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.brown[800],
                      ),
                    ),
                    leading: Icon(
                      Icons.photo,
                      color: Colors.lime[800],
                    )),
                onPressed: () =>
                    Navigator.pop(context, PhotoDialogAnswers.STORAGE),
              ),
            ],
          );
        })) {
      case PhotoDialogAnswers.STORAGE:
        File filename =
            await ImagePicker.pickImage(source: ImageSource.gallery);
        Send_image_to_server(filename);

        setState(() {
          image_path = filename;
        });
        break;

      case PhotoDialogAnswers.CAMERA:
        File filename = await ImagePicker.pickImage(source: ImageSource.camera);
        Send_image_to_server(filename);
        setState(() {
          image_path = filename;
        });
        break;
    }
  }

  Future<String> createAlertDialog(BuildContext context) {
    return showDialog(
        context: context,
        builder: (context) {
          return AlertDialog(
            backgroundColor: Colors.lightGreen.shade100,
            contentPadding: EdgeInsets.only(left: 25, right: 25),
            title: Center(
                child: Text(
              "Information",
              style:
                  TextStyle(color: Colors.green, fontWeight: FontWeight.bold),
            )),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.all(Radius.circular(20.0)),
            ),
            content: Container(
              height: 400,
              width: 300,
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: <Widget>[
                    SizedBox(
                      height: 20,
                    ),
                    Text(
                      information,
                      style: TextStyle(
                          color: Colors.brown[800],
                          fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
            ),
            actions: <Widget>[
              MaterialButton(
                  elevation: 5.0,
                  child: Text(
                    "OK",
                    style: TextStyle(
                        color: Colors.green, fontWeight: FontWeight.bold),
                  ),
                  onPressed: () {
                    Navigator.pop(context);
                  })
            ],
          );
        });
  }

  Send_image_to_server(File imageFile) async {
    var stream =
        new http.ByteStream(DelegatingStream.typed(imageFile.openRead()));
    var length = await imageFile.length();
    print(length);

    var uri = Uri.parse('http://192.168.1.77:5000/predict');
    print("connection established.");
    var request = new http.MultipartRequest("POST", uri);
    var multipartFile = new http.MultipartFile('file', stream, length,
        filename: basename(imageFile.path) + "&" + loggedInUser.uid.toString());

    request.files.add(multipartFile);
    var response = await request.send();
    var result = await response.stream.bytesToString();

    String pre;
    String conf;
    String modelN;
    String info;
    final Map<String, dynamic> responseJson =
        json.decode(result.toString()) as Map<String, dynamic>;
    print(responseJson.toString());

    if (responseJson['status'] == 'success') {
      pre = responseJson['prediction'];
      conf = responseJson['confidence'];
      modelN = responseJson['model_name'];
      info = responseJson['information'];
    }
    print(pre + "  " + conf);

    setState(() {
      prediction = pre;
      confidence = conf;
      model_name = modelN;
      information = info;
    });
    print("response");
    print(response.statusCode);
  }
}

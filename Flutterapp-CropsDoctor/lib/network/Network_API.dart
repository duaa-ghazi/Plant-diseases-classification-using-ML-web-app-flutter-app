import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:async';
import 'package:http/http.dart' as http;
import 'package:path/path.dart';
import 'dart:convert';
import 'dart:async';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'dart:io';
import 'package:async/async.dart';
import 'package:flutter/material.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';

final _firestore = Firestore.instance;
User loggedInUser;

class ImageData {
//  static String  BASE_URL ='http://192.168.1.95:5000/';
  String url;
  String prediction;
  String result;
  String model_name;
  String information;
  ImageData(this.url, this.prediction, this.result, this.model_name,
      this.information);
}

Future<List<ImageData>> GetAllImages() async {
  //to fetch all images which stored in database and display it
  final _auth = FirebaseAuth.instance;
  try {
    final User user = await _auth.currentUser;
    if (user != null) {
      loggedInUser = user;
    }
  } catch (e) {
    print(e);
  }

  var data = await http.post('http://192.168.1.77:5000/api/',
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        'user_uid': loggedInUser.uid,
      }));

  var JsonData = json.decode(data.body);
  List<ImageData> listAllImg = [];
  for (var data in JsonData) {
    ImageData img = ImageData(data['url'], data['prediction'],
        data['confidence'], data['model_name'], data['information']);
    listAllImg.add(img);
  }

  return listAllImg;
  /*




  var data = await http.get('http://192.168.1.77:5000/api/');
  var JsonData = json.decode(data.body);
  List<ImageData> listAllImg = [];
  for (var data in JsonData) {
    ImageData img = ImageData(data['url'], data['prediction'],
        data['confidence'], data['model_name']);
    listAllImg.add(img);
  }

  return listAllImg;*/
}

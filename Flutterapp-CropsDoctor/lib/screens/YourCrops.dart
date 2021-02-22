import 'package:flutter/material.dart';
import 'package:Crops_diagnosis/network/Network_API.dart';
import 'ChooseImage.dart';
import 'dart:async';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

final _firestore = Firestore.instance;
User loggedInUser;

class YourCrops extends StatefulWidget {
  @override
  _YourCropsState createState() => _YourCropsState();
}

class _YourCropsState extends State<YourCrops> {
  Future<List<ImageData>> ListOfImages;
  final _auth = FirebaseAuth.instance;
  @override
  void initState() {
    ListOfImages = GetAllImages();
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    // TODO: implement build
    return Scaffold(
      appBar: AppBar(
        title: Text(
          "Your Diseases Leaves",
          textAlign: TextAlign.left,
          style: TextStyle(
            color: Colors.white70,
          ),
        ),
        backgroundColor: Colors.green[400],
      ),
      floatingActionButton: FloatingActionButton(
        child: Icon(Icons.add),
        backgroundColor: Colors.green[400],
        onPressed: () {
          Navigator.push(context,
                  MaterialPageRoute(builder: (context) => ChooseImage()))
              .then((value) => setState(() {
                    ListOfImages = GetAllImages();
                  }));
        },
      ),
      body: FutureBuilder(
          future: ListOfImages,
          builder: (BuildContext context, AsyncSnapshot snapshot) {
            if (snapshot.hasError) return new Text('Error: ${snapshot.error}');

            switch (snapshot.connectionState) {
              case ConnectionState.waiting:
                return new LinearProgressIndicator(
                  backgroundColor: Colors.deepPurpleAccent,
                );
              default:
                return GridView.count(
                    crossAxisCount: 1,
                    children:
                        List<Widget>.generate(snapshot.data.length, (index) {
                      return Grid_Image(
                        url: snapshot.data[index].url,
                        pred: snapshot.data[index].prediction,
                        res: snapshot.data[index].result,
                        model: snapshot.data[index].model_name,
                        info: snapshot.data[index].information,
                      );
                    }));
            }
          }),
    );
  }
}

class Grid_Image extends StatelessWidget {
  String url;
  String pred;
  String res;
  String model;
  String info;
  Grid_Image({this.url, this.pred, this.res, this.model, this.info});
  @override
  Widget build(BuildContext context) {
    // TODO: implement build
    return Container(
      height: 1000,
      child: Card(
          color: Colors.amberAccent.shade100,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(40), // if you need this
            side: BorderSide(
              color: Colors.grey,
              width: 1,
            ),
          ),
          semanticContainer: true,
          clipBehavior: Clip.antiAliasWithSaveLayer,
          child: Column(mainAxisSize: MainAxisSize.min, children: <Widget>[
            Image.network(
              url,
              width: 600,
              height: 270,
            ),
            Text(
              "prediction: " + pred + "%",
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 14,
                color: Colors.brown[800],
              ),
            ),
            Text(
              "result: " + res,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 15,
                color: Colors.brown[800],
              ),
            ),
            //   Text("model_name: " + model),
            FlatButton(
                padding: EdgeInsets.fromLTRB(20.0, 10.0, 20.0, 10.0),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8.0)),
                color: Colors.green,
                textColor: Colors.white,
                onPressed: () {
                  createAlertDialog(context, info);
                },
                child: Text(
                  "More info",
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                    color: Colors.brown[800],
                  ),
                ))
          ])),
    );
  }
}

Future<String> createAlertDialog(BuildContext context, String information) {
  return showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: Colors.lightGreen.shade100,
          contentPadding: EdgeInsets.only(left: 25, right: 25),
          title: Center(
              child: Text(
            "Information",
            style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold),
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
                        color: Colors.black, fontWeight: FontWeight.bold),
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

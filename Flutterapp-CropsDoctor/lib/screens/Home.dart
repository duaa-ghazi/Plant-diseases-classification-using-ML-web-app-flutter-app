import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:Crops_diagnosis/screens/YourCrops.dart';
import 'chat_screen.dart';
//import 'Profile.dart';
import 'package:flutter/material.dart';
import 'package:Crops_diagnosis/constants.dart';
import 'package:firebase_auth/firebase_auth.dart';

class Home extends StatefulWidget {
  static const String id = 'Home_screen';
  @override
  _HomeState createState() => _HomeState();
}

class _HomeState extends State<Home> {
  final _auth = FirebaseAuth.instance;
  User loggedInUser;
  String messageText;

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

  ///////

  PageController _pageController = PageController();

  List<Widget> _screens = [
    YourCrops(),
    ChatScreen(),
    // Profile(),
  ];

  int _selectedIndex = 0;
  void _onPageChanged(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  void _onItemTapped(int selectedIndex) {
    setState(() {
      _pageController.jumpToPage(selectedIndex);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      /*appBar: AppBar(
        title: Text('Croper'),
      ),*/
      body: PageView(
        controller: _pageController,
        children: _screens,
        onPageChanged: _onPageChanged,
        //physics: NeverScrollableScrollPhysics(),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        //type: BottomNavigationBarType.fixed,
        //selectedFontSize: 25,
        //unselectedFontSize: 20,
        items: [
          BottomNavigationBarItem(
              icon: Icon(Icons.agriculture),
              title: Text('YourCrops'),
              backgroundColor: Colors.teal),
          BottomNavigationBarItem(
              icon: Icon(Icons.chat),
              title: Text('Chat'),
              backgroundColor: Colors.teal),
          /*  BottomNavigationBarItem(
              icon: Icon(Icons.person),
              title: Text('Profile'),
              backgroundColor: Colors.teal),*/
        ],
        onTap: _onItemTapped,
      ),
    );
  }
}

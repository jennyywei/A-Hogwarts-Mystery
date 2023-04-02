/*
 * File: AdventureTextGame.js
 * ------------------------
 * Provides a minimal example, where you can interact with your
 * Python Adventure program through the CS106AX JSConsole.
 */

"use strict";

function AdventureTextGame() {
  let gw = GWindow("JSGraphics", 800, 600);
  let lastRoom = "";
  gw.addEventListener("click", clickAction);
  loadStart();

  function clickAction(e) {
		let obj = gw.getElementAt(e.getX(), e.getY());
		if (obj !== null && obj.clickAction !== undefined) {
			obj.clickAction();
		}
	}

  // Create a new adventure client
  let myAdventure = new AdventureClient();
  let gameOver = false;

  // Called when we receive a response from the Python program
  function onResponse(text, ended) {
    console.log(text);
    if (ended) {
      gameOver = true;
      loadEnd();
    } else {
      myAdventure.sendCommand("GETCHANGEDROOM", onChangeResponse);
      myAdventure.sendCommand("GETROOMOBJECTS", onObjectResponse);
      console.requestInput("> ", onCommand);
    }
  }

  // command: typed into JSConsole
  function onCommand(command) {
    if (gameOver) {
      return; // Do nothing if the game is ended
    }
    console.clear();
    myAdventure.sendCommand(command, onResponse);
  }

  function onChangeResponse(text) {
    lastRoom = text;
    try {
      let path = "GraphicsImages/" + text + ".png";
      let image = GImage(path);
      gw.clear();
      gw.add(image);
    } catch(e) {
      // do nothing if there is no associated image to a room
    }
  }

  function onObjectResponse(text) {
    if (text.indexOf(">") !== -1) text = text.substring(1);
    if (text.length === 0) return;

    let objectArr = text.split(" ");
    setTimeout(addObjects, 100);

    function addObjects() {
      for (let i = 0; i < objectArr.length; i++) {
        try {
          let path = "ObjectImages/" + objectArr[i] + ".png";
          let image = GImage(path);
          gw.add(image, 257, 451);
        } catch(e) {
          // do nothing
        }
      }
    }
  }

  function loadStart() {
    let image1 = GImage("GraphicsImages/Opening1.png");
    let image2 = GImage("GraphicsImages/Opening2.png");
    let image3 = GImage("GraphicsImages/Opening3.png");
    let image4 = GImage("GraphicsImages/Opening4.png");
    
    image3.clickAction = function() {
      gw.clear();
      gw.add(image4);
    }

    image4.clickAction = function() {
      gw.clear();
      myAdventure.startGame(onResponse);
      let startImage = GImage("GraphicsImages/EntranceHall.png");
      gw.add(startImage);
    }

    loadImg1();
    setTimeout(loadImg2, 1000);
    setTimeout(loadImg3, 4000);

    function loadImg1() {
      gw.clear();
      gw.add(image1);
    }

    function loadImg2() {
      gw.clear();
      gw.add(image2);
    }

    function loadImg3() {
      gw.clear();
      gw.add(image3);
    }
  }

  function loadEnd() {
    let snake = GImage("GraphicsImages/Death.png");
    let deathScreen = GImage("GraphicsImages/DeathScreen.png");
    let winScreen1 = GImage("GraphicsImages/Ending1.png");
    let winScreen2 = GImage("GraphicsImages/Ending2.png");

    if (lastRoom === "SnakeWarning") {
      setTimeout(loadSnake, 100);
      setTimeout(loadDeath, 3000);

    } else if (lastRoom === "AfterSnakeFight") {
      setTimeout(loadWin1, 100);
      setTimeout(loadWin2, 7000);
    } else {
      setTimeout(loadDeath, 100);
    }

    winScreen2.clickAction = function() {
      console.clear();
      myAdventure.startGame(onResponse);
      let startImage = GImage("GraphicsImages/EntranceHall.png");
      gw.add(startImage);
      gameOver = false;
    }

    deathScreen.clickAction = function() {
      console.clear();
      myAdventure.startGame(onResponse);
      let startImage = GImage("GraphicsImages/EntranceHall.png");
      gw.add(startImage);
      gameOver = false;
    }

    function loadSnake() {
      gw.clear();
      gw.add(snake);
    }

    function loadDeath() {
      gw.clear();
      gw.add(deathScreen);
    }

    function loadWin1() {
      gw.clear();
      gw.add(winScreen1);
    }

    function loadWin2() {
      gw.clear();
      gw.add(winScreen2);
    }

  }



}

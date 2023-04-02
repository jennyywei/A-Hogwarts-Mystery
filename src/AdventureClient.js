/*
 * File: AdventureClient.js
 * ------------------------
 * Provides a small interface to interact with the AdventureServer.
 */

"use strict";

const SERVER_ADDRESS = "http://localhost:8080";

class AdventureClient {
  /**
   * This is a modern-style JavaScript class. You can create a new
   * Adventure client like so:
   *
   * let client = new AdventureClient()
   *   - or -
   * let client = new AdventureClient("Game Name - for if you have multiple concurrent games.")
   */
  constructor(name = "Default Adventure") {
    this._name = name;
  }

  /**
   * This is a modern-style JavaScript getter. You can get the
   * name of this AdventureClient by simply doing:
   *
   * let name = client.name;
   */
  get name() {
    return this._name;
  }

  /**
   * This starts a brand new game of Adventure.
   * Provide a callback function that will receive the starting text.
   * For example:
   *
   * function onStarted(text) {
   *  console.log(text);  // Will log "You are standing at the end of a road ..."
   * }
   *
   * client.startGame(onStarted)
   *
   * The received text will be null if an error occured
   */
  async startGame(onGameStarted) {
    try {
      const response = await fetch(`${SERVER_ADDRESS}/${this._name}/game`, {
        method: "PUT",
      });

      const text = await response.text();

      onGameStarted?.(text);
    } catch (e) {
      console.write(
        '<i><span style="color: red;">Error occured while starting the game. Is the server running?</span></i><br />'
      );
      onGameStarted?.(null);
    }
  }

  /**
   * This forcibly ends a game of Adventure.
   * Provide a callback function that will be called when the termination is complete.
   * For example:
   *
   * function onEnded() {
   *  console.log("Game ended");
   * }
   *
   * client.endGame(onEnded)
   */
  async endGame(onGameEnded) {
    try {
      await fetch(`${SERVER_ADDRESS}/${this._name}/game`, {
        method: "DELETE",
      });
      onGameEnded?.();
    } catch (e) {
      console.write(
        '<i><span style="color: red;">Error occured while ending the game.</span></i><br />'
      );
      onGameEnded?.(null);
    }
  }

  /**
   * This sends a command to a running game of Adventure.
   * Provide a callback function that will receive the response text, and
   * a boolean for if the game has ended.
   * For example:
   *
   * function onResponse(text, ended) {
   *  console.log(text);  // Will log "You are empty-handed!"
   *  if (ended) {
   *    console.log("Game over!");
   *  }
   * }
   *
   * client.sendCommand("INVENTORY", onResponse)
   *
   */
  async sendCommand(command, onResponse) {
    try {
      const response = await fetch(`${SERVER_ADDRESS}/${this._name}/command`, {
        method: "POST",
        body: command,
      });
      const text = await response.text();

      onResponse?.(text, response.headers.has("X-Game-Finished"));
      return text;
    } catch (e) {
      console.write(
        '<i><span style="color: red;">Error occured while sending a command.</span></i><br />'
      );
      onResponse?.(null);
      return null;
    }
  }
}

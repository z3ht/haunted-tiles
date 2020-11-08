var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
const request = new XMLHttpRequest();

const baseUrl = "https://haunted-tiles.xyz"
const apiToken = "ep1c-t0ken";
const strategy = "basic";
let gameId = undefined

function main(gameState, side){
  gameState = JSON.stringify(gameState).toString();
  side = JSON.stringify(side).toString();

  const token = "Api-Token=" + apiToken;

  if (gameId === undefined) {
    const args = "&Strategy=" + strategy + "&Game-State=" + gameState + "&Side=" + side
    request.open('POST', baseUrl + "/?" + token + args, false);
    request.send(null);
    gameId = request.responseText;
  } else {
    const args = "&Game-Id=" + gameId + "&Game-State=" + gameState + "&Side=" + side
    request.open('POST', baseUrl + "/update?" + token + args, false);
    request.send(null);
  }

  console.log(gameId);

  request.open('GET', baseUrl + "/move?" + token + "&Game-Id=" + gameId);
  request.send(null);
  const move = request.responseText;

  console.log(move);

  return move;
}

console.log(main({
  boardSize: [2, 2],
  tileStates: [
      [3, 1],
      [2, 0]
  ],
  teamStates: [undefined, undefined, undefined]
}, "home"));
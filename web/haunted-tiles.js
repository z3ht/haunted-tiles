process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0;

var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
const request = new XMLHttpRequest();

const baseUrl = "https://localhost:8421";
const apiToken = "ep1c-t0ken";
const strategy = "hail-mary";
let gameId = undefined;

function main(gameState, side){
  const json_gameState = JSON.stringify(gameState).toString();
  const json_side = JSON.stringify(side).toString();

  const token = "Api-Token=" + apiToken;

  if (gameId === undefined) {
    const json_strategy = JSON.stringify(strategy);
    const args = "&Strategy=" + json_strategy + "&Side=" + json_side + "&Game-State=" + json_gameState
    request.open('POST', baseUrl + "/?" + token + args, false);
    request.send(null);
    gameId = request.responseText;
  }

  const args = "&Game-Id=" + gameId + "&Game-State=" + json_gameState;
  request.open('POST', baseUrl + "/update?" + token + args, false);
  request.send(null);

  request.open('GET', baseUrl + "/move?" + token + "&Game-Id=" + gameId, false);
  request.send(null);

  return JSON.parse(request.responseText);
}

function test() {
  request.open('GET', baseUrl + "/hello_world?Api-Token=ep1c-t0ken", false);
  request.send(null);

  console.log(request.status);
  console.log(request.responseText);
}

console.log(main({
  boardSize: [7, 7],
  tileStates: [
    [3, 3, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 2, 3, 2],
    [3, 3, 3, 3, 3, 3, 3]
  ],
  teamStates: {
    away: [
      {
        coord: [5, 0],
        isDead: false
      },
      {
        coord: [5, 4],
        isDead: false
      },
      {
        coord: [5, 5],
        isDead: false
      }
    ],
    home: [
      {
        coord: [0, 0],
        isDead: false
      },
      {
        coord: [0, 3],
        isDead: false
      },
      {
        coord: [0, 6],
        isDead: false
      }
    ]
  }
}, "home"));

// test();
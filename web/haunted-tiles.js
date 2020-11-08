process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0;

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

  request.open('GET', baseUrl + "/move?" + token + "&Game-Id=" + gameId, false);
  request.send(null);
  const move = request.responseText;

  console.log(move);

  return move;
}

function test() {
  request.open('GET', baseUrl + "/?Api-Token=ep1c-t0ken");
  request.send(null);

  console.log(request.status);
  console.log(request.responseText);
}

// console.log(main({
//   boardSize: [7, 7],
//   tileStates: [
//     [1, 3, 3, 1, 3, 3, 1],
//     [3, 3, 3, 3, 3, 3, 3],
//     [3, 3, 3, 3, 3, 3, 3],
//     [3, 3, 3, 3, 3, 3, 3],
//     [3, 3, 3, 3, 3, 3, 3],
//     [1, 3, 3, 3, 2, 2, 2],
//     [3, 3, 3, 3, 2, 3, 3]
//   ],
//   teamStates: {
//     away: [
//       {
//         coord: [5, 0],
//         isDead: false
//       },
//       {
//         coord: [5, 4],
//         isDead: false
//       },
//       {
//         coord: [5, 5],
//         isDead: false
//       }
//     ],
//     home: [
//       {
//         coord: [0, 0],
//         isDead: false
//       },
//       {
//         coord: [0, 3],
//         isDead: false
//       },
//       {
//         coord: [0, 6],
//         isDead: false
//       }
//     ]
//   }
// }, "home"));

// test();
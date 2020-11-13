const request = new XMLHttpRequest();

const baseUrl = "https://haunted-tiles.xyz"
const apiToken = "ep1c-t0ken";
const strategy = "basic";
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

  console.log(gameId);

  const args = "&Game-Id=" + gameId + "&Game-State=" + json_gameState;
  request.open('POST', baseUrl + "/update?" + token + args, false);
  request.send(null);

  request.open('GET', baseUrl + "/move?" + token + "&Game-Id=" + gameId, false);
  request.send(null);

  return JSON.parse(request.responseText);
}
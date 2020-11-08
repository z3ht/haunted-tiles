const getContent = function(url) {
  // return new pending promise
  return new Promise((resolve, reject) => {
    // select http or https module, depending on reqested url
    const lib = require("https")
    const request = lib.get(url, (response) => {
      // handle http errors
      if (response.statusCode < 200 || response.statusCode > 299) {
         reject(new Error('Failed to load page, status code: ' + response.statusCode));
       }
      // temporary data holder
      const body = [];
      // on every content chunk, push it to the data array
      response.on('data', (chunk) => body.push(chunk));
      // we are done, resolve promise with those joined chunks
      response.on('end', () => resolve(body.join('')));
    });
    // handle connection errors of the request
    request.on('error', (err) => reject(err))
    })
};

function sleep(msec, start_date=Date.now()) {
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - start_date < msec);
}

const baseUrl = "https://127.0.0.1:8421"
const apiToken = "ep1c-t0ken";
const strategy = "basic";
let gameId = undefined

process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0;

async function main(gameState, side){
  gameState = JSON.stringify(gameState).toString();
  side = JSON.stringify(side).toString();

  const start_date = Date.now();
  const token = "Api-Token=" + apiToken;

  if (gameId === undefined) {
    const args = "&Strategy=" + strategy + "&Game-State=" + gameState + "&Side=" + side
    gameId = await getContent(baseUrl + "/?" + token + args);
  } else {
    const args = "&Game-Id=" + gameId + "&Game-State=" + gameState + "&Side=" + side
    await getContent(baseUrl + "/update?" + token + args).catch(console.log);
  }

  sleep(1500, start_date);

  console.log(gameId);

  const result = await getContent(baseUrl + "/move?" + token + "&Game-Id=" + gameId);

  sleep(1800, start_date);

  console.log(result)

  return result;
}

function test() {
  const token = "Api-Token=" + apiToken;
  getContent(baseUrl + "/hello_world?" + token)
      .then(console.log)
      .catch(console.error);
}

main({
  boardSize: [2, 2],
  tileStates: [
      [3, 1],
      [2, 0]
  ],
  teamStates: [undefined, undefined, undefined]
}, "home")
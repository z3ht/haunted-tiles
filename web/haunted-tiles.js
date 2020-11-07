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


const apiToken = "ep1c-t0ken";
const strategy = "basic";
let gameId = undefined;

getContent("https://haunted-tiles.xyz/?Api-Token=ep1c-t0ken")
  .then((html) => console.log(html))
  .catch((err) => console.error(err));

function main(gameState, side){
  const start_date = Date.now();

  const token = "Api-Token=" + apiToken;

  if (gameId === undefined) {
    const args = "&Strategy=" + strategy + "&Game-State=" + gameState + "&Side=" + side
    getContent("https://haunted-tiles.xyz/?" + token + args)
      .then((newGameId) => gameId = newGameId)
      .catch(console.error);
  } else {
    const args = "&Game-Id=" + gameId + "&Game-State=" + gameState + "&Side=" + side
    getContent("https://haunted-tiles.xyz/update?" + token + args)
      .then(console.log)
      .catch(console.error);
  }

  sleep(1600, start_date);

  let result = undefined
  getContent("https://haunted-tiles.xyz/move?" + token + "&Game-Id=" + gameId)
      .then((out) => result = out)
      .catch(console.error);

  sleep(1900, start_date);

  console.log(result)

  return result;
}

function test() {
  const token = "Api-Token=" + apiToken;
  getContent("https://haunted-tiles.xyz/hello_world?" + token)
      .then(console.log)
      .catch(console.error);
}

test()
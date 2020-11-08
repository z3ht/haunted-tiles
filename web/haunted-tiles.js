
const strategy = "basic";
let gameId = undefined
let myWorker = undefined

process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0;

const baseUrl = "https://haunted-tiles.xyz"
const apiToken = "ep1c-t0ken";
var request = new XMLHttpRequest();
request.open('GET', baseUrl + "/hello_world?Api-Token=ep1c-t0ken", false);
request.send(null);

if (request.status === 200) {
  console.log(request.responseText);
}


// function main(gameState, side){
//   function worker() {
//     setInterval(function() {
//       postMessage({foo: "bar"});
//     }, 1000);
//   }
//
//   var code = worker.toString();
//   code = code.substring(code.indexOf("{")+1, code.lastIndexOf("}"));
//
//   var blob = new Blob([code], {type: "application/javascript"});
//   var worker = new Worker(URL.createObjectURL(blob));
//
//   worker.onmessage = function(m) {
//     console.log("msg", m);
//   };
//
//   // const start_date = Date.now();
//   //
//   // if (myWorker === undefined) {
//   //   var blobURL = URL.createObjectURL( new Blob([ '(',
//   //     function(){
//   //       self.addEventListener('message', function(e) {
//   //         self.postMessage(e.data);
//   //       }, false);
//   //     }.toString(),
//   //     ')()' ], { type: 'application/javascript' } ) );
//   //   myWorker = new Worker( blobURL );
//   // }
//   //
//   // myWorker.postMessage([gameState, side]);
//   //
//   // worker.addEventListener('message', function(e) {
//   //   console.log('Worker said: ', e.data);
//   // }, false);
//   //
//   // sleep(1900, start_date);
//   //
//   // console.log("exit")
// }
//
// async function async_main(gameState, side, start_date=Date.now()) {
//   gameState = JSON.stringify(gameState).toString();
//   side = JSON.stringify(side).toString();
//
//   const token = "Api-Token=" + apiToken;
//
//   if (gameId === undefined) {
//     const args = "&Strategy=" + strategy + "&Game-State=" + gameState + "&Side=" + side
//     gameId = await getContent(baseUrl + "/?" + token + args);
//   } else {
//     const args = "&Game-Id=" + gameId + "&Game-State=" + gameState + "&Side=" + side
//     await getContent(baseUrl + "/update?" + token + args).catch(console.log);
//   }
//
//   sleep(1400, start_date);
//
//   console.log(gameId);
//
//   const result = await getContent(baseUrl + "/move?" + token + "&Game-Id=" + gameId);
//
//   sleep(1700, start_date);
//
//   console.log(result)
//
//   return result;
// }
//
// function test() {
//   const token = "Api-Token=" + apiToken;
//   getContent(baseUrl + "/hello_world?" + token)
//       .then(console.log)
//       .catch(console.error);
// }
//
// console.log(main({
//   boardSize: [2, 2],
//   tileStates: [
//       [3, 1],
//       [2, 0]
//   ],
//   teamStates: [undefined, undefined, undefined]
// }, "home"));
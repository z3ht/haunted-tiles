const fetch = require("node-fetch");

const apiToken = "ep1c-t0ken";
const baseUrl = "https://127.0.0.1:8421";    // Change this to https://haunted-tiles.xyz when testing production

process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0; // Remove this when testing production code

fetch(baseUrl + "/", {
    method: "GET",
    headers: {
        "Api-Token": apiToken
    },
    body: undefined
}).then(data => data.json()).then(console.log);
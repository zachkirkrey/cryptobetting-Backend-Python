const WebSocket = require('ws');
const redis = require('redis');


// Configuration: adapt to your environment
const REDIS_SERVER = "redis://localhost:6379";
const WEB_SOCKET_PORT = 8005;

// Connect to Redis and subscribe to "app:notifications" channel
var redisClient = redis.createClient(REDIS_SERVER);
redisClient.subscribe('BO-DATA');

var client = redis.createClient(REDIS_SERVER);

// Create & Start the WebSocket server
const server = new WebSocket.Server({ port: WEB_SOCKET_PORT });

function noop() { }

function heartbeat() {
    this.isAlive = true;
}

// Register event for client connection
server.on('connection', function connection(ws) {
    ws.isAlive = true;
    ws.on('pong', heartbeat);
    // client.get("BO-DATA", (err, data) => {
    //     if (err) {
    //         console.error(err);
    //         // throw err;
    //     }
    //     else {
    //         console.log("1. Get key from redis - ", data);
    //         ws.send(data);
    //     }

    // });

    ws.on('message', function (message) {
        // console.log(JSON.parse(message));
        var msg = JSON.parse(message);
        // console.log(typeof msg);
        if (msg.hasOwnProperty('ping')) {
            ws.send(JSON.stringify({ "pong": msg['ping'] }));
        }
    });

    // broadcast on web socket when receving a Redis PUB/SUB Event
    redisClient.on('message', function (channel, message) {
        console.log(message);
        ws.send(message);        
    })

});

const interval = setInterval(function ping() {
    server.clients.forEach(function each(ws) {
        if (ws.isAlive === false) return ws.terminate();

        ws.isAlive = false;
        ws.ping(noop);
    });
}, 30000);

server.on('close', function close() {
    clearInterval(interval);
});

console.log("WebSocket server started at ws://locahost:" + WEB_SOCKET_PORT);
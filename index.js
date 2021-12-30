var socket;
var enemy_move_down;var enemy_move_up;
var mySid='';var myNum=0;
var youSid='';
$(document).ready(function() {
    // Connect to the Socket.IO server.
    // The connection URL has the following format, relative to the current page:
    //     http[s]://<domain>:<port>[/<namespace>]
    socket = io('https://stormy-earth-07178.herokuapp.com/');
    // socket = io('http://localhost:5000');

    // Event handler for new connections.
    // The callback function is invoked when a connection with the
    // server is established.
    socket.on('connect', function(msg, cb) {
        socket.emit('my_event', {data: 'I\'m connected!'});
        
    });

    // Event handler for server sent data.
    // The callback function is invoked whenever the server emits data
    // to the client. The data is then displayed in the "Received"
    // section of the page.
    socket.on('my_response', function(msg, cb) {
        $('#log').append('<br>' + $('<div/>').text('Received #' + msg.count + ': ' + msg.data).html());
        if (cb)
            cb();
        // console.log(cb)
    });

    socket.on('first_connect', function(msg, cb) {
        mySid = msg.mysid;
        console.log("sid:", mySid)
        // console.log(cb)
    });

    // socket.on('my_num', function(msg, cb) {
    //     myNum = msg.data;
    //     console.log("myNum:", myNum)
    //     // console.log(cb)
    // });
    // socket.on('move_down', function(msg, cb) {
    //     // if(msg.data=="w"){

    //     // }
    //     enemy_move_down = msg.down
    //     // console.log(msg.data)
    // });
    // socket.on('move_up', function(msg, cb) {
    //     // if(msg.data=="w"){

    //     // }
    //     enemy_move_up = msg.up
    //     // console.log(msg.data)
    // });
    // Interval function that tests message latency by sending a "ping"
    // message. The server then responds with a "pong" message and the
    // round trip time is measured.
    var ping_pong_times = [];
    var start_time;
    window.setInterval(function() {
        start_time = (new Date).getTime();
        $('#transport').text(socket.io.engine.transport.name);
        socket.emit('my_ping');
    }, 1000);

    // Handler for the "pong" message. When the pong is received, the
    // time from the ping is stored, and the average of the last 30
    // samples is average and displayed.
    socket.on('my_pong', function() {
        var latency = (new Date).getTime() - start_time;
        ping_pong_times.push(latency);
        ping_pong_times = ping_pong_times.slice(-30); // keep last 30 samples
        var sum = 0;
        for (var i = 0; i < ping_pong_times.length; i++)
            sum += ping_pong_times[i];
        $('#ping-pong').text(Math.round(10 * sum / ping_pong_times.length) / 10);
    });

    // Handlers for the different forms in the page.
    // These accept data from the user and send it to the server in a
    // variety of ways
    $('form#emit').submit(function(event) {
        socket.emit('my_event', {data: $('#emit_data').val()});
        return false;
    });
    $('form#broadcast').submit(function(event) {
        socket.emit('my_broadcast_event', {data: $('#broadcast_data').val()});
        return false;
    });
    $('form#join').submit(function(event) {
        socket.emit('join', {room: $('#join_room').val(), clientSid: mySid});
        return false;
    });
    $('form#leave').submit(function(event) {
        socket.emit('leave', {room: $('#leave_room').val()});
        return false;
    });
    $('form#send_room').submit(function(event) {
        socket.emit('my_room_event', {room: $('#room_name').val(), data: $('#room_data').val()});
        return false;
    });
    $('form#close').submit(function(event) {
        socket.emit('close_room', {room: $('#close_room').val()});
        return false;
    });
    $('form#disconnect').submit(function(event) {
        socket.emit('disconnect_request');
        return false;
    });
});
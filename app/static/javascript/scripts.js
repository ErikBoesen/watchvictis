var socket = io.connect('http://' + document.domain + ':' + location.port + '/req');

var ui = {
    matchesList: document.getElementById('matches-list'),
    stream: document.getElementById('stream')
}
socket.addEventListener('response', function(data) {
    console.log(data);
});
socket.addEventListener('data', function(data) {
    console.log(data);

    ui.matchesList.innerHTML = '';

    for (i = 0; i < data.matches.length; i++) {
        row = document.createElement('tr');
        row.innerHTML = '<td>' + data.matches[i].comp_level.toUpperCase() + data.matches[i].match_number + '</td>' +
                        '<td>' + data.matches[i].teams.red[0] + ', ' +
                                 data.matches[i].teams.red[1] + ', ' +
                                 data.matches[i].teams.red[2] + '</td>' +
                        '<td>' + data.matches[i].teams.blue[0] + ', ' +
                                 data.matches[i].teams.blue[1] + ', ' +
                                 data.matches[i].teams.blue[2] + '</td>';
        ui.matchesList.appendChild(row);
    }

    // Only replace the stream contents if there's not one there already.
    // Otherwise, it will delete the stream and restart even if it's being watched.
    if (!document.querySelector('#stream iframe')) {
        if (data.webcast[0].type = 'twitch') {
            ui.stream.innerHTML =
                '<iframe src="http://player.twitch.tv/?' + ((data.webcast[0].file) ? 'video=v'  + data.webcast[0].file : 'channel=' + data.webcast[0].channel) + '" scrolling="no" allowfullscreen="true"></iframe>';
        }
    }
});

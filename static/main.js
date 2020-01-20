var socket = io.connect();
var moveAvailable = true;
var roomID;

var choices = document.getElementsByClassName('choice');
for(var i = 0; i < choices.length; i++){
    choices[i].addEventListener("click", function(){
        play(this.id)
    })
}

function updateActionMsg(text){
    document.getElementById('action-message').innerHTML = text;
}

function resetMove(_moveAvailable=true){
    moveAvailable = _moveAvailable;
    if (moveAvailable)
        updateActionMsg('გააკეთეთ სვლა');

    var choices = document.getElementsByClassName('choice');
    for(var i = 0; i < choices.length; i++)
        choices[i].classList.remove("green-glow");
}

function createRoom(maxRound){
    socket.emit("createRoom", {"maxRound": maxRound})
}

function joinRoom(roomID){
    socket.emit("joinRoom", {"roomID": roomID})
}

function play(move){
    if (!moveAvailable){
        Swal.fire(
            'სვლა უკვე გააკეთეთ',
            '',
            'error'
        )
        return
    }
    if (roomID == null){
        Swal.fire(
            'თამაშის დასაწყებად შექმენით ან შედით ოთახში',
            '',
            'error'
        )
        return
    }

    resetMove(moveAvailable=false);
    socket.emit("play", {"move": move, 'roomID': roomID})

    document.getElementById(move).classList.add("green-glow");
    updateActionMsg('დაელოდეთ მოწინააღმდეგის სვლას')
}

function createInput(fn, text){
    Swal.fire({
        title: text,
        input: 'text',
        confirmButtonText: 'გაგრძელება',
        showLoaderOnConfirm: true,
        preConfirm: (n) => {
            fn(n)
        },
        allowOutsideClick: () => !Swal.isLoading()
    })
}

socket.on('failedToJoin', function(msg) {
    Swal.fire(
        msg['error'],
        '',
        'error'
    )
});

socket.on('failedToPlay', function(msg) {
    resetMove();
    Swal.fire(
        msg['error'],
        '',
        'error'
    )
});

socket.on('roomCreated', function(msg) {
    resetMove();
    Swal.fire(
        'ოთახი შეიქმნა, კოდი - ' + msg['roomID'],
        "https://jeiranzorosi.herokuapp.com?room=" + msg['roomID'],
        'success'
    )
});

socket.on('joined', function(msg) {
    resetMove();
    Swal.fire(
        "დაუკავშირდით ოთახს - " + msg['roomID'],
        '',
        'success'
    )
    roomID = msg['roomID'];
});

socket.on('gameComplete', function(msg) {
    resetMove();
    Swal.fire(
        '',
        msg['result'],
        'success'
    )
});

socket.on('roundComplete', function(msg) {
    resetMove();
    Swal.fire(msg['result']);
});
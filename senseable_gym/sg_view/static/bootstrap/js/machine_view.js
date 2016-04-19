var current_machine_id = -1;

var get_current_machine_id = function() {
    return current_machine_id;
};

var set_current_machine_id = function(i) {
    current_machine_id = i;
};

function n(num, max, multiplier) {
    return (num + 1) / max * multiplier;
}

function collides(machines, x, y) {
    var isCollision = false;
    for (var i = 0, len = machines.length; i < len; i++) {
        var x_machine = machines[i].x, y_machine = machines[i].y, radius = machines[i].r;
        // console.log(Math.sqrt(Math.pow(x_machine - x, 2) + Math.pow(y_machine - y, 2)));
        if (Math.sqrt(Math.pow(x_machine - x, 2) + Math.pow(y_machine - y, 2)) < radius) {
            return [machines[i], i];
        }
    }
    return isCollision;
}

function machine_summary(machine) {
    var reservation_schedule = [new Date($.now())];
    /* var summary = `<ul>
        <li>ID: ${machine.machine_id}</li>
        <li>Status: ${machine.status}</li>
        <li>Reservation Schedule:
            <ul>
                <li>${reservation_schedule[0]}</li>
            </ul>
            </li>
    </ul>`;
    */

    var summary = 'hello';

    $.ajax({url: "_reservation_list/" + machine.machine_id, success: function(result){
        var summary = result;
        }}
    );


    return summary;
}


var first = true;
var locations = []

function draw_machines(elem){
    // TODO: Get the width and height of the canvas dynamically
    var height = 700, width = 700, radius = 25;
    var x_loc = 0,  y_loc = 0, x_norm = 0, y_norm = 0;

    // Create a list to hold all of the locations of the centers of the machines
    //var locations = [];
    

    var x_max = 0;
    var y_max = 0;
    
    $.ajax({
        url: "/_machine_list",
        success: function(result){
            machines = result.machines;
            for ( var i = 0; i < machines.length; i++) {
                if (x_max < machines[i].location[0] + 1) {
                    x_max = machines[i].location[0] + 1;
                }
                if (y_max < machines[i].location[1] + 1) {
                    y_max = machines[i].location[1] + 1;
                }
            }
            x_max++;
            y_max++;
            
            for ( i = 0; i < machines.length; i++) {
                if (machines[i].status == "BUSY") {
                    elem.fillStyle = "rgba(360, 77, 44, 1)";
                } else if (machines[i].status == "RESERVED") {
                    elem.fillStyle = "rgba(0, 0, 200, 1)";
                } else if (machines[i].status == "OPEN") {
                    elem.fillStyle = "rgba(200, 200, 10, 0.6)";
                } else {
                    elem.fillStyle = "rgba(0, 0, 0, 0.6)";
                }
                elem.beginPath();
                x_loc = machines[i].location[0];
                y_loc = machines[i].location[1];
                x_norm = n(x_loc, x_max, width);
                y_norm = n(y_loc, y_max, height);
                elem.arc(x_norm,
                        y_norm,
                        radius, 50 , 0, Math.PI*2);
                elem.closePath();
                elem.fill();

                if(first){
                    locations.push({'x': x_norm,
                                    'y': y_norm,
                                    'r': radius,
                                    'machine_id': machines[i].machine_id,
                                    'status': machines[i].status,
                                    'reservations': []
                    });
                }
            } 
            first = false;
            
        }
    });
}

function setup_canvas(auth){
    var canvas = document.getElementById("current_machine_status");
    var elem = canvas.getContext("2d");

    draw_machines(elem);
    setInterval(function(){draw_machines(elem)}, 1000);

    if(typeof window.orientation !== 'undefined'){ // if mobile
        $('#machine_summary').html("test");
        var pressTimer
        
        X0 = canvas.getBoundingClientRect().left
        Y0 = canvas.getBoundingClientRect().top
        
        $('#current_machine_status').on('touchstart', function(e) {
            console.log(e.type)
            pressTimer = window.setTimeout(function() {
                x = Math.round(e.originalEvent.touches[0].pageX) - X0;
                y = Math.round(e.originalEvent.touches[0].pageY) - Y0;
                reserve(x, y, auth);
            },1000)
        }).on('click', function(e) {
            status_popup(e.offsetX, e.offsetY);
        }).on('touchend', function(e) {
            console.log('touchend')
            clearTimeout(pressTimer)
        });
    } else {
        $('#current_machine_status').on('dblclick', function(e) {
            reserve(e.offsetX, e.offsetY, auth)
        });
        
        $('#current_machine_status').on('click', function(e) {
            status_popup(e.offsetX, e.offsetY)
        });
    }  
}

function reserve(x,y, auth){
    if (auth != "True"){
        return;
    }
    console.log('double or long click: ' + x + '/' + y);
    var res = collides(locations, x, y);
    var machine = res[0];
    if (machine) {
        console.log('collision {' + res[1] + '}: ' + machine.x + '/' + machine.y);
        // TODO: Only allow users to reserve somethinhg if they are logged in.
        window.location.href = $SCRIPT_ROOT + "/reserve/" + res[0].machine_id;
    } else {
        console.log('no collision');
    }
}

function status_popup(x,y){
    console.log('click: ' + x + '/' + y);
    var res = collides(locations, x, y);
    var machine = res[0];
    var c_m_id = get_current_machine_id();
    if (machine) {
        if (res[1] != c_m_id) {
            console.log('(Current Machine, Machine): ' + c_m_id + ', ' + machine.machine_id);
            set_current_machine_id(res[1]);
            $.ajax({
                url: "/_reservation_list/" + machine.machine_id,
                success: function(result){
                    var reservations_html = 
                    `<table border=1>
                        <tr>
                            <th text-align=center>Start Time</th>
                            <th>End Time </th>
                        </tr>
                    `;
                    // cr for current reservation
                    for (var cr = 0; cr < result.reservations.length; cr++) {
                        reservations_html += '<tr><td>' + 
                            result.reservations[cr].start_time + 
                            ' </td><td> ' +
                            result.reservations[cr].end_time +
                            '</td></tr>';
                    }
                    reservations_html += '</ul>';
                    $('#machine_summary').html(
                        reservations_html
                    );
                }
            });
            // window.location.href = $SCRIPT_ROOT + "/reserve/" + res[1];
        }
    }
}

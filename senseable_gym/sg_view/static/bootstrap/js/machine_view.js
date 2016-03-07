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

function draw_machines(machines){
    var canvas = document.getElementById("current_machine_status");
    var elem = canvas.getContext("2d");

    // TODO: Get the width and height of the canvas dynamically
    var height = 700;
    var width = 700;
    var radius = 25;

    var x_max = 0;
    var y_max = 0;
    for ( var i = 0, l = machines.length; i < l; i++) {
        if (x_max < machines[i].location[0] + 1) {
            x_max = machines[i].location[0] + 1;
        }
        if (y_max < machines[i].location[1] + 1) {
            y_max = machines[i].location[1] + 1;
        }
    }
    x_max++;
    y_max++;

    // Create a list to hold all of the locations of the centers of the machines
    var locations = [];

    // TODO: Set the fill style differently depending on status
    var x_loc = 0,  y_loc = 0, x_norm = 0, y_norm = 0;

    for ( i = 0; i < l; i++) {
        if (machines[i].status == "Busy") {
            elem.fillStyle = "rgba(360, 77, 44, 1)";
        }
        else {
            elem.fillStyle = "rgba(200, 200, 10, 0.6)";
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

        locations.push({'x': x_norm,
                        'y': y_norm,
                        'r': radius,
                        'machine_id': machines[i].machine_id,
                        'status': machines[i].status,
                        'reservations': []
                        });
    }

    $('#current_machine_status').on('click', function(e) {
        console.log('click: ' + e.offsetX + '/' + e.offsetY);
        var res = collides(locations, e.offsetX, e.offsetY);
        var machine = res[0];
        if (machine) {
            console.log('collision {' + res[1] + '}: ' + machine.x + '/' + machine.y);
            // window.location.href = $SCRIPT_ROOT + "/reserve/" + res[1];
        } else {
            console.log('no collision');
        }
    });

    $('#current_machine_status').mousemove(
        // When
        function(e) {
            var res = collides(locations, e.offsetX, e.offsetY);
            var machine = res[0];
            var c_m_id = get_current_machine_id();
            if (machine) {
                if (res[1] != c_m_id) {
                    console.log('(Current Machine, Machine): ' + c_m_id + ', ' + machine.machine_id);
                    set_current_machine_id(res[1]);
                    $('#machine_summary').html(
                        machine_summary(machine)
                    );
                    // window.location.href = $SCRIPT_ROOT + "/reserve/" + res[1];
                }
            }
        }
    );
}

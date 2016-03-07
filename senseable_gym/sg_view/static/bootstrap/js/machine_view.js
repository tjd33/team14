function n(num, max, multiplier) {
    return (num + 1) / max * multiplier;
}

function collides(rects, x, y) {
    var isCollision = false;
    for (var i = 0, len = rects.length; i < len; i++) {
        var x_rect = rects[i].x, y_rect = rects[i].y, radius = rects[i].r;
        // console.log(Math.sqrt(Math.pow(x_rect - x, 2) + Math.pow(y_rect - y, 2)));
        if (Math.sqrt(Math.pow(x_rect - x, 2) + Math.pow(y_rect - y, 2)) < radius) {
            return [rects[i], i];
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
    elem.fillStyle = "rgba(200, 200, 100, .6)";
    var x_loc = 0,  y_loc = 0, x_norm = 0, y_norm = 0;

    for ( i = 0; i < l; i++) {
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

        locations.push({'x': x_norm, 'y': y_norm, 'r': radius});
    }

    $('#current_machine_status').on('click', function(e) {
        console.log('click: ' + e.offsetX + '/' + e.offsetY);
        var res = collides(locations, e.offsetX, e.offsetY);
        var rect = res[0];
        if (rect) {
            console.log('collision {' + res[1] + '}: ' + rect.x + '/' + rect.y);
            window.location.href = $SCRIPT_ROOT + "/reserve/" + res[1];
        } else {
            console.log('no collision');
        }
    });
}

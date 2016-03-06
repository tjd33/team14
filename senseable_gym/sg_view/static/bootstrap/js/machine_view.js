function n(num, max, multiplier) {
    return (num + 1) / max * multiplier;
}

function draw_machines(machines){
    var canvas = document.getElementById("current_machine_status");
    var ctx = canvas.getContext("2d");

    // TODO: Get the width and height of the canvas dynamically
    var height = 700;
    var width = 700;

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

    ctx.fillStyle = "rgba(200, 200, 100, .6)";
    var x_loc = 0;
    var y_loc = 0;
    for ( i = 0; i < l; i++) {
        ctx.beginPath();
        x_loc = machines[i].location[0];
        y_loc = machines[i].location[1];
        ctx.arc(n(x_loc, x_max, width),
                n(y_loc, y_max, height),
                10, 50 , 0, Math.PI*2, true);
        ctx.closePath();
        ctx.fill();
    }
}

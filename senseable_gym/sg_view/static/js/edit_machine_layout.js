var current_machine_id = -1;

var get_current_machine_id = function() {
    return current_machine_id;
};

var set_current_machine_id = function(i) {
    current_machine_id = i;
};

function n(num, max, multiplier) {
    return 15 + (num) / max * (multiplier - 30 - size);
}

function collides(machines, x, y) {
    var isCollision = false;
    for (var i = 0, len = machines.length; i < len; i++) {
        var x_machine = machines[i].x, y_machine = machines[i].y, radius = machines[i].r;
        // console.log(Math.sqrt(Math.pow(x_machine - x, 2) + Math.pow(y_machine - y, 2)));
        console.log(Math.sqrt(Math.pow(x_machine - x, 2) + Math.pow(y_machine - y, 2)));
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


var locations = [];
var width, height;
var size = 50;
var radius = size/2;
var mobileOffset = 0;
var icons = [];

var x_max = 0;
var y_max = 0;

function draw_machines(elem, machines){
    
    var x_loc = 0,  y_loc = 0, x_norm = 0, y_norm = 0;
    // Create a list to hold all of the locations of the centers of the machines

    elem.clearRect(0, 0, width, height);

    for ( i = 0; i < machines.length; i++) {  
        x_loc = machines[i].location[0];
        y_loc = machines[i].location[1];
        x_norm = n(x_loc, x_max, width);
        y_norm = n(y_loc, y_max, height);
        elem.drawImage(icons[machines[i].type * 2 + 1], x_norm, y_norm);
 
    } 
    
}

function setup_canvas(auth){
    var canvas = document.getElementById("current_machine_status");
    width = canvas.width;
    height = canvas.height;
    var elem = canvas.getContext("2d");

    $.ajax({
            url: "/_machine_list",
            success: function(result){
                machines = result.machines;
    
            for ( var i = 0; i < machines.length; i++) {
                if (x_max < machines[i].location[0]) {
                    x_max = machines[i].location[0];
                }
                if (y_max < machines[i].location[1]) {
                    y_max = machines[i].location[1];
                }
            }
            
            for ( i = 0; i < machines.length; i++) {
                x_loc = machines[i].location[0];
                y_loc = machines[i].location[1];
                x_norm = n(x_loc, x_max, width);
                y_norm = n(y_loc, y_max, height);

               
                locations.push({'x': x_norm + 25,
                                'y': y_norm + 25,
                                'r': radius,
                                'machine_id': machines[i].machine_id
                });
                
            } 
            
            if(icons[9].complete){
                draw_machines(elem, machines);
            } else {
                icons[9].onload = function() {
                    draw_machines(elem, machines);
                }
            }
            
        }
    });

    
    

    
    
    if(typeof window.orientation !== 'undefined'){ // if mobile
        mobileOffset = 1;
        var pressTimer;
        
        X0 = canvas.getBoundingClientRect().left;
        Y0 = canvas.getBoundingClientRect().top;
        
        // $('#current_machine_status').on('touchstart', function(e) {
            // x = Math.round(e.originalEvent.touches[0].pageX) - X0;
            // y = Math.round(e.originalEvent.touches[0].pageY) - Y0;
            // console.log(e.type + '/' + x + '/' + y);
            // pressTimer = window.setTimeout(function() {
                // reserve(x, y, auth);
            // },500)
        // }).on('click', function(e) {
            // status_popup(elem, e.offsetX, e.offsetY);
        // }).on('touchend', function(e) {
            // console.log('touchend');
            // clearTimeout(pressTimer);
        // });
    } else {
        $('#current_machine_status').on('click', function(e) {
            // status_popup(elem, e.offsetX, e.offsetY);
        });
    }  
    
    var img;
    img = new Image();
    img.src = '/static/images/treadmill_free.png';
    icons.push(img);
    img = new Image();
    img.src = '/static/images/treadmill_busy.png';
    icons.push(img);
    img = new Image();
    img.src = '/static/images/bicycle_free.png';
    icons.push(img);
    img = new Image();
    img.src = '/static/images/bicycle_busy.png';
    icons.push(img);
    img = new Image();
    img.src = '/static/images/elliptical_free.png';
    icons.push(img);
    img = new Image();
    img.src = '/static/images/elliptical_busy.png';
    icons.push(img);
    img = new Image();
    img.src = '/static/images/weightmachine_free.png';
    icons.push(img);
    img = new Image();
    img.src = '/static/images/weightmachine_busy.png';
    icons.push(img);
    img = new Image();
    img.src = '/static/images/rowingmachine_free.png';
    icons.push(img);
    img = new Image();
    img.src = '/static/images/rowingmachine_busy.png';
    icons.push(img);
}


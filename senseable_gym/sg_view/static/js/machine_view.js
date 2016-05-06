var current_machine_id = -1;
var border

var get_current_machine_id = function() {
    return current_machine_id;
};

var set_current_machine_id = function(i) {
    current_machine_id = i;
};

function n(num, max, multiplier) {
    return border + (num) / max * (multiplier - border * 2 - size);
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
var popup;
var size = 50;
var radius = size/2;
var mobileOffset = 0;
var icons = [];

function draw_machines(elem, canvas){
    
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
                if (x_max < machines[i].location[0]) {
                    x_max = machines[i].location[0];
                }
                if (y_max < machines[i].location[1]) {
                    y_max = machines[i].location[1];
                }
            }
            
            //x_max++;
            //y_max++;
            size = Math.max(Math.min((width-2*border)/(x_max+1), (height-2*border)/(y_max+1))-border/2, 40);
            radius = size/2;
            width = canvas.width = Math.max(x_max*size*1.3, width);
            height = canvas.height = Math.max(y_max*size*1.4, height);
            
            elem.clearRect(0, 0, width, height);
            locations = [];
            
            for ( i = 0; i < machines.length; i++) {
                
                x_loc = machines[i].location[0];
                y_loc = machines[i].location[1];
                x_norm = n(x_loc, x_max, width);
                y_norm = n(y_loc, y_max, height);
                if (machines[i].status == "BUSY") {
                    elem.drawImage(icons[machines[i].type * 2 + 1], x_norm, y_norm, size, size);
                } else if (machines[i].status == "RESERVED") {
                    elem.fillStyle = "rgba(0, 0, 200, 1)";
                } else if (machines[i].status == "OPEN") {
                    elem.drawImage(icons[machines[i].type * 2], x_norm, y_norm, size, size);
                } else {
                    elem.fillStyle = "rgba(0, 0, 0, 0.6)";
                }


                
                locations.push({'x': x_norm + 25,
                                'y': y_norm + 25,
                                'r': radius,
                                'machine_id': machines[i].machine_id,
                                'status': machines[i].status,
                                'reservations': []
                });
                
            } 
            
            if(popup!=null){
                popup()
            }
            
            
        }
    });
}

function setup_canvas(auth){
    var canvas = document.getElementById("current_machine_status");
    width = canvas.width;
    height = canvas.height;
    var elem = canvas.getContext("2d");

    window.addEventListener('resize', resizeCanvas, false);
    function resizeCanvas() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight - 51; // would use $('#navbar').height()) but it seems inconsistant
        border = 10 + width/100 
        /*console.log("width: " + width);
        console.log("height: " + height);
        console.log("navbar: " + $('#navbar').height());*/
        
        draw_machines(elem, canvas);
    }
    
    resizeCanvas();
    setInterval(function(){draw_machines(elem, canvas)}, 1000);
    
    if(typeof window.orientation !== 'undefined'){ // if mobile
        mobileOffset = 1;
        var pressTimer;
        
        X0 = canvas.getBoundingClientRect().left;
        Y0 = canvas.getBoundingClientRect().top;
        
        $('#current_machine_status').on('touchstart', function(e) {
            x = Math.round(e.originalEvent.touches[0].pageX) - X0;
            y = Math.round(e.originalEvent.touches[0].pageY) - Y0;
            console.log(e.type + '/' + x + '/' + y);
            pressTimer = window.setTimeout(function() {
                reserve(x, y, auth);
            },500)
        }).on('click', function(e) {
            status_popup(elem, e.offsetX, e.offsetY);
        }).on('touchend', function(e) {
            console.log('touchend');
            clearTimeout(pressTimer);
        });
    } else {
        $('#current_machine_status').on('dblclick', function(e) {
            reserve(e.offsetX, e.offsetY, auth);
        });
        
        $('#current_machine_status').on('click', function(e) {
            status_popup(elem, e.offsetX, e.offsetY);
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

function reserve(x,y, auth){
    
    console.log('double or long click: ' + x + '/' + y);
    var res = collides(locations, x, y);
    var machine = res[0];
    if (machine) {
        if (auth != "True"){
            window.location.href = '/login_before_reserve/1';
            return false;
        }
        console.log('collision {' + res[1] + '}: ' + machine.x + '/' + machine.y);
        // TODO: Only allow users to reserve somethinhg if they are logged in.
        window.location.href = $SCRIPT_ROOT + "/reserve/" + res[0].machine_id;
    } else {
        console.log('no collision');
    }
}

function status_popup(elem, x,y){
    console.log('click: ' + x + '/' + y);
    var res = collides(locations, x, y);
    var machine = res[0];
    var c_m_id = get_current_machine_id();
    if (machine) {
        console.log('(Current Machine, Machine): ' + c_m_id + ', ' + machine.machine_id);
        if (res[1] != c_m_id) {
            set_current_machine_id(res[1]);
            $.ajax({
                
                url: "/_reservation_list/" + machine.machine_id,
                success: function(result){
                    popup = function() {
                        elem.fillStyle="#AAAAAA";
                        x = machine.x - radius;
                        y = machine.y + radius + 5;
                        
                        if(result.reservations.length === 0){
                            elem.fillRect(x, y, 147 + mobileOffset, Math.max(20 * result.reservations.length, 20));
                            elem.font = "15px Arial";
                            elem.fillStyle="#000000";
                            elem.fillText("No reservations soon", x + 3, y + 15);
                        } else {
                            elem.fillRect(x, y, 143 + mobileOffset * 4, Math.max(20 * result.reservations.length, 20));
                            elem.font = "15px Arial";
                            elem.fillStyle="#000000";
                            for (var cr = 0; cr < result.reservations.length; cr++) {
                                elem.fillText(result.reservations[cr].start_time + " to " + result.reservations[cr].end_time, x + 3, y + cr*20 + 15);
                            }
                        }
                    }
                    draw_machines(elem, canvas)
                    
                    /*var reservations_html = 
                    `<table border=1>
                        <tr>
                            <th text-align=center>Start Time</th>
                            <th>End Time </th>
                        </tr>
                    `;
                    // cr for current reservation
                    for (var cr = 0; cr < result.reservations.length; cr++) {
                        reservations_html += '<tr><td> ' + 
                            result.reservations[cr].start_time + 
                            '  </td><td>  ' +
                            result.reservations[cr].end_time +
                            ' </td></tr>';
                    }
                    reservations_html += '</ul>';
                    $('#machine_summary').html(
                        reservations_html
                    );*/
                }
            });
            // window.location.href = $SCRIPT_ROOT + "/reserve/" + res[1];
        }
    } else {
        popup = null;
        draw_machines(elem);
        set_current_machine_id(-1);
    }
}

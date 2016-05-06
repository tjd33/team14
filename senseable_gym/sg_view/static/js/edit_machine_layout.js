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

function reverse_n(num, max, multiplier) {
    return (num - 15) * max / (multiplier - 30 - size);
}

function collides(x, y) {
    var isCollision = false;
    for (var i = 0, len = locations.length; i < len; i++) {
        if (Math.sqrt(Math.pow(locations[i].x - x, 2) + Math.pow(locations[i].y - y, 2)) < radius) {
            return locations[i];
        }
    }
    return isCollision;
}

function calculate_locations(){
    locations = []; 
    for ( i = 0; i < machines.length; i++) {
        x_loc = machines[i].location[0];
        y_loc = machines[i].location[1];
        x_norm = n(x_loc, x_max, width);
        y_norm = n(y_loc, y_max, height);
        
        locations.push({'x': x_norm + radius,
                        'y': y_norm + radius,
                        'r': radius,
                        'machine_id': machines[i].machine_id,
                        'index' : i
        });
    } 
}


var locations = [];
var width, height;
var size = 50;
var radius = size/2;
var mobileOffset = 0;
var icons = [];
var selectedMachine = null;

var x_max = 0, y_max = 0;
var new_x = 0, new_y = 0;
var line = 0, row = 0;

function draw_machines(elem, machines){
    
    var x_loc = 0,  y_loc = 0, x_norm = 0, y_norm = 0;
    // Create a list to hold all of the locations of the centers of the machines

    elem.clearRect(0, 0, width, height);

    for ( i = 0; i < machines.length; i++) {  
        x_loc = machines[i].location[0];
        y_loc = machines[i].location[1];
        x_norm = n(x_loc, x_max, width);
        y_norm = n(y_loc, y_max, height);
        if(!selectedMachine){
            elem.drawImage(icons[machines[i].type], x_norm, y_norm, size, size);
        } else if (machines[i].machine_id != selectedMachine.machine_id){
            elem.drawImage(icons[machines[i].type], x_norm, y_norm, size, size);
        } else if (new_x != -1) {
            elem.drawImage(icons[machines[i].type], new_x, new_y, size, size);
        }
        
 
    } 
    
}

function setup_canvas(auth){
    var canvas = document.getElementById("canvas");
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
            $("#xmax").val(x_max+1);
            $("#ymax").val(y_max+1);

            calculate_locations();
            
            if(icons[4].complete){
                draw_machines(elem, machines);
            } else {
                icons[4].onload = function() {
                    draw_machines(elem, machines);
                }
            }
            
        }
    });
    
    
    $('#canvas').mousedown(function(e){
        var startX = e.offsetX
        var startY = e.offsetY
        selectedMachine = collides(startX, startY)
        draw_machines(elem, machines);
        console.log(selectedMachine)

      
    });
    $('#canvas').mouseup(function(e){
        if (selectedMachine && new_x != -1){
            machine = machines[selectedMachine.index];
            machine.location[0] = line;
            machine.location[1] = row;
            calculate_locations();
        }
        selectedMachine = null;
        new_x = -1;
        new_y = -1;
        draw_machines(elem, machines)
    });
    $('#canvas').mousemove(function(e){
        if(selectedMachine){
            var mouseX = e.offsetX
            var mouseY = e.offsetY
            line = Math.round(reverse_n(mouseX - radius, x_max, width));
            row = Math.round(reverse_n(mouseY - radius, y_max, height));
            new_x = n(line, x_max, width);
            new_y = n(row, y_max, height);
            if (collides(new_x+radius, new_y+radius)){
                new_x = -1;
                new_y = -1;
            }
            draw_machines(elem, machines);
        }

    });
    
    $("#apply").click(function(){
        x_max = $("#xmax").val()-1;
        y_max = $("#ymax").val()-1;       
        calculate_locations();
        draw_machines(elem, machines);
    });
    
    $("#save").click(function(){
        $.ajax({
            type: "POST",
            contentType: "application/json; charset=utf-8",
            url: "/_save_machine_list",
            // data: JSON.stringify({"machines" : {"test1" : "test2"}}),
            data: JSON.stringify(machines),
            success: function(result){}
        });
    });

    


    img = new Image();
    img.src = '/static/images/treadmill_busy.png';
    icons.push(img);
    
    img = new Image();
    img.src = '/static/images/bicycle_busy.png';
    icons.push(img);
    
    img = new Image();
    img.src = '/static/images/elliptical_busy.png';
    icons.push(img);
    
    img = new Image();
    img.src = '/static/images/weightmachine_busy.png';
    icons.push(img);
    
    img = new Image();
    img.src = '/static/images/rowingmachine_busy.png';
    icons.push(img);
}


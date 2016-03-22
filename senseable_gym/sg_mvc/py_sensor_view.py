from math import log10, ceil
from gi.repository import Gtk, Gdk

from senseable_gym.sg_util.machine import MachineStatus


class View(object):
    def __init__(self, model):
        self.model = model

    def get_machines(self):
        return self.model.get_machines()

    def get_machine_status(self, id):
        return self.model.get_machine_status(id)

    def get_machine_location(self, id):
        return self.model.get_machine_location(id)

    def get_machine_type(self, id):
        return self.model.get_machine_type(id)

    def format_line(self, args):
        return "| {0:3} | {1:15} |\n".format(args[0], args[1])

    def display_status(self):
        final_list = self.format_line(["ID", "Machine Type"])

        for machine in self.get_machines():
            machine_id = machine.machine_id
            final_list += self.format_line([machine_id, self.get_machine_type(machine_id)])

        return final_list

    def display_locations(self):
        """
        Prints off a grid of the locations of current machines

        :returns: A string with `\n` separated lines with the location of the each machine

        """
        final_list = list()

        # TODO: Add in the third dimension handler eventually.
        current_machines = self.get_machines()

        current_locations = {}
        for m in current_machines:
            current_locations[m.machine_id] = m.location

        print(current_machines)
        print(current_locations)

        x_max = None
        x_min = None

        y_max = None
        y_min = None

        machine_width = 0

        for loc_ind in current_locations:
            loc = current_locations[loc_ind]
            if any(num is None for num in [x_max, x_min, y_max, y_min]):
                x_min, x_max = loc[0], loc[0]
                y_min, y_max = loc[1], loc[1]

            if loc[0] > x_max:
                x_max = loc[0]

            if loc[0] < x_min:
                x_min = loc[0]

            if loc[1] > y_max:
                y_max = loc[1]

            if loc[1] < y_min:
                y_min = loc[1]

            temp_width = ceil(log10(loc_ind))
            if temp_width > machine_width:
                machine_width = temp_width

        if machine_width % 2 == 0:
            machine_width += 1

        surround_str = " "
        border_str = '-' * (machine_width + 2 * len(surround_str))

        num_side_char = 2
        left_border = border_str[0:num_side_char] + (len(border_str) - num_side_char) * surround_str
        right_border = left_border[::-1]

        y_range = y_max + 2
        x_range = x_max + 2
        for y in range(0, y_range):
            # Initialize the current row
            current_row = []

            # If y is the top or bottom row
            if y in [0, y_range - 1]:
                # Write a string of border_strings
                for temp in range(0, x_range):
                    current_row.append(border_str)
            else:
                for x in range(0, x_range):
                    if x == 0:
                        current_row.append(left_border)
                    elif x == x_max + 1:
                        current_row.append(right_border)
                    else:
                        # We have not yet found a match
                        found = False
                        for loc_ind, loc in current_locations.items():
                            print(loc_ind, loc)
                            if [x, y] == loc[0:2]:
                                # We found a match
                                found = True

                                # Handle colorful strings
                                c_machine = current_machines[loc_ind - 1]

                                if c_machine.color:
                                    additional = 10
                                else:
                                    additional = 0

                                # Add the machine number in the picture
                                current_row.append("{sur}{mac:^{width}}{sur}".format(
                                    sur=surround_str,
                                    mac=str(c_machine.machine_id),
                                    width=machine_width + additional))
                                break

                        if not found:
                            current_row.append(surround_str * (machine_width + 2 * len(surround_str)))

            final_list.append(current_row)

        # print([row for row in final_list])
        # final_string = "\n".join(["{0}{1}{0}".format(surround_str, var) for row in final_list for var in row])

        # TODO: One-liner
        place_holder = []
        for row in final_list:
            temp = "".join(var for var in row)
            place_holder.append(temp)

        final_string = "\n".join(row for row in place_holder)

        return final_string


class GTKView(Gtk.Window, View):
    def __init__(self, model):
        # Make sure our model is in place correctly
        View.__init__(self, model)

        # Initialize our window
        self.window = Gtk.Window(title="Sense-Able Gym Viewer")

        # Create a box that all of our widgets will add to.
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)

        # Store that box into our window
        self.window.add(self.grid)

        # Add any initialization variables that we will use
        self.modifying_machine_id = None

        # Get the gui_display_locations
        # self.gui_display_locations()

        # Gdk.cairo_set_source_pixbuf(cr, pixbuf, 10, 10)
        # img = Gtk.Image()
        # img.set_from_file("treadmill_occupied.jpg")
        # pixbuf = img.get_pixbuf()
        # Gtk.CellRendererPixbuf()

    def bot_row(self):
        self.set_status_switcher()

    def set_status_switcher(self):
        """
        stack = Gtk.Stack()
        label = Gtk.Label()
        label2 = Gtk.Label()
        stack.add_titled(label, "label1", "Free")
        stack.add_titled(label, "label2", "Busy")
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        self.grid.attach(stack_switcher, 0, 50, 2, 1)
        self.grid.attach(stack, 2, 50, 2, 1)
        """

        self.show_status_button = Gtk.Button.new_with_label("Show MachineStatus")
        self.show_status_button.connect("clicked", self.open_status_window)
        self.grid.attach(self.show_status_button, 0, 50, 2, 1)
        # self.grid.add(self.show_status_button)

        self.status_reserved_button = Gtk.Button.new_with_label("Set Reserved")
        self.status_reserved_button.machine_status = MachineStatus.RESERVED
        self.status_reserved_button.connect("clicked", self.set_modifying_machine_status)
        self.grid.attach(self.status_reserved_button, 2, 50, 2, 1)

        self.status_busy = Gtk.Button.new_with_label("Set Busy")
        self.status_busy.machine_status = MachineStatus.BUSY
        self.status_busy.connect("clicked", self.set_modifying_machine_status)
        self.grid.attach(self.status_busy, 4, 50, 2, 1)

        self.status_open = Gtk.Button.new_with_label("Set Open")
        self.status_open.machine_status = MachineStatus.OPEN
        self.status_open.connect("clicked", self.set_modifying_machine_status)
        self.grid.attach(self.status_open, 6, 50, 2, 1)
        # self.grid.add(self.status_open)

    def main(self):
        Gtk.main()

    def refresh_machines(self, widget):
        current_machines = self.get_machines()

        for m_id, machine in current_machines.items():
            loc = machine.get_location()

            temp_button = Gtk.Button(label=str(m_id))

            temp_button.connect("clicked", self.set_modifying_machine_id)
            self.grid.attach(temp_button, loc[0], loc[1], 1, 1)

    def set_modifying_machine_id(self, button):
        print('You are now modifying machine `{0}`'.format(button.props.label))
        self.modifying_machine_id = int(button.props.label)

    def gui_display_locations(self):
        current_machines = self.get_machines()

        max_x = 0
        max_y = 0

        for mac in current_machines:
            if mac.location[0] > max_x:
                max_x = mac.location[0]

            if mac.location[1] > max_y:
                max_y = mac.location[1]

        max_x += 1
        max_y += 1

        for i in range(1, max_x):
            self.grid.attach(Gtk.Button(label='-----'), i, 0, 1, 1)
            self.grid.attach(Gtk.Button(label='-----'), i, max_y, 1, 1)

        for i in range(1, max_y):
            self.grid.attach(Gtk.Button(label='---  '), 0, i, 1, 1)
            self.grid.attach(Gtk.Button(label='  ---'), max_x, i, 1, 1)

        for machine in current_machines:
            loc = machine.location

            temp_button = Gtk.Button(label=str(machine.machine_id))

            """
            temp_map = temp_button.get_colormap()
            color = temp_map.alloc_color("red")

            style = temp_map.get_style().copy()
            style.bg[Gtk.STATE_NORMAL] = color

            temp_button.set_style(style)
            """

            temp_button.override_background_color(Gtk.StateFlags.PRELIGHT, Gdk.RGBA(1, 0, 1, .5))

            temp_button.connect("clicked", self.set_modifying_machine_id)
            self.grid.attach(temp_button, loc[0], loc[1], 1, 1)

        for x in range(1, max_x):
            for y in range(1, max_y):
                blank_button = Gtk.Button()
                self.grid.attach(blank_button, x, y, 1, 1)

    def start_gui(self, x_size=400, y_size=400):
        """
        Start gui starts the gui of the current View

        :x_size: The size of the gui in x
        :y_size: The size of the gui in y
        :returns: None

        """
        self.window.set_border_width(10)
        self.bot_row()
        self.gui_display_locations()
        self.window.connect("delete-event", Gtk.main_quit)
        self.window.show_all()
        self.main()

    def set_modifying_machine_status(self, button):
        if self.modifying_machine_id is None:
            # TODO: Raise an error?
            return

        self.model.set_machine_status(self.modifying_machine_id, button.machine_status)
        print("Set Machine `{0}` to MachineStatus `{1}`".format(self.modifying_machine_id, button.machine_status))

    def open_status_window(self, button):
        # Open a status window
        temp_window = Gtk.Window(title="Current MachineStatus")

        temp_window.set_default_size(400, 100)

        temp_window.liststore = Gtk.ListStore(str, str)

        temp_id = str(self.modifying_machine_id)
        temp_status = str(self.model.get_machine_status(int(temp_id)))
        temp_window.liststore.append([temp_id, temp_status])

        treeview = Gtk.TreeView(model=temp_window.liststore)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Machine ID", renderer_text, text=0)
        treeview.append_column(column_text)

        renderer_editabletext = Gtk.CellRendererText()
        renderer_editabletext.set_property("editable", True)

        column_editabletext = Gtk.TreeViewColumn("Current MachineStatus",
                                                 renderer_editabletext, text=1)
        treeview.append_column(column_editabletext)

        renderer_editabletext.connect("edited", self.text_edited)

        temp_window.add(treeview)

        temp_window.show_all()

    def text_edited(self, widget, path, text):
        self.liststore[path][1] = text

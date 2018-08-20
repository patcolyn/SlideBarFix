import os
import sys
import time
import xinput
import pynput
import configparser
from bisect import bisect_left
from operator import attrgetter

'''Todo
Implement 360 GHWT controller keybinds
Guitar selection
Add DirectInput support for PS3 controllers
GUI
Multiple devices active
Bind to controller button support
Suspend hotkey
'''

# List for key presses
presses = ([0], [0, 1], [1],
           [0, 1, 2], [1, 2], [],
           [0, 2], [2], [0, 1, 2, 3],
           [0, 2, 3], [1, 2, 3], [2, 3],
           [0, 1, 3], [0, 3], [1, 3],
           [3], [0, 1, 2, 3, 4], [0, 1, 3, 4],
           [0, 2, 3, 4], [0, 3, 4], [1, 2, 3, 4],
           [1, 3, 4], [2, 3, 4], [3, 4],
           [0, 1, 2, 4], [0, 1, 4], [0, 2, 4],
           [0, 4], [1, 2, 4], [1, 4],
           [2, 4], [4])

# List for input values of x-axis
x_axis_values = (-0.4196078431372549, -0.3137254901960784, -0.2,
                 -0.10588235294117647, -0.10196078431372549, 0.0,
                 0.09803921568627451, 0.10196078431372549, 0.17254901960784313,
                 0.17647058823529413, 0.1803921568627451, 0.1843137254901961,
                 0.27450980392156865, 0.2784313725490196, 0.2823529411764706,
                 0.28627450980392155, 0.37254901960784315, 0.3764705882352941,
                 0.3803921568627451, 0.3843137254901961, 0.38823529411764707,
                 0.39215686274509803, 0.396078431372549, 0.4,
                 0.47058823529411764, 0.4745098039215686, 0.47843137254901963,
                 0.4823529411764706, 0.48627450980392156, 0.49019607843137253,
                 0.49411764705882355, 0.4980392156862745)

# List for names of button combinations
colors = ("green", "green & red", "red",
          "green, red & yellow", "red & yellow", "",
          "green & yellow", "yellow", "green, red, yellow & blue",
          "green, yellow & blue", "red, yellow & blue", "yellow & blue",
          "green, red & blue", "green & blue", "red & blue",
          "blue", "green, red, yellow, blue & orange", "green, red, blue & orange",
          "green, blue & orange", "green, yellow, blue & orange", "red, yellow, blue & orange",
          "red, blue & orange", "yellow, blue & orange", "blue & orange",
          "green, red, yellow & orange", "green, red & orange", "green, yellow & orange",
          "green & orange", "red, yellow & orange", "red & orange",
          "yellow & orange", "orange")


# List for keybind names
key_names = ('Green',
             'Red',
             'Yellow',
             'Blue',
             'Orange',
             'Suspend',
             'Continue')

# List of default keybinds
keybinds = ['q', 'w', 'e', 'r', 't', 'o', 'p']
key_set = [0, 1, 2, 3, 4, 5]


def binary_search(a, x, lo=0, hi=None):  # can't use a to specify default for hi

    hi = hi if hi is not None else len(a)  # hi defaults to len(a)
    pos = bisect_left(a, x, lo, hi)  # find insertion position
    return (pos if pos != hi and a[pos] == x else -1)  # don't walk off the end


def write_ini(config):

    # Write config file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def init_joy():

    # Get list of joysticks
    joysticks = xinput.XInputJoystick.enumerate_devices()
    device_numbers = list(map(attrgetter('device_number'), joysticks))

    # Print found devices
    print('Found {} devices, {}'.format(len(joysticks), device_numbers))

    # If no joysticks found, exit
    if not joysticks:
        input('No devices found, press enter to exit.')
        sys.exit(0)

    # Set joy to first joystick
    joy = joysticks[0]
    print('Using device {}'.format(joy.device_number))

    # Show battery info
    battery = joy.get_battery_information()
    print('Battery level: {}\n'.format(battery[1]))

    return joy


def bind_keys():

    # Iterate over key binds
    for i in range(len(keybinds)):
        # Bind keys
        keybinds[i] = input('Enter key to bind to {}: '.format(key_names[i]))
        print('')


def create_ini(config):

    # Slider positions header
    config['guitar_type'] = {}

    # Key binds header
    config['key_binds'] = {}

    # Key binds values
    for i in range(len(keybinds)):
        config['key_binds'][key_names[i]] = str(keybinds[i])


# Initialise
c_one = init_joy()  # Controller
keyboard = pynput.keyboard.Controller()  # Keyboard input
down_keys_old = []  # Global key tracker
con = configparser.ConfigParser()  # Config parser

# If no config, query settings
if not os.path.exists('config.ini'):
    print('No config file found, creating config file\n')
    bind_keys()
    create_ini(con)
    write_ini(con)

# Read in config file
con.read('config.ini')

# Move config into keybinds list
for index, key in enumerate(con['key_binds']):
    keybinds[index] = con['key_binds'][key]

# Main output loop
print("SlideBarFix has started!".format(keybinds[5]))
while True:

    # Dispatch slide events
    c_one.dispatch_events()
    time.sleep(0.001)

    # Slide event
    @c_one.event
    def on_axis(axis, value):

        global down_keys_old

        # Assign keys
        keysindex = binary_search(x_axis_values, value)
        down_keys = presses[keysindex]

        # Send down keys, do not resend keys already down
        for i in list(set(down_keys) - set(down_keys_old)):
            keyboard.press(keybinds[i])

        # Key user feedback
        print("Keys: {}".format(colors[keysindex]))

        # Send up all other keys
        for i in list(set(down_keys_old) - set(down_keys)):
            keyboard.release(keybinds[i])

        # Update old values
        down_keys_old = down_keys

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

  Copyright (c) 2016-2017 Martin Jablecnik
  Authors: Martin Jablecnik
  Description: Program for generating automatic scripts.
  
"""

import os, sys
from time import sleep, time
import config, keys
from pynput import mouse, keyboard



def write_line(file, text):
    file.write( text )
    print( text.splitlines()[0] )


def record(raw_file):
    f = open(raw_file, 'w')
    f.close()
    f = open(raw_file, 'a')
    start_time = time()

    def on_press(key):
        write_line(f, 'keyboard|press|{0}|{1}\n'.format( key, round(time() - start_time, 4) ))

    def on_release(key):
        write_line(f, 'keyboard|release|{0}|{1}\n'.format( key, round(time() - start_time, 4) ))
        if key == keyboard.Key.ctrl_r:
            return False


    t1 = keyboard.Listener(on_press=on_press, on_release=on_release)
    t1.start()



    def on_move(x, y):
        write_line( f, 'mouse|move|{0}|{1}\n'.format( (x, y), round(time() - start_time, 4) ))

    def on_click(x, y, button, pressed):
        write_line( f, 'mouse|{0}|{1}|{2}\n'.format( 'press' if pressed else 'release', button, round(time() - start_time, 4) ))

    def on_scroll(x, y, dx, dy):
        write_line( f, 'mouse|scroll-{0}|{1}|{2}\n'.format( 'down' if dy < 0 else 'up', (x, y), round(time() - start_time, 4) ))

    t2 = mouse.Listener( on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    t2.start()

    while t1.running:
        sleep(0.1)
        if not t1.running:
            t2.stop()


    f.close()
    print "closing"



def compile_keyboard(f, data):
    def transform_value(value):                                                  
        if value[0] == 'u':
            return keys.transform(value[2:-1].replace('\\x','U'))

        elif value[0:3] == 'Key':
            special_key = value.split('.')[1]
            return keys.transform(special_key)


    transformed_value = transform_value(unicode(data['value']))
    if data['event'] == 'press':
        if transformed_value != None:
            write_line(f, 'xdotool keydown {0}\n'.format( transformed_value ))

    elif data['event'] == 'release':
        if transformed_value != None:
            write_line(f, 'xdotool keyup {0}\n'.format( transformed_value ))


def compile_mouse(f, data):
    def transform_value(value):
        if value == "Button.left":
            return 1
        elif value == "Button.middle":
            return 2
        elif value == "Button.right":
            return 3

    transformed_value = transform_value(data['value'])
    if data['event'] == 'press':    
        if transformed_value != None:
            write_line(f, 'xdotool mousedown {0}\n'.format( transformed_value ))
    elif data['event'] == 'release':
        if transformed_value != None:
            write_line(f, 'xdotool mouseup {0}\n'.format( transformed_value ))
    elif data['event'] == 'move':
        x, y = eval(data['value'])
        write_line(f, 'xdotool mousemove {0} {1}\n'.format( x, y ))
    elif data['event'] == 'scroll-down':
        write_line(f, 'xdotool click 5\n')
    elif data['event'] == 'scroll-up':
        write_line(f, 'xdotool click 4\n')
        


# generating of macro code
def compile(raw_file, output_file, speed):
    with open(raw_file,'r') as f: 
        lines = f.read().splitlines()

    f = open(output_file, 'w')
    f.close()

    f = open(output_file, 'a')
    previous_time = 0.0

    for i in range(len(lines)):
        data = lines[i].split('|')
        data = dict(zip({ "input", "value", "event", "time" }, data))

        write_line(f, "sleep {0}\n".format( ( float(data['time']) - previous_time) / speed ))

        if data['input'] == 'keyboard':
            compile_keyboard(f, data)
        elif data['input'] == 'mouse':
            compile_mouse(f, data)

        previous_time = float(data['time'])

    f.close()




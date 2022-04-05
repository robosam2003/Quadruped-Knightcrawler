from __future__ import division
import time
import math
import numpy as np
import sys

import subprocess
import pygame

# Import the PCA9685 module.
import Adafruit_PCA9685


# Uncomment to enable debug output.
#import logging
#logging.basicConfig(level=logging.DEBUG)

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Configure min and max servo pulse lengths
servo_min = 110  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096

# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 60       # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)
# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)



#ps3 stuff
pygame.init()
clock = pygame.time.Clock() #added line
ps3 = pygame.joystick.Joystick(0)
ps3.init()



#__________________________________________________________________________
#__________________________________________________________________________


def angle(channel, degrees):
    degrees = int((degrees*(2.8))+servo_min)
    pwm.set_pwm(channel, 0, degrees)

def setzero():
    for x in range(0, 16):
        angle(x, 0)

def testservo():
    channel = int(input("CHANNEL: "))
    while True:
        i = int(input("ENTER ANGLE "))
        if i == -3:
            testservo()
        else:
            angle(channel, i)
            time.sleep(0.6)

class Leg:
    def __init__(self, whichleg, c0, c1, c2, l):
        self.whichleg = whichleg
        self.c0 = c0
        self.c1 = c1
        self.c2 = c2
        self.l = l
        
        
    
    
    def angles(self, a0, a1, a2):
        #config 'both knees inwards'
        '''if self.whichleg == 1:  
            angle(self.c0, (90+a0))
            angle(self.c1, (180+a1))
            angle(self.c2, (180-a2)) #left
        if self.whichleg == 2:

            angle(self.c0, (90-a0))
            angle(self.c1, (-a1)) # right
            angle(self.c2, (a2))
        if self.whichleg == 3:
            angle(self.c0, (90-a0))
            angle(self.c1, (-a1))
            angle(self.c2, (a2))#left
        if self.whichleg == 4:
            angle(self.c0, (90+a0))
            angle(self.c1, (180+a1)) #right
            angle(self.c2, (180-a2))'''

        #Config 'both knees backwards'
        if self.whichleg == 1:
            angle(self.c0, (90+a0))
            angle(self.c1, (180+a1))
            angle(self.c2, (180-a2)) #left
        if self.whichleg == 2:

            angle(self.c0, (90-a0))
            angle(self.c1, (-a1)) # right
            angle(self.c2, (a2))
        if self.whichleg == 3:
            angle(self.c0, (90-a0))
            angle(self.c1, (180+a1))
            angle(self.c2, (180-a2))#left
        if self.whichleg == 4:
            angle(self.c0, (88+a0))
            angle(self.c1, (-a1)) #right
            angle(self.c2, (a2))
        
        #1    2
        #
        #3    4

        
    def findAngles(self, x, y, z):
        l1 = 10.5  # length l1, l2, in the cosine stuff
        l2 = 10.5
        if x == 0:
            x = 0.1
        if y == 0:
            y = 0.1
            
        a0 = math.degrees(math.atan(z/y)) # z axis angle 
        dist = math.sqrt(x**2 + y**2 +z**2) # pythag
        d1 = math.degrees(math.atan2(y,x)) # tan^-1(x/y)
        d2 = math.degrees(math.acos((dist**2 + l1**2 - l2**2)/(2*l1*dist)))
        a1 = d1 + d2 # shoulder
        a2 = math.degrees(math.acos((l1**2 + l2**2 - dist**2)/(2*l1*l2))) #elbow
        print(a0)
        print(a1)
        print(a2)
        print(" ")
        return int(a0), int(a1), int(a2)

    def forwardstep(self, x, li):
        a0, a1, a2 = self.findAngles(li[x][0], li[x][1], li[x][2]) # x, y, z
        self.angles(a0, a1, a2)
        time.sleep(0.011)

    def backstep(self, x ,li):
        # ALTER FOR FASTER PROCESSING
        self.forwardstep(-x, li)
        
#--------------------------------------------------------------------------
z1 = 1
z2 = -3
def mappingLin(lim1, lim2, pn):
    l = []
    x = lim1
    depth = 30 # lower number = deeper depth
    while x != lim2:
        y = (x**2/depth) - 16/depth -18
        z = z1
        l.append([])
        l[-1].append(float(x))
        l[-1].append(float(y))
        l[-1].append(float(z))
        x += pn
    return l

def mappingLinBack(lim1, lim2, pn):
    l = []
    x = lim1
    depth = 30 # lower number = deeper depth
    while x != lim2:
        y = (x**2/depth) - 16/depth -20
        z = z1
        l.append([])
        l[-1].append(float(x))
        l[-1].append(float(y))
        l[-1].append(float(z))
        x += pn
    return l

def mappingParab(lim1, lim2, pn):
    l = []
    x = lim1
    height = 3 # lower number the higher the leg
    while x != lim2:
        y = (-x**2/height) + 16/height -18
        z = z2
        l.append([])
        l[-1].append(float(x))
        l[-1].append(float(y))
        l[-1].append(float(z))
        x += pn
    return l

def mappingParabBack(lim1, lim2, pn):
    l = []
    x = lim1
    height = 2.5 # lower number the higher the leg
    while x != lim2:
        y = (-x**2/height) + 16/height -20
        z = z2
        l.append([])
        l[-1].append(float(x))
        l[-1].append(float(y))
        l[-1].append(float(z))
        x += pn
    return l


def mappingSideParab(lim1, lim2, pn):
    l = []
    z = lim1
    height = 4 # lower number the higher the leg
    while z != lim2:
        y = (-z**2/height) + 16/height -20
        x = 0
        l.append([])
        l[-1].append(float(x))
        l[-1].append(float(y))
        l[-1].append(float(z))
        z += pn
    return l

def mappingSideLin(lim1, lim2, pn):
    l = []
    z = lim1
    depth = 30 # lower number the higher the leg
    while z != lim2:
        y = (z**2/depth) - 16/depth -20
        x = 0
        l.append([])
        l[-1].append(float(x))
        l[-1].append(float(y))
        l[-1].append(float(z))
        z += pn
    return l


limi1 = -3
limi2 = 3
res = 0.5
res1 = 2
l1 = mappingLin(limi2, limi1, -res) + mappingParab(limi1, limi2, res1)
l1 = np.array(l1)
l1 = np.roll(l1, -12)
#frontright

l1t2 = mappingLinBack(limi2, limi1, -res) + mappingParabBack(limi1, limi2, res1)
l1t2 = np.array(l1t2)
l1t2 = np.roll(l1t2, -12)
#backleft

l2 = mappingParab(limi1, limi2, res1) + mappingLin(limi2, limi1, -res)
l2 = np.array(l2)
l2 = np.roll(l2, 0)
#frontleft

l2t2 = mappingParabBack(limi1, limi2, res1) + mappingLinBack(limi2, limi1, -res)
l2t2 = np.array(l2t2)
l2t2 = np.roll(l2t2, 0)
#backright


lside1 = mappingSideLin(limi2, limi1, -res) + mappingSideParab(limi1, limi2, res1)
lside1 = np.array(lside1)
lside1 = np.roll(lside1, -21) #side

lside2 = mappingSideParab(limi1, limi2, res1) + mappingSideLin(limi2, limi1, -res)
lside2 = np.array(lside2)
lside2 = np.roll(lside2, 0) #side

#Leg class objects
frontright = Leg(2, 13, 14, 15, l1)
frontleft = Leg(1, 0, 1, 2, l1) # legtype, c0, c1, c2, l
backleft = Leg(3, 4, 5, 6, l1)
backright = Leg(4, 8, 9, 10, l1)        


#-------------------------------------------------------------------------
def dogWalkLeft():
    for x in range(0, len(lside1)):
        frontright.forwardstep(-x, lside1)
        backright.forwardstep(x, lside2)
        frontleft.forwardstep(-x, lside2)
        backleft.forwardstep(x, lside1)
def dogWalkRight():
    for x in range(0, len(lside1)):
        frontright.forwardstep(-x, lside1)
        backright.forwardstep(-x, lside2)
        frontleft.forwardstep(x, lside2)
        backleft.forwardstep(x, lside1)

    
def dogTurnLeft():
    for x in range(0, len(lside1)):
        frontright.forwardstep(x, lside1)
        backright.forwardstep(-x, lside2)
        frontleft.forwardstep(-x, lside2)
        backleft.forwardstep(x, lside1)
def dogTurnRight():
    for x in range(0, len(lside1)):
        frontright.forwardstep(-x, lside1)
        backright.forwardstep(x, lside2)
        frontleft.forwardstep(x, lside2)
        backleft.forwardstep(-x, lside1)

    

def dogWalkFast():
    for x in range(0, len(l1)):
        frontright.forwardstep(-x, l1)
        backright.forwardstep(-x, l2t2)
        frontleft.forwardstep(-x, l2)
        backleft.forwardstep(-x, l1t2)
def dogWalkBack():
    for x in range(0, len(l1)):
        frontright.forwardstep(x, l1t2)
        backright.forwardstep(x, l2)
        frontleft.forwardstep(x, l2t2)
        backleft.forwardstep(x, l1)
        

def gallop():
    for x in range(0, len(l1)):
        frontright.forwardstep(-x, l1)
        backright.forwardstep(-x, l2)
        frontleft.forwardstep(-x, l1)
        backleft.forwardstep(-x, l2)
def dogWalkSlow():
    for x in range(0, len(l1)):
        frontright.backstep(x, l1)
        backright.forwardstep(-x, l2t2)
        frontleft.forwardstep(-x, l2)
        backleft.forwardstep(-x, l1t2)
'''     
def dwm1():
    for x in range(0, len(l1)):
        frontright.forwardstep(-x, l2) 
def dwm2():
    for x in range(0, len(l1)):
        backright.forwardstep(-x, l1)
def dwm3():
    for x in range(0, len(l1)):
        frontleft.forwardstep(-x, l2)
def dwm4():
    for x in range(0, len(l1)):
        backleft.forwardstep(-x, l1)
def dogWalkMedium():
    dwm1()
    #dwm2()
    dwm3()
    dwm4()
    dwm2()
def dogWalkMedium2():
    dwm4()
    dwm3()
    dwm2()
    dwm1()
l11 = l1
l12 = l1[5:14] + l1[0:3]
l13 = l1[7:14] + l1[0:7]
l14 = l1[11:14] + l1[0:10]
def forwardMotion2():
    for x in range(0, len(l1)-1):
        frontright.forwardstep(x, l11)
        backleft.forwardstep(-x, l12)
        frontleft.forwardstep(x, l13)
        backright.forwardstep(-x, l14)
'''  

def stand():
    
    a0, a1, a2 = frontright.findAngles(0, -20, z1)
    frontright.angles(a0, a1, a2)
    frontleft.angles(a0, a1, a2)
    #time.sleep(0.1)
    backright.angles(a0, a1, a2)
    backleft.angles(a0, a1,  a2)
    time.sleep(0.3)

def goto():
    a0, a1, a2 = frontleft.findAngles(10, -10, 11)
    frontright.angles(a0, a1, a2)
    frontleft.angles(a0, a1, a2)
    #time.sleep(0.5)
    backright.angles(a0, a1, a2)
    backleft.angles(a0, a1,  a2)
    time.sleep(0.7)
    a0, a2, a3 = frontleft.findAngles(4, -4, 8)
    frontright.angles(a0, a1, a2)
    frontleft.angles(a0, a1, a2)
    #time.sleep(0.5)
    backright.angles(a0, a1, a2)
    backleft.angles(a0, a1,  a2)
    time.sleep(0.7)

def sit():
    a0, a1, a2 = frontleft.findAngles(0, -10, z1)
    backright.angles(a0, a1, a2)
    backleft.angles(a0, a1,  a2)
    a0, a1, a2 = frontleft.findAngles(0, -20, z1)
    frontright.angles(a0, a1, a2)
    frontleft.angles(a0, a1, a2)
    time.sleep(0.5)
    

def main():
    stand()   
    while True:
        pygame.event.pump()
        axis = [ps3.get_axis(0),ps3.get_axis(1),ps3.get_axis(3),ps3.get_axis(4), ps3.get_axis(5),ps3.get_axis(2)]
        print(axis)
        if axis[3] < -0.5:
            dogWalkFast() #forward
        elif axis[3] > 0.5:
            dogWalkBack() #back
            
        elif axis[2] < -0.5:
            dogTurnLeft() #left
        elif axis[2] > 0.5:
            dogTurnRight() #right
            
        elif axis[0] < -0.5:
            dogWalkLeft()
        elif axis[0] > 0.5:
            dogWalkRight()
        elif axis[4] > 0:
            stand()
        elif axis[5] > 0:
            sit()
        else:
            continue
            
            
try:
    main()
except KeyboardInterrupt:
    stand()
    time.sleep(0.5)
    sys.exit()

import pygame
import numpy as np
from time import sleep
from math import pi, cos, sin, sqrt, atan2

from src.utils.transformations import xyz_rotation_matrix, new_coordinates
from src.kinematics.kinematics import IK

import src.motion.Spot as Spot
Spot = Spot.Spot()
import src.gravity.Gravity as SpotCG
SpotCG = SpotCG.SpotCG()
import src.animation.Animacion as Animation
SpotAnim = Animation.SpotAnime()


pygame.init()
screen = pygame.display.set_mode((600, 600)) 
pygame.display.set_caption("SPOTMICRO")
clock = pygame.time.Clock()

""" Joystick Init """
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

joypos =np.zeros(6) #xbox one controller has 6 analog inputs
joybut = np.zeros(10) #xbox one controller has 10 buttons

""" XBOX One controller settings """
""" use Essai_Joystick_01.py utility to find out the right parameters """
nj = 6 # Number of joysticks
nb = 10 # number of buttons

but_walk = 7
but_sit = 2
but_lie = 3
but_twist = 1
but_pee = 0
but_move = 4
but_anim = 5

pos_frontrear = 4
pos_leftright = 3
pos_turn = 0    
pos_rightpaw = 5
pos_leftpaw = 2

#state
Free = True #Spot is ready to receive new command
walking = False #walking sequence activation
stop = False # walking stop sequence activation
lock = False

t = 0 #Initializing timing/clock
tstart = 1 #End of start sequence
tstop = 1000 #Start of stop sequence by default
tstep = 0.01 #Timing/clock step
tstep1 = tstep

distance =[] #distance to support polygon edge
timing = [] #timing to plot distance

cw = 1
walking_speed = 0
walking_direction = 0
#steeering = 1e6
module = 0

""" Walking parameters """
b_height = 200
h_amp = 100# horizontal step length
v_amp = 40 #vertical step length
track = 58.09
x_offset = 0 #body offset in x direction 
stepl = 0.125 #duration of leg lifting typically between 0.1 and 0.2
steering =200 #Initial steering radius (arbitrary)

Angle = [0, 0]

""" theta_spot = [ángulo x del suelo, ángulo y del suelo, ángulo z del cuerpo en el espacio,
ángulo x del cuerpo, ángulo y del cuerpo, ángulo z del cuerpo] """
#theta xyz of ground then theta xyz of frame/body
theta_spot = [0,0,0,0,0,0]

stance = [True, True, True, True] # True = foot on the ground, False = Foot lifted


x_spot = [0, x_offset, Spot.xlf, Spot.xrf, Spot.xrr, Spot.xlr,0,0,0]
y_spot = [0,0,Spot.ylf+track, Spot.yrf-track, Spot.yrr-track, Spot.ylr+track,0,0,0]
z_spot = [0,b_height,0,0,0,0,0,0,0]

# FL, FR, RR, RL
pos_init = np.array([[-x_offset, -x_offset, -x_offset, -x_offset],
                     [track, -track, -track, track],
                     [-b_height, -b_height, -b_height, -b_height]])

thetalf = IK(pos_init[:,0], 1)[0]
thetarf = IK(pos_init[:,1], -1)[0]
thetarr = IK(pos_init[:,2], -1)[0]
thetalr = IK(pos_init[:,3], 1)[0]

CG = SpotCG.CG_calculation (thetalf,thetarf,thetarr,thetalr)
#Calculation of CG absolute position
M = xyz_rotation_matrix(theta_spot[0],theta_spot[1],theta_spot[2],False)
CGabs = new_coordinates(M,CG[0],CG[1],CG[2],x_spot[1],y_spot[1],z_spot[1])
dCG = SpotCG.CG_distance(x_spot[2:6],y_spot[2:6],z_spot[2:6],CGabs[0],CGabs[1],stance)

x_spot = [0, x_offset, Spot.xlf, Spot.xrf, Spot.xrr, Spot.xlr,CG[0],CGabs[0],dCG[1]]
y_spot = [0,0,Spot.ylf+track, Spot.yrf-track, Spot.yrr-track, Spot.ylr+track,CG[1],CGabs[1],dCG[2]]
z_spot = [0,b_height,0,0,0,0,CG[2],CGabs[2],dCG[3]]

pos = [pos_init,theta_spot,x_spot,y_spot,z_spot]

continuer = True

while (continuer):
    clock.tick(50)     
    for event in pygame.event.get(): # User did something.
        if event.type == pygame.QUIT: # If user clicked close window.
            continuer = False     
            
    for i in range (0,nj): #read analog joystick position
        joypos[i] = joystick.get_axis(i)                        
    for i in range (0,nb):  #read buttons
        joybut[i] = joystick.get_button(i)
    
    """Animation"""
    
    if (joybut[but_walk] == 0)&(joybut[but_pee] == 0)&(joybut[but_twist] == 0)&(joybut[but_sit] == 0)&(joybut[but_lie] == 0)&(joybut[but_anim] == 0)&(joybut[but_move] == 0)&(lock == True):
        lock = False
        print("lock")
    
    #WALKING        
    if (joybut[but_walk] == 1)&(walking == True)&(stop == False)&(lock == False): #Quit walk mode
        stop = True
        lock = True
        if (abs(t-int(t))<=tstep):
            tstop = int(t)
        else:
            tstop = int(t)+1
        
        if (t==0):
            tstop = 1
    
    if (joybut[but_walk] == 1)&(walking == False)&(Free == True): #Enter in walk mode
        walking = True
        stop = False
        Free = False
        t=0
        tstart = 1
        tstop = 1000
        lock = True
        trec = int(t)
        print("walking")
        
    if (walking == True):  
        coef = 1.2
        #set walking direction and speed            
        #set steering radius
        
        if (joybut[but_move] == True)&(tstep > 0)&(lock == False):
            tstep = 0
            lock = True
            
        if (joybut[but_move] == True)&(tstep == 0)&(lock == False):
            tstep = tstep1
            lock = True    
            
        print (tstep)    
            
        if (abs(joypos[pos_leftright])>0.2)|(abs(joypos[pos_frontrear])>0.2)|(stop == True):                
            t=t+tstep
            trec = int(t)+1
            
            module_old = module
            walking_direction_old = walking_direction
            steering_old = steering
            
            x_old = module_old*cos(walking_direction_old)
            y_old = module_old*sin(walking_direction_old)
            
            #update request
            module = sqrt(joypos[pos_leftright]**2 + joypos[pos_frontrear]**2)
            walking_direction = (atan2(-joypos[pos_leftright],-joypos[pos_frontrear])%(2*pi)+pi/2)%(2*pi)
            
            x_new = module*cos(walking_direction)
            y_new = module*sin(walking_direction)
                            
            #steering update                
            if (abs(joypos[pos_turn]) < 0.2):
                cw = 1
                if (steering<2000):
                    steering = min(1e6,steering_old*coef) 
                else:
                    steering = 1e6
            else:
                steering = 2000-(abs(joypos[2])-0.2)*2000/0.8+0.001
                if ((steering/steering_old)>coef):                       
                    steering = steering_old*coef
                if ((steering_old/steering)>coef):                       
                    steering = steering_old/coef   
                    if (steering <0.001):
                        steering = 0.001
                cw = -np.sign(joypos[2])
            
            
            gap = sqrt((x_new-x_old)**2+(y_new-y_old)**2)
            
            if (gap>0.01):
                x_new = x_old+ (x_new-x_old)/gap*0.01
                y_new = y_old+ (y_new-y_old)/gap*0.01
                module = sqrt(x_new**2+y_new**2)
                walking_direction = atan2(y_new,x_new)
                                                    
            #reduces speed sideways and backwards  
            min_h_amp = h_amp*(1/2e6*steering+1/2)               
            xa = 1+cos(walking_direction-pi/2) 
            walking_speed = min (1, module) * min(h_amp,min_h_amp) * (1/8*xa**2+1/8*xa+1/4)                
            
            
        if ((abs(joypos[pos_leftright])<0.2)&(abs(joypos[pos_frontrear])<0.2))&(stop == False):  
            t=t+tstep                
            module = max (0, module - 0.01)
            walking_speed = module* h_amp * ((1+cos(walking_direction-pi/2))/2*0.75+0.25)
            if (steering<2000):
                steering = min(1e6,steering*coef) 
            else:
                steering = 1e6
            cw=1    
            if (t>trec): 
                t=trec

        """ 
        If you have an IMU that measures Angle[0] and Angle [1] 
        values can be transferred to theta_spot
        """                
        theta_spot[3] = Angle [0] # angle around x axis
        theta_spot[4] = Angle [1] # angle around y axis
        theta_spot[0] = Angle [0] # angle around x axis
        theta_spot[1] = Angle [1] # angle around y axis
                    
        if (t< tstart):           
            pos = Spot.start_walk_stop (track,x_offset,steering,walking_direction,cw,walking_speed,v_amp,b_height,stepl,t,tstep,theta_spot,x_spot,y_spot,z_spot,'start')
        else:
            if (t<tstop):
                pos = Spot.start_walk_stop (track,x_offset,steering,walking_direction,cw,walking_speed,v_amp,b_height,stepl,t,tstep,theta_spot,x_spot,y_spot,z_spot,'walk')
            else:
                pos = Spot.start_walk_stop (track,x_offset,steering,walking_direction,cw,walking_speed,v_amp,b_height,stepl,t,tstep,theta_spot,x_spot,y_spot,z_spot,'stop')    
        
        pos_init = pos[0]
        theta_spot = pos[1]
        x_spot = pos[2]
        y_spot = pos[3]                 
        z_spot = pos[4]
        
        
        if (t>(tstop+1-tstep)):
            stop = False
            walking = False
            Free = True
        
    xc = steering* cos(walking_direction)
    yc = steering* sin(walking_direction)
        
    center_x = x_spot[0]+(xc*cos(theta_spot[2])-yc*sin(theta_spot[2])) #absolute center x position
    center_y = y_spot[0]+(xc*sin(theta_spot[2])+yc*cos(theta_spot[2])) #absolute center y position


    
    thetalf = IK(pos_init[:,0], 1)[0]
    thetarf = IK(pos_init[:,1], -1)[0]
    thetarr = IK(pos_init[:,2], -1)[0]
    thetalr = IK(pos_init[:,3], 1)[0]
    
    stance = [False, False, False, False]
    if (pos[4][2] < 0.01):            
        stance[0] = True
    if (pos[4][3] < 0.01):           
        stance[1] = True
    if (pos[4][4] < 0.01):           
        stance[2] = True
    if (pos[4][5] < 0.01):              
        stance[3] = True
        
    SpotAnim.animate(pos,Angle,center_x,center_y,thetalf,thetarf,thetarr,thetalr,walking_speed,walking_direction,steering,stance)
    
    pygame.display.flip()
    if (Free == True):
        sleep(0.1)
    
    """ CG update """
    CG = SpotCG.CG_calculation (thetalf,thetarf,thetarr,thetalr)
    #Calculation of CG absolute position
    M = xyz_rotation_matrix(theta_spot[0],theta_spot[1],theta_spot[2],False)
    CGabs = new_coordinates(M,CG[0],CG[1],CG[2],x_spot[1],y_spot[1],z_spot[1])
    dCG = SpotCG.CG_distance(x_spot[2:6],y_spot[2:6],z_spot[2:6],CGabs[0],CGabs[1],stance)
    
    
    pos[2][6] = CG[0] #x
    pos[3][6] = CG[1] #y
    pos[4][6] = CG[2] #z
    
    pos[2][7] = CGabs[0] #x
    pos[3][7] = CGabs[1] #y
    pos[4][7] = CGabs[2] #z
    
    pos[2][8] = dCG[1] #xint
    pos[3][8] = dCG[2] #yint
    pos[4][8] = dCG[3] #balance
    
    distance.append(dCG[0])
    timing.append(t) 
                                          
pygame.quit()

if __name__ == "__main__":
    pass
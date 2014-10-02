import numpy #not used yet

# rounding will lead to up to 1m errors in blender coordinates. extend world to reduce?

def mapv2a(v): #map voltage to arduino
    inmin=0.54167
    inmax=2.72335
    outmin=0
    outmax=4095
    ard=(v-inmin)*(outmax-outmin)/(inmax-inmin)+outmin
    return int(ard)

def mapa2b(v): #map arduino to blender world coordintates
    inmin=0
    inmax=4095
    outmin=-10
    outmax=110
    blen=(v-inmin)*(outmax-outmin)/(inmax-inmin)+outmin
    return blen

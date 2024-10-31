#!/usr/bin/python3

# This is designed to tell a particular egg to steer to a given (theta,phi) coordinate pair

from goto import goto
from changeAxisDogleg import changeAxis
import sys
import math


# to load tty data from the db so we know which tty we want:
sys.path.append("kfDatabase")
import kfDatabase

mainDb="axis_parameters.kfdb"


def _reverseLookup(dict,val):
    #set up the reverse dictionary
    reverse_mapping={v: k for k, v in dict.items()}
    try:
        key=reverse_mapping[val]
    except KeyError as e:
        print(f"_reverseLookup failed.  KeyError: {e}")
        sys.exit()
    return key  

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def countBounces(theta,phi,axisPhi=0):
    # count the number of bounces in the light pipe's x direction and y-direction,
    # also report back if the desired theta is very close to exiting at an edge.
    # if we are at an edge, we will need to do some special calculation/steering

    # rcc:  for now, assume we are not close to an edge, and assume zero bounces

    #hard code the dimensions of the light pipe
    lightpipeLength=150
    lightpipeSide=5
    quartzRefraction=1.4997 #at 265nm, from Bob's data
    airRefraction=1.0
    #todo: this will be bench-dependent
    lightpipeXaxisAngleWrtPhi0=axisPhi
 
    #compute the total transverse distance we will travel in the pipe
    #snell's law:  n1sin(th1)=n2sin(th2)
    #hence th2=asin(n1/n2*sin(th1)
    beamAngleWrtZ=math.asin(airRefraction/quartzRefraction*math.sin(theta))
    beamLongitudinalPath=lightpipeLength
    beamTransversePath=beamLongitudinalPath*math.tan(beamAngleWrtZ)

    #compute the total distance in X and Y
    beamPathX=abs(beamTransversePath*math.cos(phi-axisPhi))
    beamPathY=abs(beamTransversePath*math.sin(phi-axisPhi))

    #todo: starting point should be something we can calibrate based on theta and phi offsets
    startX=2.5
    startY=2.5

    floatBouncesX=(beamPathX+startX)/lightpipeSide
    floatBouncesY=(beamPathY+startY)/lightpipeSide
    nBouncesX=math.floor(floatBouncesX)
    nBouncesY=math.floor(floatBouncesY)

    #to consider: at each reflection, see where we are on the other axis, see if we are close to a relfection there as well, which would mean we are at a corner.  the more corners we hit, the worse it is
    # we also know there are plastic beads and a glue seam to be avoided.

    return False,nBouncesX,nBouncesY

def debounce(phi, axisPhi, nBouncesX, nBouncesY):
    pipePhi=phi-axisPhi
    #I might have gotten X and Y confused...
    if (nBouncesX % 2 == 1): #if we bounce against X=0 once, we get reflected about the Y axis
        pipePhi=180-pipePhi
    if (nBouncesY % 2 == 1): #if we bounce against Y=0 once, we get reflected about the X axis
        pipePhi=-pipePhi
    phi=pipePhi+axisPhi    
    return 0

def getQuartzAngle(eggName,phi):
    #look up the position that points at phi0 (=pointing outward(or inward?  ask Charles) along the radial spoke)
    #TODO: s,lb=kfDatabase.readVar(mainDb,eggName+"_PH/quartzPhi")
    return 0

def getPhiMotorCoordinate(eggName,phi):
    #look up the position that points at phi0 (=pointing outward(or inward?  ask Charles) along the radial spoke)
    #TODO: phi0=kfDatabase.readVar(mainDb,eggName+"_PH/phi0")
    s,lb=kfDatabase.readVar(mainDb,eggName+"_PH/lowbound")
    s,hb=kfDatabase.readVar(mainDb,eggName+"_PH/highbound")
    phi0=0 #for now
    phiInTurns=float(phi)/360.0
    phiCoord=phiInTurns+phi0
    #TODO: determine whether this rotates clockwise or counterclockwise, and fix it so it agrees with Charles' convention

    #check if this is in bounds for this egg.  if not, add/subtract 1.0
    if phiCoord>hb:
        phiCoord=phiCoord-1.0
    elif phiCoord<lb:
        phiCoord=phiCoord+1.0

    if (phiCoord<lb):
        print("desired target phi=%s is out of range for %s matter what we do.  range=[%s,%s].  Failing."%(phi,eggName,lb,hb))
        sys.exit()
    return phiCoord

def getThetaMotorCoordinates(eggName,theta):
    #compute the short and long mirror coordinates corresponding to this theta position

    #get the position corresponding to upstream
    s,thl0=kfDatabase.readVar(mainDb,eggName+"_TH_L/upstream")
    s,ths0=kfDatabase.readVar(mainDb,eggName+"_TH_S/upstream")
    #get the mechanical limits of the long mirror (short mirror can spin freely)
    s,lb=kfDatabase.readVar(mainDb,eggName+"_TH_L/lowbound")
    s,hb=kfDatabase.readVar(mainDb,eggName+"_TH_L/highbound")

    #parameters from dan's fit for the position of the mirror arm,
    #in degrees relative to ____, to get a laser angle of 'theta' into the TPC.
    p=[0]*4
    p[0]=9.67
    p[1]=0.689
    p[2]=-0.00208
    p[3]=0.0000111
    theta=float(theta)

    thsDeg=p[0]+theta*p[1]+theta**2*p[2]+theta**3*p[3]
    #this ought to work, but is probably too snappy:
    #ths=0
    #for i in range(0,3):
    #    ths=(ths+p[3-i])*theta

    #Dan's calculation convention has thl and ths moving in the same direction when positive
    thlDegDan=thsDeg+15+theta/2
    #but the actual thl encoder counts positive in the opposite direction, so we flip the sign
    thlDeg=-thlDegDan

    #convert from degrees to rotations, including the offsets
    #go to 'upstream', then go an additional amount to the desired coordinate.
    thsCoord=thsDeg/360.0+ths0
    thlCoord=thlDeg/360.0+thl0

    #check that they are within our reachable thL range, fix if we can.
    '''
    if thlCoord>hb:
        print("Desired thL=%s is > hb=%s, so trying -1: %s"%(thlCoord,hb,thlCoord-1))
        thlCoord=thlCoord-1.0
    elif thlCoord<lb:
        print("Desired thL=%s is < lb=%s, so trying +1: %s"%(thlCoord,lb,thlCoord+1))
        thlCoord=thlCoord+1.0

    if (thlCoord<lb):
        print("desired target theta=%s is out of range for  %s_TH_L matter what we do.  range=[%s,%s].  Failing."%(theta,eggName,lb,hb))
        sys.exit()

'''
    #set the thS within our range of -1 to +1.  This can't fail;
    while thsCoord >1:
        thsCoord=thsCoord-1
    while thsCoord <-1:
        thsCoord=thsCoord+1
    
    return thsCoord, thlCoord
    


def aimAt(laserName, eggName=None, theta=None, phi=None, sOff=0, lOff=0):
    #assume we have phi and theta in degrees

    #TODO: sanity check the inputs

    #get our phi motor position:
    if(phi!=None):
        #get the quartz angle with respect to the phi origin so we can count bounces correctly
        quartzPhi=getQuartzAngle(eggName,phi)
        #see how much we bounce
        if(theta!=None):
            tooCloseToEdge,bouncesX, bouncesY=countBounces(phi,theta)
        else:
            bouncesX=0
            bouncesY=0
        #correct the requested phi angle for the number of bounces in each direction
        debouncedPhi=debounce(phi, quartzPhi,bouncesX,bouncesY)
        #and finally get the phi coordinate that gets that phi angle
        phiCoord=getPhiMotorCoordinate(eggName,debouncedPhi)

    #get our theta motor position
    if(theta!=None):
        thetaS,thetaL=getThetaMotorCoordinates(eggName,theta)


    #TODO:
    # if tooCloseToEdge:
    #     doExtraCalculations to find the offset that gets us a safe trajectory?
    # or maybe we want the ability to steer /along/ the exit facet edge, for calibration purposes?
 
    #TODO: see if this is in the lb-hb range of the phi motor, and add a bounce if it is not
    
    if (theta!=None and phi!=None):
        #moving both
        print("aimAt(%s,%s)==>Move %s(%s) to:(p%s,ts%s,tl%s)"%(theta,phi,laserName,eggName,phiCoord,thetaS,thetaL))
        print("aimAt(%s,%s) reports nBounces (x%s,y%s)"%(bouncesX,bouncesY))
        retPh=goto(laserName+"_PH",phiCoord)
        retThS=goto(laserName+"_TH_S",thetaS+float(sOff))
        retThL=goto(laserName+"_TH_L",thetaL+float(lOff))
        print("aimAt attempted:  %s_PH:%s  %s_TH_S:%s  %s_TH_L:%s"%(laserName,phiCoord,laserName,thetaS,laserName,thetaL))
        print("aimAt returns:  %s_PH:%s  %s_TH_S:%s  %s_TH_L:%s"%(laserName,retPh,laserName,retThS,laserName,retThL))
    if (theta!=None and phi==None):
        #only moving theta
        print("aimAt(%s,nophi)==>Move %s(%s) to:(ts%s,tl%s)"%(theta,laserName,eggName,thetaS,thetaL))
        retThS=goto(laserName+"_TH_S",thetaS+float(sOff))
        retThL=goto(laserName+"_TH_L",thetaL+float(lOff))
        print("aimAt attempted:  %s_TH_S:%s  %s_TH_L:%s"%(laserName,thetaS,laserName,thetaL))
        print("aimAt returns:  %s_TH_S:%s  %s_TH_L:%s"%(laserName,retThS,laserName,retThL))
    if (theta==None and phi!=None):
        #only moving phi
        print("aimAt(notheta,%s)==>Move %s(%s) to:(p%s)"%(phi,laserName,eggName,phiCoord))
        retPh=goto(laserName+"_PH",phiCoord)
        print("aimAt attempted:  %s_PH:%s"%(laserName,phiCoord))
        print("aimAt returns:  %s_PH:%s"%(laserName,retPh))

    return


if __name__ == "__main__":
    #check args
    if len(sys.argv)==4:
        #assume (eggDbName,theta,phi).
        #TODO:  specify which laser (port,axis), and which egg?  Or should we mate those permanently in the db?
        #get its port from the db
        laserName=sys.argv[1]
        theta=sys.argv[2]
        phi=sys.argv[3]
        shortOffset=0
        longOffset=0
    elif len(sys.argv)==6:
        #assume (eggDbName,theta,phi).
        #TODO:  specify which laser (port,axis), and which egg?  Or should we mate those permanently in the db?
        #get its port from the db
        laserName=sys.argv[1]
        theta=sys.argv[2]
        phi=sys.argv[3]
        shortOffset=sys.argv[4]
        longOffset=sys.argv[5]
    else:
        print("NOT EXECUTED. Wrong number of arguments.  Correct usage is:")
        print("   ./aimAt.py [axis] [theta] [phi]")
        sys.exit()
    #if wrong arguments, exit with explanation

    aimAt(laserName,laserName,theta,phi,shortOffset,longOffset)

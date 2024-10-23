#!/usr/bin/python3

# This is designed to tell a particular egg to steer to a given (theta,phi) coordinate pair

from goto import goto
from changeAxisDogleg import changeAxis
import sys



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
    
def countBounces(theta,phi):
    # count the number of bounces in the light pipe's x direction and y-direction,
    # also report back if the desired theta is very close to exiting at an edge.
    # if we are at an edge, we will need to do some special calculation/steering

    # rcc:  for now, assume we are not close to an edge, and assume zero bounces



    return False,0,0

def debounce(phi, bouncesX, bouncesY):
    #I might have gotten X and Y confused...
    if (bouncesX % 2 == 1): #if we bounce against X=0 once, we get reflected about the Y axis
        phi=180-phi
    if (bouncesY % 2 == 1): #if we bounce against Y=0 once, we get reflected about the X axis
        phi=-phi
        
    return phi
        
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
    s,thl0=kfDatabase.readVar(mainDb,eggName+"_TH_L/upstream")
    s,ths0=kfDatabase.readVar(mainDb,eggName+"_TH_S/upstream")
    s,lb=kfDatabase.readVar(mainDb,eggName+"_TH_L/lowbound")
    s,hb=kfDatabase.readVar(mainDb,eggName+"_TH_L/highbound")

    #parameters from dan's fit:
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

    tooCloseToEdge,bouncesX, bouncesY=countBounces(phi,theta)

    #TODO:
    # if tooCloseToEdge:
    #     doExtraCalculations to find the offset that gets us a safe trajectory?
    # or maybe we want the ability to steer /along/ the exit facet edge, for calibration purposes?

    debouncedPhi=debounce(phi, bouncesX,bouncesY)

    #TODO: see if this is in the lb-hb range of the phi motor, and add a bounce if it is not
    
    phiCoord=getPhiMotorCoordinate(eggName,debouncedPhi)
    thetaS,thetaL=getThetaMotorCoordinates(eggName,theta)

    print("(%s,%s)==>Move %s(%s) to:(p%s,ts%s,tl%s)"%(theta,phi,laserName,eggName,phiCoord,thetaS,thetaL))

    retPh=goto(laserName+"_PH",phiCoord)
    retThS=goto(laserName+"_TH_S",thetaS+float(sOff))
    retThL=goto(laserName+"_TH_L",thetaL+float(lOff))
    print("aimAt attempted:  %s_PH:%s  %s_TH_S:%s  %s_TH_L:%s"%(laserName,phiCoord,laserName,thetaS,laserName,thetaL))
    print("aimAt returns:  %s_PH:%s  %s_TH_S:%s  %s_TH_L:%s"%(laserName,retPh,laserName,retThS,laserName,retThL))



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
        print("   ./steetTo.py egg_name theta phi")
        sys.exit()
    #if wrong arguments, exit with explanation

    aimAt(laserName,laserName,theta,phi,shortOffset,longOffset)

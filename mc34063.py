#!/usr/bin/env python3
#-------------------------------------------------------
# mc34063.py
# by Fabio Sturman fabio.sturman@gmail.com (c) 2023
# This program is covered by
# GNU General Public License, version 3
#-------------------------------------------------------
# this program computes the components value
# for switching regulator with mc34063
# in step down, step up and invert mode
# Prints on  standard output aproximate values using
# e12 series for resistors and timing capacitor Ct
# e6 for Lmin and Cout
# Rsc is composed of three equal resistors in parallel
# for increased power
# Needs python3 and PySimpleGui
#-------------------------------------------------------

import PySimpleGUI as sg

e12=[1,1.2,1.5,1.8,2.2,2.7,3.3,3.9,4.7,5.6,6.8,8.2,10.0]
e6=[1.0,1.5,2.2,3.3,4.7,6.8,10.0]
version='MC3x063A Calculator - by Fabio Sturman - Ver 0.1'

GREEN='#00ff00'
RED='#ff0000'

# default values
mode='StepDown'
vsat=0.2
vf=0.4
vin=12.0
vout=5.0
iout=1.0
fmin=50000.0
vripple=0.05

# values to compute
ct=1e-9
rsc=0.1
lmin=1e-6
cout=1e-6
r1=1.0
r2=1.0

ton=0
toff=0
tonontoff=0
tonplustoff=0

rescolor=GREEN

# c=value s=series (e6 or e12)
def matchval(c,s):
    m=6
    if s==e12:
        m=12
    elif s==e6:
        m=6
    n=1
    while c<1:
        c=c*10
        n=n/10
    while c>10:
        c=c/10
        n=n*10
    err=[]
    for i in range(m+1):
        err.append((c-s[i])/s[i])
    mm=1
    idx=0
    for i in range(m+1):
        if abs(err[i])<mm:
            mm=err[i]
            idx=i
            # standard_value, error_percent, index_in_ex
    return int((s[idx]*n)*1000)/1000, int((err[idx]*100)*10)/10, idx

# r2=alfa*r1
# r1 in e12
# find best r2 in e12
def bestres(alfa):
    # val: r
    val=[]
    for i in range(12):
        r1=e12[i]
        r2=alfa*r1
        t=matchval(r2,e12)
        val.append([r1,t[0],t[1],t[2]])
    e=100
    for i in range(12):
        if val[i][2]<e:
            e=val[i][2]
            idx=val[i][3]
    return val[idx]

# prints valus on standard out
def printc():
    print('================================================')
    print(version)
    print('Mode=',mode)
    global ct, rsc, vin, vout, vripple, lmin, cout
    print('Vin=',vin,'V')
    print('Vout=',vout,'V')
    print('Vripple=',vripple*1000,'mV')
    print('Vf=',vf,'V')
    print('Vsat=',vsat,'V')
    t=matchval(ct/1e-12,e12)
    print('Ct=',t[0],'pF (',-1*t[1],'%)')
    t=matchval(rsc*3,e12)
    print('Rsc=3 //',t[0],'Ohm (',-1*t[1],'%)')
    t=bestres(abs(vout)/1.25-1.0)
    print('R1=',t[0],'kOhm  R2=',t[1],'kOhm (',-1*t[2],'%)')
    t=matchval(lmin/1e-6,e6)
    print('Lmin=',t[0],'uH (',-1*t[1],'%)')
    t=matchval(cout/1e-6,e6)
    print('Cout=',t[0],'uF (',-1*t[1],'%)')

def mccompute(mode):
    global r1, r2, cout, lmin, rsc, ipk, ct, ton, toff
    global tonplustoff, tonontoff, vripple
    global vout, vf, vin, vsat, fmin, vout
    if iout<=0 or vripple<=0 or fmin <10000 or vsat<=0 or vf<=0:
        return False
    if mode=='VoltageInverting':
        if vout>=0 or vin<=0 :
            return False
        tonontoff=(abs(vout)+vf)/(vin-vsat-vout)
        tonplustoff=1/fmin
        toff=tonplustoff/(tonontoff+1.0)
        ton=tonplustoff-toff
        ct=0.00004*ton
        ipk=2*abs(iout)*(tonontoff+1.0)
        rsc=0.3/ipk
        lmin=(vin-vsat)/ipk*ton
        cout=9*iout*ton/vripple
        r1=1000.0
        r2=(abs(vout)/1.25-1.0)*r1
    elif mode=='StepDown':
        if vout<=0 or vin<=0 or vout>=vin:
            return False
        tonontoff=(abs(vout)+vf)/(vin-vsat-vout)
        tonplustoff=1/fmin
        toff=tonplustoff/(tonontoff+1.0)
        ton=tonplustoff-toff
        ct=0.00004*ton
        ipk=2*abs(iout)
        rsc=0.3/ipk
        lmin=(vin-vsat-vout)/ipk*ton
        cout=ipk*tonplustoff/(8*vripple)
        r1=1000.0
        r2=(abs(vout)/1.25-1.0)*r1
    else: # StepUp
        if vout<=0 or vin<=0 or vout<=vin:
            return False
        tonontoff=(abs(vout)+vf-vin)/(vin-vsat)
        tonplustoff=1/fmin
        toff=tonplustoff/(tonontoff+1.0)
        ton=tonplustoff-toff
        ct=0.00004*ton
        ipk=2*abs(iout)*(tonontoff+1)
        rsc=0.3/ipk
        lmin=(vin-vsat)/ipk*ton
        cout=9*iout*ton/vripple
        r1=1000.0
        r2=(abs(vout)/1.25-1.0)*r1
    printc()
    return True
        
def mcdisplay():
    global ct, rsc, lmin, cout, r1, r2, mode
    ctsg(ctopf(ct),text_color=rescolor)
    rscsg(rto1000(rsc),text_color=rescolor)
    lminsg(ltouh(lmin),text_color=rescolor)
    coutsg(ctouf(cout),text_color=rescolor)
    r1sg(r1,text_color=rescolor)
    r2sg(r2,text_color=rescolor)
    modesg(mode)

def ltouh(l):
    return str(int(l/1e-6))

def ctopf(c):
    return str(int(c/1e-12))

def ctonf(c):
    return str(int(c/1e-9))

def ctouf(c):
    return str(int(c/1e-6))

def rto1000(r):
    return str( int(r*1000) / 1000 )

def is_float(v):
    try:
        f=float(v)
    except ValueError:
        return False
    return True

# start program

mccompute(mode)

ctsg=  sg.Text('',font=("Courier", 12),text_color=rescolor)
rscsg= sg.Text('',font=("Courier", 12),text_color=rescolor)
lminsg=sg.Text('',font=("Courier", 12),text_color=rescolor)
coutsg=sg.Text('',font=("Courier", 12),text_color=rescolor)
r1sg=  sg.Text('',font=("Courier", 12),text_color=rescolor)
r2sg=  sg.Text('',font=("Courier", 12),text_color=rescolor)
modesg=sg.Text('',font=("Courier", 12))

vsatsg=   sg.InputText(str(vsat),size=(10,10),font=("Courier", 12))
vfsg=     sg.InputText(str(vf),size=(10,10),font=("Courier", 12))
vinsb=    sg.InputText(str(vin),size=(10,10),font=("Courier", 12))
voutsg=   sg.InputText(str(vout),size=(10,10),font=("Courier", 12))
ioutsg=   sg.InputText(str(iout),size=(10,10),font=("Courier", 12))
fminsg=   sg.InputText(str(fmin),size=(10,10),font=("Courier", 12))
vripplesg=sg.InputText(str(vripple),size=(10,10),font=("Courier", 12))

layout = \
[
   [sg.Text('Vsat_switch(V): ',font=("Courier", 12)),vsatsg,    sg.Text('Ct(pF)=  ',font=("Courier", 12)),ctsg],
   [sg.Text('VF_rectifier(V):',font=("Courier", 12)),vfsg,      sg.Text('Rsc(Ohm)=',font=("Courier", 12)),rscsg],
   [sg.Text('Vin(V):         ',font=("Courier", 12)),vinsb,     sg.Text('Lmin(uH)=',font=("Courier", 12)),lminsg],
   [sg.Text('Vout(V):        ',font=("Courier", 12)),voutsg,    sg.Text('Cout(uF)=',font=("Courier", 12)),coutsg],
   [sg.Text('Iout(A):        ',font=("Courier", 12)),ioutsg,    sg.Text('R1(Ohm)=  ',font=("Courier", 12)),r1sg],
   [sg.Text('fmin(Hz):       ',font=("Courier", 12)),fminsg,    sg.Text('R2(Ohm)=  ',font=("Courier", 12)),r2sg],
   [sg.Text('Vripple(V):     ',font=("Courier", 12)),vripplesg, sg.Button('Mode'), modesg],

   [sg.Button('Ok'), sg.Button('Cancel')]
]

# Create the Window
window = sg.Window(version, layout,finalize=True)

mcdisplay()

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    elif event=='Mode':
        if mode=='VoltageInverting':
            mode='StepDown'
        elif mode=='StepDown':
            mode='StepUp'
        else:
            mode='VoltageInverting'
            
    # test for foating inputs
    fl=[]
    flag=True
    for i in range(7):
        fl.append(is_float(values[i]))
    for i in range(7):
        flag=flag and fl[i]

    if flag:
        rescolor=GREEN
        vf=float(values[1])
        vin=float(values[2])
        vout=float(values[3])
        iout=float(values[4])
        fmin=float(values[5])
        vripple=float(values[6])
    
        if mccompute(mode):
            pass
        else:
            rescolor=RED
    else:
        rescolor=RED
    mcdisplay()

window.close()

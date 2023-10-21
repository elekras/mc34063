#!/usr/bin/env python3
'''
This program computes the components value
for switching regulator with mc34063
in step down, step up and invert mode.
It also prints on standard output aproximate values using
e12 series for resistors and timing capacitor Ct
e24 for R1 and R2
e6 for Lmin and Cout
Rsc is composed of three equal resistors in parallel
for increased power
Uses python3 and PySimpleGui

(c) Fabio Sturman fabio.sturman@gmail.com - 2023
This program is covered by
GNU General Public License, version 3

'''
import datetime
import base64
import PySimpleGUI as sg
import mc34063img as im

e24=[1.0,1.1,1.2,1.3,1.5,1.6,1.8,2.0,2.2,2.4,2.7,3.0,3.3,
     3.6,3.9,4.3,4.7,5.1,5.6,6.2,6.8,7.5,8.2,9.1,10.0]
e12=[1,1.2,1.5,1.8,2.2,2.7,3.3,3.9,4.7,5.6,6.8,8.2,10.0]
e6=[1.0,1.5,2.2,3.3,4.7,6.8,10.0]

VERSION= 'MC34063  Calculator - by Fabio Sturman - Ver 0.6'
VERSION1='(c) Fabio Sturman fabio.sturman@gmail.com - 2023'
GNU3=    'GNU General Public License, version 3'

COLOR_OK='#000000'
COLOR_ERR='#ff0000'

# default values for in parameters
mode='StepDown'
vsat=1.0
vf=0.4
vin=12.0
vout=5.0
iout=0.5
fmin=33000.0
vripple=0.05

# values to compute for out
ct=1e-9
rsc=0.1
lmin=1e-6
cout=1e-6
r1=1.0
r2=1.0

# aux values for out
ton=0
toff=0
tonontoff=0
tonplustoff=0

# text color
# GREEN= ok
# RED= error in input data
rescolor=COLOR_OK

def matchval(c,s):
    '''searches for best value of c in s
    input:
      c= value to match
      s= series to use (e6|e12|e24)
    output:
      best value found,
      error in %,
      index in s'''

    if s==e24:
        m=24
    elif s==e12:
        m=12
    else:
        m=6
    n=1
    while c<1:
        c=c*10
        n=n/10
    while c>=10:
        c=c/10
        n=n*10
    err=[]
    for i in range(m+1):
        err.append((c-s[i])/s[i])
    mm=1
    idx=0
    for i in range(m+1):
        if abs(err[i])<mm:
            mm=abs(err[i])
            idx=i
            # best value found, error in %, index s
    return int((s[idx]*n)*1000)/1000, int((err[idx]*100)*10)/10, idx

def bestres(alfa,s):
    '''search for best value of r2(=alfa*r1) and r1 in s
    Foreach value of r1 in s compute r2 and search for best value
    of r2 in s
    input:
      alfa=r2/r1
      s= series to use (e6|e12|e24)
    out:
      (r1, r2, error in %, index)'''

    if s==e24:
        m=24
    elif s==e12:
        m=12
    else:
        m=6
    val=[]
    for i in range(m):
        r1=s[i]
        r2=alfa*r1
        t=matchval(r2,s)
        val.append([r1,t[0],t[1],t[2]])
    e=100
    for i in range(m):
        if abs(val[i][2])<e:
            e=abs(val[i][2])
            idx=i
    #print(val)
    return val[idx]

def printc():
    ''' print all data on standard output'''
    print('================================================')
    print(VERSION)
    print(datetime.datetime.now())
    print('Mode=',mode)
    print('------------------------------------------------')
    print('Vin=',vin,'V')
    print('Vout=',vout,'V')
    print('Iout=',iout,'A')
    print('Vripple=',vripple*1000,'mV')
    print('Vf=',vf,'V')
    print('Vsat=',vsat,'V')
    print('fmin=',fmin,'Hz')
    print('------------------------------------------------')
    t=matchval(ct/1e-12,e12)
    print('Ct=',t[0],'pF (',-1*t[1],'%)')
    t=matchval(rsc*3,e12)
    print('Rsc=3 //',t[0],'Ohm (',-1*t[1],'%)')
    t=bestres(abs(vout)/1.25-1.0,e24)
    print('R1=',t[0],'kOhm  R2=',t[1],'kOhm (',-1*t[2],'%)')
    t=matchval(lmin/1e-6,e6)
    print('Lmin=',t[0],'uH (',-1*t[1],'%)')
    t=matchval(cout/1e-6,e6)
    print('Co=',t[0],'uF (',-1*t[1],'%)')

def mccompute(mode):
    '''compute r1, r2, cout, lmin, rsc, ipk, ct, ton, toff'''
    global r1, r2, cout, lmin, rsc, ct, ton, toff
    if iout<=0 or vripple<=0 or fmin <24000 or fmin>42000 or vsat<=0 or vf<=0:
        return False
    if mode=='Inverting':
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
    '''refresh displayed data'''
    ctsg(topico(ct),text_color=rescolor)
    rscsg(rto1000(rsc),text_color=rescolor)
    lminsg(tomicro(lmin),text_color=rescolor)
    coutsg(tomicro(cout),text_color=rescolor)
    r1sg(r1,text_color=rescolor)
    r2sg(r2,text_color=rescolor)
    modesg(mode)
    if rescolor==COLOR_ERR:
        st('Error in data')
    else:
        st('Press <ENTER> or click on COMPUTE')

def tomicro(l):
    '''convert to u(micro)'''
    return str(int(l/1e-6))

def topico(c):
    '''convert to p(pico)'''
    return str(int(c/1e-12))

def tonano(c):
    '''convert to n(nano)'''
    return str(int(c/1e-9))

def rto1000(r):
    '''round to 1/1000'''
    return str( int(r*1000) / 1000 )

def is_float(v):
    '''test if float'''
    try:
        float(v)
    except ValueError:
        return False
    return True

# main program

# compute out values from in default values
mccompute(mode)

# select theme
sg.theme('SystemDefault')

# read base64 encoded png images
ImgStepDown= base64.b64decode(im.StepDown)
ImgStepUp= base64.b64decode(im.StepUp)
ImgInverting= base64.b64decode(im.Inverting)

# create texts
ctsg=  sg.Text('',font=("Courier", 12),text_color=rescolor)
rscsg= sg.Text('',font=("Courier", 12),text_color=rescolor)
lminsg=sg.Text('',font=("Courier", 12),text_color=rescolor)
coutsg=sg.Text('',font=("Courier", 12),text_color=rescolor)
r1sg=  sg.Text('',font=("Courier", 12),text_color=rescolor)
r2sg=  sg.Text('',font=("Courier", 12),text_color=rescolor)
modesg=sg.Text('',font=("Courier", 12))

# create inputs
vsatsg=   sg.InputText(str(vsat),size=(10,10),font=("Courier", 12))
vfsg=     sg.InputText(str(vf),size=(10,10),font=("Courier", 12))
vinsb=    sg.InputText(str(vin),size=(10,10),font=("Courier", 12))
voutsg=   sg.InputText(str(vout),size=(10,10),font=("Courier", 12))
ioutsg=   sg.InputText(str(iout),size=(10,10),font=("Courier", 12))
fminsg=   sg.InputText(str(fmin),size=(10,10),font=("Courier", 12))
vripplesg=sg.InputText(str(vripple),size=(10,10),font=("Courier", 12))

# create image
imagesg=  sg.Image(ImgStepDown)
st=sg.StatusBar('                                                      ')

# lay out the window
layout = \
[
   [sg.Text('Vsat_switch(V): ',font=("Courier", 12)),vsatsg,  \
    sg.Text('Ct(pF)=  ',font=("Courier", 12)),ctsg],
   [sg.Text('VF_rectifier(V):',font=("Courier", 12)),vfsg, \
    sg.Text('Rsc(Ohm)=',font=("Courier", 12)),rscsg],
   [sg.Text('Vin(V):         ',font=("Courier", 12)),vinsb, \
    sg.Text('Lmin(uH)=',font=("Courier", 12)),lminsg],
   [sg.Text('Vout(V):        ',font=("Courier", 12)),voutsg, \
    sg.Text('Co(uF)=  ',font=("Courier", 12)),coutsg],
   [sg.Text('Iout(A):        ',font=("Courier", 12)),ioutsg, \
    sg.Text('R1(Ohm)= ',font=("Courier", 12)),r1sg],
   [sg.Text('fmin(Hz):       ',font=("Courier", 12)),fminsg, \
    sg.Text('R2(Ohm)=  ',font=("Courier", 12)),r2sg],
   [sg.Text('Vripple(V):     ',font=("Courier", 12)),vripplesg, \
    sg.Button('Mode'), modesg],

   [sg.Button('About'),sg.Button('Compute'), sg.Button('Exit')],
   [imagesg],
   [st]

]

# create the Window
window = sg.Window(VERSION, layout,finalize=True)

window.bind("<Return>", "_Enter")

# display computed values
mcdisplay()

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit': # if user closes window or clicks cancel
        break
    elif event=='Mode':
        if mode=='Inverting':
            mode='StepDown'
            imagesg(ImgStepDown)
        elif mode=='StepDown':
            mode='StepUp'
            imagesg(ImgStepUp)
        else:
            mode='Inverting'
            imagesg(ImgInverting)
    elif event=='About':
        sg.popup(VERSION+'\n'+VERSION1+'\n'+GNU3, title='MC34063')

    # test for floating point inputs
    fl=[]
    flag=True
    for i in range(7):
        fl.append(is_float(values[i]))
    for i in range(7):
        flag=flag and fl[i]

    # convert from strings to fp
    if flag:
        vsat=float(values[0])
        vf=float(values[1])
        vin=float(values[2])
        vout=float(values[3])
        iout=float(values[4])
        fmin=float(values[5])
        vripple=float(values[6])

        if mccompute(mode):
            rescolor=COLOR_OK
        else:
            rescolor=COLOR_ERR
    else:
        rescolor=COLOR_ERR
        
    # display out data
    mcdisplay()

window.close()

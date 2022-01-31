#Imports
from tkinter import *
from tkinter import filedialog
import math, random, os, io, time
from PIL import Image

#GUI Class
class GUI(object):
    def __init__(self):
        self.root = Tk()
        self.root.title("Fluid Simulator")

        self.createCanvas()
        self.createMenu()
        
        self.field = VecField()

        self.resolution = 0.01
        self.maxtime = 25

##        for n in range(0,99):
##            self.field = LineSource(1,(1-n/100,0))
##            field = LineSource(-1,(-1+n/100,0))
##            self.field + field
##            self.drawmesh(5,(-2,2,-2,2))
##            self.save(n)

##        self.field = LineSource(1,(0,0))
##        self.drawmesh(5,(-2,2,-2,2))
##        print(self.canvas.bbox("feature0"))
        
        self.root.mainloop()

    def createMenu(self):
        menu = Menu(self.root)

        self.displayfeatures = BooleanVar()
        self.displayfeatures.set(True)
        
        filemenu = Menu(menu, tearoff=0)
        filemenu.add_command(label="Clear", command=self.clear)
        filemenu.add_checkbutton(label="Show Features", onvalue=1, offvalue=0, variable=self.displayfeatures)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_command(label="Exit", command=lambda:self.root.destroy())
        menu.add_cascade(label="File", menu=filemenu)
        
        newmenu = Menu(menu, tearoff=0)
        newmenu.add_command(label="Uniform Flow", command=lambda:self.newfield("Uniform"))
        newmenu.add_command(label="Line Source", command=lambda:self.newfield("Line Source"))
        newmenu.add_command(label="Vortex", command=lambda:self.newfield("Vortex"))
        menu.add_cascade(label="Create", menu=newmenu)
        
        self.root.config(menu=menu)

    def createCanvas(self):
        self.canvas = Canvas(self.root,width=400,height=400)
        self.canvas.grid(row=0,column=0)

    def drawpath(self,x0,y0):
        particle = (x0,y0)
        t=0
        while t<self.maxtime:
            velocity = self.field.move(t,particle[0],particle[1])
            if velocity[0]**2+velocity[1]**2 == 0 or abs(particle[0])+abs(particle[1])>5:
                break
            inc = self.resolution/(velocity[0]**2+velocity[1]**2)+0.001
            newparticle = (particle[0]+velocity[0]*inc,particle[1]+velocity[1]*inc)
            self.canvas.create_line(particle[0]*100+200,particle[1]*100+200,
                                    newparticle[0]*100+200,newparticle[1]*100+200,
                                    width=2,smooth=1)
            particle=newparticle
            t+=inc
            
        particle = (x0,y0)
        t=0
        while t>-self.maxtime:
            velocity = self.field.move(t,particle[0],particle[1])
            if velocity[0]**2+velocity[1]**2 == 0 or abs(particle[0])+abs(particle[1])>5:
                break
            inc = self.resolution/(velocity[0]**2+velocity[1]**2)+0.001
            newparticle = (particle[0]-velocity[0]*inc,particle[1]-velocity[1]*inc)
            self.canvas.create_line(particle[0]*100+200,particle[1]*100+200,
                                    newparticle[0]*100+200,newparticle[1]*100+200,
                                    width=2,smooth=1)
            particle=newparticle
            t-=inc

    def clear(self,*args):
        self.field = VecField()
        self.canvas.delete("all")

    def newfield(self,fieldtype):
        if fieldtype == "Uniform":
            sel = FieldSelector(self,fieldtype,True,False)

        elif fieldtype == "Line Source" or fieldtype == "Vortex":
            sel = FieldSelector(self,fieldtype,True,True)


    def createfield(self,fieldtype,config):
        if fieldtype == "Uniform":
            field = Uniform(config[0])
            self.field+field

        elif fieldtype == "Line Source":
            field = LineSource(config[0],config[1])
            self.field+field

        elif fieldtype == "Vortex":
            field = Vortex(config[0],config[1])
            self.field+field

        self.drawmesh(10,(-2,2,-2,2))

    def drawmesh(self,points,span):
        self.canvas.delete("all")
        for x in range(0,points+1):
            for y in range(0,points+1):
                self.drawpath(span[0]+x*(span[1]-span[0])/points,
                              span[2]+y*(span[3]-span[2])/points)
        if self.displayfeatures.get():
            self.drawfeatures()
        self.canvas.update()

    def drawfeatures(self):
        for feature in self.field.getproperties():
            self.canvas.create_oval(feature[2][0]*100+200-5,feature[2][1]*100+200-5,feature[2][0]*100+200+5,feature[2][1]*100+200+5,fill="#ff0000",tags="feature")
        self.canvas.tag_bind("feature", '<Enter>', self.displayinfo)
        self.canvas.tag_bind("feature", '<Leave>', self.removeinfo)

    def displayinfo(self,event):
        for feature in self.field.getproperties():
            if abs(feature[2][0]*100+200-event.x)+abs(feature[2][1]*100+200-event.y)<10:
                self.canvas.create_rectangle(feature[2][0]*100+200,feature[2][1]*100+200,feature[2][0]*100+280,feature[2][1]*100+242,fill="#ffffff",tags="info")
                self.canvas.create_text(feature[2][0]*100+205,feature[2][1]*100+205,text=feature[0]+"\nStrength: "+str(feature[1]),anchor=NW,fill="#000000",tags="info")
                #print(feature[0],feature[1])
        self.canvas.update()

    def removeinfo(self,event):
        self.canvas.delete("info")
        self.canvas.update()

    def save(self,*args):
        filepath = filedialog.asksaveasfile(mode='w',defaultextension="jpg")
        ps = self.canvas.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps.encode('utf-8')))
        try:
            img.save(filepath)
        except ValueError:
            img.save(filepath+".jpg")
        


#Field Selector Class
class FieldSelector(object):
    def __init__(self,gui,fieldtype,strength,position):
        self.root = Tk()
        self.root.title("Create "+fieldtype)
        if strength:
            self.createStrength()
        if position:
            self.createPosition()
        Button(self.root,text="CREATE",command=lambda:self.done(gui,fieldtype,strength,position)).grid(column=0,columnspan=2,row=2)
        self.root.mainloop()

    def createStrength(self):
        self.strengthscale = Scale(self.root,from_=-2,to=2,orient=HORIZONTAL,length=200,label="Strength",resolution=0.01)
        self.strengthscale.grid(column=0,columnspan=2,row=0)


    def createPosition(self):
        self.xscale = Scale(self.root,from_=-1,to=1,orient=HORIZONTAL,label="x Coordinate",resolution=0.01)
        self.xscale.grid(column=0,row=1)
        self.yscale = Scale(self.root,from_=-1,to=1,orient=HORIZONTAL,label="y Coordinate",resolution=0.01)
        self.yscale.grid(column=1,row=1)

    def done(self,gui,fieldtype,strength,position):
        if strength and position:
            gui.createfield(fieldtype,[self.strengthscale.get(),(self.xscale.get(),self.yscale.get())])
        elif strength:
            gui.createfield(fieldtype,[self.strengthscale.get()])
        elif position:
            gui.createfield(fieldtype,[(self.xscale.get(),self.yscale.get())])
        self.root.destroy()


#Vector Field Class
class VecField(object):
    def __init__(self):
        self.properties = []

    def getproperties(self):
        return self.properties
    
    def u(self,x,y,t):
        return 0

    def v(self,x,y,t):
        return 0

    def move(self,t,x,y):
        return (self.u(x,y,t),self.v(x,y,t))

    def getu(self):
        return self.u

    def getv(self):
        return self.v

    def __add__(self,obj):
        myu = self.u
        myv = self.v
        addu = obj.getu()
        addv = obj.getv()
        self.u = lambda x,y,t : myu(x,y,t)+addu(x,y,t)
        self.v = lambda x,y,t : myv(x,y,t)+addv(x,y,t)
        self.properties += obj.getproperties()



#Uniform Flow Class
class Uniform(VecField):
    def __init__(self,strength):
        self.strength = strength
        super().__init__()

    def u(self,x,y,t):
        return self.strength



#Line Source Class
class LineSource(VecField):
    def __init__(self,strength,centre):
        self.strength = strength
        self.centre = centre
        self.properties = [("Line Source",self.strength,self.centre)]

    def u(self,x,y,t):
        if abs(x-self.centre[0])+abs(y-self.centre[1])<0.05:
            return 0
        else:
            return self.strength*(x-self.centre[0])/(2*math.pi*((x-self.centre[0])*(x-self.centre[0])+(y-self.centre[1])*(y-self.centre[1])))

    def v(self,x,y,t):
        if abs(x-self.centre[0])+abs(y-self.centre[1])<0.05:
            return 0
        else:
            return self.strength*(y-self.centre[1])/(2*math.pi*((x-self.centre[0])*(x-self.centre[0])+(y-self.centre[1])*(y-self.centre[1])))


#Vortex Class
class Vortex(VecField):
    def __init__(self,strength,centre):
        self.strength = strength
        self.centre = centre
        self.properties = [("Vortex",self.strength,self.centre)]

    def u(self,x,y,t):
        return (self.strength/(2*math.pi))*(y-self.centre[1])/((x-self.centre[0])*(x-self.centre[0])+(y-self.centre[1])*(y-self.centre[1]))

    def v(self,x,y,t):
        return (self.strength/(2*math.pi))*(-x+self.centre[0])/((x-self.centre[0])*(x-self.centre[0])+(y-self.centre[1])*(y-self.centre[1]))


gui = GUI()                           

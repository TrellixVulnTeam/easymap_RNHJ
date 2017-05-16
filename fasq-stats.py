#!/usr/bin/python
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageOps

parser = argparse.ArgumentParser()
parser.add_argument('-fasq', action="store", dest = 'File', required = "True")

args = parser.parse_args()
reverse = "no"
files = args.File


#phred_not="J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,[,\,],^,_,`,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,{,|,},~"

def character_to_ASCII(string):
	st = []
	for items in string:
		ascii = ord(items)
		ascii = ascii-33
		st.append(int(ascii))
	return st

def fasq_preprocess(fil):
	fastaq_list = []
	i = 0
	with open(fil) as fastaq:
		p = 1
		for lines in fastaq:
			lines = lines.rstrip()
			if p%4 == 0:
				fastaq_list.append(lines)
			i += 1
			p +=1
			if i > 20000:
				break
		return fastaq_list
def fasq_process(fil,x,group):
	dic = {}
	dic[str(x)+"_"+str(x+group)] = []
	i = 0
	p = 1
	with open(fil) as fastaq:
		for lines in fastaq:
			lines = lines.rstrip()
			if p%4== 0:
				for items in range(x,x+group):
					#print x, x+group,items
					try:
						dic[str(x)+"_"+str(x+group)].append(lines[items])
					except:
						h = "h"
				i += 1
			
			if i >= 500000:
				break
			p += 1
	qual_dic= {}
	for position in dic:
		qual_dic[position] = character_to_ASCII(dic[position])
	return qual_dic
def average(lista):
	n = 0 
	l = []
	for items in lista:
		l.append(float(items))
		n += 1
	try:
		average = sum(l)/n
	except:
		average = 0
	return average 
def boxplot_stats(lista):
	lista = sorted(lista)
	lenght = len(lista)
	position1 = float(lenght/2)
	if position1.is_integer():
		per_50 = lista[int(position1)]
	else:
		position1 = position1.split(".")[0]
		position2 = position1 + 1
		position1 =  lista[int(position1)]
		position2 = lista[int(position2)]
		per_50 = (postion1 + position2)/2 

	position2 = float((lenght+1)/4)
	if position2.is_integer():
		per_25 = lista[int(position2)]
	else:
		position2 = position2.split(".")[0]
		position3 = position2 + 1
		position2 =  lista[int(position2)]
		position3 = lista[int(position3)]
		position4 = position2 + position3*position2.split(".")[1]*((lenght+1)/4)
		per_25 = int(position4) 

	position3 = float((lenght+1)*3/4)
	if position3.is_integer():
		per_75 = lista[int(position3)]
	else:
		position3 = position3.split(".")[0]
		position4 = position4 + 1
		position3 =  lista[int(position3)]
		position4 = lista[int(position4)]
		position5 = position3 + position4*position3.split(".")[1]*((lenght+1)*3/4)
		per_75 = int(position5) 
	
	IQR = int(per_75) - int(per_25)
	Extreme_positive = 1.5*IQR + float(per_75)
	Extreme_negative =  float(per_25)-1.5*IQR 
	
	if Extreme_negative < 0:
		Extreme_negative = 0
	
	if float(min(lista))> float(Extreme_negative): Extreme_negative = min(lista)
	
	if float(max(lista))< float(Extreme_positive): Extreme_positive = max(lista)
	
	
	return float(Extreme_negative), float(per_25), float(per_50), float(per_75), float(Extreme_positive)

def calculations(dic_pos): 	
	for item in dic_pos:
		average_val = average(dic_pos[item])
		stats = boxplot_stats(dic_pos[item])

	return average_val,stats[0],stats[1],stats[2],stats[3],stats[4]

def lenght_reads_cal(pre_dic):
	value_list = []
	biggest = 0
	for reads in pre_dic:	
		if len(reads) > biggest:
			biggest = len(reads) 
	return biggest

def Draw_box_plot(table):
	fnt1 = ImageFont.truetype('easymap-server/fonts/VeraMono.ttf', 7)
	#Size of the window
	print table
	a = 20
	b = 20
	c = 20
	x_window = len(table)*10+ 10+ a + b 
	y_window = 400
	#Generation of the file
	im = Image.new("RGB", (x_window, y_window), (255,255,255))	
	draw = ImageDraw.Draw(im)
	#Creation of the axes: exes will start with an indentation of 20 above, below and beside. Each Phred quality score will be in a X% proportion of the y_window  px
	size_y_exe = y_window-40 #Total size minus above and below indentations
	position_y_exe= size_y_exe+20
	draw.line(((a, c) + (a, position_y_exe)), fill=(0, 0, 0, 0), width=1)
	size_x_exe = len(table)*10 +10 #number of positions*10 pxls which is one will take + 10 for the position 1. 
	draw.line(((a, position_y_exe) + (a+size_x_exe, position_y_exe)), fill=(0, 0, 0, 0), width=1) 
	#Close chart
	draw.line(((a, c) + (size_x_exe+a, c)), fill=(0, 0, 0, 0), width=1)
	draw.line(((size_x_exe+a, c) + (size_x_exe+a, position_y_exe)), fill=(0, 0, 0, 0), width=1)
	#Vertical values
	step = float(size_y_exe)/42
	for values in range(42,-1,-1):
		#pos = str(values+1)
		draw.line(((a,20+abs(values-42)*step) + (a-4,20+abs(values-42)*step)), fill=(0, 0, 0, 0), width=1)
		#draw.text((a-8,20+values*step) + (a-8,20+values*step), pos, font=fnt1, fill=(0,0,0,0))
		if values%5 == 0:
			draw.line(((a,20+abs(values-42)*step) + (a-5,20+abs(values-42)*step)), fill=(0, 0, 0, 0), width=1)
			##draw.text((a-8,20+values*step) + (a-10,20+values*step), str(values-42), font=fnt1, fill=(0,0,0,0))

	i = 10 + a #indentation + space for the first box (same space as in size_x_exe)
	for position in table:
		name = position[0]
		position = position[1:]
		

		#write the position in the x axe
		draw.line(((i, position_y_exe) + (i, position_y_exe+5)), fill=(0, 0, 0, 0), width=1)
		##draw.text((i, position_y_exe+8) + (i,position_y_exe+8), name, font=fnt1, fill=(0,0,0,0))

		#Create a line from the begining to the end of the parameters
		beg = float(position[1]) * step
		end = float(position[-1]) * step
		draw.line(((i, position_y_exe-beg) + (i, position_y_exe-end)), fill=(0, 0, 0, 0), width=1)

		#Create the boxplot using CORREGIR!!!!!!!!!!
		beg = float(position[2]) * step
		end = float(position[-2]) * step
		draw.rectangle([(i-3, position_y_exe-beg), (i+3, position_y_exe-end)], fill=(24, 56, 214), outline= None)

		#Draw the average and the MEDIANA?
		av = float(position[0]) * step
		med = float(position[3]) * step
		draw.line(((i-3, position_y_exe-med) + (i+3, position_y_exe-med)), fill=(191, 17, 54), width=1)
		draw.line(((i, position_y_exe-av) + (i, position_y_exe-av)), fill=(50, 214, 25), width=1)
		i +=10


	#save image, specifying the format with the extension
	im.save("result.png")




pre_dic = fasq_preprocess(files)
lenght_reads = int(lenght_reads_cal(pre_dic))

if lenght_reads<80: group = 1
if 100>=lenght_reads>80: group = 2
if lenght_reads>100: group = 5


x =0
final_dic= {}
#print range((lenght_reads/group)-1)
#exit()
final_list=[]

for repetitions in range((lenght_reads/group)-1):
	print repetitions
	lis = []
	position_table=fasq_process(files,x,group)
	result = calculations(position_table)
	lis.append(str(x+1)+"-"+str(x+group))
	lis.extend(result)
	final_list.append(lis)
	
	#final_dic[str(x+1)+"-"+str(x+group)]= result
	x += group

Draw_box_plot(final_list)



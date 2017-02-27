#from __future__ import division
import argparse
from PIL import Image, ImageDraw, ImageFont, ImageOps


parser = argparse.ArgumentParser()
parser.add_argument('-a', action="store", dest = 'input')
parser.add_argument('-b', action="store", dest = 'input_f')
#parser.add_argument('-c', action="store", dest = 'output_overview')
#parser.add_argument('-d', action="store", dest = 'output_paired')
#parser.add_argument('-e', action="store", dest = 'output_local')
parser.add_argument('-f', action="store", dest = 'output_html')
parser.add_argument('-m', action="store", dest = 'mode')
args = parser.parse_args()

#Input 1
input = args.input
f1 = open(input, 'r')
lines = f1.readlines()	


#__________________________________________Insertions overview image_____________________________________________________________
#Input 2
finput = args.input_f
f2 = open(finput, 'r')
flines = f2.readlines()	
#define a superlist with innerlists, each of them containing all the info of each contig 
superlist = list()

#Create a list with all the genome contigs
contigs = []
length = 0
n = 0

#dict_contigs = dict()
lengthlist = list()

#read fasta file to determine number of contigs
for i, line in enumerate(flines):
	if line.startswith('>'): #fasta sequences start with '>'
		sp = line.split(' ')  #because some names have whitespaces and extra info that is not written to sam file
		cont = sp[0].strip()  #strip() is to remove the '\r\n' hidden chars
		cont = cont[1:]       #to remove the first char of string (>)
		if cont not in contigs:
			contigs.append(cont)
			innerlist = list()
			innerlist.append(cont)
			superlist.append(innerlist)


#Calculate the width of the image acording to the number of contigs
num_contigs = 0
for c in superlist: 
	num_contigs+=1
contigs_image_width = 200 * num_contigs

im = Image.new("RGB", (contigs_image_width + 80, 600), (255,255,255))



#append length of contig to current innerlist
if len(superlist) > 1: 
	for c in superlist:
		c = str(c)[2:-2]
		for i, line in enumerate(flines):
			if '>' in line and c in line: 
				pass
			elif '>' in line: 
				try:
					superlist[n].append(length)
					length = 0
					n+=1
				except: 
					pass
			else: 
				length = length + len(line.strip())
				
elif len(superlist) == 1: 
	for c in superlist:
		c = str(c)[2:-2]
		for i, line in enumerate(flines):
			if '>' in line and c in line: 
				pass
			elif '>' in line: 
				try:
					superlist[n].append(length)
					length = 0
					n+=1
				except: 
					pass
			else: 
				length = length + len(line.strip())

		superlist[n].append(length)




#calculate length of longest chr and a contigs scaling factor for drawing
for c in superlist:
	try:
		max_list.append(int(c[1]))
	except:
		max_list = list()
		max_list.append(int(c[1]))
		
max_length = max(max_list)
contigs_scaling_factor = max_length / 400.0


#translate real chromosome lengths into image i and f coordinates
contig_counter = 1
contig_yi_coord = 100

for c in superlist:
	contig_x_coord = ((contigs_image_width / num_contigs) * contig_counter) - 100
	contig_yf_coord = int(contig_yi_coord + c[1]/contigs_scaling_factor)
	contig_counter +=1
	c.append(contig_x_coord)
	c.append(contig_yi_coord)
	c.append(contig_yf_coord)
	
	
#add insertions aproximate position to superlist
tag_list = list()
for i, line in enumerate(lines):
	if not line.startswith('@'):	
		sp = line.split('\t')
		contig = str(sp[1].strip())
		insertion = str(sp[2])
		if '-' not in insertion:
			tag = contig + '-' + insertion
			if tag not in tag_list: 
				tag_list.append(tag)
for c in superlist: 
	position_list = list()
	for t in tag_list:
		n_reads = 1
		p_reads = 0 		
		for i, line in enumerate(lines):
			if not line.startswith('@'): 
				sp = line.split('\t')
				contig = str(sp[1].strip())
				insertion = str(sp[2])
				if '-' not in insertion and sp[5].strip() == 'TOTAL' and contig == c[0].strip():
					tag2 = contig + '-' + insertion
					if tag2 == t:
						n_reads = n_reads + 1
						p_reads = p_reads + int(sp[3])											
					else:
						aprox_position = p_reads/n_reads
			aprox_position = p_reads/n_reads
		if aprox_position != 0: 
			position_list.append(aprox_position)	
	c.append(position_list)


#initialize draw
draw = ImageDraw.Draw(im)
#get fonts from foler 'fonts'
fnt1 = ImageFont.truetype('fonts/arial.ttf', 20)
fnt2 = ImageFont.truetype('fonts/arial.ttf', 10)
fnt3 = ImageFont.truetype('fonts/arial.ttf', 14)
tab = 50


#Drawing frame
#draw.polygon([(2,2), ((contigs_image_width - 2), 2), ((contigs_image_width - 2), 598), (2, 598) ], fill = (255, 255, 255, 255))

number = 1

#Drawing the chromosomes:
for c in superlist:
	draw.line((c[2], c[3]) + (c[2], c[4]), fill=256, width=8)
	draw.ellipse((c[2]-2, c[3]-2, c[2]+4, c[3]+3), fill=256)
	draw.ellipse((c[2]-2, c[4]-2, c[2]+4, c[4]+3), fill=256)
	draw.text(((c[2] - tab), (c[3] - 50)), c[0], font=fnt1, fill=(0,0,0,255))
	for i in c[5]:
		draw.polygon([(c[2]+ 5, (i/contigs_scaling_factor+contig_yi_coord)), (c[2]+15, (i/contigs_scaling_factor+contig_yi_coord)+10), (c[2]+15, (i/contigs_scaling_factor + contig_yi_coord)-10)], fill = (200, 0, 0, 200))
		draw.text(((c[2] + 20), (i/contigs_scaling_factor+contig_yi_coord - 8)), ('Insertion ' + str(number)), font=fnt3, fill=(0,0,0,255))
		number = number + 1


#save image, specifying the format with the extension
im.save("3_workflow-output/insertions_overview.png")



#__________________________________________Local and paired analysis graphs_____________________________________________________________
insertions = list()

for i, line in enumerate(lines):
	if not line.startswith('@'):	
		sp = line.split('\t')
		insertion = str(sp[2]).strip()
		if insertion not in insertions and insertion != '-':
			insertions.append(insertion)
	
			
for e in insertions:
	try:
		del region_min
	except:
		pass
	region_max = 0
	rd_max = 0
	for i, line in enumerate(lines):
		if not line.startswith('@'):
			sp = line.split('\t')
			#Max and min for genome region in graphic
			if sp[2] == e: 
				if int(sp[3]) > region_max:
					region_max = int(sp[3])
				else:
					try:
						if sp[3] < region_min: 
							region_min = int(sp[3])
					except:
						region_min = int(sp[3])
		
			#Max and min read depth 
			if sp[2] == e: 
				if int(sp[4]) > rd_max:
					rd_max = int(sp[4])					

	rd_max = rd_max + 10
	region_max = region_max + 100
	if region_min > 200:
		region_min = region_min - 100

	#Images, axes and title PAIRED
	im = Image.new("RGB", (600, 500), (255,255,255))
	draw = ImageDraw.Draw(im)
	draw.line((80, 350) + (500, 350), fill=256, width=3)
	draw.line((80, 100) + (80, 350), fill=256, width=3)
	draw.text(((250), (20)), ('Insertion ' + str(e)), font=fnt1, fill=(0,0,0,255))
	draw.text(((260), (370)), ('Nucleotide'), font=fnt1, fill=(0,0,0,255))
	draw.text(((30), (72)), ('RD'), font=fnt1, fill=(0,0,0,255))
	
	
	#Images, axes and title LOCAL
	im2 = Image.new("RGB", (600, 500), (255,255,255))
	draw2 = ImageDraw.Draw(im2)
	draw2.line((80, 350) + (500, 350), fill=256, width=3)
	draw2.line((80, 100) + (80, 350), fill=256, width=3)
	draw2.text(((250), (20)), ('Insertion ' + str(e)), font=fnt1, fill=(0,0,0,255))
	draw2.text(((260), (370)), ('Nucleotide'), font=fnt1, fill=(0,0,0,255))
	draw2.text(((30), (72)), ('Aligment cuts'), font=fnt1, fill=(0,0,0,255))
	
	
	#PAIRED
	#Scaling factors 
	nucleotides = region_max - region_min
	scaling_factor_x = nucleotides/420.0
	scaling_factor_y = rd_max/250.0
	
		
	#Data selection for drawing
	for i, line in enumerate(lines):
		if not line.startswith('@'):
			sp = line.split('\t')
			ins_contig = sp[1]
			if sp[2] == e and sp[0].strip() == 'PAIRED' and sp[5].strip() != 'TOTAL':
				raw_x_position = int(sp[3])
				img_x_position = int(raw_x_position/scaling_factor_x)
				img_relative_x_position = img_x_position - int(region_min/scaling_factor_x) + 81
				
				try:
					if img_relative_x_position == img_relative_x_position_2:
						raw_y_position = int(sp[4])
						img_y_position = 350 - int(raw_y_position/scaling_factor_y)
					
						if img_y_position > img_y_position_2: 	
							img_y_position_2 = img_y_position
					
					img_relative_x_position_2 = img_relative_x_position
				except:
					img_relative_x_position_2 = img_relative_x_position
					raw_y_position = int(sp[4])
					img_y_position = 350 - int(raw_y_position/scaling_factor_y)

			
				#draw
				if sp[5].strip() == 'R':
					draw.line((img_relative_x_position, 348) + (img_relative_x_position, img_y_position), fill=(0, 200, 0, 100), width=1)	
					
				elif sp[5].strip() == 'F':
					draw.line((img_relative_x_position, 348) + (img_relative_x_position, img_y_position), fill=(0, 0, 200, 100), width=1)


	#Candidate regions
	for i, line in enumerate(lines):
		if line.startswith('@#'):
			sp = line.split(',')
			if int(sp[2].strip()) == int(e):
					draw.text(((30), (430)), ('Your candidate region is (' + sp[0].strip('@#') + ', ' + sp[1].strip()+')'), font=fnt3, fill=(0,0,0,255))
					draw.line((((80 +int(sp[0].strip('@#'))/scaling_factor_x - int(region_min/scaling_factor_x)) , 348) + ((80 +int(sp[0].strip('@#'))/scaling_factor_x - int(region_min/scaling_factor_x)) , 100)), fill=(255, 0, 0, 100), width=1)
					draw.line((((80 +int(sp[1].strip())/scaling_factor_x - int(region_min/scaling_factor_x)) , 348) + ((80 +int(sp[1].strip())/scaling_factor_x - int(region_min/scaling_factor_x)) , 100)), fill=(255, 0, 0, 100), width=1)

	
	
	#LOCAL
	#Region
	try:
		del region_min_l
	except:
		pass
	region_max_l = 0
	rd_max_l = 0
	for i, line in enumerate(lines):
		if not line.startswith('@'):
			sp = line.split('\t')
			#Max and min for genome region in local graphic
			if  sp[0].strip() == 'LOCAL' and sp[5].strip() == 'TOTAL' and e == sp[2].strip():
				if int(sp[3]) > region_max_l:
					region_max_l = int(sp[3])
				elif int(sp[3]) < region_max_l:
					print 'okai' 
					try:
						if sp[3] < region_min_l: 
							region_min_l = int(sp[3])
					except:
						region_min_l = int(sp[3])
				else:
					region_min_l = region_max_l
			
					
			#Max and min read depth 
			if e == sp[2].strip() and sp[0].strip() == 'LOCAL' and sp[5].strip() == 'TOTAL': 
				if int(sp[4]) > rd_max_l :
					rd_max_l = int(sp[4])					

	rd_max_l = rd_max_l + 10
	region_max_l = region_max_l + 6
	try:
		if region_min_l > 20:
			region_min_l = region_min_l - 6
	except:
		region_min_l = region_max_l - 12	

	#Scaling factors (local)
	nucleotides_l = region_max_l - region_min_l
	scaling_factor_local_x = 420.0/nucleotides_l #pixels/nt; aprox; 20 nts in 420 pixels
	
	#Data selection for drawing
	for i, line in enumerate(lines):
		if not line.startswith('@'):
			sp = line.split('\t')
			if sp[0].strip() == 'LOCAL' and int(sp[3]) in range(int(region_min), int(region_max)) and e == sp[2].strip() and sp[5].strip() == 'TOTAL': 
				raw_x_position_l = int(sp[3])
				img_x_position_l = int(raw_x_position_l/scaling_factor_local_x)
				img_relative_x_position_l = img_x_position_l - int(region_min_l/scaling_factor_local_x) + ((raw_x_position_l - region_min_l)*scaling_factor_local_x) + 81
	
				raw_y_position_l = int(sp[4])
				img_y_position_l = 350 - int(raw_y_position_l/scaling_factor_y)
			
				#draw
				draw2.line((img_relative_x_position_l, 348) + (img_relative_x_position_l, img_y_position_l), fill=200, width=30)
	
	#Axis anotations
	#x Axis
	x_p = 80 + int(100/scaling_factor_x)
	x_l = 80 + (1*scaling_factor_local_x)
	ruler = region_min + 100
	ruler_l = region_min_l + 1
	
	while x_p in range(80, 500):
		draw.line((x_p, 350) + (x_p, 355), fill=256, width=1)
		draw.text((x_p - 12, 357), (str(ruler)), font=fnt2, fill=(0,0,0,255))  #NOPE
		ruler = ruler + 100
		x_p = int(x_p + (100/scaling_factor_x)) #Ruler with 100 nts separations
	
	
	while x_l in range(80, 500):
		draw2.line((x_l+1, 350) + (x_l+1, 355), fill=256, width=1)
		draw2.text((x_l - 12, 357), (str(ruler_l)), font=fnt2, fill=(0,0,0,255))
		x_l = int(x_l + (1*scaling_factor_local_x)) #Ruler with 1 nt separations		
		ruler_l = ruler_l + 1  
		
		
	
	#y Axis
	y_p = 350 - int(10/scaling_factor_y)
	y_l = 350 - int(10/scaling_factor_y)
	counter = 10
	counter_l = 10
	while y_p in range(100, 351): 
		draw.line((80, y_p) + (75, y_p), fill=256, width=3)
		draw.text((48, y_p-10), ( str(counter)), font=fnt1, fill=(0,0,0,255))
		counter = counter + 10
		y_p = int(y_p - (10/scaling_factor_y))

	while y_l in range(100, 351): 
		draw2.line((80, y_l) + (75, y_l), fill=256, width=3)
		draw2.text((48, y_l-10), ( str(counter_l)), font=fnt1, fill=(0,0,0,255))
		counter_l = counter_l + 10
		y_l = int(y_l - (10/scaling_factor_y))
		
	im.save('3_workflow-output/paired_' + str(e) + '.png')
	im2.save('3_workflow-output/local_' + str(e) + '.png')
	
#_____________________________HTML file


output_html = args.output_html
f3 = open(output_html, 'w')
	
f3.write('<html>' + '\n')

f3.write('<br><h3>Insertions overview</h3>' + '\n')
f3.write('<br>' + '\n')
f3.write('<img src="insertions_overview.png"></img>' + '\n')
f3.write('<br>' + '\n')

for e in insertions: 
	f3.write('<br><h3>Insertion ' + e + '</h3>' + '\n')
	f3.write('<table border="1">' + '\n')
	f3.write('	<tr>' + '\n')
	f3.write('		<td><img src="paired_' + e + '.png"></img></td>' + '\n')
	f3.write('		<td><img src="local_' + e + '.png"></img></td>' + '\n')
	f3.write('	</tr>' + '\n')
	f3.write('</table>' + '\n')


f3.write('<br><br>Here is your processed data:<br>' + '\n')
f3.write('<a href="sorted_insertions.txt" target="_blank">Sorted insertions</a>' + '\n')

f3.write('</html>')
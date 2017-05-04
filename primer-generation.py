#!/usr/bin/python
import math
import argparse
from string import maketrans
#Script used in order to obtain primers.

parser = argparse.ArgumentParser()
parser.add_argument('-file', action="store", dest = 'File', required = "True")
parser.add_argument('-fasta', action = "store", dest = "genome", required = "True")
parser.add_argument('-fq', action = "store", dest = "fq_lim")

args = parser.parse_args()

genome = args.genome

#Tm calculation of an oligo. Based on biophp script of Joseba Bikandi https://www.biophp.org/minitools/melting_temperature/demo.php
def Tm_calculation(oligo):
	primer = float(400) #400 nM are supposed as a standard [primer]	
	mg = float(2) #2 mM are supposed as a standard [Mg2+]
	salt = float(40)  #40 mM are supposed as a standard salt concentration
	s = 0
	h = 0
	#Enthalpy and entrophy values from http://www.ncbi.nlm.nih.gov/pmc/articles/PMC19045/table/T2/ (SantaLucia, 1998)
	dic = {

	"AA": [-7.9,-22.2], 
	"AC": [-8.4,-22.4],
	"AG": [-7.8, -21.0],
	"AT": [-7.2,-20.4],	
	"CA": [-8.5,-22.7],
	"CC": [-8.0, -19.9],
	"CG": [-10.6,-27.2],
	"CT": [-7.8,-21.0],
	"GA": [-8.2,-22.2],
	"GC": [-9.8, -24.4],
	"GG": [-8.0, -19.9],
	"GT": [-8.4, -22.4],
	"TA": [-7.2,-21.3],
	"TC": [-8.2,-22.2],
	"TG": [-8.5,-22.7],
	"TT": [-7.9,-22.2]}

	#Effect on entropy by salt correction; von Ahsen et al 1999
	#Increase of stability due to presence of Mg
	salt_effect = (salt/1000)+((mg/1000)*140)
	#effect on entropy
	s+=0.368 * (len(oligo)-1)* math.log(salt_effect)
	#terminal corrections. Santalucia 1998
	firstnucleotide= oligo[0]
	if firstnucleotide=="G" or firstnucleotide=="C": h+=0.1; s+=-2.8
	if firstnucleotide=="A" or firstnucleotide=="T": h+=2.3; s+=4.1

	lastnucleotide= oligo[-1]
	if lastnucleotide=="G" or lastnucleotide=="C": h+=0.1; s+=-2.8
	if lastnucleotide=="A" or lastnucleotide=="T": h+=2.3; s+=4.1
	#compute new H and s based on sequence. Santalucia 1998
	for i in range(0,len(oligo)-1):
		f = i+ 2
		substring = oligo[i:f]
		try:
			h = h + float(dic[substring][0])
			s =s + float(dic[substring][1])
		except:
			return 0

	
   	tm=((1000*h)/(s+(1.987*math.log(primer/2000000000))))-273.15
   	return tm


def reverse_complementary(oligo):
	revcomp = oligo.translate(maketrans('ACGT', 'TGCA'))[::-1]
	return revcomp	


# Function to parse fasta file (based on one of the Biopython IOs)
def read_fasta(fp):
	name, seq = None, []
	for line in fp:
		line = line.rstrip()
		if line.startswith('>'):
			if name: yield (name, ''.join(seq))
			name, seq = line, []
		else:
			seq.append(line)
	if name: yield (name, ''.join(seq))



def genome_selection(contig,genome):
	with open(genome) as fp:
		for name_contig, seq_contig in read_fasta(fp):
			if name_contig[1:].lower() == contig:
				genome = seq_contig
		return genome

def rule_1(oligo,sense):
	last_element = len(oligo)
	if sense == "reverse" : oligo = reverse_complementary(oligo)
	while True:
		end_of_primer = 21
		begin_of_primer = 0
		oligo = oligo[:last_element]
		guanine = oligo.rfind("G")
		cytosine = oligo.rfind("C")
		
		#Checking wheter there are both G and C in the oligo
		if guanine != -1 and cytosine != -1:
			last_element =  max([guanine,cytosine])
		else:
			if guanine == -1 and cytosine == -1:
				found = "no"
				return found, found, "-"
				break
			elif guanine == -1 and cytosine != -1:
				last_element = cytosine
			elif guanine != -1 and cytosine == -1:
				last_element = guanine
		begin = last_element - end_of_primer 
		end = last_element 
		while end - begin < 26 and end - begin > 16:
			if begin < 0:
				break
			primer = oligo[begin:end+1]
			Tm = Tm_calculation(primer)
			if Tm > 60 and Tm < 64:
				found = "yes"
				return found, primer, Tm
			elif Tm < 60:
				begin -= 1
			elif Tm > 64:
				begin += 1
def rule_2(oligo,sense):
	#This rule just looks for primers which 
	begin_of_primer = 0
	if sense == "reverse" : oligo = reverse_complementary(oligo)
	while True:
		end_of_primer =21 + begin_of_primer

		if end_of_primer > len(oligo):
			found = "no"
			return found, found, "-"
		while end_of_primer - begin_of_primer < 26 and end_of_primer - begin_of_primer > 16:
			primer = oligo[begin_of_primer:end_of_primer+1]
			Tm = Tm_calculation(primer)
			if Tm >= 60 and Tm <= 64:
				found = "yes"
				return found, primer, Tm
			elif Tm < 60:
				end_of_primer += 1
			elif Tm > 64:
				end_of_primer -= 1		
		begin_of_primer +=1


def snp_calculation(position,genome):
	#Total size of the amplification 
	size_i = 300
	size_f = 500

	oligos = []
	Tms = []
	#upstream primer
	up_primer_pos = int(position) - size_i
	oligo = genome[up_primer_pos-1 : up_primer_pos + 100]
	result = rule_1(oligo, "upstream")
	if result[0] == "no":
		result = rule_2(oligo, "upstream")
		if result[0] == "no":
			oligos.append("not found")
			oligos.append("-")
			Tms.append("-")
			Tms.append("-")
	if result[0] == "yes":
		oligos.append(result[1])
		Tms.append(str(result[2])) 
		#downstream primer
		down_primer_pos = int(position) + size_f
		oligo = genome[down_primer_pos-1 : down_primer_pos + 100]
		result = rule_1(oligo,"downstream")
		if result[0] == "no":
			result = rule_2(oligo, "downstream")
			if result[0] == "no":
				oligos.append("not found")
				Tms.append("-")
		if result[0] == "yes":
			oligos.append(result[1])
			Tms.append(str(result[2]))
	return oligos,Tms
def insertion_calculation(position,genome,contig_used):
	size= 600
	oligos = []
	Tms = []
	selection = "5"
	try_size = 100
	pos_n_contig = contig_used+"_"+position
	#insertion primer
	#Generation of the oligo from the insertion where the primer will be searched	
	for selection in [5,3]:
		if selection == 3:
			lenght_consensus = len(consensus_3[pos_n_contig])
			how = "forward"
			try_oligo = consensus_3[pos_n_contig][:lenght_consensus]
		elif selection == 5:
			lenght_consensus = len(consensus_5[pos_n_contig])
			how = "reverse"
			try_oligo = consensus_5[pos_n_contig][:lenght_consensus]			

		if lenght_consensus < 10:
			oligos.extend(["not found","-","-"])
			Tms.extend(["-","-","-"])		

		result = rule_1(try_oligo,how)
		if result[0] == "no":
			result = rule_2(try_oligo, how)
			if result[0] == "no":
				oligos.extend(["not found","-","-"])
				Tms.extend(["-","-"])
				return oligos,Tms
		if result[0] == "yes":
			oligos.append(result[1])
			Tms.append(str(result[2]))

	#Generation of the forward and reverse oligos
	up_primer_pos = int(position) - size
	try_oligo = genome[up_primer_pos-1 : up_primer_pos + 100]
	result = rule_1(try_oligo, "forward")
	if result[0] == "no":
		result = rule_2(try_oligo, "forward")
		if result[0] == "no":
			oligos.append("not found")
			oligos.append("-")
			Tms.append("-")
			Tms.append("-")
	if result[0] == "yes":
		oligos.append(result[1])
		Tms.append(str(result[2])) 
		#downstream primer
		down_primer_pos = int(position) + size
		try_oligo = genome[down_primer_pos-1 : down_primer_pos + 100]
		result = rule_1(try_oligo,"reverse")
		if result[0] == "no":
			result = rule_2(try_oligo, "reverse")
			if result[0] == "no":
				oligos.append("not found")
				Tms.append("-")
		if result[0] == "yes":
			oligos.append(result[1])
			Tms.append(str(result[2]))
	return oligos,Tms  





def fastaq_to_dic(fq):
	#It gets two dictionaries for 3' and 5' sequences. 
	dic_fas_3= {}
	dic_fas_5= {}
	fq = open(fq,"r")
	for line in fq:
		split = line.split("_") #Data format is chr_postion_3/5'
		if line.startswith("@"): #This line will be the header, the followings until find + have to be together
			i = 1
			m= 0
		if line.startswith("+"):
			m = 1
		
		if i == 1: #header, we take off the "/" that get in as input in the header 
			h = split[0].split("/")[-1]+"_"+split[1]
			#Depending on whether the reads are in the 3' or 5' extreme they will go to one dic or another.
			if split[2].strip()=="3":
				n = 1
				dic_fas_3[h]=""
			if split[2].strip()=="5":
				n= 2
				dic_fas_5[h]=""
			#Sequences are pasted together in each position
		if m == 0 and i!= 1:
			line = line.upper().rstrip()
			if n == 1:
				dic_fas_3[h]+= line
			if n == 2:
				dic_fas_5[h]+= line
		i += 1
	return dic_fas_3,dic_fas_5

positions = open(args.File,"r")
result = open("variants2.txt","w")

n = 0
first_list = []
for line in positions.readlines():
	line = line.split("\t")
	if n != 0:
		first_list.append(line)	
	n += 1
former = ""
list2= []
contig_used = ""
mode = first_list[0][0]
if mode == "snp":
	result.write("@type\tcontig\tposition\tref_base\talt_base\thit\tmrna_start\tmrna_end\tstrand\tgene_model\tgene_element\taa_pos\taa_ref\taa_alt\tdistance_to_selected_position\tforward primer\tTm forward\treverse primer\tTm reverse\n")
if mode == "lim":
	#try:
	consensus = fastaq_to_dic(args.fq_lim)
	consensus_3 = consensus[0]
	consensus_5 = consensus[1]
	#except:
	#	print "Fq file missing"
	#	exit()
	result.write("@type\tcontig\tposition\tref_base\talt_base\thit\tmrna_start\tmrna_end\tstrand\tgene_model\tgene_element\taa_pos\taa_ref\taa_alt\tforward primer\tTm forward\tinsertion primer 5'\tTm insertion primer 5'\tinsertion primer 3'\tTm insertion primer 3'\treverse primer\tTm reverse\n")

for line in first_list:
	if mode == "snp": v = line[0]+"\t"+line[1]+"\t"+line[2]+"\t"+line[3]+"\t"+line[4]+"\t"+line[5]+"\t"+line[6]+"\t"+line[7]+"\t"+line[8]+"\t"+line[9]+"\t"+line[10]+"\t"+line[11]+"\t"+line[12]+"\t"+line[13]+"\t"+line[14].rstrip()
	else: v = line[0]+"\t"+line[1]+"\t"+line[2]+"\t"+line[3]+"\t"+line[4]+"\t"+line[5]+"\t"+line[6]+"\t"+line[7]+"\t"+line[8]+"\t"+line[9]+"\t"+line[10]+"\t"+line[11]+"\t"+line[12]+"\t"+line[13].rstrip()
	if line[5] == "nh":
		if mode == "snp": list2.append(v+"\t-\t-\t-\t-\n")
		else: list2.append(v+"\t-\t-\t-\t-\t-\t-\n")
	else:
		a = line[1]+"-"+line[2]
		if a == former:
			if mode == "snp": list2.append(v+"\t-\t-\t-\t-\n")
			else: list2.append(v+"\t-\t-\t-\t-\t-\t-\n")
		elif a != former:
			if mode == "snp":
				if line[1] != contig_used:
					genom = genome_selection(line[1],genome)
					contig_used = line[1]
				r = snp_calculation(line[2],genom)
				list2.append(v+"\t"+r[0][0]+"\t"+r[1][0]+"\t"+r[0][1]+"\t"+r[1][1]+"\n")
			if mode == "lim":
				if line[1] != contig_used:
					genom = genome_selection(line[1],genome)
					contig_used = line[1]
				r = insertion_calculation(line[2],genom,contig_used)
				list2.append(v+"\t"+r[0][2]+"\t"+r[1][2]+"\t"+r[0][0]+"\t"+r[1][0]+"\t"+r[0][1]+"\t"+r[1][1]+"\t"+r[0][3]+"\t"+r[1][3]+"\n") 


		former = a
		







for items in list2:
	result.write(items)
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-f2_mut', action="store", dest = 'input_mut')
parser.add_argument('-f2_wt', action="store", dest = 'input_wt')
parser.add_argument('-out', action="store", dest = 'output')
parser.add_argument('-f_input', action="store", dest = 'f_input')

args = parser.parse_args()

import time
start_time = time.time()

#Input 
input1 = args.input_mut
f1 = open(input1, 'r')
mut_lines = f1.readlines()	

input2 = args.input_wt
f2 = open(input2, 'r')
wt_lines = f2.readlines()	

f_input = args.f_input


#Output
output = args.output
f3 = open(output, 'w')

#This function enables to obtain data regarding chromosomes and lenght of the,
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

ch = list()
#From the data of read_fasta, I create a dictionary with the name of the contigs and its lenght
with open(f_input) as fp:
	for name_contig in read_fasta(fp):
		ch.append(name_contig[0][1:])

for chr in ch:
	dic_mut = {}
	dic_wt = {}
	list_mut = list()
	list_wt = list()

	for i, line in enumerate(mut_lines):
		if not line.startswith('#'):
			sp = line.split('\t')
			if chr == sp[0]:
				dic_mut[sp[1]] = [sp[2], sp[3], sp[4], sp[5], sp[6].strip('\n')]
				list_mut.append(sp[1])

	for i, line in enumerate(wt_lines):
		if not line.startswith('#'):
			sp = line.split('\t')
			if chr == sp[0]:
				dic_wt[sp[1]] = [sp[2], sp[3], sp[4], sp[5], sp[6].strip('\n')]
				list_wt.append(sp[1])

	set_2 = frozenset(list_mut)

	intersection = [x for x in list_wt if x in set_2]

	for i in intersection:
		f3.write( str(chr) + '\t' + str(i) + '\t' + str(dic_mut[i][0]) +'\t' +  str(dic_mut[i][1]) +'\t' +  str(dic_mut[i][2]) + '\t' + str(dic_mut[i][3]) + '\t' + str(dic_mut[i][4]) + '\t' + str(dic_wt[i][3]) +'\t' +  str(dic_wt[i][4]) + '\n')
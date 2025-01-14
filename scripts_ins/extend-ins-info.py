# Comando pruebas: 
#		./scripts_ins/extend-ins-info.py --project-name user_projects/project-ins

# This scrip retrieves the upstream and downstream sequences of each insertion site and the reconstructed sequences of the 5 and 3 prime ends of the insertion and adds the information to the insertions_output.txt file.

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--project-name', action="store", dest='project_name', required=True)
args = parser.parse_args()
project = args.project_name

# Input files: fasta genome and insertions_output.txt
fp = open(project + '/1_intermediate_files/gnm_ref_merged/genome.fa', 'r')
input_file = open(project + '/3_workflow_output/insertions_output.txt', 'r')

# This function parses the information from the fasta files
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

# We create a list of all the contigs with the format [[contig_name, sequence], [contig_name, sequence] ...]
fastalist = list()
for name_contig, seq_contig in read_fasta(fp):
	fastalist.append([name_contig.lower(), seq_contig])

# We retrieve the upstream and downstream sequences of each insertion from the fastalist. We also create a new list with the complete lines
final_lines = list()
for line in input_file:
	if not line.startswith('@'):
		sp = line.split()
		chromosome = str(sp[1])
		position = str(sp[2])
		for chrm in fastalist:
			if chrm[0].strip() == '>'+chromosome.strip().lower():
				upstream =  chrm[1][int(position)-51:int(position)-1]
				downstream =  chrm[1][int(position):int(position)+50]
				line = line.strip('\n')
				line = line + '\t' + upstream + '\t' + downstream
				final_lines.append(line)

# We re-write the file with the extended information to the output file from the final_lines list
output_file = open(project + '/3_workflow_output/insertions_output.txt', 'w')

output_file.write('@type\tcontig\tposition\tref_base\talt_base\thit\tmrna_start\tmrna_end\tstrand\tgene_model\tgene_element\taa_pos\taa_ref\taa_alt\tgene_funct_annot\tf_primer\ttm_f_primer\tinsertion_primer_5\ttm_insertion_primer_5\tinsertion_primer_3\ttm_insertion_primer_3\tr_primer\ttm_r_primer\tupstream\tdownstream\n')    
for line in final_lines:
	output_file.write(line + '\n')

output_file.close()


# _______________________________________________________________________________________

# Now we will retrieve the reconstructed sequences of the 5 and 3 prime ends of the insertion 

fi = open(project + '/1_intermediate_files/all_insertions_cns.fq', 'r')
input_file = open(project + '/3_workflow_output/insertions_output.txt', 'r')

ins_extr = list()
for line in fi:
	if line.startswith('@user_projects'):
		switch = 'seq'
		sp = line.split('/')
		data = sp[-1]
		sp2 = data.split('_')
		chromosome = sp2[0].lower()
		position = sp2[1]
		end = sp2[2].strip('\n')
		sequence = ''

	if "c" in str(line).lower() or "a" in str(line).lower() or "t" in str(line).lower() or "g" in str(line).lower() and switch == 'seq':
		if not line.startswith('@'):
			sequence = sequence + (str(line).strip('\n'))

	if line.startswith('+\n'):
		switch = 'qual'
		purged_sequence = '-'
		for i, n in enumerate(sequence): 
			if n.lower() == 'n':
				continue 
			if n.lower() != 'n':
				purged_sequence = sequence[i:]
				break

		if len(str(purged_sequence)) <= 1: 
			purged_sequence = '-'

		ins_extr.append([chromosome, position, end, purged_sequence])
	

final_lines = list()
for line in input_file:
	if not line.startswith('@'):
		sp = line.split()
		chromosome = str(sp[1]).lower()
		position = str(sp[2])
		for ins in ins_extr:
			if ins[0] == chromosome and int(ins[1]) == int(position) and ins[2] == '5':
				line = line.strip('\n') + '\t' + str(ins[3])

		for ins in ins_extr:
			if ins[0] == chromosome and int(ins[1]) == int(position) and ins[2] == '3':
				line = line.strip('\n') + '\t' + str(ins[3])
				final_lines.append(line)

# We re-write the file with the extended information to the output file from the final_lines list
output_file = open(project + '/3_workflow_output/insertions_output.txt', 'w')

output_file.write('@type\tcontig\tposition\tref_base\talt_base\thit\tmrna_start\tmrna_end\tstrand\tgene_model\tgene_element\taa_pos\taa_ref\taa_alt\tgene_funct_annot\tf_primer\ttm_f_primer\tinsertion_primer_5\ttm_insertion_primer_5\tinsertion_primer_3\ttm_insertion_primer_3\tr_primer\ttm_r_primer\tupstream\tdownstream\t5_end_ins\t3_end_ins\n')    
for line in final_lines:
	output_file.write(line + '\n')

output_file.close()
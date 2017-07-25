#python ./graphic_output/report.py -variants ./user_projects/project/3_workflow_output/candidate_variants.txt -log ./user_projects/project/2_logs/log.log -output_html ./user_projects/project/3_workflow_output/report.html -project user_projects/project  -mut_type snp -files_dir ./user_projects/project/3_workflow_output/
#python ./graphic_output/report.py -variants ./user_projects/project/3_workflow_output/insertions_output.txt -log ./user_projects/project/2_logs/log.log -output_html ./user_projects/project/3_workflow_output/report.html -project user_projects/project  -mut_type lin -files_dir ./user_projects/project/3_workflow_output/

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-mut_type', action="store", dest = 'mut_type')
parser.add_argument('-variants', action="store", dest = 'variants')
parser.add_argument('-log', action="store", dest = 'log')
parser.add_argument('-output_html', action="store", dest = 'output_html')
parser.add_argument('-project', action="store", dest = 'project')
parser.add_argument('-files_dir', action="store", dest = 'files_dir')

args = parser.parse_args()

#Log input
input_log = args.log

#VAriants input
input_var = args.variants


#HTML output
output_html = args.output_html
output = open(output_html, 'w')

#Others
mut_type = args.mut_type

#______________________________________________List output '+files_dir+'__________________________________________________
from os import listdir
from os.path import isfile, join

files_dir = args.files_dir

files = [f for f in listdir(files_dir) if isfile(join(files_dir, f))]

#______________________________________________Log info___________________________________________________________
with open(input_log, 'r') as f1:
	for line in f1:
		if line.startswith('Project name'):
			sp = line.split()
			project_name = str(sp[-1])

		if line.startswith('Reference sequence:'):
			sp = line.split()
			ref_files = str(sp[-1])

		if line.startswith('Insertion sequence:'):
			sp = line.split()
			ins_file = str(sp[-1])

		if line.startswith('Library type (problem sample):'):
			sp = line.split()
			reads_type = str(sp[-1])

		if line.startswith('Single-end reads (problem sample):'):
			sp = line.split()
			reads_s = str(sp[-1])

		if line.startswith('Forward reads (problem sample):'):
			sp = line.split()
			reads_f = str(sp[-1])

		if line.startswith('Reverse reads (problem sample):'):
			sp = line.split()
			reads_r = str(sp[-1])

		if line.startswith('Library type (control sample):'):
			sp = line.split()
			reads_type_control = str(sp[-1])

		if line.startswith('Single-end reads (control sample):'):
			sp = line.split()
			reads_s_control = str(sp[-1])

		if line.startswith('Forward reads (control sample):'):
			sp = line.split()
			reads_f_control = str(sp[-1])

		if line.startswith('Reverse reads (control sample):'):
			sp = line.split()
			reads_r_control = str(sp[-1])

		if line.startswith('GFF file:'):
			sp = line.split()
			gff_file = str(sp[-1])

		if line.startswith('Annotation file:'):
			sp = line.split()
			if str(sp[-1]) == "n/p": ann_file = "Not provided"

		if line.startswith('Data source:'):
			sp = line.split()
			data_source = str(sp[-1])

		if line.startswith('Type of cross [bc/oc]:'):
			sp = line.split()
			if str(sp[-1]) == 'bc': cross_type = 'backcross'
			if str(sp[-1]) == 'oc': cross_type = 'outcross'

		if line.startswith('Mutant strain [ref/noref]:'):
			sp = line.split()
			if str(sp[-1]) == 'ref': mut_background = 'reference'
			if str(sp[-1]) == 'noref': mut_background = 'non-reference'

		if line.startswith('SNP analysis type [par/f2wt]:'):
			sp = line.split()
			if str(sp[-1]) == 'par': snp_analysis_type = 'parental'
			if str(sp[-1]) == 'f2wt': snp_analysis_type = 'wild type F2'

		if line.startswith('Parental used as control [mut/nomut/np]:'):
			sp = line.split()
			if str(sp[-1]) == 'mut': parental_used_as_control = 'mutant'
			if str(sp[-1]) == 'nomut': parental_used_as_control = 'wild type'

if mut_type == 'snp':
	#SNP mappint control samples
	if snp_analysis_type == 'parental' and parental_used_as_control == 'mutant' : control = ' parental of the mutant strain.'
	if snp_analysis_type == 'parental' and parental_used_as_control == 'wild type' : control = ' wild type parental of the mapping crossing.'
	if snp_analysis_type == 'wild type F2' : control = ' wild type F2 of the mapping cross.'

if data_source == 'sim':
	with open(input_log, 'r') as f1:
		for line in f1:
			if line.startswith('Simulator (sim-mut.py) command:'):
				sp = line.split()
				number_mutations = str(sp[-1].split('+')[0])

			if line.startswith('Simulator (sim-seq.py) command:'):
				sp = line.split()
				read_depth = str(sp[-1].split('+')[0])



if mut_type == 'lin':
	#______________________________________________Get list of insertions_____________________________________________
	insertions_list = list()

	infile = './'+args.project+'/3_workflow_output/sorted_insertions.txt'
	sorted_insertions = open(infile, 'r')

	for line in sorted_insertions:
		if not line.startswith('@'):
			sp = line.split()
			if sp[2].strip() not in insertions_list:
				insertions_list.append(sp[2].strip())

	insertions_pos_list = list()
	with open(input_var) as f:
		for line in f:
			if not line.startswith('@'):
				sp = line.split()
				ins_localizer = str(sp[1].strip().lower() + '-' + sp[2].strip())
				with open(infile) as f2:
					for line in f2:
						if not line.startswith('@'):
							sp2 = line.split()
							ins_localizer_2 = str(sp2[1].strip().lower() + '-' + sp2[3].strip())
							if ins_localizer == ins_localizer_2:
								for insertion in insertions_list:
									if insertion == sp2[2]:
										sublist = [insertion, str(sp2[3]), sp[1]]
										if sublist not in insertions_pos_list:
											insertions_pos_list.append(sublist)

#______________________________________________Writting header____________________________________________________

#HTML/CSS stuff
output.write(
'<!DOCTYPE html>' + '\n'
'<html>' + '\n'
'<head>' + '\n'

'	<meta charset="utf-8" />' + '\n'
'	<title>Easymap - report</title>' + '\n'
'	<style>' + '\n'
'		#wrapper {' + '\n'
'			width: 100%;' + '\n'
'			max-width: 1050px;' + '\n'
'			margin: 0 auto;' + '\n'
'			font-family: arial, helvetica;' + '\n'
'		}	' + '\n'
'		.easymap {' + '\n'
'			border: 0;' + '\n'
'			color: rgb(139, 167, 214);' + '\n'
'			background-color: rgb(139, 167, 214);' + '\n'
'			height: 5px;' + '\n'
		
'		}	' + '\n'
'		.img { width: 100%; }' + '\n'
'		.result1 { max-width: 864px; }' + '\n'
'		.result2 { max-width: 1000px; }' + '\n'


'		table {border-collapse:collapse; table-layout:fixed;}' + '\n'
'		table td {border:solid 0px #fab;  word-wrap:break-word; vertical-align:top;}' + '\n'
'       tr:hover { background-color: #ededed; }' + '\n'
'		#t {  border: 0px solid red; word-wrap:break-word; table-layout:fixed; }' + '\n'
'		#candidates { line-height: 10px; text-align:left; word-wrap:break-word; ; }' + '\n'

'	</style>' + '\n'

'</head>' + '\n'
)

#Header and run summary
output.write(
'<body>' + '\n'
'	<div id="wrapper">' + '\n'
'		<hr class="easymap">' + '\n'
'		<h1>Poject: ' +  project_name + '</h1>' + '\n'
'		<hr class="easymap">' + '\n'

)

#Exp/sim and read files
output.write(
'		<h2>Run summary</h2>' + '\n'
'		<table id="t">' + '\n'
'		<col width="300">' + '\n'
'		<col width="700">' + '\n'
	)

output.write(

'		<tr>' + '\n'
'			<td> <b>Input genome files :</b></td>' + '\n'
'			<td>' + ref_files + '</td>' + '\n'
'		</tr>' + '\n'

	)


#Read files
if mut_type == 'lin' and data_source == 'exp': 
	if reads_type == 'pe':
		output.write(
'		<tr>' + '\n'
'			<td> <b>Input reads files:</b></td>' + '\n'
'			<td>' + reads_f + ', &nbsp;&nbsp;&nbsp;&nbsp;' + reads_r + '</td>' + '\n'
'		</tr>' + '\n'
		)

	elif reads_type == 'se':
		output.write(
'		<tr>' + '\n'
'			<td> <b>Input reads files:</b></td>' + '\n'
'			<td>' + reads_s + '</td>' + '\n'
'		</tr>' + '\n'
			)


if mut_type == 'snp' and data_source == 'exp': 
	if reads_type == 'pe':
		output.write(
'		<tr>' + '\n'
'			<td> <b>Input problem reads files:</b></td>' + '\n'
'			<td>' + reads_f + ', &nbsp;&nbsp;&nbsp;&nbsp;' + reads_r + '</td>' + '\n'
'		</tr>' + '\n'
		)

	elif reads_type == 'se':
		output.write(
'		<tr>' + '\n'
'			<td> <b>Input problem reads files:</b></td>' + '\n'
'			<td>' + reads_s + '</td>' + '\n'
'		</tr>' + '\n'
			)

	if reads_type_control == 'pe':
		output.write(
'		<tr>' + '\n'
'			<td> <b>Input control reads files:</b></td>' + '\n'
'			<td>' + reads_f_control + ', &nbsp;&nbsp;&nbsp;&nbsp;' + reads_r_control + '</td>' + '\n'
'		</tr>' + '\n'
		)

	elif reads_type_control == 'se':
		output.write(
'		<tr>' + '\n'
'			<td> <b>Input control reads files:</b></td>' + '\n'
'			<td>' + reads_s_control + '</td>' + '\n'
'		</tr>' + '\n'
			)




if data_source == 'sim':
	if mut_type == 'lin':
		output.write(
'		<tr>' + '\n'
'			<td> <b>Number of insertions (simulation)</b></td>' + '\n'
'			<td>' + number_mutations + '</td>' + '\n'
'		</tr>' + '\n'
'		<tr>' + '\n'
'			<td> <b>Read depth (simulation):</b></td>' + '\n'
'			<td>' + read_depth + '</td>' + '\n'
'		</tr>' + '\n'
		)

	elif mut_type == 'snp':
		output.write(
'		<tr>' + '\n'
'			<td> <b>Number of mutations (simulation)</b></td>' + '\n'
'			<td>' + number_mutations + '</td>' + '\n'
'		</tr>' + '\n'
'		<tr>' + '\n'
'			<td> <b>Read depth (simulation):</b></td>' + '\n'
'			<td>' + read_depth + 'x</td>' + '\n'
'		</tr>' + '\n'
		)
		

if mut_type == 'snp': 
	output.write(

'		<tr>' + '\n'
'			<td> <b>Experimental design: </b></td>' + '\n'
'			<td> Mutation in ' + mut_background + ' genetic background. A ' + cross_type + ' was performed to obtain the mapping population. The control sample is the ' + control +'</td>' + '\n'
'		</tr>' + '\n'

		)

#Gff and ann '+files_dir+'
output.write(

'		<tr>' + '\n'
'			<td> <b>Structural annotation file:</b></td>' + '\n'
'			<td>' + gff_file + '</td>' + '\n'
'		</tr>' + '\n'

'		<tr>' + '\n'
'			<td> <b>Functional annotation file:</b></td>' + '\n'
'			<td>' + ann_file + '</td>' + '\n'
'		</tr>' + '\n'
'		</table>' + '\n'

)

#Link to log file
output.write(
'		<a href=../2_logs/log.log target="_blank">Cick to see log file</a>' + '\n'
'		<hr class="easymap">' + '\n'
)


#Input data quality assessment
if data_source == 'exp':

	output.write(
	'		<h2>Input data quality assessment</h2>' + '\n'
		)

	if mut_type == 'lin': 
		if reads_type == 'pe':
			output.write(
	'		<b>Paired end reads quality assessment<br></b>' + '\n'
	'		<center> <img src="./paired-end-problem-forward-reads-qual-stats.png" width="500" > <img src="./paired-end-problem-reverse-reads-qual-stats.png" width="500" > </center> ' + '\n'

			)

		if reads_type == 'se':
			output.write(
	'		<b>Single end reads quality assessment<br></b>' + '\n'
	'		<center> <img src="./single-end-problem-reads-qual-stats.png" width="500" > </center> ' + '\n'

			)


	if mut_type == 'snp': 
		if reads_type == 'pe':
			output.write(
	'		<b>Problem paired end reads quality assessment<br></b>' + '\n'
	'		<center> <img src="./'+'/qual1.png" width="500" > <img src="./qual2.png" width="500" > </center> ' + '\n'

			)

		if reads_type == 'se':
			output.write(
	'		<b>Problem single end reads quality assessment<br></b>' + '\n'
	'		<center> <img src="./single-end-problem-reads-qual-stats.png" width="500" > </center> ' + '\n'

			)

		if reads_type_control == 'pe':
			output.write(
	'		<b>Control paired end reads quality assessment<br></b>' + '\n'
	'		<center> <img src="./qual1.png" width="500" > <img src="./qual2.png" width="500" > </center> ' + '\n'

			)

		if reads_type_control == 'se':
			output.write(
	'		<b>Control single end reads quality assessment<br></b>' + '\n'
	'		<center> <img src="./single-end-problem-reads-qual-stats.png" width="500" > </center> ' + '\n'

			)

		output.write(
	'		<b>Problem sample and control sample read depth distribution<br></b>' + '\n'
	'		<center> <img src="./frequence_depth_alignment_distribution_sample.png" width="500" > <img src="./frequence_depth_alignment_distribution_control.png" width="500" > </center> ' + '\n'
	'		<hr class="easymap">' + '\n'
			)


#__________________________________LIN cartographic report________________________________________________________________
if mut_type == 'lin': 
	#Genome overview
	output.write(
	'		<h2>Genomic overview</h2>' + '\n'
	'		<center> <img src="./'+'/insertions_overview.png" align="middle" >  </center>' + '\n'
	)

	#Table

	output.write(
		#Table
		'		<h3>Insertions summary</h3>' + '\n'

		'		<table id="candidates" border="0" align="center" cellpadding="10">' + '\n'
		'		  <tr>' + '\n'
		'		    <th>Ins</th>' + '\n'
		'		    <th>Contig</th>' + '\n'
		'		    <th>Position</th>' + '\n'
		'		    <th>Gene (gene element)</th>' + '\n'
		'		    <th>Wt aminoacids</th>' + '\n'
		'		  </tr>' + '\n'


		)

	with open(input_var) as candidates:
		variants_list=list()
		for line in candidates:
			if not line.startswith('@'):
				sp = line.split('\t')
				contig = str(sp[1]).strip()
				position = str(sp[2]).strip()
				aminoacid = str(sp[11]).strip() 
				primer_f = str(sp[15]).strip()
				primer_r = str(sp[21]).strip()
				primer_5 = str(sp[17]).strip()
				primer_3 = str(sp[19]).strip()
				upstream = str(sp[23]).strip()
				downstream = str(sp[24]).strip()
				if str(sp[9]).strip() !='-':
					gene = str(sp[9]).strip() + ' (' + str(sp[10]).strip() + ')'
				else:
					gene = '-'
				if str(sp[14]).strip() != '-':
					annotation = str(sp[14]).strip()  
				else:
					annotation = ' Functional annotation file not provided'

				for i in insertions_pos_list:
					if int(i[1]) == int(position) and str(i[2]).lower().strip() == contig.lower():
						ins = str(i[0])

				variants_list.append([ins, contig, position, gene, aminoacid, primer_f, primer_r, primer_5, primer_3, upstream, downstream, annotation])

				output.write(
				'		  <tr>' + '\n'
				'		    <td>'+ins+'</th>' + '\n'
				'		    <td>'+contig+'</th>' + '\n'
				'		    <td>'+position+'</th>' + '\n'
				'		    <td>'+gene+'</th>' + '\n'
				'		    <td>'+aminoacid+'</th>' + '\n'
				'		  </tr>' + '\n'
					)

		output.write(
			'	</table>' + '\n'
			)

	#Link to variants file
	output.write(
	'		<br><a href=./insertions_output.txt target="_blank">Cick to see full information</a>' + '\n'
	'		<hr class="easymap">' + '\n'
	)
	#Insertions
	for ins in insertions_list:
		for f in sorted(files): 
			if '_ins_' + ins[0] in str(f):
				output.write(
				'		<h2> Insertion   ' +  str(ins[0]) +'</h2>' + '\n'
				'		<center> <img src="./'  +  str(f)  + ' " align="middle" >  </center>' + '\n'
				)

		for f in sorted(files):
			if '_lin_' + ins[0] in str(f):

				gene = str(f).split('_')[5].split('.')[0]+'.'+str(f).split('_')[5].split('.')[1]
				for i in variants_list:
					if gene in str(i[3]):

						output.write(
						'		<h3>  ' +  gene +'</h3>' + '\n'
						'		<center> <img src="./'  +  str(f)  + ' " align="middle" >  </center>' + '\n'
						'		<p>Functional annotation:' + str(i[11]) + '<br>Forward primer: '+str(i[5])+ '<br> Reverse primer: ' + str(i[6]) +'<br>Insertion 5 primer: '+str(i[7])+ '<br> Insertion 6 primer: ' +str(i[8]) +' <p>' + '\n'



						)




#__________________________________SNP cartographic report________________________________________________________________
if mut_type == 'snp':

	#Chromosomes FA vs POS
	#Mapping
	output.write(
	'		<h2>Mapping analysis overview</h2>' + '\n'
		) 
	for f in sorted(files):
		if 'img_2_mapping' in str(f):
			output.write(
			'		<left> <img src="./' +  str(f)  + ' " align="middle" >  </left>' + '\n'
			)

	#Candidates
	#selected chromosome:

	for f in sorted(files):
		if 'img_2_candidates' in str(f) and 'zoom' in str(f):
			sp = str(f).split('_')
			selected_chromosome = str(sp[3]).strip()

	output.write(
	'		<h3>Candidate polymorphisms overview</h3>' + '\n'
		) 

	#Candidates 
	for f in sorted(files):
		if 'img_2_candidates_'+selected_chromosome in str(f).lower() and 'zoom' not in str(f):
			output.write(
			'		<left> <img src="./'  +  str(f)  + ' " align="middle" >  </left>' + '\n'
			)
	#Candidates zoom
	for f in sorted(files):
		if 'img_2_candidates' in str(f) and 'zoom' in str(f):
			output.write(
			'		<left> <img src="./'  +  str(f)  + ' " align="middle" >  </left>' + '\n'
			)
			

	#Legend
	output.write(
	'		<h3>Legend</h3>' + '\n'
	'		<left> <img src="./legend.png " align="middle" >  </left>' + '\n'
	)


	#Candidates table:
	output.write(
		#Table
		'		<h3>Candidate region analysis</h3>' + '\n'

		'		<table id="candidates" border="0" align="center" cellpadding="10">' + '\n'
		'		  <tr>' + '\n'
		'		    <th>ID</th>' + '\n'
		'		    <th>Contig</th>' + '\n'
		'		    <th>Position</th>' + '\n'
		'		    <th>AF</th>' + '\n'
		'		    <th>DTP</th>' + '\n'
		'		    <th>Nucleotide (Ref/Alt)</th>' + '\n'
		'		    <th>Gene (gene element)</th>' + '\n'
		'		    <th>Aminoacid (Ref/Alt)</th>' + '\n'
		'		  </tr>' + '\n'
		)

	with open(input_var) as candidates:
		i=1
		variants_list=list()
		for line in candidates:
			if not line.startswith('@'):
				sp = line.split('\t')
				contig = str(sp[1]).strip()
				position = str(sp[2]).strip()
				AF = str(sp[8]).strip()
				DTP = str(sp[9]).strip()
				nucleotide = str(sp[3]).strip() + '/' + str(sp[4]).strip()
				aminoacid = str(sp[17]).strip() + '/' + str(sp[18]).strip()
				primer_f = str(sp[20]).strip()
				primer_r = str(sp[22]).strip()
				upstream = str(sp[24]).strip()
				downstream = str(sp[25]).strip()
				if str(sp[14]).strip() != '-':
					gene = str(sp[14]).strip() + ' (' + str(sp[15]).strip() + ')'
				else:
					gene = '-'
				if str(sp[19]).strip() != '-':
					annotation = str(sp[19]).strip()  
				else:
					annotation = ' Functional annotation file not provided'

				variants_list.append([str(i), contig, position, AF, DTP, nucleotide, gene, aminoacid, primer_f, primer_r, upstream, downstream, annotation])

				output.write(
				'		  <tr>' + '\n'
				'		    <td>'+str(i)+'</th>' + '\n'
				'		    <td>'+contig+'</th>' + '\n'
				'		    <td>'+position+'</th>' + '\n'
				'		    <td>'+AF+'</th>' + '\n'
				'		    <td>'+DTP+'</th>' + '\n'
				'		    <td>'+nucleotide+'</th>' + '\n'
				'		    <td>'+gene+'</th>' + '\n'
				'		    <td>'+aminoacid+'</th>' + '\n'
				'		  </tr>' + '\n'
					)

				i=i+1

		output.write(
			'	</table>' + '\n'
			)

	#Link to variants file
	output.write(
	'		<br><a href=./candidate_variants.txt target="_blank">Cick to see full information</a>' + '\n'
	'		<hr class="easymap">' + '\n'
	)

	#Candidate SNPs
	output.write(
	'		<h2>Candidate mutations</h2>' + '\n'
		) 
	for var in variants_list:
		gene_name = var[6].split(' (')[0]
		for f in sorted(files):
			if 'gene_plot_snp' in str(f) and gene_name in str(f) and var[2] in str(f):
				output.write(
				'		<h3>' + str(var[0]) + '. ' + gene_name + '</h3>' + '\n'
				'		<left> <img src="./'  +  str(f)  + ' " align="middle" >  </left>' + '\n'
				'		<p>Functional annotation:' + annotation + '<br>Forward primer: '+primer_f+ '<br> Reverse primer: ' +primer_r +' <p>' + '\n'

				)
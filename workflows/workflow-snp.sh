#!/bin/bash
# This is the command sent by 'master.sh':
# ./workflow-x.sh $my_log_file $project_name $workflow $data_source $lib_type $ins_seq $read_s $read_f $read_r $gff_file $ann_file
#
# This command is always the same, regardless of the workflow
#
# Fields that can be equal to 'n/p' (= not provided) are the following: $ins_seq, $read_s, $read_f, $read_r, $ann_file
# If $ins_seq = n/p, that is because $workflow = snp. Therefore, no insertion seq is needed and $ins_seq is ignored by hte program.
# If $read_s = n/p, that is because $lib_type = pe, so it is ignored by the program.
# If $read_f and $read_r = n/p, that is because $lib_type = se, so it is ignored by the program.
# If $ann_file = n/p, this is because user did no have it. This program has the deal with this: if data not provided, simply do not
# include gene annotated info to the report.
#
# my_log_file		>	$1
# project_name		>	$2
# workflow			>	$3
# data_source		>	$4
# lib_type			>	$5
# ins_seq			>	$6
# read_s			>	$7
# read_f			>	$8
# read_r			>	$9
# gff_file			>	${10}
# ann_file			>	${11}
# read_s_par			>	${12}
# read_f_par			>	${13}
# read_r_par			>	${14}
#cross_type			>	${15} 
#is_ref_strain		>	${16} 
# parental_reads_provided			>	${17}
# [21] $snp_analysis_type [par/f2wt]	>  ${18}
# lib_type_control			>	${19}



# Set 'exit_code' (flag variable) to 0
exit_code=0

# Set location of log file
my_log_file=$1


start_time=`date +%s`


#Create input variables
my_log_file=$1
project_name=$2
my_sample_mode=$5 														#[pe, se], paired/single  
my_control_mode=${19}													#TEMPORAL, in future independent						<------------------------------------------------------------------------
my_rd=$7											 			#reads (single)
my_rf=$8 														#forward reads
my_rr=$9												 		#reverse reads 			
my_p_rd=${12}											 	#reads (single) parent	<------------------------------------------------------------------------
my_p_rf=${13} 													#forward reads parent	<------------------------------------------------------------------------
my_p_rr=${14}											 		#reverse reads parent	<------------------------------------------------------------------------
my_gs=gnm_ref_merged/genome.fa 									#genome sequence
my_ix=genome_index 							
my_gff=${10}													#Genome feature file
my_ann=${11}													
my_rrl=250 														#Regulatory region length
my_log_file=$1
my_mut=snp  													#my_mut takes the values 'snp' in this workflow and 'lin' in the large insertions workflow, for the execution of the graphic output module



my_cross=${15}													#oc / bc : f2 obtained by outcross or backcross 									<------------------------------------------------------------------------
my_mutbackgroud=${16}											#ref / noref : genetic background of the mutation									<------------------------------------------------------------------------
my_pseq=${17}													#mut / nomut : sequenced parental provided is the mutagenized one or the other		<------------------------------------------------------------------------

snp_analysis_type=${18}


#Define the folders in the easymap directory 
f0=user_data
f1=$project_name/1_intermediate_files
f2=$project_name/2_logs
f3=$project_name/3_workflow_output

# Write PID to status file
my_status_file=$f2/status
echo 'pid workflow '$BASHPID >> $my_status_file

#Save path to bowtie2-build and bowtie2 in variable BT2
export location="$PWD" 


#Execute bowtie2-build on genome sequence 
{
	$location/bowtie2/bowtie2-build $f1/$my_gs $f1/$my_ix 1> $f2/bowtie2-build_std1.txt 2> $f2/bowtie2-build_std2.txt

} || {
	echo $(date) ': Bowtie2-build on genome sequence returned an error. See log files.' >> $my_log_file
	exit_code=1
	echo $exit_code
	exit
}
echo $(date) ': Bowtie2-build finished.' >> $my_log_file


##################################################################################################################################################################################
#																																												 #
#																																												 #
#																	F2 FQ PROCESSING 																							 #
#																																												 #
#																																												 #
##################################################################################################################################################################################

if [ $my_sample_mode == se ] 
then
	#Execute bowtie2 unpaired to align raw F2 reads to genome 
	{
		$location/bowtie2/bowtie2 --very-sensitive --mp 3,2 -x $f1/$my_ix -U $my_rd -S $f1/alignment1.sam 2> $f2/bowtie2_std2.txt

	} || {
		echo $(date) ': Bowtie2 returned an error during the aligment of F2 reads. See log files.' >> $my_log_file
		exit_code=1
		echo $exit_code
		exit
	}
	echo $(date) ': Bowtie2 finished the alignment of F2 reads to genome.' >> $my_log_file
fi


if [ $my_sample_mode == pe ] 
then
	#Execute bowtie2 paired to align raw F2 reads to genome 
	{
		$location/bowtie2/bowtie2 --very-sensitive -X 1000 --mp 3,2 -x $f1/$my_ix -1 $my_rf -2 $my_rr -S $f1/alignment1.sam 2> $f2/bowtie2_std2.txt

	} || {
		echo $(date) ': Bowtie2 returned an error during the aligment of F2 reads. See log files.' >> $my_log_file
		exit_code=1
		echo $exit_code
		exit
	}
	echo $(date) ': Bowtie2 finished the alignment of F2 reads to genome.' >> $my_log_file
fi

#SAM to BAM
{
	$location/samtools1/samtools sort $f1/alignment1.sam > $f1/alignment1.bam 2> $f2/sam-to-bam_std2.txt

} || {
	echo 'Error transforming SAM to BAM.' >> $my_log_file
	exit_code=1
	echo $exit_code
	exit
}
echo $(date) ': SAM to BAM finished.' >> $my_log_file


#Variant calling
{

	$location/samtools1/samtools mpileup  -B -t DP,ADF,ADR -uf $f1/$my_gs $f1/alignment1.bam 2> $f2/mpileup_std.txt | $location/bcftools-1.3.1/bcftools call -mv -Ov > $f1/raw_variants.vcf 2> $f2/call_std.txt

} || {
	echo $(date) ': Error during variant-calling of F2 data.' >> $my_log_file
	exit_code=1
	echo $exit_code
	exit
}
echo $(date) ': F2 data variant calling finished.' >> $my_log_file


#Groom vcf
{
	python $location/scripts_snp/groomer/vcf-groomer.py -a $f1/raw_variants.vcf -b $f1/F2_raw.va 

} || {
	echo $(date) ': Error during execution of vcf-groomer.py with F2 data.' >> $my_log_file
	exit_code=1
	echo $exit_code
	exit
}
echo $(date) ': VCF grooming of F2 data finished.' >> $my_log_file


#Execute vcf filter
{
	python $location/scripts_snp/filter/variants-filter.py -a $f1/F2_raw.va -b $f1/F2_filtered.va -step 1

} || {
	echo 'Error during execution of variants-filter.py with F2 data.' >> $my_log_file
	exit_code=1
	echo $exit_code
	exit
}
echo $(date) ': First VCF filtering step of F2 data finished.' >> $my_log_file


##################################################################################################################################################################################
#																																												 #
#																																												 #
#																	control FQ PROCESSING																						 #
#																																												 #
#																																												 #
##################################################################################################################################################################################

if [ $my_control_mode == se ] 
then
	#Execute bowtie2 unpaired to align raw F2 reads to genome 
	{
		$location/bowtie2/bowtie2 --very-sensitive --mp 3,2 -x $f1/$my_ix -U $my_p_rd -S $f1/alignment1P.sam 2> $f2/bowtie2_std2.txt

	} || {
		echo $(date) ': Bowtie2 returned an error during the aligment of control reads. See log files.' >> $my_log_file
		exit_code=1
		echo $exit_code
		exit
	}
	echo $(date) ': Bowtie2 finished the alignment of control reads to genome.' >> $my_log_file
fi


if [ $my_control_mode == pe ] 
then
	#Execute bowtie2 paired to align raw F2 reads to genome 
	{
		$location/bowtie2/bowtie2 --very-sensitive -X 1000 --mp 3,2 -x $f1/$my_ix -1 $my_p_rf -2 $my_p_rr -S $f1/alignment1P.sam 2> $f2/bowtie2_std2.txt

	} || {
		echo $(date) ': Bowtie2 returned an error during the aligment of control reads. See log files.' >> $my_log_file
		exit_code=1
		echo $exit_code
		exit
	}
	echo $(date) ': Bowtie2 finished the alignment of control reads to genome.' >> $my_log_file
fi

#SAM to BAM
{
	$location/samtools1/samtools sort $f1/alignment1P.sam > $f1/alignment1P.bam 2> $f2/sam-to-bam_std2.txt

} || {
	echo $(date) ': Error transforming SAM to BAM' >> $my_log_file
	exit_code=1
	echo $exit_code
	exit
}
echo $(date) ': SAM to BAM finished' >> $my_log_file


#Variant calling
{

	$location/samtools1/samtools mpileup  -B -t DP,ADF,ADR -uf $f1/$my_gs $f1/alignment1P.bam 2> $f2/mpileup_std.txt | $location/bcftools-1.3.1/bcftools call -mv -Ov > $f1/raw_p_variants.vcf 2> $f2/call_std.txt

} || {
	echo $(date) ': Error during variant-calling of control data' >> $my_log_file
	exit_code=1
	echo $exit_code
	exit
}
echo $(date) ': Control data variant calling finished' >> $my_log_file


#Groom vcf
{
	python $location/scripts_snp/groomer/vcf-groomer.py -a $f1/raw_p_variants.vcf -b $f1/control_raw.va 

} || {
	echo $(date) ': Error during execution of vcf-groomer.py with control data.' >> $my_log_file
	exit_code=1
	echo $exit_code
	exit
}
echo $(date) ': VCF grooming of control data finished.' >> $my_log_file


#Execute vcf filter
{
	python $location/scripts_snp/filter/variants-filter.py -a $f1/control_raw.va -b $f1/control_filtered.va -step 1

} || {
	echo $(date) ': Error during execution of variants-filter.py with control data.' >> $my_log_file
	exit_code=1
	echo $exit_code
	exit
}
echo $(date) ': First VCF filtering step of control data finished.' >> $my_log_file



##################################################################################################################################################################################
#																																												 #
#																																												 #
#																			DATA ANALYSIS 																						 #
#																																												 #
#																																												 #
##################################################################################################################################################################################

#_____________________________________________________________________________OPERATIONS__________________________________________________________________________________________
#Setting up operation mode: 

if [ $snp_analysis_type == par ]
then

	#Mutation in refference backgroud, outcross with non-refference background, sequencing refference parental
	if [ $my_mutbackgroud == ref ] && [ $my_pseq == mut ] && [ $my_cross == oc ]
	then
		my_operation_mode=A
	fi

	#Mutation in refference backgroud, outcross with non-refference background, sequencing non-refference parental
	if [ $my_mutbackgroud == ref ] && [ $my_pseq == nomut ] && [ $my_cross == oc ]
	then
		my_operation_mode=I
	fi

	#Mutation in refference backgroud, backcross with non-refference background, sequencing refference parental
	if [ $my_mutbackgroud == ref ] && [ $my_pseq == mut ] && [ $my_cross == bc ]
	then
		my_operation_mode=A
	fi

	#Mutant in non-reference background, outcross with reference, sequencing non-refference parental
	if [ $my_mutbackgroud == noref ] && [ $my_pseq == mut ] && [ $my_cross == oc ]
	then
		my_operation_mode=I
	fi

	#Execute vcf operations
	{
		python $location/scripts_snp/operations/variants-operations.py -a $f1/F2_filtered.va -b $f1/control_filtered.va -c $f1/F2_control_comparison.va -mode $my_operation_mode -primary 1  

	} || {
		echo $(date) ': Error during first execution of variants-operations.py .' >> $my_log_file
		exit_code=1
		echo $exit_code
		exit
	}
	echo $(date) ': VCF operations finished.' >> $my_log_file
fi

if [ $snp_analysis_type == f2wt ]
then
	{
		python $location/scripts_snp/af_comparison/af-comparison.py -f2_mut $f1/F2_filtered.va -f2_wt $f1/control_filtered.va -out $f1/F2_control_comparison.va -f_input $f1/$my_gs

	} || {
		echo $(date) ': Error during execution of af_comparison.py .' >> $my_log_file
		exit_code=1
		echo $exit_code
		exit
	}
	echo $(date) ': Allelic frequence comparison finished.' >> $my_log_file
fi

#_________________________________________________________________________________ANALYSIS_____________________________________________________________________________________________

#Setting up analysis mode:

#Mutation in refference backgroud, outcross with non-refference background, sequencing refference parental
if [ $my_cross == oc ] 
then
	my_analysis_mode=out
fi

#Mutation in refference backgroud, outcross with non-refference background, sequencing non-refference parental
if [ $my_cross == bc ] 
then
	my_analysis_mode=back
fi

#Execute vcf analysis 
{
	python $location/scripts_snp/analysis/map-mutation.py -fichero $f1/F2_control_comparison.va -fasta $f1/$my_gs -mode $my_analysis_mode -window_size 250000 -window_space 250000 -output $f1/map_info.txt -control_modality $my_mutbackgroud -interval_width 4000000 -snp_analysis_type $snp_analysis_type  


} || {
	echo $(date) ': Error during execution of map-mutation.py .' >> $my_log_file
	exit_code=1
	echo $exit_code
	exit
}
echo $(date) ': Mutation mapping module finished.' >> $my_log_file

#__________________________________________________________________________________FILTER____________________________________________________________________________________________


#Execute vcf filter, selecting snps in the candidate region defined by map-mutation.py, with an alelic frequency > 0.8 and corresponding to EMS mutations
{
	python $location/scripts_snp/filter/variants-filter.py -a $f1/F2_filtered.va -b $f1/F2_filtered2.va -step 2 -cand_reg_file $f1/map_info.txt -af_min 0.8 -mut_type EMS

} || {
	echo $(date) ': Error during the second execution of variants-filter.py .' >> $my_log_file
	exit_code=1
	echo $exit_code
	exit
}
echo $(date) ': Second VCF filtering step finished.' >> $my_log_file



#__________________________________________________________________________________OPERATIONS________________________________________________________________________________________


#Setting up operation mode: 
if [ $snp_analysis_type == par ]
then

	#Mutation in refference backgroud, outcross with non-refference background, sequencing refference parental
	if [ $my_mutbackgroud == ref ] && [ $my_pseq == mut ] && [ $my_cross == oc ]
	then
		my_operation_mode=A
	fi

	#Mutation in refference backgroud, outcross with non-refference background, sequencing non-refference parental
	if [ $my_mutbackgroud == ref ] && [ $my_pseq == nomut ] && [ $my_cross == oc ]
	then
		my_operation_mode=A
	fi

	#Mutation in refference backgroud, backcross with non-refference background, sequencing refference parental
	if [ $my_mutbackgroud == ref ] && [ $my_pseq == mut ] && [ $my_cross == bc ]
	then
		my_operation_mode=A
	fi

	#Mutant in non-reference background, outcross with reference, sequencing non-refference parental
	if [ $my_mutbackgroud == noref ] && [ $my_pseq == mut ] && [ $my_cross == oc ]
	then
		my_operation_mode=A
	fi

	#Execute vcf operations
	{
		python $location/scripts_snp/operations/variants-operations.py -a $f1/F2_filtered2.va -b $f1/control_filtered.va -c $f1/final_variants.txt -mode $my_operation_mode -primary 1  

	} || {
		echo $(date) ': Error during second execution of operations.py .' >> $my_log_file
		exit_code=1
		echo $exit_code
		exit
	}
	echo $(date) ': VCF operations finished.' >> $my_log_file

fi

if [ $snp_analysis_type == f2wt ]
then 
	my_operation_mode=N

	#Execute vcf operations
	{
		python $location/scripts_snp/operations/variants-operations.py -a $f1/F2_filtered2.va -b $f1/control_filtered.va -c $f1/final_variants.txt -mode $my_operation_mode -primary 1  

	} || {
		echo $(date) ': Error during execution of operations.py .' >> $my_log_file
		exit_code=1
		echo $exit_code
		exit
	}
	echo $(date) ': VCF operations finished.' >> $my_log_file
fi

#__________________________________________________________________________________VARANALYZER INPUT_________________________________________________________________________________


#snp-to-varanalyzer.py
{
	python $location/scripts_snp/snp_to_varanalyzer/snp-to-varanalyzer.py -a $f1/final_variants.txt -b $f1/final_variants2.txt	
	
} || {
	echo $(date) ': Error during execution of snp-to-varanalyzer.py .' >> $my_log_file
	exit_code=1
	echo $exit_code
	exit
}
echo $(date) ': Input for varanalyzer finished.' >> $my_log_file



#__________________________________________________________________________________VARANALYZER_______________________________________________________________________________________


#varanalyzer
{
	python $location/varanalyzer/varanalyzer.py -itp snp -con $f1/$my_gs -gff $f0/$my_gff -var $f1/final_variants2.txt -rrl $my_rrl -pname $project_name

} || {
	echo $(date) ': Error during execution of varanalyzer.py .' >> $my_log_file
	exit_code=1
	echo $exit_code
	exit
}
echo $(date) ': Varanalyzer finished.' >> $my_log_file



#_______________________________________________________________________________PRIMER GENERATION_______________________________________________________________________________


#Primer generation script
{
	$location/primers/primer-generation.py -file $location/variants.txt -fasta $location/genome.fa    
}|| {
	echo $(date) ': Error Primer-generation.py module failed. See details above in log. '>> $my_log_file
}
echo $(date) ': Primer-generation.py module finished.' >> $my_log_file












##################################################################################################################################################################################
#																																												 #
#																																												 #
#																				REPORT 	 																						 #
#																																												 #
#																																												 #
##################################################################################################################################################################################


# FILTER TO SELECT SNPS TO DRAW: (para el backcross es especialmente relevante quitar la "basura" a la hora de dibujar los SNPs)
if [ $my_cross == oc ]
then
	af_min=0.1
fi

if [ $my_cross == bc ]
then
	af_min=0.25
fi

{
	python $location/scripts_snp/filter/variants-filter.py -a $f1/F2_control_comparison.va -b $f1/F2_control_comparison2.va -step 1 -af_min $af_min

} || {
	echo $(date) ': Error during third execution of variants-filter.py . ' >> $my_log_file
	exit_code=1
	echo $exit_code
	exit
}
echo $(date) ': THird VCF filtering step finished.' >> $my_log_file


#__________________________________________________________________________________GRAPHIC OUTPUT_____________________________________________________________________________________



#COMANDO PRUEBAS GRAPHIC OUTPUT :
#	python ./graphic_output/graphic-output.py -my_mut snp -asnp ./user_projects/project/1_intermediate_files/F2_control_comparison.va -bsnp ./user_projects/project/1_intermediate_files/gnm_ref_merged/genome.fa -rrl 100 -iva ./user_projects/project/1_intermediate_files/variants.txt -gff ./user_data/chr1+4.gff -pname user_projects/project  -cross bc

#Graphic output
{
	python $location/graphic_output/graphic-output.py -my_mut $my_mut -asnp $f1/F2_control_comparison2.va -bsnp $f1/$my_gs -rrl $my_rrl -iva $2/3_workflow_output/variants.txt -gff $f0/$my_gff -pname $2  -cross $my_cross -snp_analysis_type $snp_analysis_type  
	
} || {
	echo $(date) ': Error during execution of graphic-output.py .' >> $my_log_file
	exit_code=1
	echo $exit_code
	exit
}
echo $(date) ': Graphic output created.' >> $my_log_file

echo $exit_code >> $my_log_file

echo $exit_code


#HTML file

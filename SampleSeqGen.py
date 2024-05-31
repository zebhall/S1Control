import csv
from tkinter import filedialog
import os

# ZH 2024/04/10
# inserts

# assumes sample list is given as csv file with one sample name/id per line only


def main():
	"""Generates a partial sample sequence CSV file for use with S1Control & GeRDA system.
	automates process of manually inserting CRM and Silica Blank breaks."""
	path_to_sample_list_csv = filedialog.askopenfilename(
		title="Select Sample Names CSV file",
		filetypes=[("CSV File", "*.csv")],
		initialdir=os.getcwd(),
	)
	number_samples_between_crms = int(input("Number of samples between CRMs: "))
	number_of_crms = int(input("Number of CRMs to run each time: "))
	crms = []
	for i in range(1, number_of_crms + 1):
		crms.append(input(f"Enter Name of CRM {i}: "))
	crm_suffix_starting_num = int(
		input(
			"CRM suffix starting number (e.g. '4' = first crms will be named SiO2_004, etc. **if unsure, set to 1**): "
		)
	)
	with open(path_to_sample_list_csv, "r") as sample_list_csv:
		reader = csv.reader(sample_list_csv)
		row_num = 0
		new_sample_seq = []
		for row in reader:
			if row_num % number_samples_between_crms == 0:
				for crm in crms:
					new_sample_seq.append(
						[f"{crm}_{str(crm_suffix_starting_num).zfill(4)}"]
					)
				crm_suffix_starting_num += 1
			new_sample_seq.append(row)
			row_num += 1
		# then one final crm run at end
		for crm in crms:
			new_sample_seq.append([f"{crm}_{str(crm_suffix_starting_num).zfill(4)}"])

	outputname = "sample_seq.csv"
	with open(outputname, mode="x", newline="") as sample_seq_csv:
		writer = csv.writer(sample_seq_csv)
		writer.writerows(new_sample_seq)

	print(f"sample sequence csv saved as '{outputname}'...")
	input()


if __name__ == "__main__":
	main()

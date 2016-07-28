import numpy as np
import pandas as pd
import os

import json
import argparse
import sys

def open_to_blocks(filename):
	with open(filename, 'r') as f:
		blocks = []
		while True:
			this_block = f.readline()
			if len(this_block) > 0:
				blocks.append(json.loads(this_block))
			else:
				break
	return blocks

def make_dataframe(blocks):
	out_dataframe = pd.DataFrame.from_records(blocks)
	
	return out_dataframe

def make_csv(out_dataframe, file):
	csv_file_pre = file.strip(".json")
	csv_file = csv_file_pre.strip('behavioral')
	
	if not os.path.exists('data/'):
		os.makedirs('data')
	
	pd.DataFrame.to_csv(out_dataframe, path_or_buf = "data" + csv_file + ".csv")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Take .json files and covert to .csv")
	parser.add_argument(nargs='+', dest='files',
						help="Files to process"
						)

	args = parser.parse_args()
	
	for file in args.files:
		blocks = open_to_blocks(file)
		out_df = make_dataframe(blocks)
		make_csv(out_df, file)
	
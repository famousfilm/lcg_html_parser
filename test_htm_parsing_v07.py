import os
import datetime
import time
import sys
from sys import argv
from HTMLParser import HTMLParser
# HTMLParser is an OLD, OLD style class. It might be deprecated. It 
# would be ideal not to use it going forward. For classes, it does not
# support the 'super' method, which is a no-no in the event that the 
# sublclass would use multiple classes : 
# for example, class ParseData(HTMLParser, OtherClass):

script, folder_location = argv

class ParseData(HTMLParser):
	
	def __init__(self, *args, **kwargs):
		HTMLParser.__init__(self, *args, **kwargs)
		# This is an old-style class, and this diction is BAD. Usually,
		# you would use 'super' here, but we can't b/c the class is old.
		self.data_listed = []
	
	def handle_data(self, data):
		self.data_listed.append(data.strip())
		
	def format_data(self):
		# formats the captured html data -- removing & replacing
		# unwanted characters -- and returns a list of all the data
		
		d = {}
		# build a dictionary for replacing (i.e. '_1' with '-1')
		data = []
		for n in range(0, 10):
			d['_' + str(n)] = '-' + str(n)
		for i in self.data_listed:
			x = i.strip(')').replace('(', '_').replace(' ', '_').replace('/', '_').replace(':', '_RESULT')
			for orig, repl in d.items():
				if orig in x:
					x = (x.replace(orig, repl))
			data.append(x)
		return data
		
	def collate_data(self):
		# puts all of the formatted html data into a dictionary
		# returns the dictionary.
		
		relevant_data_dict = {
			'TRADING' : {'DAY' : '', 'MTD' : '', 'YTD' : ''},
			'INTEREST' : {'DAY' : '', 'MTD' : '', 'YTD' : ''},
			'REBATE_INTEREST' : {'DAY' : '', 'MTD' : '', 'YTD' : ''},
			'OTHER_TRADING_COSTS' : {'DAY' : '', 'MTD' : '', 'YTD' : ''},
			'BROKER' : {'DAY' : '', 'MTD' : '', 'YTD' : ''},
			'OMNI_SSR_SL' : {'DAY' : '', 'MTD' : '', 'YTD' : ''},
			'COUPON' : {'DAY' : '', 'MTD' : '', 'YTD' : ''},
			'OMNI_COC' : {'DAY' : '', 'MTD' : '', 'YTD' : ''},
			'TOTAL_RESULT' : {'DAY' : '', 'MTD' : '', 'YTD' : ''},
			'MKT_VALUE_L' : '',
			'MKT_VALUE_S' : '',
			'CASH_BALANCE' : '',
		}

		relevant_data_search_items = ['DAY', 'MTD', 'YTD']
		# this exists because not all of the keys in relevant_data_dict
		# require a DAY, MTD, and YTD element. 
		
		data_listed_formatted = self.format_data()
		
		for key in relevant_data_dict:
			index_at_key = data_listed_formatted.index(key) 
			# this finds the index point (an integer) where the key 
			# value appears in the master list
			holding_list = data_listed_formatted[index_at_key:
				index_at_key + 
				data_listed_formatted[index_at_key:].index('')]
			# makes a holding list of the first "chunk" of data to see 
			# if 'DAY' appears in it at all
			l = []
			if relevant_data_search_items[0] in holding_list:
				for item in relevant_data_search_items:
					index_at_search_term = data_listed_formatted.index(key) + data_listed_formatted[index_at_key:].index(item) 
					index_end = index_at_search_term + data_listed_formatted[index_at_search_term:].index('')
					l = data_listed_formatted[index_at_search_term:index_end]
					if len(l) > 2:
						del l[l.index(item) + 1 : -1]
					else:
						l = [item, '']
					relevant_data_dict[key][item] = l[-1]
			else:
				if len(holding_list) < 2:
					relevant_data_dict[key] = 'NA'
				else:
					relevant_data_dict[key] = holding_list[-1]
				# this will get the data for the last three elements in the
				# dictionary, which do not have the search terms but are 
				# still data that is needed.
		return relevant_data_dict
				
	def get_the_date(self):
		# combs the list of formatted html data for the date and
		# returns it as a string in YYYYMMDD format.
		
		month_list = {
			'jan' : '01',
			'feb' : '02',
			'mar' : '03',
			'apr' : '04',
			'may' : '05',
			'jun' : '06',
			'jul' : '07',
			'aug' : '08',
			'sep' : '09', 
			'oct' : '10', 
			'nov' : '11', 
			'dec' : '12',
		}
			
		date_a = ''
		for key in month_list:
			for n in self.format_data():
				if key + '-' in n.lower():
					date_a = n
		date_elements = date_a.replace(',', '').lower().split('-')
		
		for key, value in month_list.items():
			if key in date_elements:
				date_elements[date_elements.index(key)] = value
				
		date_b = date_elements[2] + date_elements[0] + date_elements[1]
		
		return date_b

	def data_out_final(self):
		# takes the dictionary of data and the date and returns a list
		# of the data in KEY.VALUE[DATE]=AMOUNT format.
		
		date = self.get_the_date()
		data_dict = self.collate_data()
		final_list = []
		
		for key, value in data_dict.items():
			if type(value) is dict:
				for time, amount in value.items():
					if amount == '':
						pass
						# we might use this "blank" data, might not.
					else:
						final_list.append(key + '.' + time + '[' + date + ']=' + amount.replace(',',''))
			else:
				# the value is not a dict, so it is a string - one of
				# the items without DAY, MTD, and YTD. 
				final_list.append(key + '.DAY[' + date + ']=' + value.replace(',',''))
		
		return final_list


class Folders(object):
	
	def __init__(self, folder):
		self.folder = folder
	
	def verify_folder_location(self):
		# makes sure the given folder exists. if it doesn't exits and
		# tells user the folder DNE.
		
		folder_check = self.folder
		
		if os.name == 'posix':
			if folder_check[-1] != '/':
				folder_check = folder_check + '/'
		elif os.name == 'nt':
			if folder_check[-1] != '\\':
				folder_check = folder_check + '\\'
		if os.path.exists(folder_check) == False:
			print "The folder you provided does not exist"
			exit(1)
		else:
			return folder_check
		
	def build_list_of_files(self):
		# returns a list of all of the '.htm' files in the directory.
		
		main_folder = self.verify_folder_location()
		contents_of_folder = os.listdir(main_folder)
		list_of_files = []
		
		for somefile in contents_of_folder:
			if '.htm' in somefile:
				list_of_files.append(somefile)
		
		list_of_files.sort()
		return list_of_files
	
	
def open_parse_append_close(folder):
	# creates a text file named "2008_data_[timestamp].txt", checks for
	# .htm files with duplicate dates and ignores the .htm file if it is
	# a duplicate or writes all of the acquired data if the data is new.
	
	timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
	folder_inst = Folders(folder)
	containing_folder = folder_inst.verify_folder_location()
	files_to_parse = folder_inst.build_list_of_files()
	
	createfile = open(containing_folder + '2008_data_' + timestamp + '.txt', 'w')
	createfile.close()
	# creating the file is necessary in order to open it with 'read'
	# permissions and check for duplicate data.
	
	for afile in files_to_parse:
		thehtmlfile = open(containing_folder + afile)
		parser = ParseData()
		parser.feed(thehtmlfile.read())
		parsed_data = parser.data_out_final()
		dup_date_check = '[' + parser.get_the_date() + ']'
		dup_found = False
		
		with open(containing_folder + '2008_data_' + timestamp + '.txt', 'r') as f:
			for line in f:
				if dup_date_check in line:
					dup_found = True 
		
		if dup_found == False:
			finaloutput = open(containing_folder + '2008_data_' + timestamp + '.txt', 'a')
			for line in parsed_data:
				item = line.encode('ascii')
				finaloutput.write(item)
				finaloutput.write('\n')
			finaloutput.close()
		parser.close()
		thehtmlfile.close()

open_parse_append_close(folder_location)

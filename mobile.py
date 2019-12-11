import regex, sys, csv, functools,operator,time
from helper import *

#########################
#    NONE DECORATOR EXCEPTION
#########################
def catch_exception(func):
	def func_wrapper(self,*args,**kwargs):
		try:
			#actually run function
			data = func(self,*args,**kwargs)
		except:
			data = None
		return data
	return func_wrapper

#########################
#    RULES
#########################
rules_d = {'0244230000':'Shandi Grenville (or another person who attended the phones at the Beechwood offices)',
'0242245500':'Shandi Grenville (or another person who attended the phones at the Beechwood offices)',
'0404821015':'Trevor Moffatt (Beechwood)',
'0242960139':'"Matt Slee (Building & Design Team - South Coast:\' Beechwood)"',
'0412605594':'Anthony Higgins (Southern Trenching)',
'0404821914':'Wayne Braid (Beechwood)',
'0296160999':'someone at the Beechwood Sydney Business Centre (Head Office)',
'0244221233':'someone at Leslie & Thompson Pty Ltd',
'0402350828':'"Thomas Smith (Building & Design Team:\' Beechwood)"',
'0244240012':'someone at the Twin Waters estate (Beechwood)',
'0414975583':'"Geoff Slee (Building & Design Team - South Coast, Beechwood)"'}
rules_d_k = list(rules_d.keys())


#########################
#    REGEX VARIABLES
#    //ANCHOR: Variables
#########################
format_regex = ''
time_regex = '\d{1,2}:\d{1,2}:\d{1,2}'
date_regex = '\d{4}\-\d{1,2}\-\d{1,2}'
space_new_regex = '[\s|\n]*'
any_regex = '.*?'
date_time_regex = date_regex + space_new_regex + time_regex
time_date_regex = time_regex + space_new_regex + date_regex
overall_date_regex = '(' + time_date_regex + '|' + date_time_regex + ')'
look_start_regex = '(?<=^|\s)'
look_end_regex = '(?=\s|$)'
series_of_words_regex = look_start_regex + '\d*\s*[A-Za-z]*[A-Za-z|\-|\s]*' + look_end_regex
disk_space_regex = look_start_regex + '\d{1,2}\.\d{1,2}MB|GB' + look_end_regex
currency_regex = look_start_regex + '\$\d*\.\d*' + look_end_regex
duration_regex = look_start_regex + '\d{1,2}:\d{1,2}' #00:22 + look_end_regex
phone_number_regex = look_start_regex + '[0-9]+' + look_end_regex
integer_regex = look_start_regex + '[0-9]+' + look_end_regex
input_base_path = 'C:/makeshift/files/australia_mobile/data/'
csv_base_path = 'C:/makeshift/files/australia_mobile/csv/'
csv_all_file_name = 'phone_all.csv'
csv_filtered_file_name = 'phone_filtered.csv'
csv_rules_file_name = 'rules_total.csv'
csv_all_file_path = csv_base_path + csv_all_file_name
csv_filtered_file_path = csv_base_path + csv_filtered_file_name
csv_rules_file_path = csv_base_path + csv_filtered_file_name
input_files = ['logs_mobile.txt','logs_2016.txt','logs_2017.txt']
input_files = ['logs_mobile_2.txt','logs_2016.txt','logs_2017.txt']
nodes = []
row = []
schema = ''
usage_type = ''
called_number = None
schema_allowed = ['mobile','phone','sms_national','data']
# input_files = ['logs_2017.txt']
#DO SHIT FOR RULES_COUNT_CSV!!! 
rules_count_d = {}
for phone_number, name in rules_d.items():
	rules_count_d[str(phone_number)] = {}
	rules_count_d[phone_number]['name'] = name
	for input_file in input_files:
		rules_count_d[phone_number][input_file] = 0

#note
#
#TWO TYPES OF ROWS
#
#1) data = ['Data', '0.02MB', '0.02MB', '$0.00000', '$0.00000', '$0.00000']
#
#
#2) calls =  ['Mobile', 'Call', '09:46', '0418695084', '0.00MB', '$9.35000', '$0.00000', '$0.00000']
#
#//ANCHOR: REGEX ROWS
data_regex_row = '(%s)%s(%s)%s(%s)%s(%s)%s(%s)%s(%s)' % (series_of_words_regex , space_new_regex , disk_space_regex , space_new_regex , disk_space_regex , space_new_regex , currency_regex , space_new_regex , currency_regex , space_new_regex , currency_regex)
calls_mobile_regex_row = '(%s)%s(%s)%s(%s)%s(%s)%s(%s)%s(%s)%s(%s)' % (series_of_words_regex , space_new_regex, duration_regex , space_new_regex , phone_number_regex , space_new_regex , disk_space_regex , space_new_regex , currency_regex , space_new_regex , currency_regex , space_new_regex , currency_regex)
sms_national_regex_row = '(%s)%s(%s)%s(%s)%s(%s)%s(%s)%s(%s)%s(%s)' % (series_of_words_regex , space_new_regex, integer_regex , space_new_regex , phone_number_regex , space_new_regex , disk_space_regex , space_new_regex , currency_regex , space_new_regex , currency_regex , space_new_regex , currency_regex)
calls_phone_regex_row = '(%s)%s(%s)%s(%s)%s(%s)%s(%s)' % (series_of_words_regex , space_new_regex, duration_regex , space_new_regex , phone_number_regex , space_new_regex , currency_regex , space_new_regex , duration_regex)


#########################
#    GET NODES!!! the nodes is a list of dictionaries, and the dictionaries have values of date_time & data
#########################
for input_file in input_files:
	input_file_path = input_base_path + input_file
	with open(input_file_path,'r') as f:
		lines = f.readlines()
		for index,line in enumerate(lines):
			#IF IT STARTS WITH DATE & TIME
			if regex.match("^" + any_regex + date_time_regex,line):
				date_time = regex.findall(date_regex,line)[0] + " " + regex.findall(time_regex,line)[0]
				data = regex.findall(date_time_regex + "(.*)" + look_end_regex,line)[0]
				nodes.append({'date_time':date_time,'data':data,'file':input_file})
				# pass
			#handles the very weird situation of DATE + DATA + TIME
			if regex.match("^" + time_regex + "$",line.strip()):
				#get date
				date = lines[index-2].strip()
				if(regex.match(date_regex,date) is None):
					for i in range(-1,-10,-1):
						try:
							date = regex.findall(date_regex,nodes[i]['date_time'])[0]
						except:
							continue
				date_time = str(date) + " " + line.strip()
				data = lines[index-1]
				nodes.append({'date_time':date_time,'data':data,'file':input_file})

#########################
#    CLIENT
#########################
#Inside File
csv_all_handle = open(csv_all_file_path,'w')
csv_filtered_handle = open(csv_filtered_file_path,'w')
csv_rules_handle = open(csv_rules_file_path,'w')
for node in nodes:
	#if the row is not neat, it will reflect in the default if statement below
	ignore_row = False
	date_time = node['date_time']
	messy_line = node['data']
	try:
		#VARIABLES THAT WILL BE IN THE ROW
		try:
			time_tuple = time.strptime(date_time,"%Y-%m-%d %H:%M:%S")
			date_row_value = time.strftime('%d/%m/%Y %H:%M:%S', time_tuple)
			description_date_value = time.strftime('%H:%M', time_tuple)
		except:
			#if reaching here, the row will likely not even show up
			overall_date = None
			date_row_value = None
			description_date_value = None
		#Note: string is already stripped in regex_groups function as it calls the strip_iterate function
		#CALL SCHEMA (MOBILE)!!! (follows call structure define above)!!!
		#['Call', 'to', 'non-Optus', 'GSM', '01:35', '0412977644', '0.00MB', '$2.15000', '$0.00000', '$0.00000']
		if regex_groups(calls_mobile_regex_row,messy_line) is not None:
			schema = 'mobile'
			rgo = regex_groups(calls_mobile_regex_row,messy_line)
			usage_type = l(rgo,0)
			duration = l(rgo,1)
			called_number = l(rgo,2).strip()
			# debug
			# print("CALL",row)
			# pass
		#DATA SCHEMA (follows data structure define above)!!!
		#['Data', '5.85MB', '5.85MB', '$0.00000', '$0.00000', '$0.00000']
		elif regex_groups(data_regex_row,messy_line) is not None:
			#according to Sarah, ignore all data
			ignore_row = True
			# debug
			# print("DATA",row)
			# pass
		#SMS NATIONAL TYPE OF DATA SCHEMA
		#['SMS', 'National', '1', '0406665748', '0.00MB', '$0.00000', '$0.00000', '$0.00000']
		elif regex_groups(sms_national_regex_row,messy_line) is not None:
			schema = 'sms_national'
			rgo = regex_groups(sms_national_regex_row,messy_line)
			usage_type = l(rgo,0)
			duration = l(rgo,1)
			called_number = l(rgo,2).strip()
			# print("SMS",row)
			# pass
		#CALL PHONE!!
		elif regex_groups(calls_phone_regex_row,messy_line) is not None:
			schema = 'phone'
			rgo = regex_groups(calls_phone_regex_row,messy_line)
			usage_type = l(rgo,0)
			duration = l(rgo,1)
			called_number = l(rgo,2).strip()
			# print("PHONE", row) 
			pass
		#Fits No Criteria
		else:	
			ignore_row = True
			pass
		#is_sms? 
		is_sms = 1 if 'sms' in usage_type.lower() else 0
		#what is person's name in the rule sheet
		person_name = dvkp(rules_d,called_number[1:])
		describe_event = 'At %s I called %s and spoke with %s on the telephone.' % (description_date_value, called_number, person_name)
		input_file = node['file']
	except KeyError:
		print("KeyError in " + str(index))
		pass
	except IndexError:
		print("IndexError in " + str(index))
		pass
	except ValueError:
		print("ValueError in " + str(index))
		pass
	except TypeError:
		print("TypeError in " + str(index))
		pass

	#########################
	#    WRITE CSV ROW HERE
	#########################
	if(ignore_row == False and date_row_value is not None):
		row = [date_row_value,duration,is_sms,called_number,input_file]
		# print(row)
		csv_all_handle.write(str(','.join(list(map(str,row)))))
		csv_all_handle.write('\n')
		csv_all_handle.flush()
	#FILTERED SHEET
	#ignore row here means don't print data
	#person_name filter means only show values inside the rules section
	#date_row_value means don't show funny looking rows
	if(ignore_row == False and date_row_value is not None and person_name is not None):
		row = [date_row_value,duration,is_sms,describe_event,input_file]
		print(row)
		#record tallies for the next rules csv sheet
		rules_count_d[called_number][input_file] += 1
		# print(rules_count_d)
		csv_filtered_handle.write(str(','.join(list(map(str,row)))))
		csv_filtered_handle.write('\n')
		csv_filtered_handle.flush()

#########################
#    WORK ON RULES CSV FILE
#########################
# for phone_number,node in rules_count_d.items():
# 	row = [node[input_file] for input_file in input_files]
# 	total_sum = sum(row)
# 	row.insert(0,node['name'])
# 	row.insert(1,phone_number)
# 	row.append(total_sum)
# 	csv_rules_handle.write(str(','.join(list(map(str,row)))))
# 	csv_rules_handle.write('\n')
# 	csv_rules_handle.flush()
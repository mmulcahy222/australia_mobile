import regex

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
#    FUNCTIONS
#########################
def l(iter, index, default=None):
	try:
		return iter[index]
	except:
		return default
def clean_text(text):
	text = text.replace('\n',' ')
	return text
def strip_iterable(iter):
	return list(map(str.strip,iter))
@catch_exception
def regex_groups(pattern,messy_line):
	groups = regex.search(pattern,messy_line).groups()
	groups = strip_iterable(groups)
	return groups
def empty( variable ):
	if not variable:
		return True
	return False
time_regex = '\d{1,2}:\d{1,2}:\d{1,2}'
date_regex = '\d{4}\-\d{1,2}\-\d{1,2}'
space_new_regex = '[\s|\n]*'
date_time_regex = date_regex + space_new_regex + time_regex
time_date_regex = time_regex + space_new_regex + date_regex
#flip around if it's date & time
def time_date(overall_date):
	if regex.match(time_date_regex,overall_date) is not None:
		ms = regex.findall("(" + time_regex + "|" + date_regex + ")",overall_date)
		return l(ms,1) + ' ' + l(ms,0)
	return overall_date
#get key value by part
def dvkp(dict, key_part, default=None):
	try:
		return [value for key,value in dict.items() if key_part in key][0]
	except:
		return default

import sys
import db
import test_fields
from pyjon.reports import ReportFactory


# generates the report of the given file with given data (data is a dictionary)
class Report:

	output = []
	fields_list = []
	frames = []
	# all units are in points
	PAGE_WIDTH = 595
	PAGE_HEIGHT = 842
	LEFT_MARGIN = 36
	RIGHT_MARGIN = 36
	TOP_MARGIN = 198 # 2.75 in
	BOTTOM_MARGIN = 0
	FRAME_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN # in points (7.5 in inches)
	FRAME_HEIGHT = 0
	CURRENT_Y_AXIS = PAGE_HEIGHT - TOP_MARGIN # MODIFY reset_current_y_axis() AS WELL. This holds the y coordinate for the next frame
	FRAME_ID = 0 # holds the frame id
	SPACE_BETWEEN_TESTS = 20
	LINE_HEIGHT = 24 # for Garamond size 12

	MAIN_FRAME_HEIGHT = LINE_HEIGHT * 5 # number of rows are 4 (Serial no, Name, Sample collected on, Requested by doctor and column headers)

	test_field = None
	tests_dict = None # holds fields list for multiple tests in the same report

	data = {} # holds the dict with test results
	main_data = None # holds patient information

	def reset_current_y_axis(self):
		self.CURRENT_Y_AXIS = self.PAGE_HEIGHT - self.TOP_MARGIN

	# sets dimentions of the main report
	def get_main_dimensions(self):
		self.CURRENT_Y_AXIS -= self.MAIN_FRAME_HEIGHT # number of rows are 4 (Serial no, Name, Sample collected on, Requested by doctor)
	
	# main report (patient information)
	def generate_main(self):
		self.output.append(self.get_main())
		self.get_main_dimensions()
		self.frames.append('''<frame id="main" x1="0.5in" y1="''' + str(self.CURRENT_Y_AXIS)  + '''" width="''' + str(self.FRAME_WIDTH) + '''" height="''' + str(self.MAIN_FRAME_HEIGHT) + '''" showBoundary="1"/>''')
		self.CURRENT_Y_AXIS -= self.SPACE_BETWEEN_TESTS

	def generate_report(self):
		temp_from_definition = self.test_field.get_test_name_and_fields() # fields read from the test definition file (no test result values)
		
		# replace field type with values and prepare fields list
		for t in temp_from_definition[1:]:
			tem = t.split(';')
			tem[1] = str(self.data[db.validate(tem[0])])
			self.fields_list.append(';'.join(tem))

		self.increase_frame_height(24 * len(self.fields_list))

		# go to next page if vertical space left is not sufficient for the frame
		if (self.CURRENT_Y_AXIS - (self.BOTTOM_MARGIN + self.SPACE_BETWEEN_TESTS)) < self.FRAME_HEIGHT: # not sufficient space left
			self.output.append('<nextPage />')
			self.reset_current_y_axis()
			self.get_main_dimensions()
			self.output.append(self.get_main()) # append patient information at the start of the new page
			self.CURRENT_Y_AXIS -= self.SPACE_BETWEEN_TESTS

		# start of keepInFrame
		self.output.append('''<keepInFrame frame="F''' + str(self.FRAME_ID) + '''">''')

		if len(self.fields_list) > 1:
			self.output.append(self.get_title(temp_from_definition[0]))
	
		self.output.append(self.get_fields(self.fields_list))
		
		# end of keepInFrame
		self.output.append('</keepInFrame>')


		self.CURRENT_Y_AXIS = self.CURRENT_Y_AXIS - self.FRAME_HEIGHT
#		self.write_xml()

		# add fields list to tests_dict
		self.tests_dict['data' + str(self.FRAME_ID)] = self.fields_list
		
		# add frame
		self.frames.append('''<frame id="F''' + str(self.FRAME_ID) + '''" x1="0.5in" y1="''' + str(self.CURRENT_Y_AXIS)  + '''" width="''' + str(self.FRAME_WIDTH) + '''" height="''' + str(self.FRAME_HEIGHT) + '''" showBoundary="1"/>''')

		self.FRAME_HEIGHT = 0
		self.CURRENT_Y_AXIS -= self.SPACE_BETWEEN_TESTS

	def increase_frame_height(self, height):
		self.FRAME_HEIGHT += height

	# title of the test (for tests with multiple fields)
	def get_title(self, title):
		self.increase_frame_height(28) # title in 14p
		return '<para style="report_title">' + title + '</para>\n'

	def get_fields(self, fields):
		temp = '''<blockTable style="fields" repeatRows="1" alignment="left" colWidths="234 140.4 46.8 46.8">
	    <tr><td py:for="i in range(4)"></td></tr>
	    <tr py:for="line in data''' + str(self.FRAME_ID) + '''"><td py:for="col in line.split(';')" py:content="col" /></tr>
	  </blockTable>'''

		return temp

	# returns the xml for main report (patient details)
	def get_main(self):
		# patient information and table headers (Result, Unit, Reference Range)
		temp = '''<keepInFrame frame="main">
	<blockTable style="main" repeatRows="1" alignment="left" colWidths="110 300 50 50">
	    <tr><td py:for="i in range(4)"></td></tr>
	    <tr py:for="line in main"><td py:for="col in line.split(';')" py:content="col" /></tr>
	  </blockTable>
	<blockTable style="header" repeatRows="1" alignment="left" colWidths="234 140.4 46.8 46.8">
	<tr>
		<td></td>
		<td>Result</td>
		<td>Unit</td>
		<td>Reference Range</td>
		
	</tr>
	</blockTable>
	</keepInFrame>'''
		return temp 

	# writes the xml output of the report
	def write_xml(self):

		f = open('temp.xml','w')

		# string for frames
		frames_string = ''
		for frame in self.frames:
			frames_string = frames_string + frame

		# header of the xml
		f.write('''<?xml version="1.0" encoding="iso-8859-1" standalone="no" ?>
	<!DOCTYPE document SYSTEM "rml_1_0.dtd">
	<document xmlns:py="http://genshi.edgewall.org/" filename="test.pdf" compression="true">
	<docinit>
		<registerTTFont faceName="Garamond" fileName="font/Garamond.ttf"/>
		<registerTTFont faceName="Garamond-bold" fileName="font/Garamonb.ttf"/>
	</docinit>
	<template pageSize="(''' + str(self.PAGE_WIDTH) + ''',''' + str(self.PAGE_HEIGHT) + ''')" leftMargin="''' + str(self.LEFT_MARGIN)  + '''" rightMargin="''' + str(self.RIGHT_MARGIN)  + '''" showBoundary="0">
	  <pageTemplate id="main">
'''#	    <frame id="first" x1="0.5in" y1="''' + str(self.CURRENT_Y_AXIS)  + '''" width="''' + str(self.FRAME_WIDTH) + '''" height="''' + str(self.FRAME_HEIGHT) + '''" showBoundary="1"/>
+ str(frames_string) +
'''
	  </pageTemplate>
	</template>
	<stylesheet>
		<paraStyle name="report_title" fontName="Garamond-bold" fontSize="14"/>
		<blockTableStyle id="fields">
			<blockFont name="Garamond" size="12" start="0,0" stop="-1,-1"/>
			<blockFont name="Garamond-bold" size="12" start="1,1" stop="1,-1" />
		</blockTableStyle>
		<blockTableStyle id="main">
			<blockFont name="Garamond" size="12" start="0,0" stop="-1,-1"/>
			<blockFont name="Garamond-bold" size="12" start="1,1" stop="1,1" />
		</blockTableStyle>
		<blockTableStyle id="header">
			<blockFont name="Garamond" size="12" start="0,0" stop="-1,-1"/>
		</blockTableStyle>
	</stylesheet>
	<story>''')

		# write title and fields
		temp = ''

		for line in self.output:
			temp += line

		f.write(temp)

		# footer of the xml
		f.write("""</story>
	</document>
	""")

		f.close()
	
		self.write_pdf('temp.xml')

	def write_pdf(self, fi):
		factory = ReportFactory()
		
		# define lists separately for tests
		for i in self.tests_dict.keys():	
			exec '%s=self.tests_dict[i]' % i	

		# build data string
		data_string = ''
		for i in range(1, self.FRAME_ID+1):
			data_string = data_string + ', data' + str(i) + '=data' + str(i)

		exec 'factory.render_template(template_file=fi %s , main=self.main_data)' % (data_string) # output will be like 'factory.render_template(template_file=fi, data1=data1, data2=data2)
		factory.render_document('test.pdf')
		factory.cleanup()

	# sets the data list for main report (patient information)
	def set_main_data_list(self, list_temp):
		self.main_data = list_temp.split('#')
		
	# inputs the test definition file and next data for the next test and the variables are modified accordingly
	def set_test_info(self, test_definition_file, data):
		self.test_field = test_fields.TestField(test_definition_file)
		self.data = data
		self.FRAME_ID += 1
		self.fields_list = []

#	def __init__(self, test_definition_file, data):
		#self.test_field = test_fields.TestField(test_definition_file)
		#self.data = data

	def __init__(self):
		self.output = []
		self.frames = []
		self.tests_dict = {}

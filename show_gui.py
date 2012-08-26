# displays the gui of the specified test

from gi.repository import Gtk
import sys
import db
import test_fields

builder = Gtk.Builder()

class Handler:
	global builder

	def onDeleteWindow(self, *args):
		Gtk.main_quit(*args)
	

	def done(self, button):
		test_definition_file = builder.get_object('test_filename').get_text()
		fields = test_fields.get_gui_field_list(test_definition_file)

		values = {} # to hold the field names and values to be fed into the table
		for field in fields:
			obj =  builder.get_object(field)
			if obj == None:
				continue

			object_type = obj.get_name()
			
			if object_type == 'GtkEntry':
				values[field] = get_gtkEntry_value(obj)
			elif object_type == 'GtkTextView':
				values[field] = get_gtkTextView_value(obj)
			elif object_type == 'GtkComboBoxText':
				values[field] = get_gtkComboBoxText_value(obj)


		print values



def get_gtkEntry_value(obj):
	return obj.get_text()

def get_gtkTextView_value(obj):
	buf = obj.get_buffer()
	return buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)

def get_gtkComboBoxText_value(obj):
	return obj.get_active_text()


def main():
	global builder
	
	builder.add_from_file(sys.argv[1])
	builder.connect_signals(Handler())

	window = builder.get_object("main")
	window.show_all()

	Gtk.main()

if __name__ == '__main__':
	main()

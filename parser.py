import re
import os
import time
import sys
import email
import config

class Parser:
	mail = config.mail
	working_dir = config.working_dir
	blat_dir = config.blat_dir
	display = config.display
	displayrewers = config.displayrewers
	inputfile = config.inputfile
	outputfile = config.outputfile

	def __init__(self,firm = ''):
		self.firm = firm
		print "Order for : " + self.firm
		self.openFiles();

		ifbase = re.search(r"base64", self.filecontent)

		if ifbase is None:
			self.getRegexWithoutBase64()
		else:
			self.getRegexWithBase64()
			self.makeEmail()

		self.searchFiles()
		self.sendEmailAndClean()

	def openFiles(self):
		#display
		d = open(self.display, 'r')
		self.displaycontent = d.read()

		#display rewers
		d2 = open(self.displayrewers, 'r')
		self.displayrewerscontent = d2.read()

		for dirname, dirnames, filenames in os.walk(self.working_dir+self.firm):
		    # print path to all subdirectories first.
		    # print path to all filenames.
		    for filename in filenames:
		        fileindir = (os.path.join(dirname, filename))

		base64check = r"base64"
		self.f = open(fileindir, 'r')
		self.filecontent = self.f.read()
		self.modified = open(self.inputfile,'w')
		self.a = 1;

	def getRegexWithoutBase64(self):
		print "Without Base64"
		if (self.firm in config.firms):
			if ('regex' in config.firms[self.firm]['no_base']):
				self.regex = config.firms[self.firm]['no_base']['regex']
			if ('regex2' in config.firms[self.firm]['no_base']):
				self.regex2 = config.firms[self.firm]['no_base']['regex2']
			if ('regex3' in config.firms[self.firm]['no_base']):
				self.regex3 = config.firms[self.firm]['no_base']['regex3']
			if ('regex4' in config.firms[self.firm]['no_base']):
				self.regex4 = config.firms[self.firm]['no_base']['regex4']
		else:
			print "Nie wybrales zadnej firmy kolego"
			sys.exit()

	def getRegexWithBase64(self):
		print "With Base64"
		self.regex2 = r"([0-9]{13})"
		if (self.firm in config.firms):
			if ('regex' in config.firms[self.firm]['base64']):
				self.regex = config.firms[self.firm]['base64']['regex']
			if ('regex2' in config.firms[self.firm]['base64']):
				self.regex2 = config.firms[self.firm]['base64']['regex2']
			if ('regex3' in config.firms[self.firm]['base64']):
				self.regex3 = config.firms[self.firm]['base64']['regex3']
			if ('regex4' in config.firms[self.firm]['base64']):
				self.regex4 = config.firms[self.firm]['base64']['regex4']
		else:
			print "Nie wybrales zadnej firmy kolego"
			sys.exit()

	def makeEmail(self):
		m = email.message_from_string(self.filecontent)
		for part in m.walk():
			if part.get_content_type() == "text/plain":
				self.decodedbase = part.get_payload().decode('base64')
			if self.firm == "sante":
				if part.get_content_type() == "text/html":
					self.decodedbase = part.get_payload().decode('base64')
			else:
				self.decodedbase = part.get_payload().decode('base64')

	def searchFiles(self):
		if hasattr(self, 'decodedbase'):
			matches = re.findall(self.regex, self.decodedbase)
			matches = sorted(set(matches), key=matches.index)
		else:
			matches = re.findall(self.regex, self.filecontent)

		for match in matches:
			if not hasattr(self, 'regex2'):
				self.regex2 = r"([0-9]{13})"
			ean = re.findall(self.regex2,match)
			ilosc = re.findall(self.regex3,match)
			if hasattr(self, 'regex4'):
				iloscszt = re.findall(self.regex4,match)

			for pureean in ean:
				print "%s" % (pureean)
				if self.firm == "sante":
					ifdisplay = re.search('(' + pureean + '.*)', self.displaycontent)
					if ifdisplay is None:
						print "Nie display"
						dsp = False
					else:
						print "display"
						dsp = True
						displayqty = re.split("\s",ifdisplay.group(0));
			if (ilosc):
				for pureilosc in ilosc:
					ifdisplay2 = None #re.search('(' + pureean + '.*)', self.displayrewerscontent)
					if ifdisplay2 is None:
						print "Nie przyprawa"
					else:
						print "Przyprawa"
						display2qty = re.split("\s",ifdisplay2.group(0));
						pureilosc = int(pureilosc) * int(display2qty[1]);

					if self.firm == "sante" and dsp == True:
						pureilosc = float(pureilosc) / int(displayqty[1]);
						if pureilosc.is_integer():
							pureilosc = int(pureilosc)
							print "%i" % (pureilosc)
						else:
							print "%.1f" % (pureilosc)
							pureilosc = str(pureilosc).replace('.',',')
					else:
						print "%s" % (pureilosc)

					if ('iloscszt' in locals()):
						for pureilosc in iloscszt:
							print "%s" % (pureilosc)

					self.modified.write(str(self.a) + '. ' + pureean + ' ' + str(pureilosc) + '\n')
					self.a = self.a+1;

	def sendEmailAndClean(self):
		self.modified.close()
		self.f.close()

		os.rename(self.inputfile, self.outputfile)
		time.sleep(1)
		if (config.send == 1):
			send_email = config.blat_dir + ' -attach ' + config.outputfile + ' -to ' + config.mail + ' -subject ' + config.firm.title() + ' -body ' + config.firm.title() + 'Plik -u ' + config.mail_username + ' -pw ' + config.mail_password
			os.system(send_email)
		if (config.delete == 1):
			delete_file = 'del /q "' + config.working_dir + config.firm + '\*"'
			os.system(delete_file)
		os.system('pause')

time.sleep(6) # wait for file to be ready
p = Parser(sys.argv[1])
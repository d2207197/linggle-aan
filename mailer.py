# -*- coding: utf-8 -*-

import smtplib, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Mailer():

	def __init__(self):
		self.msg = MIMEMultipart('alternative')
		self.parts = []
		# pass
	def To(self, you):
		self.msg['To'] = you
	def From(self, me):
		self.msg['From'] = me


	# def Content(self, msg):
		# self.msg = msg
	def Content(self, content, minetype='plain'):

		# if minetype == 'plain':

		# 	content = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
			
		# else:
		# 	content = """<html><head></head><body><p>Hi!<br>How are you?<br>Here is the <a href="http://www.python.org">link</a> you wanted.</p></body></html>"""

		# content = text

		self.parts.append(MIMEText(content, minetype))

	# Attach parts into message container.
	def _attach(self):
		for part in self.parts:
			self.msg.attach(part)

	def Subject(self, text):
		self.msg['Subject'] = text

	def Auth(self, username, password):
		self.username = username
		self.password = password

	def Server(self, smtp_server_address='gmail', smtp_server_port=''):


		if smtp_server_address.lower() == 'gmail':
			smtp_server_address = 'smtp.gmail.com'
			smtp_server_port = '587'
		
		self.smtp_server = smtp_server_address + ':' + str(smtp_server_port)

		# print smtp_server_address + ':' + smtp_server_port

	def send(self, debug=True):

		if debug:
			print '# Attaching content parts...'
			sys.stdout.flush()
		self._attach()


		if debug:
			print '# Setting smtp server',self.smtp_server,'...',
			sys.stdout.flush()
		server = smtplib.SMTP(self.smtp_server)
		server.starttls()

		if debug:
			print 'done.\n# Login to server...',
			sys.stdout.flush()
		server.login(self.username, self.password)

		if debug:
			print 'done.\n# Sending mail...',
			sys.stdout.flush()
		server.sendmail(self.msg['from'], self.msg['to'], self.msg.as_string())

		if debug:
			print 'done.\n# Finished.'
			sys.stdout.flush()
		server.quit()

if __name__ == '__main__':

	mailer = Mailer()

	mailer.Server('Gmail')

	mailer.To('maxis1718@gmail.com')
	mailer.From('maxis1718@gmail.com')

	mailer.Auth('maxis1718', 'seefish1030')

	mailer.Content('Hi')
	mailer.Content('<a>http://127.0.0.1</a>', 'html')

	mailer.Subject('Hi Linggler!')

	mailer.send(True)

# mailer.Config.Server.address('123')

# mailer.Config.

# fromaddr = 'maxis1718@gmail.com' 
# toaddrs  = 'vincent732@gmail.com'
# msg = 'Hello python email!'

# # Credentials (if needed)  
# username = 'maxis1718'
# password = 'seefish1030'

# # The actual mail send 
# server = smtplib.SMTP('smtp.gmail.com:587')
# server.starttls()
# server.login(username,password)
# server.sendmail(fromaddr, toaddrs, msg)
# server.quit()
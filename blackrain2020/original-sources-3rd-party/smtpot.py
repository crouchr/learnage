#!/sw/bin/python
#
# smtpot.py -- standalone SMTP honeypot, accumulates mail to mailbox files.
#
# Copyright (C) 2002, 2003 Karl A. Krueger
# Freely redistributable, no warranty.  If you do anything interesting with
# this, please let me know -- email "kkrueger AT whoi DOT edu".
#
# Version 0.3.2 -- added timestamp toys
# 
# Depends on portalocker.py, available from ActiveState:
#     http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65203
#
# For a native Windows SMTP honeypot, see SWiSH by "Canned Ham":
#     http://shat.net/swish/
#
# Developed on Mac OS X BSD with Debian Fink and Python 2.2
# Tested on Debian GNU/Linux for i386 and PowerPC
# Tested on Windows 2000 with Cygwin by Bob Zinn
# Suggestions & hints from Bob Zinn, Paul Vader.
#
# TODO:
#     * Add some sort of address sanity checking so we don't VRFY or
#       accept mail to "(@#(*@(#*@ <*!&@#@@&#*@>".
#     * Fix responses to actually resemble Sendmail!
#
# BUGS:
#     * Does not look like Sendmail in at least these ways:
#         + Per-command HELP giveth not, though claimeth so.
#         + Response messages lacketh detail, specificity.
#         + Distinguisheth not EHLO from HELO sessions.
#         + Implementeth not VERB, nor declareth same.
#         + Distinguisheth nohow local from remote addresses.
#         + Indeed, performeth but no address validation.
#     * Does not keep a command log -- connections which do nothing but
#       probe don't get logged.  Run tcpflow if you want this for now.

import SocketServer, socket, sys, time, thread, portalocker


### BEGIN CONFIGURATION ###

# Our "mail spool" files -- one for localhost mail, one for spam.  There
# are two because some systems (like Mac OS X) will send mail to themselves
# on the loopback if they find an SMTP listening!
MAILSPOOL  = "/Users/karl/mail/smtpot"
LOCALSPOOL = "/Users/karl/mail/localmail"

# VRFY_MODE -- how do we respond to VRFY and EXPN?
# 	0 = return 502 Not implemented ("secure MTA")
# 	1 = return 252 Go ahead and try ("snarky MTA")
# 	2 = return 250 <address> ("slutty MTA", treats everything as local)
#	3 = return 251 User not local, will deliver to <address> ("open relay")
VRFY_MODE = 3

# TARPIT_SLEEP -- how many seconds do we pause after every command?
TARPIT_SLEEP = 0.5

# ERROR_SLEEP -- how many seconds do we pause after an -error-?
ERROR_SLEEP = 1

# SERVER_TYPE -- what kind of TCPServer should we be?
#	SocketServer.TCPServer -- single-connection server
#	SocketServer.ForkingTCPServer -- multi-process server
#	SocketServer.ThreadingTCPServer -- multi-thread server
SERVER_TYPE = SocketServer.TCPServer

# Version string -- placed in Received: header
VERSION = "smtpot.py 0.3.2"

# All SMTP message strings defined here.
SMTP_BANNER =	"220 localhost ESMTP Sendmail 8.2.0/8.2.0; %s\r\n"
SMTP_UNREC =	"500 Command unrecognized\r\n"
SMTP_BYE =	"221 %s closing connection\r\n"
SMTP_OK =	"250 Ok\r\n"
SMTP_VRFY =	"250 %s\r\n"
SMTP_VRFY_TRY =	"252 Go ahead\r\n"
SMTP_VRFY_ERR = "502 Command unimplemented\r\n"
SMTP_VRFY_FWD = "251 User not local, will deliver to %s\r\n"
SMTP_ARG = 	"501 Invalid or missing argument\r\n"
SMTP_HELLO =	"250 Hello %s [%s], pleased to meet you\r\n"
SMTP_TWO_MAIL = "503 Nested MAIL command\r\n"
SMTP_NO_MAIL =	"503 Need MAIL command first\r\n"
SMTP_NO_RCPT =	"503 Need RCPT command first\r\n"
SMTP_GO_AHEAD =	"354 Go ahead.  <CRLF>.<CRLF> to finish.\r\n"
SMTP_SUCCESS =	"250 Got it, mail from %s to %s for %s lines\r\n"
SMTP_NOHAPPEN = "500 This can't happen\r\n"
SMTP_HELP = 	"""\
214-Commands:\r
214-    HELO    EHLO    MAIL    RCPT    DATA\r
214-    RSET    NOOP    QUIT    HELP    VRFY\r
214-    EXPN\r
214-For more info use "HELP <topic>".\r
214-For local information send email to Postmaster at your site.\r
214 End of HELP info\r
"""

# Banner timestamp control.  The first is a time.strftime() format which
# is used in the SMTP banner.  The second is how far off to be from the
# correct time!  This allows the emulation of very broken systems.
BANNER_TIME_FORMAT = '%a, %d %b %Y %X %Z'
BANNER_TIME_WRONGNESS = -63113852L


### END CONFIGURATION ###

# Commands, and arg lengths (0 = either 1 or 2)
SMTP_COMMANDS = { "HELO": 2, "EHLO": 2, "MAIL": 2, "RCPT": 2, "DATA": 1,
                  "VRFY": 2, "EXPN": 2, "RSET": 1, "HELP": 0, "NOOP": 1,
                  "QUIT": 1 }

# Utility, may as well do it here.
WRITELOCK = thread.allocate_lock()

# Okay, ugly capitalized globals done with!

class SMTPHandler(SocketServer.BaseRequestHandler):
	"""Request handler for a single SMTP session."""
	def setup(self):
		self.hello = None
		self.sender = None
		self.recips = []
		self.mailbuf = []
		self.quitting = 0
		self.sockOut = self.request.makefile('wb')
		self.sockIn = self.request.makefile('r')
		self.interface = self.request.getsockname()[0]
		if self.client_address[0] == "127.0.0.1":
			self.targetfile = LOCALSPOOL
		else:
			self.targetfile = MAILSPOOL

	def writeOut(self, text):
		"""Write a line to the socket, aborting on 'broken pipe'."""
		try:
			self.sockOut.write(text)
		except IOError:
			self.quitting = 1

	def writeErr(self, text):
		"""Write a line as an error message."""
		time.sleep(ERROR_SLEEP)
		self.writeOut(text)

	def dumpmail(self):
		"""Called after DATA to store the mail buffer to the file."""
		fd = file(self.targetfile, 'a')
		WRITELOCK.acquire()
		portalocker.lock(fd, portalocker.LOCK_EX)
		fd.write("""\
From %s %s
Received: from %s (%s [%s])
	by %s [%s] (%s)
	for %s; %s
""" % (self.sender, time.ctime(), self.hello,
       socket.getfqdn(self.client_address[0]), self.client_address[0], 
       socket.getfqdn(self.interface), self.interface, VERSION,
       repr(self.recips),
       time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())))
       		for line in self.mailbuf:
			fd.write(line)
		fd.write("\n")	
		portalocker.unlock(fd)
		WRITELOCK.release()

	# SMTP Command Handlers begin
	# Each of these functions implements the SMTP command
	# it is named for.

	def rset(self):
		self.sender = None
		self.recips = []
		self.mailbuf = []
		self.writeOut(SMTP_OK)

	def quit(self):
		self.quitting = 1
		self.writeOut(SMTP_BYE % 
                    socket.getfqdn(self.interface))

	def noop(self):
		self.writeOut(SMTP_OK)

	def vrfy(self, addr):
		# See top for definition of VRFY_MODE
		if VRFY_MODE == 0:
			self.writeErr(SMTP_VRFY_ERR)
		elif VRFY_MODE == 1:
			self.writeOut(SMTP_VRFY_TRY)
		elif VRFY_MODE == 2:
			self.writeOut(SMTP_VRFY % addr)
                else:
                        self.writeOut(SMTP_VRFY_FWD % addr)

	def help(self):
		self.writeOut(SMTP_HELP)

	def helo(self, addr):
		self.hello = addr
		self.writeOut(SMTP_HELLO % 
                    (socket.getfqdn(self.client_address[0]),
                     self.client_address[0]))

	def mail(self, arg):
		if not arg.upper().startswith("FROM:"):
			self.writeErr(SMTP_ARG)
		elif self.sender:
			self.writeErr(SMTP_TWO_MAIL)
		else:
			addr = arg[5:].strip()
			self.sender = addr
			self.writeOut(SMTP_OK)

	def rcpt(self, arg):
		if not arg.upper().startswith("TO:"):
			self.writeErr(SMTP_ARG)
		elif not self.sender:
			self.writeErr(SMTP_NO_MAIL)
		else:
			addr = arg[3:].strip()
			self.recips.append(addr)
			self.writeOut(SMTP_OK)

	def data(self):
		if self.recips == []:
			self.writeErr(SMTP_NO_RCPT)
		else:
			self.writeOut(SMTP_GO_AHEAD)
			self.sockOut.flush()
			while 1:
				line = self.sockIn.readline()
				if line.rstrip() == ".":
					break
				if line.startswith("From "):
					line = ">" + line
				self.mailbuf.append(line)
			self.dumpmail()
			self.writeOut(SMTP_SUCCESS % (self.sender,
				repr(self.recips), len(self.mailbuf)))
			self.sender = None
			self.recips = []
			self.mailbuf = []

	# SMTP Command Handlers end

	def handle(self):
		"""Called by the SocketServer to handle one session."""

		# Print the banner
		self.writeOut(SMTP_BANNER % 
			time.strftime(BANNER_TIME_FORMAT,
				time.localtime( time.time() 
				              + BANNER_TIME_WRONGNESS )))

		# Loop over command inputs
		while not self.quitting:
			# See if the user closed the pipe on us
			try:
				self.sockOut.flush()
			except IOError:
				self.quitting = 1
				continue

			# Read a command line (should be pipeline safe)
			argv = self.sockIn.readline().rstrip().split(None, 1)

			# Idle for a moment (see top)
			time.sleep(TARPIT_SLEEP)

			# Handle blank line
			if len(argv) == 0:
				self.writeErr(SMTP_UNREC)
				continue
			argv[0] = argv[0].upper()			

			# This is kind of weird.  SMTP_COMMANDS tells us both 
			# whether the command is valid, and whether it takes
			# an argument.
			if argv[0] not in SMTP_COMMANDS.keys():
				self.writeErr(SMTP_UNREC)
			elif ( SMTP_COMMANDS[argv[0]] and 
			       len(argv) != SMTP_COMMANDS[argv[0]] ):
				self.writeErr(SMTP_ARG)
			elif argv[0] == "EHLO" or argv[0] == "HELO":
				# We declare no extensions, so EHLO == HELO.
				self.helo(argv[1])
			elif argv[0] == "MAIL":
				self.mail(argv[1])
			elif argv[0] == "RCPT":
				self.rcpt(argv[1])
			elif argv[0] == "DATA":
				self.data()
			elif argv[0] == "VRFY" or argv[0] == "EXPN":
				self.vrfy(argv[1])
			elif argv[0] == "RSET":
				self.rset()
			elif argv[0] == "HELP":
				self.help()
			elif argv[0] == "NOOP":
				self.noop()
			elif argv[0] == "QUIT":
				self.quit()
			else:
				# Can't happen
				self.writeOut(SMTP_NOHAPPEN)
				
		  
if __name__ == '__main__':
	myServer = SERVER_TYPE(('', 25), SMTPHandler)
	myServer.serve_forever()


#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  king_phisher/smtp_server.py
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the project nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# This used to be built on the stdlib's asyncore/smtpd modules. Both were
# removed from the standard library in Python 3.12 (PEP 594), which made
# this module fail to import at all on 3.12+ (see upstream issue #522 --
# confirmed reproducible on a python:3.13-slim image, and the upstream
# maintainer confirmed this codebase won't get the fix). Rebuilt on asyncio
# (stdlib) via aiosmtpd, the de facto maintained replacement for smtpd. The
# public surface (constructor signature, serve_forever/shutdown,
# process_message) is unchanged so tools/debug_smtp_server.py needs no
# changes.

import logging
import threading

from aiosmtpd.controller import Controller

class BaseSMTPServer(object):
	"""
	An SMTP server useful for debugging. Messages handled by this server
	are not forwarded anywhere.
	"""
	def __init__(self, localaddr, remoteaddr=None):
		"""
		:param tuple localaddr: The local address to bind to.
		:param tuple remoteaddr: The remote address to use as an upstream SMTP relayer.
		"""
		self.logger = logging.getLogger('KingPhisher.SMTPD')
		self._stop_event = threading.Event()
		self._controller = Controller(self, hostname=localaddr[0], port=localaddr[1])
		self.logger.info("smtp server listening on {0}:{1}".format(localaddr[0], localaddr[1]))

	async def handle_DATA(self, server, session, envelope):
		"""
		The handler hook aiosmtpd calls once a full message has been
		received. Adapts it to the :py:meth:`.process_message` signature
		this class has always exposed.
		"""
		self.process_message(session.peer, envelope.mail_from, envelope.rcpt_tos, envelope.content)
		return '250 Message accepted for delivery'

	def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
		self.logger.info("received message from {0} ({1}) to {2}".format(mailfrom, peer[0], ', '.join(rcpttos)))

	def serve_forever(self):
		"""
		Process requests until :py:meth:`BaseSMTPServer.shutdown` is called.
		"""
		self._controller.start()
		try:
			self._stop_event.wait()
		finally:
			self._controller.stop()

	def shutdown(self):
		self._stop_event.set()

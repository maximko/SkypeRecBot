#!/usr/bin/env python

'''
Copyright (C) 2014 maximko <me@maximko.org>
This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See the COPYING file for more details.
'''

import Skype4Py
import logging
import random
import string
import time


# Settings
# Set to None if you don't want to receive link to a recorded file
fileurl = 'http://example.com/records/%s'
# Path to record files (must be writable!)
files_path = '/home/user/records'
# Log level (python logging)
loglevel = logging.INFO


class SkypeRecBot(object):

    def __init__(self):
        # Preparing logger
        self.logger = logging.basicConfig(format='%(asctime)s: %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)
        
        # Connecting to Skype
        self.skype = Skype4Py.Skype(Events=self)
        self.skype.FriendlyName = "SkypeRecordBot"
        self.skype.Attach()
        
        # Active call state and user
        self.has_active_call = False
        self.active_call_user = '' #FIXME: Use call id instead this
            
    def AttachmentStatus(self, status):
        if status == Skype4Py.apiAttachSuccess:
            self.set_user_status(Skype4Py.cusSkypeMe, 'Ready to record')
            self.logger.info('Successfully attached to Skype %s user %s' % (self.skype.Version,
                                                                            self.skype.CurrentUser.Handle))
        elif status == Skype4Py.apiAttachAvailable:
            self.skype.Attach()
    
    # Call processing   
    def CallStatus(self, call, status):
        self.logger.debug("CallStatus %s, from %s" % (status, call.PartnerHandle))
        
        # Incoming call, answer if no other active calls
        if status == Skype4Py.clsRinging and (call.Type == Skype4Py.cltIncomingP2P or call.Type == Skype4Py.cltIncomingPSTN) and not self.has_active_call:
            self.logger.info('Answering incoming call from %s' % call.PartnerHandle)
            call.Answer()
            self.has_active_call = True
            # Reset record fiename
            self.filename = ''
        
        # After answer, start record     
        elif status == Skype4Py.clsInProgress and self.has_active_call:
            self.active_call_user = call.PartnerHandle
            # Changing status to UNAVAILABLE
            self.set_user_status(Skype4Py.cusNotAvailable, 'Busy with another call')
            # Building record filename
            self.filename = '%s-%s-%s.wav' % (time.strftime('%d-%b-%Y-%H-%M-%S'), call.PartnerHandle, 
                                              ''.join([random.choice(string.hexdigits) for n in xrange(10)]))
            path = files_path + '/' + self.filename
            self.logger.info('Start recording to %s' % path)
            # Record
            call.OutputDevice(Skype4Py.callIoDeviceTypeFile, path)
        
        # We have another active call
        elif status == Skype4Py.clsRefused and self.has_active_call:
            self.logger.info('Refused call from %s due to another active call with %s, sending info message' % (call.PartnerHandle, self.active_call_user))
            self.skype.SendMessage(call.PartnerHandle, "Sorry, but I'm recording another call right now. Please try again later.")

        # Finishing call, sending file or link to user
        elif status == Skype4Py.clsFinished and self.has_active_call and self.active_call_user == call.PartnerHandle:
            self.logger.info('Call with %s finished' % call.PartnerHandle)
            self.has_active_call = False
            self.active_call_user = ''
            # Changing status to SkypeMe!
            self.set_user_status(Skype4Py.cusSkypeMe, 'Ready to record')
            # Sending download link
            if fileurl is not None:
                self.logger.info('Sending download link to %s' % call.PartnerHandle)
                self.skype.SendMessage(call.PartnerHandle, fileurl % self.filename)
                

    def UserAuthorizationRequestReceived(self, user):
        self.logger.info('Authorizing user %s' % user.Handle)
        # Authorizing user
        user.IsAuthorized = True

    def set_user_status(self, status, moodtext):
        if status:
            self.logger.debug("Changing status to %s: %s" % (status, moodtext))
            try:
                self.skype.ChangeUserStatus(status)
                self.skype.CurrentUserProfile.MoodText = moodtext
            except Skype4Py.SkypeError, e:
                self.logger.error(str(e))

if __name__ == "__main__":
    bot = SkypeRecBot()  
    while True:
        time.sleep(1.0)

#!/usr/bin/python
#
# Copyright (C) 2007 Google Inc.
# Refactored in 2009 to work for Google Analytics by Sal Uryasev at Juice Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This script requires the installation of Google's gdata module
# and the Analytics gdata patch from Juice Analytics Inc.
# To see the installation instructions for the dgapi (gdata.analytics), 
# module, go to http://suryasev.github.com/python-degapi/


# __original_authors__ = ['kunalmshah.userid (Kunal Shah)', 'suryasev.userid (Sal Uryasev)']
__author__ = 'Me'

import sys
import os.path
import getopt

try:
    import gdata.auth
except:
    print "It appears that gdata is not installed.  Read the installation instructions"
    print "for details on how to install gdata."
    exit(1)
try:
    import gdata.analytics.service
except:
    print "It appears that the analytics addon is not installed.  Read the installation"
    print "instructions for details on how to install gdata."
    exit(1)


class OAuthSample(object):
    """An OAuthSample object demonstrates the three-legged OAuth process."""

    def __init__(self, consumer_key, consumer_secret):
        """Constructor for the OAuthSample object.
        
        Takes a consumer key and consumer secret, authenticates using OAuth
        mechanism and lists the document titles using Document List Data API.
        Uses HMAC-SHA1 signature method.
        
        Args:
            consumer_key: string Domain identifying third_party web application.
            consumer_secret: string Secret generated during registration.
        
        Returns:
            An OAuthSample object used to run the sample demonstrating the
            way to use OAuth authentication mode.
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.gd_client = gdata.analytics.service.AnalyticsDataService()

    def _PrintFeed(self, feed):
        """Prints out the contents of a feed to the console."""
        
        if not feed.entry:
            print 'No entries in feed.\n'
            
        i = 1
        for entry in feed.entry:
            print "%d. %s" % (i, ', '.join([{% for dim in dimension_list %}entry.{{dim}}.value,{% endfor %}] + [{% for met in metric_list %}entry.{{met}}.value,{% endfor %}]))
            i += 1
            
    def _PrintAccountFeed(self, feed):
        """Prints out the contents of an account feed to the console"""
        
        if not feed.entry:
            print 'No entries in feed.\n'
            
        i = 1
        for entry in feed.entry:
            print '%d. %s: %s, %s' % (i, entry.accountId.value, entry.profileId.value, entry.accountName.value)
            i += 1

    def _ListAllAccounts(self):
        """Retrieves a list of all of a user's accounts/profiles and displays them."""
        
        feed = self.gd_client.GetAccountList('default')
        self._PrintAccountFeed(feed)
        
    def _DataFeed(self):
        """
        Retrieves a list of all the data with a certain set of parameters.
        
        This particular piece of code pulls a maximum of 5000 or possible rows.
        """
        maximum_results = 5000
        
        feed = self.gd_client.GetData(ids='{{ids}}', 
                                      dimensions='{{dimensions}}',
                                      metrics='{{metrics}}',
                                      filters='{{filters}}',
                                      sort='{{sort}}',
                                      start_date='{{start_date}}',
                                      end_date='{{end_date}}')
                                                    
        total_results = feed.total_results.text
        
        i = 1000
        while i < min(maximum_results, total_results):
            additional_feed = self.gd_client.GetData(ids='{{ids}}', 
                                                     dimensions='{{dimensions}}',
                                                     metrics='{{metrics}}',
                                                     filters='{{filters}}',
                                                     sort='{{sort}}',
                                                     start_date='{{start_date}}',
                                                     end_date='{{end_date}}',
                                                     start_index=i+1)
                                                    
            feed.entry += additional_feed.entry
            i += 1000
        
        self._PrintFeed(feed)
    
    def Run(self):
        """Demonstrates usage of OAuth authentication mode and retrieves a list of
        accounts/analytics using Analytics Data API."""
        print '\nSTEP 1: Set OAuth input parameters.'
        self.gd_client.SetOAuthInputParameters(
                gdata.auth.OAuthSignatureMethod.HMAC_SHA1,
                self.consumer_key, consumer_secret=self.consumer_secret)
        print '\nSTEP 2: Fetch OAuth Request token.'
        request_token = self.gd_client.FetchOAuthRequestToken()
        print 'Request Token fetched: %s' % request_token
        print '\nSTEP 3: Set the fetched OAuth token.'
        self.gd_client.SetOAuthToken(request_token)
        print 'OAuth request token set.'
        print '\nSTEP 4: Generate OAuth authorization URL.'
        auth_url = self.gd_client.GenerateOAuthAuthorizationURL()
        print 'Authorization URL: %s' % auth_url
        raw_input('Manually go to the above URL and authenticate.'
                            'Press a key after authorization.')
        print '\nSTEP 5: Upgrade to an OAuth access token.'
        self.gd_client.UpgradeToOAuthAccessToken()
        print 'Access Token: %s' % (
                self.gd_client.token_store.find_token(request_token.scopes[0]))
                
        print '\nYour Accounts:\n'
        self._ListAllAccounts()
        raw_input("Press ENTER to continue")
        
        print '\nYour Documents:\n'
        self._DataFeed()
        raw_input("Press ENTER to continue")

        print 'STEP 6: Revoke the OAuth access token after use.'
        self.gd_client.RevokeOAuthToken()
        print 'OAuth access token revoked.'


def main():
    """Demonstrates usage of OAuth authentication mode.
    
    Prints a list of documents. This demo uses HMAC-SHA1 signature method.
    """
    # Parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', ['consumer_key=',
                                                      'consumer_secret='])
    except getopt.error, msg:
        print ('python oauth_example.py --consumer_key <key> '
                     '--consumer_secret <secret> ')
        sys.exit(2)

    consumer_key = ''
    consumer_secret = ''
    # Process options
    for option, arg in opts:
        if option == '--consumer_key':
            consumer_key = arg
        elif option == '--consumer_secret':
            consumer_secret = arg

    while not consumer_key:
        consumer_key = raw_input('Please enter consumer key: ')
    while not consumer_secret:
        consumer_secret = raw_input('Please enter consumer secret: ')

    sample = OAuthSample(consumer_key, consumer_secret)
    sample.Run()


if __name__ == '__main__':
    main()
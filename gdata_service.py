from django.conf import settings

import gdata.auth
import gdata.analytics.service

class DjangoGoogleAnalyticsService(gdata.analytics.service.AnalyticsDataService):
    def __init__(self):
        """
        This is a convenience class for interfacing with the Google gdata oauth service
        
        Other useful functions include:
        SetOAuthToken(request_token)
        GenerateOAuthAuthorizationURL()
        UpgradeToOAuthAccessToken()
        RevokeOAuthToken()
        
        how to fetch account results:
            feed = self.GetAccountList('myemail@juiceanalytics.com')
            for entry in feed:
                print entry.accountId.value, entry.profileId.value, 
                      entry.accountName.value, entry.webPropertyId.value,
                      entry.title.text
                      
        how to fetch data results:
            feed = self.GetData(ids='ga:3175372', 
                                dimensions='ga:keyword',
                                metrics='ga:pageviews,ga:visits',
                                # filters='ga:requestUri1==/writing/',
                                sort='-ga:pageviews',
                                start_date='2008-07-22',
                                end_date='2008-08-22',
                                start_index=1)
            for entry in feed:
                print (entry.keyword.value, entry.pageviews.value, entry.visits.value)
                
        to see the total number of entries look up:
            feed.total_results.text
                
        when data exceeds 1000 values, multiple calls need to be made, augmenting start_index by 1000
        
        """
        self.callback_url = ""
        
        self.site_id = 0
        
        self.token_upgraded = False
        
        super(DjangoGoogleAnalyticsService, self).__init__()
        self.SetOAuthInputParameters(
            gdata.auth.OAuthSignatureMethod.HMAC_SHA1,
            settings.CONSUMER_KEY, 
            consumer_secret=settings.CONSUMER_SECRET)
        self.ssl = True
        
    def request_token(self):
        """
        shortcut to request oauth token and set oauth token
        """
        request_token = self.FetchOAuthRequestToken()
        self.SetOAuthToken(request_token)
        self.token_upgraded = False
        return True
        
    def authorization_url(self):
        """
        return an authorization url with the callback url attached
        """
        return self.GenerateOAuthAuthorizationURL(callback_url=self.callback_url,
                                                 include_scopes_in_callback=True)
        
    def upgrade_token(self):
        """
        wrapper for the function
        
        this is to be called after the authorization url goes through
        it returns the access token on success, and None otherwise
        
        token, if passed in, sets an OAuthToken
        """
        
        # scopes = gdata.service.lookup_scopes(self.service)
        # if not isinstance(scopes, (list, tuple)):
        #     scopes = [scopes,]
        # 
        # authorized_request_token = gdata.auth.OAuthToken(key=token, scopes=scopes,
        #                                                  oauth_input_params=self._oauth_input_params)
        # # authorized_request_token.oauth_input_params = self._oauth_input_params
        # 
        # return self.SetOAuthToken(authorized_request_token)
        try:
            self.UpgradeToOAuthAccessToken()
            self.token_upgraded = True
            return True
            # return self.token_store.find_token(request_token.scopes[0])
        except gdata.service.TokenUpgradeFailed:
            return False
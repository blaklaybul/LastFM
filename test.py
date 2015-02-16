#
# http://www.last.fm/api/show/geo.getTopTracks
#
from pprint import pprint
import urllib, urllib2
import inspect
import pandas as pd
try:
    import json
except ImportError:
    import simplejson as json

class LastFM:
    def __init__(self ):
        self.API_URL = "http://ws.audioscrobbler.com/2.0/"
        self.API_KEY = "efd4d182fb0ea0f3fa61ca00dc96d052"
    
    def send_request(self, args, **kwargs):
        #Request specific args
        kwargs.update( args )
        #Global args
        kwargs.update({
          "api_key":  self.API_KEY,
          "format":   "json"
        })
        try:
            #Create an API Request
            url = self.API_URL + "?" + urllib.urlencode(kwargs)
            #Send Request and Collect it
            data = urllib2.urlopen( url )
            #Print it
            response_data = json.load( data )
            #Close connection
            data.close()
            return response_data
        except urllib2.HTTPError, e:
            print "HTTP error: %d" % e.code
        except urllib2.URLError, e:
            print "Network error: %s" % e.reason.args[1]

    def get_top_artists(self, method, dict ):
        #find the key          
        args = {
            "method": method,
            "limit":  100
        }
        for key in dict.keys():
          args[key] = dict[key]
        
        response_data = self.send_request( args )
        artists = pd.DataFrame(response_data)

        print "~~~~~~~~~~~~~~" + str( args["method"] ) + "~~~~~~~~~~~~~~"
        
        #Get the first artist from the JSON response and print their name
        for artist in response_data["topartists"]["artist"]:
          print artist["name"]
    

def main():
    last_request = LastFM()
    last_request.get_top_artists( "tag.gettopartists", { "tag": "rock" } )

if __name__ == "__main__": main()
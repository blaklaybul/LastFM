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

        print "~~~~~~~~~~~~~~" + str( args["method"] ) + "~~~~~~~~~~~~~~"
        
        #Get the first artist from the JSON response and print their name
        for artist in response_data["topartists"]["artist"]:
          print artist["name"]
          

    def get_tags_by_artist (self, artist_name, **kwargs):
        # set the additioal parameters for this particulare API request
        kwargs.update({
            "method": "artist.gettoptags",
            "artist":   artist_name,
        })

        # get data from api using the api_request method (above)
        response_data = self.api_request(**kwargs)

        # access just the tags data from the response
        tags = response_data['toptags']['tag']
        
        # prepare to find the total count of tags for each artist in order to
        # determine the relevance each tag is to the artist
        total_tag_count = 0

        for tag in tags:
            # get the encoded tag name and tag count for each result
            tag_name = tag['name'].encode('utf8')
            tag_count = tag['count']

            # for each iterationn, add the tag count to the total (  )
            total_tag_count = total_tag_count + int(tag_count)

            try:
                # add the tag to the DB
                self.add_tag(tag_name)

                # find the artist and tag id (see db.py)

                artist_id = self.get_artist_by_name(artist_name) 
                tag_id = self.get_tag_by_name(tag_name)

                # add the artist_id, tag_id relation and the tag count (see db.yp)
                self.add_artist_to_tag(artist_id, tag_id, tag_count)

                print tag_name # for debugging

            # this try/except block deals with the issue in which a tag is BLANK
            # i consider this bad data, but regardless this issue had to be dealt with
            except StatementError:
                pass

        # update the tag percentage column for each tag
        self.set_tag_pct(artist_id, total_tag_count)

    

def main():
    last_request = LastFM()
    last_request.get_top_artists( "tag.gettopartists", { "tag": "rock" } )

if __name__ == "__main__": main()
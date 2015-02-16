import pandas as pd
import requests as re
import json

def populateTags():
	for artist in topArtists.index:
		getArtistTags(artist)

def getArtistTags(mbid):
	i = len(topTags)
	df_artistTags = pd.read_json(tagUrl + mbid)
	for tag in df_artistTags["toptags"][1]:
		topTags.loc[i] = [mbid, tag["name"], tag["count"]]
		i=i+1
	print "finished with " + topArtists.loc[mbid]["name"]

def getArtists(self,url):
	print "starting"
	df_artists = pd.read_json(url)
	for artist in df_artists["artists"][1]:
		topArtists.loc[artist["mbid"]] = [artist["name"], artist["playcount"], artist["listeners"]]

def main():
	artistUrl = "http://ws.audioscrobbler.com/2.0/?method=chart.gettopartists&page=1&limit=1000&api_key=efd4d182fb0ea0f3fa61ca00dc96d052&format=json"

	tagUrl = "http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&api_key=efd4d182fb0ea0f3fa61ca00dc96d052&format=json&mbid="

	i=0
	j=0

	topArtists = pd.DataFrame(columns = ["name", "plays", "listeners"])

	getArtists(artistUrl)


if __name__ == "__main__": main()
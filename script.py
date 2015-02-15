import pandas as pd
import requests as re
import json

# API Key: efd4d182fb0ea0f3fa61ca00dc96d052
# Secret: is 87218485d334cd8754d745f3cdefcca6


artistUrl = "http://ws.audioscrobbler.com/2.0/?method=chart.gettopartists&page=1&limit=1000&api_key=efd4d182fb0ea0f3fa61ca00dc96d052&format=json"

tagUrl = "http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&api_key=efd4d182fb0ea0f3fa61ca00dc96d052&format=json&mbid="

i=0

df_artists = pd.read_json(artistUrl)

topArtists = pd.DataFrame(columns = ["name", "plays", "listeners"])
topTags = pd.DataFrame(columns = ["mbid","tag","count"])

#have artists dataframe with their id, name, playcount, and number of listeners
for artist in df_artists["artists"][1]:
		topArtists.loc[artist["mbid"]] = [artist["name"], artist["playcount"], artist["listeners"]]

for tag in df_tags["toptags"][1]:
		topTags.loc["2342"] = [tag["name"], tag["count"]]

def populateTags():
	for artist in topArtists.index:
		getArtistTags(artist)

##i need to set it up so that the json is loaded before it loops
def getArtistTags(mbid):
	i = len(topTags)
	df_artistTags = pd.read_json(tagUrl + "mbid")
	for tag in df_tags["toptags"][1]:
		topTags.loc[i] = [mbid, tag["name"], tag["count"]]
		i=i+1
	print "finished with " + topArtists.loc[mbid]["name"] + i + "total tags"

for i in range(0,len(df_tags["toptags"][1])):
	topTags = topTags.append("324233412", df_tags[1][i]["name"], df_tags[1][i]["count"])
for tag in df_tags["toptags"][1]

i=0
for tag in df_tags["toptags"][1]:
	topTags.loc[i] = ["2342352", tag["name"], tag["count"]]
	i++

	for i in range(0,len(df_artistTags["toptags"][1])):
		topTags.append(mbid, df_artistTags[1][i]["name"],  df_artistTags[1][i]["count"])
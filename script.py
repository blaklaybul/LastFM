import pandas as pd
import requests as re
import json

# API Key: efd4d182fb0ea0f3fa61ca00dc96d052
# Secret: is 87218485d334cd8754d745f3cdefcca6


artistUrl = "http://ws.audioscrobbler.com/2.0/?method=chart.gettopartists&page=1&limit=1000&api_key=efd4d182fb0ea0f3fa61ca00dc96d052&format=json"

tagUrl = "http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&api_key=efd4d182fb0ea0f3fa61ca00dc96d052&format=json&mbid="

i=0
j=0

df_artists = pd.read_json(artistUrl)

#dataframes to be populated
topArtists = pd.DataFrame(columns = ["name", "plays", "listeners"])
topTags = pd.DataFrame(columns = ["mbid","tag","count"])
tagPairs = pd.DataFrame(columns = ["tag1","tag2","pairs"])

#have artists dataframe with their id, name, playcount, and number of listeners
for artist in df_artists["artists"][1]:
		topArtists.loc[artist["mbid"]] = [artist["name"], artist["playcount"], artist["listeners"]]

#remove artists without an mbid
topArtists = topArtists[topArtists.index !='']

#methods for populating tags dataframe
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


#get rid of tags with count = 0. Not sure why they appear in the JSON, but they don't appear on lastfm artist pages.
topTags["count"] = topTags["count"].astype(int)
topTags = topTags[topTags["count"] > 0]

#create an aggregate table to see how many instances of each tag we have. this will be useful when considering tag pairs, as we want to check what percent of a tags total occurrences appear with another tag.
aggTags = topTags.groupby["name"].sum("count")

#merge Artist's with their tags
ArtistsWithTags = pd.merge(topArtists, topTags, left_index = True, right_on = ["mbid"])

#join tags table on itself to get pairs
ArtistsWithTagPairs = pd.merge(ArtistsWithTags, ArtistsWithTags, left_on=["mbid"], right_on=["mbid"])

#remove x,x tag pairs
ArtistsWithTagPairs = ArtistsWithTagPairs[ArtistsWithTagPairs["tag_x"] != ArtistsWithTagPairs["tag_y"]]

#now we want a new frame that consists of tag pairs with their minimum count.. 
#e.g. if we have rock 100, electronic 45.. we take the pair rock, electronic to have occurred 45 times.
ArtistsWithTagPairs["min"] = ArtistsWithTagPairs.apply(lambda row: min(row["count_x"], row["count_y"]), axis=1)


#just take the pairs
tagPairs = ArtistsWithTagPairs[["tag_x","tag_y","min"]]

##create a groupby object to get total occurences of tag pairs. will need to dedupe
tagGroups = tagPairs.groupby(["tag_x","tag_y"], as_index=False).sum()

##we will only consider tags that co-occur more than 15 times together. This is for the sake of the output files, and to weed out weak relationships.
tagGroups = tagGroups[tagGroups["min"]>15]
tagGroups.columns = ["tag_1", "tag_2", "count"]

aggPairs = tagGroups.groupby(tagGroups.tag_x).sum()
aggPairs.columns = ["tag", "number_of_pairs"]

##for each tag, we consider all pairs it has, and take the percentage represented by a single pair

#first get x tags
tagGroupsAnal = pd.merge(tagGroups, aggPairs, left_on=["tag_x"], right_on = ["tag"])
tagGroupsAnal.drop(["tag"], axis=1,inplace=True)
tagGroupsAnal.rename(columns = {"number_of_pairs":"number_of_pairs_x"}, inplace=True)

#now get y tags
tagGroupsAnal = pd.merge(tagGroupsAnal, aggPairs, left_on=["tag_y"], right_on = ["tag"])
tagGroupsAnal.drop(["tag"], axis=1,inplace=True)
tagGroupsAnal.rename(columns = {"number_of_pairs":"number_of_pairs_y"}, inplace=True)

#now get strength scores. note that pairs ordered.. in that (rock, skate punk) is different from (skate punk, rock)
tagGroupsAnal["strength_of_pair"] = tagGroupsAnal.apply(lambda row: float(row["min"]) / row["number_of_pairs_x"], axis=1)
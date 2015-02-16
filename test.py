import pandas as pd
import json

# API Key: efd4d182fb0ea0f3fa61ca00dc96d052
# Secret: is 87218485d334cd8754d745f3cdefcca6

def getArtists(artistUrl):
	topArtists = pd.DataFrame(columns = ["name", "plays", "listeners"])
	df_artists = pd.read_json(artistUrl)
	
	#have artists dataframe with their id, name, playcount, and number of listeners
	for artist in df_artists["artists"][1]:
		topArtists.loc[artist["mbid"]] = [artist["name"], artist["playcount"], artist["listeners"]]

	#remove artists without an mbid.. there were a few.
	topArtists = topArtists[topArtists.index !='']

#methods for populating tags dataframe
#in case of json request error, exclude makes sure artists are not repeated in subsequent requests.
def populateTags():
	topTags = pd.DataFrame(columns = ["mbid","tag","count"])
	exclude = pd.unique(topTags.mbid)
	for artist in topArtists[~topArtists.index.isin(exclude)].index:
		getArtistTags(artist)

def getArtistTags(mbid):
	i = len(topTags)
	df_artistTags = pd.read_json(tagUrl + mbid)
	for tag in df_artistTags["toptags"][1]:
		topTags.loc[i] = [mbid, tag["name"], tag["count"]]
		i=i+1
	print "finished with " + topArtists.loc[mbid]["name"]

#method for returning similar tags 
def getSimilarTags(tag):
	print tagGroupsAnalyze[tagGroupsAnalyze.tag_1 == tag].sort("score",ascending=False).head(10)

def tagAnalysis():
	#get rid of tags with count = 0, they don't appear on lastfm artist pages.
	topTags["count"] = topTags["count"].astype(int)
	topTags = topTags[topTags["count"] > 0]

	#create an aggregate table to see how many instances of each tag we have across all artists
	#we will want to check what percent of a tags total occurrences appear with another tag.
	aggTags = topTags.groupby(["tag"], as_index=False).sum()

	#merge Artist's with their tags 
	ArtistsWithTags = pd.merge(topArtists, topTags, left_index = True, right_on = ["mbid"])

	#join tags table on itself to get pairs and remove (x,x) pairs
	ArtistsWithTagPairs = pd.merge(ArtistsWithTags, ArtistsWithTags, left_on=["mbid"], right_on=["mbid"])
	ArtistsWithTagPairs = ArtistsWithTagPairs[ArtistsWithTagPairs["tag_x"] != ArtistsWithTagPairs["tag_y"]]

	#now we want a new frame that consists of tag pairs with their minimum count per artist.. 
	#e.g. if we have rock 100, electronic 45.. we take the pair rock, electronic to have occurred 45 times.
	ArtistsWithTagPairs["min"] = ArtistsWithTagPairs.apply(lambda row: min(row["count_x"], row["count_y"]), axis=1)


	#just take the pairs
	tagPairs = ArtistsWithTagPairs[["tag_x","tag_y","min"]]

	##create a groupby object to get total occurences of tag pairs.
	##we will only consider tags that co-occur 15 or more times together. 
	#This is for the sake of the output files, and to weed out weak relationships.
	tagGroups = tagPairs.groupby(["tag_x","tag_y"], as_index=False).sum()
	tagGroups = tagGroups[tagGroups["min"]>=15]
	tagGroups.columns = ["tag_1", "tag_2", "count"]

	#only need to group by first column, since all tags are stored as (a,b) and (b,a)
	#this gives us how many times each tag appears in a pair
	aggPairs = tagGroups.groupby(tagGroups.tag_1, as_index=False).sum()
	aggPairs.columns = ["tag", "number_of_pairs"]

	##for each tag, we consider all pairs it has, and take the percentage represented by a single pair

	#first get x tags
	tagGroupsAnalyze = pd.merge(tagGroups, aggPairs, left_on=["tag_1"], right_on = ["tag"])
	tagGroupsAnalyze.drop(["tag"], axis=1,inplace=True)
	tagGroupsAnalyze.rename(columns = {"number_of_pairs":"number_of_pairs_x"}, inplace=True)

	#now get y tags
	tagGroupsAnalyze = pd.merge(tagGroupsAnalyze, aggPairs, left_on=["tag_2"], right_on = ["tag"])
	tagGroupsAnalyze.drop(["tag"], axis=1,inplace=True)
	tagGroupsAnalyze.rename(columns = {"number_of_pairs":"number_of_pairs_y"}, inplace=True)

	tagGroupsAnalyze["totalPairs"]=tagGroupsAnalyze.sum(axis=0)["count"]

	#We assign a strength of pair metric that is determined by the number of times the tags appear together divided by the sum of the total pairs they appear in individually.
	tagGroupsAnalyze["pair_percent_of_total"] = tagGroupsAnalyze.apply(lambda row: float(row["count"]) / (row["totalPairs"]), axis=1)

	tagGroupsAnalyze["pair_percent_of_x"] = tagGroupsAnalyze.apply(lambda row: float(row["count"]) / (row["number_of_pairs_x"]), axis=1)

	tagGroupsAnalyze["pair_percent_of_y"] = tagGroupsAnalyze.apply(lambda row: float(row["count"]) / (row["number_of_pairs_y"]), axis=1)

	tagGroupsAnalyze["perc_x_y_sum"] = tagGroupsAnalyze.pair_percent_of_x + tagGroupsAnalyze.pair_percent_of_y

	tagGroupsAnalyze["score"] = (tagGroupsAnalyze.pair_percent_of_x*tagGroupsAnalyze.pair_percent_of_y)*tagGroupsAnalyze.pair_percent_of_total*1000000

def main():
	#dataframes to be populated

	tagUrl = "http://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&api_key=efd4d182fb0ea0f3fa61ca00dc96d052&format=json&mbid="
	getArtists("http://ws.audioscrobbler.com/2.0/?method=chart.gettopartists&page=1&limit=10&api_key=efd4d182fb0ea0f3fa61ca00dc96d052&format=json")
	populateTags()
	tagAnalysis()
	getSimilarTags("indie")

if __name__ == "__main__": main()

i=0
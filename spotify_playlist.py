import requests
import os
import eyed3
import json
import time
import logging

logging.basicConfig(filename='spotifylog.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logger=logging.getLogger(__name__)

logger.setLevel(logging.DEBUG) 


failed_cases =[]

playListId = <PLAYLIST_ID>
dirPath = <DIRECTORY_WHERE_SONGS_ARE_STORED>

headers = {
    'Authorization': <TOKEN>,
}

def prepareQueryString(name, artist):
    queryString = "{name}&artist={artist}".format(name = name, artist = artist)
    return queryString


def addItemToPlaylist(songUris):
    url = "https://api.spotify.com/v1/playlists/{playListId}/tracks".format(playListId=playListId)

    payload = json.dumps({
      "uris": songUris
    })

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 201:
        data = response.json()
        logger.info("The final response while adding songs is ", data)
        return data
    else:
        logger.error("Attemopt to add the songs failed")

def getSongSpotifyUri(name, artist):
    try:
        queryString = prepareQueryString(name, artist)

        params = {
            "q": queryString,
            "type": "track",
            "limit": 1
        }
        logger.info("The params to search the song uri is", params)

        response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
        logger.info("The response for search is ")
        logger.info(response)
        if response.status_code == 200:
            data = response.json()
            logger.info("The name of the song is : {name}".format(name = data['tracks']['items'][0]['name']))
            trackUri = data['tracks']['items'][0]['uri']
            logger.info("The track URI is")
            logger.info(trackUri)
            return trackUri
        else:
            logger.error("Request failed for song {name} & {artist}".format(name=name, artist=artist))
    except:
        failed_cases.append(name)

def getListOfSongs(dirPath):
    dir_list = os.listdir(dirPath)
    listOfSongs = []
    for x in dir_list:
        if x.endswith(".mp3"):
            # Prints only mp3 file present in My Folder
            listOfSongs.append(x)
    print(listOfSongs)
    return listOfSongs

def getSongMetadata(song):
    try:
        audiofile = eyed3.load(dirPath + song)
        return [audiofile.tag.artist, audiofile.tag.title]
    except:
        logger.error("getting metadata failed", song)
        failed_cases.append(song)

def main():
    try:
        logger.info("Starting the script...")
        start_time = time.time()
        listOfSongs = getListOfSongs(dirPath)
        print(len(listOfSongs))
        logger.info("Total number of songs: {counter}".format(counter = len(listOfSongs)))
        spotifyUris = []
        count = 0
        for x in listOfSongs:
            logger.info("The counter is: {count}".format(count=count))
            logger.info("The song is: {song}".format(song=x))
            count+=1
            print(count)
            [artist, title] = getSongMetadata(x)
            print(artist, title)
            logger.info("Got the song metadata: artist: {artist}, title: {title}".format(artist=artist, title=title))
            spotifyUri = getSongSpotifyUri(title, artist)
            logger.info("Got the spotify Uri: {spotifyUri}".format(spotifyUri=spotifyUri))
            spotifyUris.append(spotifyUri)
        logger.info("All song uris:\n {spotifyUris}".format(spotifyUris=spotifyUris))
        logger.info("The total uris :\n {spotifyUris}".format(spotifyUris=len(spotifyUris)))
        response = addItemToPlaylist(spotifyUris)
        logger.info("The response to added playlist is")
        logger.info(response)
        end_time = time.time()
        logger.info("the total time taken for script is {total_time}".format(total_time = end_time-start_time))
        logger.info("All the failed cases")
        logger.info(failed_cases)
    except:
        logger.error("Some error occured")




if __name__ == '__main__':
    main()
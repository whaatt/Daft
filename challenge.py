from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import Spotify
import csv, random

# Spotify client credentials. DO NOT COMMIT.
CLIENT = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
DaftPunk = 'spotify:artist:4tZwfgrHOc3mvqYlEYSvVi'

def Q1(spotify):
  '''Retrieves and sorts similar artists to Daft Punk.'''
  daftGenres = set(spotify.artist(DaftPunk)['genres'])
  related = spotify.artist_related_artists(DaftPunk)['artists']

  for artist in related:
    artist['similarity'] = len(daftGenres.intersection(artist['genres']))
  # Sort DESC first by the number of common genres, then sort by popularity.
  related.sort(key = lambda x: (-x['similarity'], -x['popularity']))

  # Output header and result rows for a CSV file.
  rows = [['Rank', 'Name', 'Similarity', 'Popularity']]
  for i in range(len(related)):
    artist = related[i]
    rows.append([i + 1, artist['name'], artist['similarity'],
                 artist['popularity']])
  return rows

artistAlbums = {}
def computeTopThreeAlbumsForRelatedArtists(spotify):
  '''Finds top three albums by popularity for each related artist.'''
  related = spotify.artist_related_artists(DaftPunk)['artists']
  for artist in related:
    # First, extract all the albums for each related artist.
    albums = spotify.artist_albums(artist['uri'])['items']
    albums = [spotify.album(album['uri']) for album in albums]

    # Next, filter out all the albums that are not available in America.
    available = filter(lambda x: 'US' in x['available_markets'], albums)

    # Finally, sort and pick top three albums.
    albums.sort(key = lambda x: (-x['popularity']))
    artistAlbums[artist['name']]  = albums[:3]

def Q2(spotify):
  '''A shim around topThreeForRelated to create CSV output.'''
  rows = [['Name', 'Album One', 'Album Two', 'Album Three']]

  # Extract artist names.
  for artist in artistAlbums:
    albums = artistAlbums[artist]
    albumNames = [album['name'] for album in albums]
    rows.append([artist] + albumNames)
  return rows

def Q3(spotify):
  '''Compute a set list using the top three albums overall.'''
  flatten = lambda l: [item for subList in l for item in subList]
  allAlbums = flatten(artistAlbums.values())

  # Find the top three albums across all related artists.
  allAlbums.sort(key = lambda x: (-x['popularity']))
  topAlbums = allAlbums[:3]

  rows = []
  contribution = []
  # Compute each album's contribution to the set list.
  T, S = sum([album['popularity'] for album in topAlbums]), 15
  for album in topAlbums:
    contribution.append(round(album['popularity'] * 1.0 / T * S))
    T = T - album['popularity']
    S = S - contribution[-1]

    # Include each album name and its contribution in CSV.
    rows.append([album['name'], contribution[-1]])

  songs = []
  # Have each album contribute songs.
  for i in range(len(contribution)):
    # Songs chosen randomly now; could use popularity?
    tracks = spotify.album_tracks(topAlbums[i]['uri'])['items']
    songs = songs + random.sample(tracks, min(len(tracks), contribution[i]))

  # Convert to CSV result rows and shuffle.
  songs = [[song['name']] for song in songs]
  random.shuffle(songs)
  return rows + [[]] + songs

def writeCSV(name, function):
  '''Writes a set of rows from a function to a CSV file.'''
  with open(name + '.csv', 'w', newline = '') as CSVFile:
    writer = csv.writer(CSVFile)
    writer.writerows(function(spotify))

if __name__ == '__main__':
  credentials = SpotifyClientCredentials(client_id = CLIENT,
                                         client_secret = SECRET)
  spotify = Spotify(client_credentials_manager = credentials)
  computeTopThreeAlbumsForRelatedArtists(spotify)
  writeCSV('Q1', Q1)
  writeCSV('Q2', Q2)
  writeCSV('Q3', Q3)

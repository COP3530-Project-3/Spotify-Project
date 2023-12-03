from authorize import auth_credentials
from songInfo import get_song_info, get_playlist_tracks, get_track_recommendations, exponential_backoff
from songPCA import song_pca
import time, sys, re

def is_spotify_playlist(input_string):
    pattern = r'^(spotify:|https://open.spotify.com/)(playlist|user/.+/playlist)/[a-zA-Z0-9]+(\?.*)?$'
    return bool(re.match(pattern, input_string))

def main():
  start_time = time.time()
  # login
  spotify = auth_credentials()

  # Replace 'YOUR_PLAYLIST_ID' with the link to the spotify playlist
  # Extracted ID from the playlist URL
  playlist_id = input("Your playlist link: ")

  if is_spotify_playlist(playlist_id):

      # Gather audio features
      playlist, playlist_title = get_playlist_tracks(spotify, playlist_id)
      songs_metadata, song_ids = get_song_info(spotify, playlist, 100, 'playlist')
      print("Got ur songs...")

      # Rank song IDs along with songs_metadata by similarity
      similar_songs, mean, n_components = song_pca(songs_metadata, song_ids, playlist_title, 'playlist') # n_comp = 4*log(track num) cosine = 0.7, euclidean = 0.3
      print("Determined your taste...")

      # Gets recommendations 2 standard deviations from the mean, using the calculated top similar tracks in the playlist
      print('Asking Spotify API to not rate limit me...')
      track_ids = list(similar_songs.values())
      rec_metadata, rec_ids = get_track_recommendations(spotify, track_ids, mean)
      rec_songs, mean, n_components = song_pca(rec_metadata, rec_ids, f'{playlist_title} radio', 'recommend', mean, n_components)
      
      end_time = time.time()
      elapsed_time = end_time - start_time
      print(f"Runtime: {elapsed_time:.2f} seconds")

  else:
      print("I can't work with this link. Try again")
      main()

if __name__ == "__main__":
  main()

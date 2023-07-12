import xbmc
import xbmcaddon
import xbmcgui

addon = xbmcaddon.Addon()

def get_current_album():
    playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    if not playlist:
        return None
    current_song = playlist[playlist.getposition()]
    current_album = current_song["album"]
    return current_album

def get_album_songs(album):
    songs = xbmc.MusicDatabase().getSongs(filter={"album": album})
    return songs

def average_rating(songs):
    ratings = [song["rating"] for song in songs if song["rating"] > 0]
    if not ratings:
        return 0
    avg_rating = sum(ratings) / len(ratings)
    return avg_rating

def run():
    current_album = get_current_album()
    if not current_album:
        xbmc.executebuiltin("Notification(%s, %s, time=2000)" % ('Not Album', 'true'))
        return
    album_songs = get_album_songs(current_album)
    avg_rating = average_rating(album_songs)
    xbmc.executebuiltin("Notification(%s, %s, time=2000)" % ('Its Album', 'true'))

if __name__ == "__main__":
    run()

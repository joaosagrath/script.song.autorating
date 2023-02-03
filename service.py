import xbmc
import xbmcaddon
import json
import time

class Monitor(xbmc.Monitor):
    def __init__(self):
        self.is_library_song = False
        # Unused variables for now
        self.current_song = ""
        self.playing_song = ""
        pass

    def status_check(self):
        # perform monitor status check
        pass

    def onPlayBackStarted(self):
        self.is_library_song = True

    # When the song ends, either by user action, or when the song is
    # the last in the playlist and the "repeat" function is disabled.
    def onPlayBackStopped(self):
        if self.is_library_song and current_time > 5:
            # If the song has no rating yet, or the rating is "0", this will be its new rating.
            if song_rating == 0:
                new_rating = int(current_time/song_parts)

            # If the song already has a rating, here the current rating value will
            # be added to the new rating calculation, to obtain an average rating.
            elif song_rating != 0:
                new_rating = (song_rating + calculated_rating) / 2

            # Saving the new rating as the song stops.
            xbmc.executebuiltin("Notification(%s, %s)" % ("New Rating", new_rating))
            xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"AudioLibrary.SetSongDetails","params":{"songid": %d, "userrating":%d},"id":1}' % (song_id, new_rating))
            self.is_library_song = False

monitor = Monitor()
player = xbmc.Player()
original_rating = calculated_rating = 0

while not monitor.abortRequested():
    try:
        while True:

            if xbmc.Player().isPlayingAudio():
                # Retrieve the currently playing song
                xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"JSONRPC.Introspect","id":1}')
                result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Player.GetItem","params":{"playerid":0,"properties":["userrating"]},"id":1}')

                # Extract the song ID and rating
                song_details = json.loads(result)["result"]["item"]
                if "id" in song_details:               # Ensure music file exists in Kodi database
                    song_id = song_details["id"]
                    song_rating = song_details["userrating"]

                    # To have all the necessary time calculations.
                    song = player.getMusicInfoTag()
                    song_title = song.getTitle()
                    song_length = song.getDuration()
                    song_parts = int(song_length / 11)
                    current_time = int(player.getTime())

                    # To avoid an error where the calculation would be divided by zero
                    #if current_time == 0:
                    #xbmc.sleep(1000)

                    if current_time > 0:
                        calculated_rating = int(current_time / song_parts)

                    monitor.onPlayBackStarted()

                    # For a future try to idenfy the song change without stopping the player,
                    # when the song ends and the next one in the playlist starts.
                    # if self.current_song == "":
                        # self.current_song = xbmc.getInfoLabel('MusicPlayer.Title')

                    # If the song has no rating yet, or the rating is "0", this will be its new rating.
                    if song_rating == 0:
                        new_rating = int(current_time/song_parts)

                    # If the song already has a rating, here the current rating value will
                    # be added to the new rating calculation, to obtain an average rating.
                    elif song_rating != 0:
                        new_rating = int((song_rating + calculated_rating) / 2)

                    # Notification only to "see"the script working.
                    if calculated_rating > original_rating:
                        xbmc.executebuiltin("Notification(%s, %s, time=2000)" % ("New 0 Rating", new_rating))

                    # Saving the new rating as the song progresses.
                    # ----------------------------------------------------------------------------
                    # HERE IS WHERE IT CAUSES THE "REFRESH" EFFECT, I NEED TO FIND A WAY AROUND IT.
                    # ----------------------------------------------------------------------------
                    #xbmc.log('Autorater is here: ' + str(current_time), xbmc.LOGINFO)
                        xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"AudioLibrary.SetSongDetails","params":{"songid": %d, "userrating":%d},"id":1}' % (song_id, new_rating))
                        original_rating = calculated_rating
                else:
                    monitor.onPlayBackStopped()
                    original_rating = calculated_rating = 0

            monitor.status_check()
            #time.sleep(1) # wait for 60 seconds before checking again

            if monitor.waitForAbort(1): # Sleep/wait for abort for 1 second
                break                   # Abort was requested while waiting. Exit the while loop.

    except Exception as e:
        xbmc.executebuiltin("Notification(%s, %s)" % ("An error occurred: ", e))
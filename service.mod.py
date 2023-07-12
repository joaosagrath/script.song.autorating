import xbmc
import xbmcaddon
import json
import time

addon = xbmcaddon.Addon()
addon_name = addon.getAddonInfo('name')
addon_path = addon.getAddonInfo("path")

class Monitor(xbmc.Monitor):
    def __init__(self):
        self.is_library_song = False
        pass

    def status_check(self):
        # perform monitor status check
        pass

    def onPlayBackStarted(self):
        # Music Library music is set to "True"
        if start_notification == 'true':
            xbmc.executebuiltin("Notification(%s, %s, time=2000)" % (addon_name, '{} Started'.format(current_song)))
        self.is_library_song = True

    def onPlayBackStopped(self, current_song, song_id, new_rating):
        # The song stops, the UserRating of the song is saved, then song ID is set to "0", 
        # and currentMusic to "empty" again. Library music is set to "False"
        if self.is_library_song and current_time > 5:            
            if show_notification == 'true' and addon_running == 'true':
                xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"AudioLibrary.SetSongDetails","params":{"songid": %d, "userrating":%d},"id":1}' % (song_id, new_rating))
            xbmc.executebuiltin("Notification(%s, %s, time=2000)" % (addon_name, ' {} rating is {}'.format(current_song, new_rating)))
            self.is_library_song = False


monitor             = Monitor()
player              = xbmc.Player()
current_song        = ''
song_count          = 0
new_rating          = 0
current_id          = 0 #  Add to match current song tracking
song_id             = 0 #  Add to match original song tracking
song_DBID           = ''

while not monitor.abortRequested():
    try:
        while True:
            
            if xbmc.Player().isPlayingAudio():            
                #  Variables to check if Notifications are ON/OF
                show_notification = 'true' if addon.getSetting("show_notification") == 'true' else 'false'
                start_notification = 'true' if addon.getSetting("start_notification") == 'true' else 'false'
                real_show_notification = 'true' if addon.getSetting("real_show_notification") == 'true' else 'false'
                # Variable to ON/OFF Auto Ratings.
                addon_running = 'true' if addon.getSetting("addon_running") == 'true' else 'false'
                # To check if Kodi is playing a song that is in the library
                song_DBID = xbmc.getInfoLabel('MusicPlayer.DBID') 
                
                if addon_running == 'true' and song_DBID != '':    
                    # Retrieve Song Data from the player
                    song_title      = xbmc.getInfoLabel('MusicPlayer.Title')
                    song_rating     = xbmc.getInfoLabel('MusicPlayer.UserRating')
                    song_length     = int(xbmc.Player().getTotalTime())
                    current_time    = int(player.getTime())
                    song_parts      = int(song_length / 11)
                    song_time_left  = (song_length - current_time)  
                    
                    # To to ensure UserRating is at least "0"
                    if song_rating == '':
                        song_rating = 0    
                    else:
                        song_rating = int(song_rating)
                    
                    # To avoid error "divided by zero"
                    if current_time > 0:
                        calculated_rating = int(current_time / song_parts)                
                        if song_rating == 0 or song_rating == '':
                            new_rating = int(current_time/song_parts)
                            if new_rating > 10:
                                new_rating = 10
                        if song_rating > 0:
                            new_rating = int((song_rating + calculated_rating) / 2)
                            if new_rating > 10:
                                new_rating = 10
                                
                    if current_song == '':
                        monitor.onPlayBackStarted()
                        
                        # Start the JSONRPC
                        xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"JSONRPC.Introspect","id":1}')
                        
                        # Retrieve Song Data as player start:
                        song = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Player.GetItem","params":{"playerid":0,"properties":["userrating"]},"id":1}')
                        song_details = json.loads(song)["result"]["item"]
                        song_id = song_details["id"]
                        #  Get database Id of new song                        
                        current_id = xbmc.getInfoLabel('MusicPlayer.DBID')
                        
                        # Retrieve Album ID from song as player start:                        
                        result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Player.GetItem","params":{"playerid":0,"properties":["albumid"]},"id":1}')
                        album_details = json.loads(result)["result"]["item"]
                        album_id = album_details["albumid"]
                        
                        # Retrieve album details including the number of songs
                        result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"AudioLibrary.GetSongs","params":{"filter":{"albumid":' + str(album_id) + '}},"id":2}')
                        album_info = json.loads(result)["result"]["songs"]

                        # Count the number of songs in the album
                        song_count = len(album_info)
                        
                        # Retrieve user ratings for each song in the album
                        total_rating = 0
                        for song in album_info:
                            song_id = song["songid"]
                            result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"AudioLibrary.GetSongDetails","params":{"songid":' + str(song_id) + ',"properties":["userrating"]},"id":3}')
                            song_details = json.loads(result)["result"]["songdetails"]
                            user_rating = song_details["userrating"]
                            total_rating += user_rating

                        # Calculate the average rating
                        song_count = len(album_info)
                        average_rating = total_rating / song_count
                        

                        # Set current song from player:
                        current_song = xbmc.getInfoLabel('MusicPlayer.Title')  

                    # If song has changed, first will save current data in previous song,
                    # Then will retrieve data for the new song:
                    if current_song != song_title:
                        
                        # Save Song Data in previous song:
                        xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"AudioLibrary.SetSongDetails","params":{"songid": %d, "userrating":%d},"id":1}' % (song_id, new_rating))
                        if show_notification == 'true':
                            xbmc.executebuiltin("Notification(%s, %s, time=2000)" % (addon_name, ' {} rating is {}'.format(current_song, new_rating)))
                        
                        # Retrieve Song Data from new song:
                        xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"JSONRPC.Introspect","id":1}')
                        result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Player.GetItem","params":{"playerid":0,"properties":["userrating"]},"id":1}')
                        song_details = json.loads(result)["result"]["item"]
                        song_id = song_details["id"]
                        
                        # Set new current song from player:
                        current_song = xbmc.getInfoLabel('MusicPlayer.Title')
                    
                    # Show Real Time Rating
                    if real_show_notification == 'true':
                        xbmc.executebuiltin("Notification(%s, %s, time=2000)" % (addon_name, ' {} rating is {}'.format(current_song, new_rating)))
                        # xbmc.executebuiltin("Notification(%s, %s, time=2000)" % (addon_name, 'Song ID: {}'.format(song_id)))
                        # xbmc.executebuiltin("Notification(%s, %s, time=2000)" % (addon_name, 'Album ID: {}'.format(album_id)))
                        # xbmc.executebuiltin("Notification(%s, %s, time=2000)" % (addon_name, 'Songs: {}'.format(song_count)))
                        # xbmc.executebuiltin("Notification(%s, %s, time=2000)" % (addon_name, 'Total Rating: {}'.format(average_rating)))
                        
            else:
                # For use when the user stops playback.
                monitor.onPlayBackStopped(current_song, song_id, new_rating)
                current_song = ''
                if song_DBID != '':
                    current_id = song_id = 0
                new_rating = 0
                
            monitor.status_check()

            if monitor.waitForAbort(1):
                break
    except Exception as e:
        xbmc.executebuiltin("Notification(%s, %s)" % ("An error occurred: ", e))
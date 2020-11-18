#! Basic necessities to get the CLI running
from spotdl.search.spotifyClient import initialize

from spotdl.cli.displayManager import DisplayManager
from spotdl.download.downloadManager import DownloadManager

from spotdl.cli.argumentHandler import get_cli_options

from spotdl.search.utils import get_playlist_tracks, get_album_tracks, search_for_song
from spotdl.search.songObj import SongObj


#! to avoid packaging errors
from multiprocessing import freeze_support




#! Usage is simple - call 'python __main__.py <links, search terms, tracking files seperated by spaces>
#! Eg.
#!      python __main__.py https://open.spotify.com/playlist/37i9dQZF1DWXhcuQw7KIeM?si=xubKHEBESM27RqGkqoXzgQ 'old gods of asgard Control' https://open.spotify.com/album/2YMWspDGtbDgYULXvVQFM6?si=gF5dOQm8QUSo-NdZVsFjAQ https://open.spotify.com/track/08mG3Y1vljYA6bvDt4Wqkj?si=SxezdxmlTx-CaVoucHmrUA
#!
#! Well, yeah its a pretty long example but, in theory, it should work like a charm. 
#!
#! A '.spotdlTrackingFile' is automatically  created with the name of the first song in the playlist/album or
#! the name of the song supplied. We don't really re re re-query YTM and Spotify as all relevant details are
#! stored to disk.
#!
#! Files are cleaned up on download failure.
#!
#! All songs are normalized to standard base volume. the soft ones are made louder, the loud ones, softer.
#!
#! The progress bar is synched across multiple-processes (4 processes as of now), getting the progress bar to
#! synch was an absolute pain, each process knows how much 'it' progressed, but the display has to be for the
#! overall progress so, yeah... that took time.
#!
#! spotdl will show you its true speed on longer download's - so make sure you try downloading a playlist.
#!
#! still yet to try and package this but, in theory, there should be no errors.
#!
#!                                                          - cheerio! (Michael)
#!
#! P.S. Tell me what you think. Up to your expectations?

#! Script Help
help_notice = '''
To download a song run,
    spotdl $trackUrl
    eg. spotdl https://open.spotify.com/track/08mG3Y1vljYA6bvDt4Wqkj?si=SxezdxmlTx-CaVoucHmrUA

To download a album run,
    spotdl $albumUrl
    eg. spotdl https://open.spotify.com/album/2YMWspDGtbDgYULXvVQFM6?si=gF5dOQm8QUSo-NdZVsFjAQ

To download a playlist run,
    spotdl $playlistUrl
    eg. spotdl https://open.spotify.com/playlist/37i9dQZF1DWXhcuQw7KIeM?si=xubKHEBESM27RqGkqoXzgQ

To search for and download a song (not very accurate) run,
    spotdl $songQuery
    eg. spotdl 'The HU - Sugaan Essenna'

To resume a failed/incomplete download run,
    spotdl $pathToTrackingFile
    eg. spotdl 'Sugaan Essenna.spotdlTrackingFile'

    Note, '.spotDlTrackingFiles' are automatically created during download start, they are deleted on
    download completion

You can chain up download tasks by seperating them with spaces:
    spotdl $songQuery1 $albumUrl $songQuery2 ... (order does not matter)
    eg. spotdl 'The Hu - Sugaan Essenna' https://open.spotify.com/playlist/37i9dQZF1DWXhcuQw7KIeM?si=xubKHEBESM27RqGkqoXzgQ ...

Spotdl downloads up to 4 songs in parallel - try to download albums and playlists instead of
tracks for more speed
'''

def console_entry_point():
    '''
    This is where all the console processing magic happens.
    Its super simple, rudimentary even but, it's dead simple & it works.
    '''

    # Initialize the Display Mannager. 
    with DisplayManager() as disp:

        # Initialize the Download Manager. 
        with DownloadManager() as downloader:

            cli_options = get_cli_options()

            if cli_options.quiet:
                disp.quiet = True

            if cli_options.spotify_client_id:
                if cli_options.spotify_client_secret:
                    disp.print('Using id:', cli_options.spotify_client_id)
                    disp.print('Using secret:', cli_options.spotify_client_secret)
                    initialize(
                        clientId=cli_options.spotify_client_id,
                        clientSecret=cli_options.spotify_client_secret
                    )
                else: 
                    disp.print('Spotify Secret has to be supplied with ID')
            else:
                initialize(
                    clientId='4fe3fecfe5334023a1472516cc99d805',
                    clientSecret='0f02b7c483c04257984695007a4a8d5c'
                )

            if cli_options.url:
                request = cli_options.url
                disp.print('gonna get song by url: ' + request)
                if 'open.spotify.com' in request and 'track' in request:
                    disp.print('Fetching Song...')
                    songObj = SongObj.from_url(request)

                    if songObj.get_youtube_link() != None:
                        downloader.download_single_song_async(songObj, callback = disp.monitor_process)
                    else:
                        disp.print('Skipping %s (%s) as no match could be found on youtube' % (
                            songObj.get_song_name(), request
                        ))
                
                elif 'open.spotify.com' in request and 'album' in request:
                    disp.print('Fetching Album...')
                    songObjList = get_album_tracks(request)
                    downloader.download_multiple_songs_async(songObjList, callback = disp.monitor_process)
                
                elif 'open.spotify.com' in request and 'playlist' in request:
                    disp.print('Fetching Playlist...')
                    songObjList = get_playlist_tracks(request)

                    downloader.download_multiple_songs_async(songObjList, callback = disp.monitor_process)


            elif cli_options.file:
                disp.print('File')
                downloader.resume_download_from_tracking_file_async(cli_options.file, callback = disp.monitor_process)

            elif cli_options.query:
                for request in cli_options.query:
                    if 'open.spotify.com' in request and 'track' in request:
                        disp.print('Fetching Song...')
                        songObj = SongObj.from_url(request)

                        if songObj.get_youtube_link() != None:
                            downloader.download_single_song_async(songObj, callback = disp.monitor_process)
                        else:
                            disp.print('Skipping %s (%s) as no match could be found on youtube' % (
                                songObj.get_song_name(), request
                            ))
                    
                    elif 'open.spotify.com' in request and 'album' in request:
                        disp.print('Fetching Album...')
                        songObjList = get_album_tracks(request)
                        downloader.download_multiple_songs_async(songObjList, callback = disp.monitor_process)
                    
                    elif 'open.spotify.com' in request and 'playlist' in request:
                        disp.print('Fetching Playlist...')
                        songObjList = get_playlist_tracks(request)

                        downloader.download_multiple_songs_async(songObjList, callback = disp.monitor_process)
                    
                    elif request.endswith('.spotdlTrackingFile'):
                        disp.print('Preparing to resume download...')
                        downloader.resume_download_from_tracking_file_async(request, callback = disp.monitor_process)
                    
                    else:
                        disp.print('Searching for song "%s"...' % request)
                        try:
                            songObj = search_for_song(request)
                            disp.print('Closest Match: "%s"' % songObj.get_display_name())
                            downloader.download_single_song_async(songObj, callback = disp.monitor_process)

                        except Exception as e:
                            disp.print('No song named "%s" could be found on spotify' % request)


if __name__ == '__main__':
    freeze_support()

    console_entry_point()





   
                


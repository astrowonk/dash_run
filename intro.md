### Additional  Details

I'm not sure about other workout/fitness trackers, but the Apple Watch reports distance and pace based on the pedometer, not the GPS. While the Apple Watch [should calibrate itself using the GPS](https://support.apple.com/en-us/HT204516), I have seen about a 3% discrepancy between the Apple Fitness and the GPS for my runs.

The output of this appear appears to be very similar to the *Correct Distance* feature for activities at [Strava](https://strava.com), though Strava doesn't appear to display or record the error/discrepancy or characterize it in terms of a percentage. Strava also computes a *moving time* which can trim a few seconds off the total time.

*Privacy Policy*: By default, this web application stores no information of any kind. The [Dash upload component](https://dash.plotly.com/dash-core-components/upload) encodes the file as a base64 string which is then passed to the code that computes the pace and distance in memory with no file caching. The source code for this site [is open source on github](https://github.com/astrowonk/dash_run).

The __opt-in store summmary data checkbox__ will store a [sha 256 hash of the file](https://docs.python.org/3/library/hashlib.html), the submitted distance, the computed distance, and user-submitted device type. As I am a data scientist, I am curious about the statistics on in-device pace and distance vs the GPS data. If I collect enough data, I will add some graphs/histograms.

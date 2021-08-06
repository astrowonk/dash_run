## GPX Based Workout Summary

This app calculates pace and distance of a workout from a GPX file using the time and GPS latitude/longitude. It is powered by [gpxrun](https://github.com/astrowonk/gpxrun) and [gpxcsv](https://pypi.org/project/gpxcsv/) and built on the [Dash](https://dash.plotly.com) framework.

I'm not sure about other workout/fitness trackers, but the Apple Watch reports distance and pace based on the pedometer, not the GPS. While the Apple Watch [should calibrate itself using the GPS](https://support.apple.com/en-us/HT204516), I have seen about a 3% error discrepancy between the Apple Fitness and the GPS, where the Watch says I have run about 3% longer than I have. (This corresponds to similar increase in pace.)

Submitting a GPX file will compute the GPS based pace and distance. You may optionally submit the distance in miles that is reported by Apple Fitness or whatever device you have. This will be used to compute the GPS based error of your fitness tracker/device.

The output of this appear appears to be similar/identical to the "Correct Distance" feature for activities at [Strava](https://strava.com), though Strava doesn't appear to display or record the error/discrepancy. Strava also computes a "moving time" which can trim a few seconds off the total time.

**Privacy**: This web application currently stores no information of any kind. The [Dash upload component](https://dash.plotly.com/dash-core-components/upload) encodes the file as a base64 string which is then passed to the code that computes the pace and distance in memory with no file caching. Nothing persists on the server.

In a future version, there will be an opt-in to store store a hash of the file, the submitted distance, the computed distance, and the percent error as I am curious on overall statistics of GPS vs pedometer accuracy.

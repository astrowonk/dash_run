## GPX Based Workout Summary

This app calculates pace and distance of a workout from a GPX file. It is powered by [gpxrun](https://github.com/astrowonk/gpxrun) and [gpxcsv](https://pypi.org/project/gpxcsv/).

I'm not sure about other workout/fitness trackers, but the Apple Watch reports distance and pace based on the pedometer, not the GPS. While the Apple Watch should calibrate itself using the GPS, I continue to see about 3% error in my runs, where the Watch says I have run 3% longer than I have. This corresponds to similar increase in pace.

Submitting a GPX file will compute the GPS based pace and distance. You may optionally submit the distance in miles that is reported by Apple Fitness or whatever device you have. This will be used to compute the GPS based error of your fitness tracker/device.

**Privacy**: This web application currently stores no information of any kind. The submitted file is encode as a base64 string which is then passed to the GpxRun class which computes the pace and distance in memory with no file caching. Nothing persists on the server.

In a future state, there will be an opt-in to store store a hash of the file, the submitted distance,the computed distance, and the error as I am curious on overall statistics of GPS vs pedometer accuracy.

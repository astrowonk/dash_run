### Additional  Details

The output of this appear appears to be very similar to the *Correct Distance* feature for activities at [Strava](https://strava.com), though Strava doesn't appear to display or record the error/discrepancy or characterize it in terms of a percentage. Strava also computes a __moving time__ which can trim a few seconds off the total time.

*Privacy*: This web application currently stores no information of any kind. The [Dash upload component](https://dash.plotly.com/dash-core-components/upload) encodes the file as a base64 string which is then passed to the code that computes the pace and distance in memory with no file caching. Nothing persists on the server.

In a future version, there will be an opt-in to store store a hash of the file, the submitted distance, the computed distance, and the percent error as I am curious on overall statistics of GPS vs pedometer accuracy.

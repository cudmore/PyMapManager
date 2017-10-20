### Python code to run a Flask server to serve Map Manager files.

### See [mmio][3] for a python wrapper to streamline loading map Manager maps from the server

### Example server is running at [http://cudmore.duckdns.org][2] on port 5010.

Username is 'public'
Map is 'rr30a'

#### Get Map Header

    [http://cudmore.duckdns.org:5010/public/rr30a/header][1]

#### Get 3D object map

    http://cudmore.duckdns.org:5010/public/rr30a/objmap

#### Get 3D segment map

    http://cudmore.duckdns.org:5010/public/rr30a/segmap


#### Get timepoint 1 stack db

    http://cudmore.duckdns.org:5010/public/rr30a/1/stackdb

#### Get timepoint 1, intensity for channel 2

    http://cudmore.duckdns.org:5010/public/rr30a/1/int/2

#### Get timepoint 1 segment tracing

    http://cudmore.duckdns.org:5010/public/rr30a/1/line

#### Get timepoint 1 image, slice 10, channel 2 (for now, this downloads the whole stack)

    http://cudmore.duckdns.org:5010/public/rr30a/1/image/10/2

#### get a zip file of the map (now raw data included)

    http://cudmore.duckdns.org:5010/public/rr30a/zip         

[1]: http://cudmore.duckdns.org:5010/public/rr30a/header
[2]: http://cudmore.duckdns.org
[3]: https://github.com/cudmore/PyMapManager/tree/master/PyMapManager/mmio
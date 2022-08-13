# Webcomic Formatter 

# Goal
Make a commandline tool that will take a fullsize image and scale it to fit serialization for various web platforms. Prepare a package of data that can then be manually uploaded to each webcomic site for publication including authored text, images, thumbnail, etc. 

# Proposed Features
- [x] Be able to provide config data for each webcomic site format (config file below)
- [x] copy and resize the full comic image into the correct size for each format
- [x] Cut up the comic into images to fit. First resize to the right width and then cut the image up based on the height into pages and output those png files.
- [x] place all of the cut up images into their respective folders separate from the original
- [x] cut the thumbnails for each format
- [ ] png compress all images
- [x] give all of the sequential image proper filenames
- [x] recut thumbnail based on the original thumbnail
- [x] be able to detect which image is the thumbnail -- in this case look for the "-thumb" part of the file name.
 * What if there is no thumbnail? Do we try and generate one based on the image? How do we do that to get some satisfying thumbnails. Maybe we need an optional feature for that.
- [x] generate a template markdown file for posting on tmc that includes all of the data in the header ready to go
- [x] be able to write post as a text file that gets copy and added to each folder. 
- [x] If folders already exist for the specified outputs then don't overwrite them. Just leave them be and put the new data in there. User is responsible for clearing the data.

# Config File Format
json:
```json
{
    "formats": [
        {
            "output-suffix": "site",
            "max-width": 2048,
            "max-height": 3641,
            "thumb-width": 512,
            "thumb-height": 512,
            "process-as-md": true,
            "will-process-flag": true,
            "include-soc-media-flag" : true
        },
        {
            "output-suffix": "tapas",
            "max-width": 940,
            "max-height": 1504,
            "thumb-width": 300,
            "thumb-height": 300,
            "process-as-md": false,
            "will-process-flag": true,
            "include-soc-media-flag" : false
        },
        {
            "output-suffix": "webtoon",
            "max-width": 800,
            "max-height": 1280,
            "thumb-width": 160,
            "thumb-height": 151,
            "process-as-md": false,
            "will-process-flag": false,
            "include-soc-media-flag" : false
        }
    ]
}
```

# For Testing
Command line: 
```shell
python .\webcomic-formatter.py <fullpath>
```
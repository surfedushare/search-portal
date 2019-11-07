media-to-local:
	rsync -zrthv --progress $(remote):/volumes/surf/media .

media-to-remote:
	rsync -zrthv --progress media $(remote):/volumes/surf/

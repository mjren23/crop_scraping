# crop_scraping

Project with the goal of scraping information on cropping patterns from the [Agriculture Census of India website](https://agcensus.dacnet.nic.in/TalukCharacteristics.aspx).

loop.py is the main program that loops through all desired years and crops. It grabs table data and saves it in a directory called saved_tables (not included in git respository), then uploads it to a connected Dropbox folder. It also creates log files detailing the run process. loop.py expects a .env file in the root directory that contains a Dropbox developer app key, secret, and refresh token to be able to upload files to Dropbox. 

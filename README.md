# LAFD_Activity_and_Weather_Data

#### Background
DSCI 510: Principles of Programming for Data Science<br />
USC Viterbi School of Engineering Data Science Program<br />
Final Project

#### Sources / Websites Scraped
1. [LA’s Weather Source - laalmanac.com](http://www.laalmanac.com/weather/we04a.php)
2. [LAFD Alert Page Source - lafd.org](https://www.lafd.org/alerts?incident_type=&neighborhood=&bureau=&page=0)
3. [LA County’s Fire Department Public Information Office Twitter Account - @LACoFDPIO](https://x.com/lacofdpio?lang=en)

#### General Note
* You can run the code by running the scraper.py command on the terminal.
* All of my code used to scrape all 3 websites are in the same scraper.py file.
* My included database file, lafdresponses.db, is used to run with --static command.
* You can read about the results in the paper 510_FinalReport_MelissaReyes.pdf

#### Packages Required
import requests<br />
from bs4 import BeautifulSoup<br />
import sys<br />
import sqlite3<br />
import matplotlib.pyplot as plt<br />
import numpy as np<br />

#### Files Required:
* scraper.py
* lafdresponses.db

#### How to run the code:
1. Inside the scraper.py file I have a main(argv) function that will scrape all the data sources, create a database, and perform the analysis if you run scraper.py as "python3 scraper.py" with no arguments.
	- Note: There will be print statements that will print out as each source is scraped. The run time is less than 5 minutes overall. The longest part to scrape is the LAFD alert source that you'll know is being scraped when you see the print line "Scraping alerts". After it scrapes each source, information about each source will print that includes the length and sample rows. When it analyzes the data, 8 graphs will pop up. The code will finish running when you exit out of these graphs. The analysis will end with information on the combined database include the database length and sample rows. The graphs are also saved in the same folder all the files are in.

2. If you run it with --static then the command line should be "python3 scraper.py --static lafdresponse.db" and analyze the given database.
	- Note: When it analyzes the data, 8 graphs will pop up. The code will finish running when you exit out of these graphs. The analysis will end with information on the combined database include the database length and sample rows. The graphs are also saved in the same folder all the files are in.


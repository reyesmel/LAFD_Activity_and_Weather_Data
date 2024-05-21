import requests
from bs4 import BeautifulSoup
import sys
import sqlite3
import matplotlib.pyplot as plt
import numpy as np


def get_lafd(end_date):
    base_url = 'https://www.lafd.org/alerts?incident_type=&neighborhood=&bureau=&page='
    count = 0
    alert_list = []
    update_list = []
    knockdown_list = []
    misc_list = []
    scrape = True
    while scrape:
        url = base_url + str(count)
        content = requests.get(url)
        soup = BeautifulSoup(content.content, 'html.parser')

        a_tags = soup.find_all('h2', {"class": "alert-node-title"})
        links_list = []

        for tag in a_tags:
            link = tag.get_text().strip()
            temp = link.split()
            title = temp[0] + " " + temp[1]
            if '/' not in temp[2]:
                title += " " + temp[2]
            title += " " + temp[-1]
            date = temp[-2]

            if date.startswith("04"):
                if "Update" in str(link) and end_date not in link:
                    update_list.append((date, title, "update"))
                if "Knockdown" in str(link) and end_date not in link:
                    knockdown_list.append((date, title, "knockdown"))
                elif "Fire" in str(link) and end_date not in link:
                    alert_list.append((date, title, "fire"))
                elif ("Fire" and "Update") not in str(link) and end_date not in link:
                    misc_list.append((date, title, "misc"))
            if end_date in link:
                scrape = False
                break

        count += 1
    result = []
    result.extend(alert_list)
    result.extend(update_list)
    result.extend(knockdown_list)
    result.extend(misc_list)

    return result  # alert_list, update_list, knockdown_list, misc_list


def static_data(filename):
    dataset = open(filename, 'r')
    lines = dataset.readlines()
    for i in range(len(lines)):
        lines[i] = lines[i].split(",")
    return lines


def get_weather():
    url = 'https://weather.com/weather/monthly/l/a4bf563aa6c1d3b3daffff43f51e3d7f765f43968cddc0475b9f340601b8cc26'
    content = requests.get(url)
    soup = BeautifulSoup(content.content, 'html.parser')

    calendar_tag = soup.find('div', {'class': 'Calendar--gridWrapper--3kkmJ'})
    output = []
    for button_tag in calendar_tag.find_all('button', {'data-testid': 'ctaButton'}):
        date = button_tag['data-id'].split('-')[1] + "/2021"
        if date.startswith('4'):
            for svgtag in button_tag.find_all('svg', {"set": "weather"}):
                weather_desc = svgtag.text
            for spantag in button_tag.find_all('span', {"data-testid": "TemperatureValue"}):
                temp = spantag.text[:-1]
                if temp == "-":
                    cur_temp = soup.find('span', {'class': 'styles--temperature--1Jdtf'})
                    temp = cur_temp.text[:-1]
                break
            output.append((date, temp, weather_desc))
    return output


def get_tweets():
    user_id = 919373695
    params = {"tweet.fields": "created_at", "max_results": 100, "start_time": "2021-04-01T00:00:01Z",
              "end_time": "2021-04-30T00:00:01Z"}
    url = "https://api.twitter.com/2/users/{}/tweets".format(user_id)
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAG9yOwEAAAAAkpq0Pox24%2BACA%2BrxUVUub1VgdyU%3DBoDws0i0YaqCWsmnspQYfbDLhu5zHcvvbXk7mM3yBmECLGbYoI"
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    response = requests.request("GET", url, headers=headers, params=params)
    data = response.json()["data"]
    result = []
    for item in data:
        temp = item["created_at"].split("T")
        date = format_date(temp[0])
        tweet = item["text"].split("|")[0]
        if "fire" in tweet.lower() or "update" in tweet.lower() or "knockdown" in tweet.lower() or "structure" in tweet.lower():
            result.append((date, tweet))

    return result


def format_date(date):
    dates = date.split("-")
    formatted_date = dates[1] + "/" + dates[2] + "/" + dates[0]
    return formatted_date


def create_database(data_dict):
    conn = sqlite3.connect('lafdresponses.db')
    c = conn.cursor()
    c.execute("""DROP TABLE IF EXISTS combined""")
    query = """CREATE TABLE combined (
                                              date text,
                                              temperature integer,
                                              weather_desc text,
                                              knockdown integer,
                                              updates integer,
                                              fire integer,
                                              misc integer,
                                              tweets integer
                                          )"""
    c.execute(query)
    for (date, values_dict) in data_dict.items():
        c.execute("""INSERT INTO combined VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (
            date, values_dict["temp"], values_dict["temp_desc"], values_dict["update"], values_dict["knockdown"],
            values_dict["fire"], values_dict["misc"], values_dict["tweet"]))
        conn.commit()
    conn.close()


def analysis(db_rows):
    labels = []  # date,temp,desc
    dates = []
    temps = []
    knockdowns = []
    updates = []
    fires = []
    miscs = []
    tweets = []

    for (date, temp, weather_desc, knockdown, update, fire, misc, tweet) in db_rows:
        dates.append(date)
        label = date + ", " + str(temp) + ", " + str(weather_desc)
        labels.append(label)
        temps.append(temp)
        knockdowns.append(knockdown)
        updates.append(update)
        fires.append(fire)
        miscs.append(misc)
        tweets.append(tweet)

    x = np.arange(len(labels))  # the label locations
    margin = 0.09
    width = (1. - 2. * margin) / 5
    fig, ax = plt.subplots()

    rects1 = ax.bar(x - 2 * width, fires, width, label='Fires', align="center")
    rects2 = ax.bar(x - width, updates, width, label='Updates', align="center")
    rects3 = ax.bar(x, knockdowns, width, label='Knockdowns', align="center")
    rects4 = ax.bar(x + width, miscs, width, label='Misc', align="center")
    rects5 = ax.bar(x + 2 * width, tweets, width, label='Tweets', align="center")
    ax.set_ylabel('Frequency')
    ax.set_title('LAFD Alerts by Date')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.legend()

    fig.tight_layout()
    plt.savefig("combined_with_weather.png")
    plt.legend()

    plot2 = plt.figure("Combined w/o Weather")
    plt.plot(dates, fires, label="Fires")
    plt.plot(dates, knockdowns, label="Knockdowns")
    plt.plot(dates, updates, label="Updates")
    plt.plot(dates, miscs, label="Misc")
    plt.plot(dates, tweets, label="Tweets")
    plt.xticks(rotation=45, ha='right')
    plt.title('LAFD Alerts by Date')
    plt.tight_layout()
    plt.savefig("combined_without_weather.png")

    plot3 = plt.figure('Fires')
    plt.plot(dates, fires, label="Fires")
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.title('LAFD Fires by Date')
    plt.tight_layout()
    plt.savefig("fires.png")

    plot4 = plt.figure("Knockdowns")
    plt.plot(dates, knockdowns, label="Knockdowns")
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.title('LAFD Knockdowns by Date')
    plt.tight_layout()
    plt.savefig("knockdowns.png")

    plot5 = plt.figure("Updates")
    plt.plot(dates, updates, label="Updates")
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.title('LAFD Updates by Date')
    plt.tight_layout()
    plt.savefig("updates.png")

    plot6 = plt.figure("Misc")
    plt.plot(dates, miscs, label="Misc")
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.title('LAFD Misc by Date')
    plt.tight_layout()
    plt.savefig("misc.png")

    plot6 = plt.figure("Tweets")
    plt.plot(dates, tweets, label="Tweets")
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.title('LAFD Tweets by Date')
    plt.tight_layout()
    plt.savefig("tweets.png")

    plot7 = plt.figure("Temperatures")
    plt.plot(dates, temps, label="Temperatures")
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.title('LA County Temperatures by Date')
    plt.tight_layout()
    plt.savefig("temperatures.png")

    plt.show()


def get_database(path):
    print(path)
    conn = sqlite3.connect(str(path))
    c = conn.cursor()
    output = []
    query = """SELECT * FROM combined"""
    for row in c.execute(query):
        output.append(row)

    conn.close()
    return output


def format_data(alert_data, weather_data, tweet_data):
    data_dict = {}

    for (date, temp, description) in weather_data:
        if len(date.split('/')[0]) == 1:
            date = "0" + date
            if len(date.split('/')[1]) == 1:
                date = date.split('/')[0] + "/0" + date.split('/')[1] + "/" + date.split('/')[2]
            # print(date)
        if date not in data_dict:
            data_dict[date] = {"fire": 0, "update": 0, "knockdown": 0, "misc": 0, "tweet": 0, "temp": 0,
                               "temp_desc": ""}

        data_dict[date]["temp"] = int(temp)
        data_dict[date]["temp_desc"] = description

    for (date, description, type) in alert_data:
        data_dict[date][type] += 1

    for (date, tweet) in tweet_data:
        data_dict[date]["tweet"] += 1

    return data_dict


'''
CREATE TABLE "sqlb_temp_table_2" (
	"date"	TEXT,
	"temperature"	REAL,
	"weather_description"	TEXT,
	"update" INTEGER, "knockdown"	INTEGER, "fire"	INTEGER, "misc"	TEXT, "tweets"	TEXT)
'''


def main(argv):
    dates = []

    if len(argv) == 0:  # Run all datasets
        alert_result = get_lafd('3/31/2021')
        print("Dataset size:", len(alert_result), "Row Length: 2", "Sample Rows:", alert_result[:3])
        weather_data = get_weather()
        print("Dataset size:", len(weather_data), "Row length: 3", "Sample Rows:", weather_data[:3])
        #
        tweet_result = get_tweets()
        print("Dataset size:", len(tweet_result), "Row length: 2", "Sample Rows:", tweet_result[:3])
        combined_data = format_data(alert_result, weather_data, tweet_result)
        create_database(combined_data)
    else:
        if argv[0] == '--scrape':  # Only return the first 5 datasets
            print(get_lafd('4/10/2021')[:5])
            print(get_weather()[:5])
            print(get_tweets()[:5])
        elif argv[0] == '--static':
            path = argv[1]
            result = get_database(path)
            analysis(result)
            print("Dataset size:", len(result), "Row Length:", len(result[0]), "Sample Rows:", result[:4])


if __name__ == "__main__":
    main(sys.argv[1:])

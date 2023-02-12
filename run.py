import os

from sites import SITES
import json
from bs4 import BeautifulSoup
import re
import requests

import matplotlib.pyplot as plt
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
german_stop_words = stopwords.words('german')

dict_href_links = {}


def getdata(url):
    r = requests.get(url)
    return r.text


def get_links(website_link, website):
    html_data = getdata(website_link)
    soup = BeautifulSoup(html_data, "html.parser")
    list_links = []
    for link in soup.find_all("a", href=True):

        # Append to list if new link contains original link
        if str(link["href"]).startswith((str(website_link))):
            list_links.append(link["href"])

        if not str(link["href"]).startswith("https://") and not "#" in str(link["href"])\
                and not str(link["href"]).startswith("mailto") and not str(link["href"]).startswith("javascript")\
                and not str(link["href"]).startswith("skipNavigation") and not str(link["href"])=="./"\
                and not str(link["href"]).startswith("http://") and not str(link["href"]).startswith("webcal://"):
            if link["href"] not in dict_href_links:
                print(link["href"])
                dict_href_links[link["href"]] = None
                link_with_www = website + link["href"]
                print("adjusted link =", link_with_www)
                list_links.append(link_with_www)

        # Include all href that do not start with website link but with "/"
        if str(link["href"]).startswith("/") and not str(link["href"]).startswith("/#"):
            if link["href"] not in dict_href_links:
                print(link["href"])
                dict_href_links[link["href"]] = None
                link_with_www = website_link + link["href"][1:]
                print("adjusted link =", link_with_www)
                list_links.append(link_with_www)

    # Convert list of links to dictionary and define keys as the links and the values as "Not-checked"
    dict_links = dict.fromkeys(list_links, "Not-checked")
    return dict_links


def get_subpage_links(l, website):

    for link in l:
        # If not crawled through this page start crawling and get links
        if l[link] == "Not-checked":
            dict_links_subpages = get_links(link, website)
            # Change the dictionary value of the link to "Checked"
            l[link] = "Checked"
        else:
            # Create an empty dictionary in case every link is checked
            dict_links_subpages = {}
        # Add new dictionary to old dictionary
        l = {**dict_links_subpages, **l}

        print(l)

    return l


def find_subpages():
    for name, website in SITES.items():

        dict_links = {website: "Not-checked"}

        counter, counter2 = None, 0
        while counter != 0:
            counter2 += 1
            dict_links2 = get_subpage_links(dict_links, website)

            # Count number of non-values and set counter to 0 if there are no values within the dictionary equal to the string "Not-checked"
            # https://stackoverflow.com/questions/48371856/count-the-number-of-occurrences-of-a-certain-value-in-a-dictionary-in-python
            counter = sum(value == "Not-checked" for value in dict_links2.values())

            dict_links = dict_links2
            # Save list in json file
            a_file = open(f"subpages/{name}.json", "w")
            json.dump(list(dict_links.keys()), a_file)
            a_file.close()


def create_wordcloud(text, name):

    tokens = text.split()
    text = " ".join([word for word in tokens if word not in german_stop_words])

    wordcloud = WordCloud(
        background_color='white',
        width=512,
        height=384
    ).generate(text)
    plt.imshow(wordcloud)  # image show
    plt.axis('off')  # to off the axis of x and y
    plt.savefig(f'wordclouds/{name}-World_Cloud.png')


def count_words():

    # Load json file
    files = os.listdir("subpages")
    for file in files:

        all_text = ""
        wirtschaft_count = 0
        digital_count = 0
        word_count = 0
        with open(f"subpages/{file}") as json_file:
            data = json.load(json_file)

        for page in data:

            if "impressum" in page or "datenschutz" in page:
                continue

            site_content = requests.get(page).content

            if "html" in site_content.decode("iso-8859-1"):

                soup = BeautifulSoup(site_content, "html.parser")
                text = soup.getText(separator=u" ").lower()

                matches_wirtschaft = re.findall("wirtschaft", text)
                matches_digital = re.findall("digital", text)

                if len(matches_wirtschaft) > 0:
                    print(page)
                    print(f"Anzahl Wirtschaft: {len(matches_wirtschaft)}")

                if len(matches_digital) > 0:
                    print(page)
                    print(f"Anzahl digital: {len(matches_digital)}")

                wirtschaft_count += len(matches_wirtschaft)
                digital_count += len(matches_digital)
                word_count += len(text.split())
                all_text += text

        create_wordcloud(all_text, file[:-5])

        print(
            f"{file.split('.')[0]} hat {wirtschaft_count} Erwähnungen 'Wirtschaft', {digital_count} Erwähnungen 'digital' und {word_count} Wörter auf der Website")


if __name__ == "__main__":

    # find_subpages()

    count_words()
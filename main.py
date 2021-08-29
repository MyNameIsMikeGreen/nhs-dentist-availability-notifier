import logging
import os

import requests
from bs4 import BeautifulSoup

MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
RECIPIENT = os.getenv("RECIPIENT")
DENTAL_CHOICES_SEARCH_URL = os.getenv("DENTAL_CHOICES_SEARCH_URL")
MAX_DISTANCE_MILES = float(os.getenv("MAX_DISTANCE_MILES", "20"))


class RequestFailureError(Exception):
    pass


class Dentist(object):
    def __init__(self, name, address, distance_miles, last_updated):
        self.name = name
        self.address = address
        self.distance_miles = distance_miles
        self.last_updated = last_updated

    def __str__(self):
        return f"{self.name}\n{self.address}\n{self.distance_miles} Miles Away\n{self.last_updated}"


def transform_listing_item_to_dentist(listing_item):
    name = listing_item.find("h2").text.strip()
    listing_detail = listing_item.find("div", attrs={"class": "listing-details"})
    address = listing_detail.find("p", attrs={"class": "listing-address"}).text.strip()
    distance_text = listing_detail.find("p", attrs={"class": "listing-distance"}).text.strip()
    distance = float(distance_text.lstrip().split(" ")[0])
    last_updated = listing_detail.find("p", attrs={"class": "listing-takingon"}).find("span", attrs={"class": "recency"}).text.strip()
    return Dentist(name, address, distance, last_updated)


def fetch_available_dentists():
    response = requests.get(DENTAL_CHOICES_SEARCH_URL)
    if response.status_code == 200:
        results_page = BeautifulSoup(response.text, "html.parser")
        listing_items = results_page.find_all("div", attrs={"class": "listing-item"})
        dentists = []
        for listing_item in listing_items:
            dentists.append(transform_listing_item_to_dentist(listing_item))
        return dentists
    else:
        raise RequestFailureError(f"Failed to connect to ${DENTAL_CHOICES_SEARCH_URL}")


def notify(dentists):
    dentist_info_text = ""
    for dentist in dentists:
        dentist_info_text += str(dentist) + "\n\n\n"
    response = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={"from": f"NHS Dentist Availability Notifier <mailgun@{MAILGUN_DOMAIN}>",
              "to": [RECIPIENT],
              "subject": f"Available NHS Dentist(s) found",
              "text": f"MyNameIsMikeGreen's NHS dentist availability notifier has found the following available NHS dentists nearby:\n\n\n{dentist_info_text}Project: https://github.com/MyNameIsMikeGreen/nhs-dentist-availability-notifier/"
              })
    if response.status_code == 200:
        logging.info("Notification sent!")
    else:
        logging.info(f"HTTP {response.status_code}: {response.text}")
        raise RequestFailureError("Failed to send notification")


def shortlist_dentists(dentists):
    return [dentist for dentist in dentists if dentist.distance_miles <= MAX_DISTANCE_MILES]


def main():
    available_dentists = fetch_available_dentists()
    logging.info(f"Found {len(available_dentists)} available dentists")
    shortlist = shortlist_dentists(available_dentists)
    if shortlist:
        logging.info(f"Shortlisted {len(shortlist)} dentists. Sending notification...")
        notify(shortlist)
    else:
        logging.info(f"No suitable dentists found :(")


if __name__ == '__main__':
    logging.basicConfig(filename='nhsDentistNotifierNotifier.log',
                        level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S')
    main()

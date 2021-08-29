NHS Dentist Availability Notifier
=====================

* Uses [Dental Choices](https://dentalchoices.org) to find nearby NHS dentists that are accepting new patients.
* Filters results accoring to supplied maximum distance.
* If suitable dentists are found, sends a notification email.

# Usage

* Create a [Mailgun](https://www.mailgun.com/) account.
* Set the following environment variables:
    * **RECIPIENT**: Email address to notify
    * **MAILGUN_API_KEY**: API key for the Mailgun account to send notification email from
    * **MAILGUN_DOMAIN**: Maingun sending domain to send email from
    * **DENTAL_CHOICES_SEARCH_URL**: Dental Choices results page for user's location (e.g. https://dentalchoices.org/find-nhs-dentists-in/england/greater-manchester/)
    * **MAX_DISTANCE_MILES**: Maximum distance, in miles, of a dentist from the user's search location
* Run `./run.sh`
    * Ideally, this will be run periodically with a scheduler

# Bulk Unsubscribe for Mailchimp

Unsubscribes a set of email addresses from *all* lists in your
Mailchimp instance, using the 3.0 API.

## Instructions

  * Set BASE_URL and MC_API_KEY (your API key) in config.py.
  * Populate the blacklist file (bl.csv by default) with email
    addresses that have to be unsubscribed.
  * Run the unsub.py script.

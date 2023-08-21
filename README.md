# Rudimentary PrivacyBot for Yahoo Mail
This is a simple program inspired by [PrivacyBot](https://github.com/privacybot-berkeley/privacybot). It sends deletion requests to various data brokers and people search websites via email. PrivacyBot was written for Gmail; this is a rudimentary port for Yahoo (and Sky) Mail.  

Data broker details (including email addresses) can be found in `services_list_06May2021.csv`. This is taken straight from [PrivacyBot](https://github.com/privacybot-berkeley/privacybot). 

There is a [PrivacyBot Demo](https://www.youtube.com/watch?v=B24EYAAXpAE) available on YouTube. This code has the same basic structure as PrivacyBot, so the video is well worth watching.

## Usage:
Populate `userdata.json` with your details, then run:
```
python privacy_bot.py
```

## Notes:
- This currently only works for Yahoo mail. To get it to work for other email providers, you'll have to update the SMTP function calls.
- Many email providers will interrupt your connection if you're sending lots of emails in quick succession. I currently have a very hacky work-around (wait 5 minutes then try again). I may come up with a better solution if I ever revisit this, but for now, the script takes a very long time to run. I suggest you let it run overnight.
- Currently, the `generate_html` and `generate_plain_text` functions are quite crudely implemented. If you change the contents of `template.html` or `template.txt`, you'll have to modify the functions `generate_html` and `generate_plain_text`. 
- You can supply more than one email address to the `email` field of `userdata.json`. The first email address should be the address you'd like to send the deletion requests from. The order of the other email addresses do not matter. 

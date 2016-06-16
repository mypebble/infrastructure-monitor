# infrastructure-monitor
The infrastructure monitoring tool checks active systems and reports issues to Slack

Before you deploy, please ensure you set the config file correctly. For advice on how to do this, please see the Config section below.

### Deploying
To run the program:

`test.py -c <configfile> -s <slack-configfile>`

You may also do `test.py -h` which will display the above.

Finally, you can specify the full name of the argument with `--config` and `--slackconfig`

This loads in the config and then checks all the sites in the config file.

**Please note, domains have not been implemented yet.**

#### Unexpected Site Status Code
The standard error message to slack is:
`System Error @devs: Error at http://example.org. Expected status code expected: 302 | Actual status code: 200`

### Monitor Config

Example config:
```
---
sites:
- url: http://example.com
  status_code: 200
- url: http://example.org
  status_code: 302
domains:
- main: 8.8.8.8
```

##### Sites
- `url`: this field determines the URL which you would like to check the status of
- `status_code`: this is the status code which you expect the `url` to have **this field is entirely optional and will default to 200 if missing or blank**

##### Domains
- `main`: this is the ip address or url of the domain you would like to check

##### Config errors
The following errors in the config will result in a message to Slack:
- missing the url field out or not having a url field (even if you have a status_code field) [url is required even if status_code isn't]
- having no config file at all [requires a config file]
- having a malformed config file such as everything on one line [requires valid yaml]

##### Config sites errors
The following errors in the config sites section will result in a message to Slack:
- example.com [requires a protocol prefix e.g. http:// or https://]
- http://example [requires a suffix e.g. .com]

##### Config default behaviour
The following error in the config sites section will result in a default expected status code of 200 being assigned:
- missing the status_code out or not having a status_code field even if you have a url field

### Slack Config

Example config:
```
---
slack_api_token: "my_token"
slack_username: "@my.bot.name"
slack_channel: "#help-fire"
slack_shoutout: "@fire.fighters"
slack_emote: ":scream:"
```

- `slack_api_token`: this is the token required to auth with Slack
- `slack_username`: this is the username of the bot or person you want the alerts to come from
- `slack_channel`: this is the channel (*or user*) to whom you wish the messages to be sent
- `slack_shoutout`: this can be a user or a group to whom you wish to be alerted
- `slack_emote`: 

### Example Slack Messages

##### Expected Status Code Error
```
@my.bot.name BOT [10:00 AM]  
This is a test! System Error @fire.fighters: Error at http://example.org. Expected status code expected: 302 | Actual status code: 501
```

##### Invalid Monitor Config Examples (none exhaustive)
```
@my.bot.name BOT [3:49 PM]  
System Error @fire.fighters: Invalid URL 'example': No schema supplied. Perhaps you meant http://example.co.uk?
```
```
@my.bot.name BOT [10:00 AM]  
System Error @fire.fighters: No config file has been found. Please ensure you have a config.yaml file.
```
```
@my.bot.name BOT [10:00 AM]  
System Error @fire.fighters: KeyError: Check the url field in your config.yaml, it appears to be missing!
```
```
@my.bot.name BOT [10:00 AM]  
System Error @fire.fighters: A malformed config file has been found. Please check the formatting of your config.yaml file.
```
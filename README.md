# infrastructure-monitor
The infrastructure monitoring tool checks active systems and reports issues to Slack

Before you deploy, please ensure you set the config file correctly. For advise on how to do this, please see the Config section below.

### Deploying
To run the program:
`python main.py`

This loads in the config and then checks all the sites in the config file.

**Please note, domains have not been implemented yet.**

#### Unexpected Site Status Code
The standard error message to slack is:
`System Error @devs: Error at http://example.org. Expected status code expected: 302 | Actual status code: 200`

### Config
The config file is located in the monitor folder within the project folder.

Example config:
```
---
sites:
- url: http://example.com
  status_code: 200
- url: http://example.org
  status_code: 302
domains:
- url: 8.8.8.8
```

##### Sites
- `url`: this field determines the URL which you would like to check the status of
- `status_code`: this is the status code which you expect the `url` to have

##### Domains
- `url`: this is the ip address or url of the domain you would like to check

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

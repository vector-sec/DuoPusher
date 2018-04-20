# DuoPusher
Duo MFA auditing tool to test users' likelihood of approving unexpected push notifications.

- [Install](#install)
- [Duo Setup](#duo-setup)
- [Usage](#usage)
- [Reporting](#reporting)

**Feedback welcome!**

# Install
```
$ pip install -r requirements.txt
$ cp settings.config.sample settings.config
``` 

# Duo Setup

## Auth API
You will need to create a Auth API application in the Duo console.

This application is what you'll be sending push notifications on behalf of, so make sure to make the name something convincing :)

The integration key should be put in your settings.config as the APP_IKEY, and the secret key should be APP_SKEY.

## Admin API

You will also need to create a Admin API application in the Duo console.

This application only needs the "read resource" permission in order to enumerate users.

The integration key should be put in your settings.conf as the ADMIN_IKEY, and the secret key should be ADMIN_SKEY

# Usage
usage: **duopusher.py** [-h] [-v] [-u USER] [-r RANDNUM]
```

Arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -u USER, --user USER  specific user to test
  -r RANDNUM, --random RANDNUM
                        number of active users to select at random
```

# Reporting
Because all push notifications are coming from a new Auth API application, you can go into the Duo console and generate reports on approved/denied pushes for that application.

"""
Duo Pusher
Security Tool for assessing users' ability to spot fradulent
Duo push requests and deny them accordingly.
"""
import base64, email, hmac, hashlib, urllib, requests, \
argparse, ConfigParser, os, json, random

def sign(method, host, path, params, skey, ikey):
    """
    Return HTTP Basic Authentication ("Authorization" and "Date") headers.
    method, host, path: strings from request
    params: dict of request parameters
    skey: secret key
    ikey: integration key
    """

    # create canonical string
    now = email.Utils.formatdate()
    canon = [now, method.upper(), host.lower(), path]
    req_args = []
    for key in sorted(params.keys()):
        val = params[key]
        if isinstance(val, unicode):
            val = val.encode("utf-8")
        req_args.append(
            '%s=%s' % (urllib.quote(key, '~'), urllib.quote(val, '~')))
    canon.append('&'.join(req_args))
    canon = '\n'.join(canon)

    # sign canonical string
    sig = hmac.new(skey, canon, hashlib.sha1)
    auth = '%s:%s' % (ikey, sig.hexdigest())

    # return headers
    return {'Date': now, 'Authorization': 'Basic %s' % base64.b64encode(auth)}

def phish_push(user):
    """ Sends a Duo push notification to the specified user """
    params = {'username':user, 'factor':'push', 'device':'auto', 'async':'True'}
    headers = sign("POST", CONFIG.get("SETTINGS", "HOST"), "/auth/v2/auth",
        params, CONFIG.get("SETTINGS", "APP_SKEY"),
        CONFIG.get("SETTINGS", "APP_IKEY"))
    req = requests.post("https://"+CONFIG.get("SETTINGS", "HOST")+"/auth/v2/auth", headers=headers, data=params)
    if req.status_code == 200:
       print "Push notification sent to {}".format(user)
    else:
        print "Status Code: {} Error: {}".format(req.status_code, req.text)

def get_random_users(num):
    """ Returns num random users from all active Duo users """
    params = {}
    headers = sign("GET", CONFIG.get("SETTINGS", "HOST"), "/admin/v1/users",
        params, CONFIG.get("SETTINGS", "ADMIN_SKEY"),
        CONFIG.get("SETTINGS", "ADMIN_IKEY"))
    req = requests.get("https://"+CONFIG.get("SETTINGS", "HOST")
    +"/admin/v1/users", headers=headers)
    if req.status_code == 200:
        users = json.loads(req.text)
        users = users['response']
        users = [user for user in users if user['status'] == 'active']
        selected_users = random.sample(users, num)
        users = []
        for duo_user in selected_users:
            users.append(duo_user['username'])
        return users
    else:
        print "Status Code: {} Error: {}".format(req.status_code, req.text)

if __name__ == "__main__":
    if os.path.exists("settings.config"):
        CONFIG = ConfigParser.RawConfigParser()
        CONFIG.read('settings.config')
    else:
        raise Exception("Could Not find configuration file")
    PARSER = argparse.ArgumentParser(version="DuoPusher 1.0",
    description="A Duo Push Auditing Tool")
    PARSER.add_argument("-u", "--user", dest='user',
    help="specific user to test", metavar="USER")
    PARSER.add_argument("-r", "--random", dest='randnum',
    help="number of active users to select at random", metavar="RANDNUM")
    ARGS = PARSER.parse_args()
    if ARGS.user:
        phish_push(ARGS.user)
    elif ARGS.randnum:
        if ARGS.randnum.isdigit():
            USERS = get_random_users(int(ARGS.randnum))
            for duser in USERS:
                phish_push(duser)
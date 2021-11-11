import os
import json

import telepot
from InstagramAPI import InstagramAPI

PROBS = False
DB_FILE = "ig.json"
ERROR_MSG = "‼️⁉️📸 Instagram follower/unfollower check failed "\
    "for account <b>{}</b>\nError:\n{}"
ZERO_FOLLOWERS = "0️⃣📸 <b>{}</b>\nZero Followers Retrieved"
ZERO_FOLLOWINGS = "0️⃣📸 <b>{}</b>\nZero Followings Retrieved"
NEWFOLLOWER = "⤴️📸 <b>{}</b>\n"\
    "New IG Follower: <b>{}</b>\nhttp://instagram.com/{}\n"\
    "Total Followers: <code>{}</code>\nTotal Followings: <code>{}</code>"
UNFOLLOWER = "⤵️📸 <b>{}</b>\n"\
    "New IG Unfollower: <b>{}</b>\nhttp://instagram.com/{}\n"\
    "Total Followers: <code>{}</code>\nTotal Followings: <code>{}</code>"


def getTotalFollowings(api, user_id):
    """ RETRIEVE WHO I FOLLOW """
    following = []
    next_max_id = True
    while next_max_id:
        #first iteration hack
        if next_max_id == True:
            next_max_id=''
        _ = api.getUserFollowings(user_id, maxid=next_max_id)
        following.extend (api.LastJson.get('users',[]))
        next_max_id = api.LastJson.get('next_max_id','')
    return following


def getTotalFollowers(api, user_id):
    """ RETRIEVE WHO FOLLOWS ME """
    follower = []
    next_max_id = True
    while next_max_id:
        # first iteration hack
        if next_max_id is True:
            next_max_id = ''
        _ = api.getUserFollowers(user_id, maxid=next_max_id)
        follower.extend(api.LastJson.get('users', []))
        next_max_id = api.LastJson.get('next_max_id', '')
    return follower


if __name__ == "__main__":
    with open(DB_FILE, "r") as f:
        db = json.load(f)
    for a in db:
        print(a)
        user = a
        pwd = db[a]["pwd"]
        bot_key = db[a]["bot"]
        dest = db[a]["telegram"]
        old_followers = db[a]["followers"]
        old_followings = db[a]["followings"]
        bot = telepot.Bot(bot_key)
        bot.sendMessage(dest, f"ig_check started - {a}", 'HTML')
        api = InstagramAPI(user, pwd)
        api.login()
        user_id = api.username_id
        print("user id: " + str(user_id))
        try:
            print("### Check {} ###".format(a))
            # Check Followers & Followings
            followers = [x['username'] for x in getTotalFollowers(api, user_id)]
            followings = [x['username'] for x in getTotalFollowings(api, user_id)]
            idont = [x for x in followers if x not in followings]
            youdont = [x for x in followings if x not in followers]
            tot_followers = len(followers)
            tot_followings = len(followings)
            if len(old_followers) > 0 and len(followers) > 0:
                newfollowers = [x for x in followers if x not in old_followers]
                unfollowers = [x for x in old_followers if x not in followers]
                for n in newfollowers:
                    MOD = True
                    print("New Follower: " + n)
                    bot.sendMessage(dest,
                        NEWFOLLOWER.format(user,n,n,tot_followers,tot_followings),
                        'HTML')
                for u in unfollowers:
                    MOD = True
                    print("New Unfollower: " + u)
                    bot.sendMessage(dest,
                        UNFOLLOWER.format(user,u,u,tot_followers,tot_followings),
                        'HTML')
            if len(followers) == 0:
                bot.sendMessage(dest,ZERO_FOLLOWERS.format(user),'HTML')
            if len(followings) == 0:
                bot.sendMessage(dest,ZERO_FOLLOWINGS.format(user),'HTML')
            db[a]["followers"] = followers
            db[a]["followings"] = followings
            db[a]["i_dont"] = idont
            db[a]["you_dont"] = youdont
        except Exception as err:
            bot.sendMessage(dest,ERROR_MSG.format(user, err),'HTML')
        bot.sendMessage(dest, f"ig_check ended {a}", 'HTML')
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)
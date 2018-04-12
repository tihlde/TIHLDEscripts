import re

from tihldelib.ipahttp import ipa

api = ipa('ipa1.tihlde.org', sslverify=True)
with open('/home/staff/drift/passord/ipa.pw') as f:
    api.login('admin', f.read().replace('\n', '').strip())

pattern = re.compile(r"[,|]")
for user in api.user_find()["result"]["result"]:
    if "gecos" in user:
        for entry in user["gecos"]:
            if entry.find("@") + 1:
                for geco in pattern.split(entry):
                    if geco.find("@") + 1:
                        uid = user["uid"][0]
                        email = geco.strip()
                        api.user_mod(uid, addattrs=["mail=" + email])
                        print("Added", email, "for user", uid)


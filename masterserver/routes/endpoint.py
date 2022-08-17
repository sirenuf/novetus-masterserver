import re
from functools import wraps
from time import monotonic
from base64 import b64encode as b64
from flask import (
    Blueprint,
    request,
    render_template
)

serverList = {}
novetusVer = "1.3 v8.2022.1"

bp = Blueprint("endpoints", __name__)

def convertTime(seconds):
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)

    num = "%d:%02d:%02d" % (hour, min, sec)
    tA = [int(num) for num in num.split(":")]

    s = "second"
    m = "minute"
    h = "hour"

    if not tA[2] == 1:
        s += "s"
    if not tA[1] == 1:
        m += "s"
    if not tA[0] == 1:
        h += "s"

    if tA[0] > 0:
        return f"{tA[0]} {h}, {tA[1]} {m}, {tA[2]} {s}"
    elif tA[1] > 0:
        return f"{tA[1]} {m}, {tA[2]} {s}"
    else:
        return f"{tA[2]} {s}"


def replaceVars(name, map: str, client: str):
    name = name.upper()
    name = name.replace("%MAP%", map[:-5])
    name = name.replace("%CLIENT%", client)
    return name

def UArequired(func):
    @wraps(func)
    def decor_funct(*args, **kwargs):
        if str(request.user_agent) != "Roblox":
            return "user agent failure.", 400
    
        return func(*args, **kwargs)
    return decor_funct


def validateRequest(id, client, players, mapName, port):
    '''Make sure the creation request is valid'''
    if not id or not client or not players:
        return False
    
    if len(id) != 50:
        return False
    
    if not re.search("^\d+(\/\d+)*$", players):
        return False
    
    try:    port = int(port)
    except: return False

    if port <= 65535 and not port >= 1:
        return False

    return True


@bp.route("/server/create")
@UArequired
def createServer():
    id      = request.args.get("id")
    client  = request.args.get("client")
    players = request.args.get("players")
    mapName = request.args.get("map")
    portNum = request.args.get("port")
    serName = request.args.get("name")
    ipAddr  = request.remote_addr

    if serName == "":
        serName = mapName

    if id in serverList:
        return "", 404

    if not validateRequest(id, client, players, mapName, portNum):
        return "I can't validate the request.", 400

    serName = replaceVars(serName, mapName, client)

    # Create Novetus URI
    novetusURI = f"{ b64(ipAddr.encode('ascii')).decode() }|{ b64(portNum.encode('ascii')).decode() }|{ b64(client.encode('ascii')).decode() }"
    novetusURI = b64(novetusURI.encode("ascii"))

    # Master server string:
    # better solution than .encode spam?
    encodedStr = f"{ b64(serName.encode('ascii')).decode() }|{ b64(ipAddr.encode('ascii')).decode() }|{ b64(portNum.encode('ascii')).decode() }|{ b64(client.encode('ascii')).decode() }|{ b64(novetusVer.encode('ascii')).decode() }"
    encodedStr = b64(encodedStr.encode("ascii"))

    serverList.update({
        id: {
            "client":     client,
            "players":    players,
            "starttime":  monotonic(),
            "uptime":     convertTime(1),
            "map":        mapName,
            "port":       portNum,
            "ip":         ipAddr,
            "b64uri":     f"onclick=\"window.location.href='novetus://{novetusURI.decode()}';\"", # What the fuck
            "b64master":  encodedStr.decode(),
            "name":       serName,
            "novetusver": novetusVer,
            "keepAlive":  monotonic()
        }})

    # 404 for safety
    return "", 404

@bp.route("/server/keepAlive<integer>")
@UArequired
def keepAlive(integer):
    id      = request.args.get("id")
    client  = request.args.get("client")
    mapName = request.args.get("map")
    portNum = request.args.get("port")
    serName = request.args.get("name")
    ipAddr  = request.remote_addr

    players = request.args.get("players")

    try: server = serverList[id]
    except: return "I can't validate the request.", 400

    if ipAddr != server["ip"]:
        return "I can't validate the request.", 400

    # Replace server name if has variables
    serName = replaceVars(serName, mapName, client)

    if not server["name"] == serName or not server["client"] == client or not server["map"] == mapName or not server["port"] == portNum:
        return "I can't validate the request.", 400
    
    # Because roblox duplicates requests
    if server["keepAlive"] == monotonic():
        return "", 404
    
    server.update({
        "keepAlive": monotonic(),
        "players":   players,
        "uptime":    convertTime(monotonic() - server["starttime"])
    })

    return "", 404


@bp.route("/serverlist.txt")
def novetusServerBrowser():
    returStr = ""
    for _, v in serverList.items():
        returStr += v["b64master"] + "\n"
    
    return returStr, {"Content-Type": "text/plain"}


@bp.route("/")
def serverLister():
    return render_template("serverlist.html", array=serverList)
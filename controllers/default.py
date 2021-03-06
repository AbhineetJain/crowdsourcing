# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################
import requests, json
imp = local_import('imp')

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """

    response.flash = T("Welcome to DisRes!!!")
    url = imp.APP_URL + "disasters/"
    r = requests.get(url,
                     headers=session.headers,
                     cookies=session.cookies,
                     proxies=imp.PROXY)
    dis_list = json.loads(r.text)
    table = TABLE(TR(TH("Created"), TH("Disaster"), TH("Latitude"), TH("Longitude")),
                  _class="table")
    for i in dis_list:
        table.append(TR(TD(imp.getdatetime(i["created"])), TD(imp.mapping[i["dis_type"]]), TD(i["latitude"]), TD(i["longitude"])))

    if session.user is None:
        response.flash = "Please Login!"
    elif session.user == "admin":
        redirect(URL(c="default", f="admin"))
    elif session.user == "organisation":
        redirect(URL(c="default", f="organisation"))
    return dict(table=table)

def organisation():
    t = TABLE(TR(TH("Created"), TH("Disaster"), TH("Latitude"), TH("Longitude"), TH("Message"), TH("Take Action")),
              _class="table")
    url = imp.APP_URL + "sos/"
    headers = {'content-type': 'application/json'}
    r = session.client.get(url,
                           headers=session.headers,
                           cookies=session.cookies,
                           proxies=imp.PROXY)
    soss = json.loads(r.text)
    for i in soss:
        t.append(TR(TD(imp.getdatetime(i["created"])), TD(imp.mapping[i["dis_type"]]), TD(i["latitude"]), TD(i["longitude"]), TD(i["message"]),
                    TD(FORM(INPUT(_type="submit", _value="Respond"),
                            _action=URL(c='response', f='index', args=[i["id"]])))))

    return dict(t=t)

def admin():
    # Send HTTP request to the REST server
    url = imp.APP_URL + "disasters/"
    r = session.client.get(url,
                           headers=session.headers,
                           cookies=session.cookies,
                           proxies=imp.PROXY)
    list_organisations = json.loads(r.text)

    t = TABLE(TR(TH("Created"), TH("Disaster Type"), TH("Latitude"), TH("Longitude"), TH("Confirm Disaster")),
              _class="table")
    for i in list_organisations:
        tr = TR(TD(A(imp.getdatetime(i["created"]), _href=URL(c="default", f="disaster_details", args=[i["id"]]))),
                TD(A(imp.mapping[i["dis_type"]], _href=URL(c="default", f="disaster_details", args=[i["id"]]))),
                TD(A(i["latitude"], _href=URL(c="default", f="disaster_details", args=[i["id"]]))),
                TD(A(i["longitude"], _href=URL(c="default", f="disaster_details", args=[i["id"]]))))
        form = FORM(_action=URL(c="default", f="disaster_status", args=[i["id"]]))
        if i["verified"] is False:
            form.append(INPUT(_type="submit", _name="confirm", _value="Confirm"))
        form.append(INPUT(_type="submit", _name="delete", _value="Delete"))
        tr.append(TD(form))
        t.append(tr)

    return dict(t=t)

def user():
    return dict()

def disaster_status():
    dis_id = request.args[0]
    if request.vars.has_key("confirm"):
        if dict(session.client.cookies).has_key("csrftoken") is False:
            redirect(URL("login", "index"))
        pdata = json.dumps({"verified": True})
        pURL = imp.APP_URL + "disasters/" + dis_id + "/"
        r = session.client.patch(pURL,
                                 data=pdata,
                                 headers=session.headers,
                                 cookies=session.cookies,
                                 proxies=imp.PROXY)
        
        pURL = imp.APP_URL + "organisations/"
        headers = dict(session.headers)
        headers["disaster"] = dis_id
        r = session.client.get(pURL,
                           headers=headers,
                           cookies=session.cookies,
                           proxies=imp.PROXY)
        r = json.loads(r.text)
        org_list = []
        for i in r:
          org_list.append(str(i["email"]))
        email(org_list)  



    elif request.vars.has_key("delete"):
        if dict(session.client.cookies).has_key("csrftoken") is False:
            redirect(URL("login", "index"))
        pURL = imp.APP_URL + "disasters/" + dis_id + "/"
        r = session.client.delete(pURL,
                                  headers=session.headers,
                                  cookies=session.cookies,
                                  proxies=imp.PROXY)
    else:
        return "Some error ocurred"
    redirect(URL("default", "admin"))

def disaster_details():
    dis_id = request.args[0]
    if dict(session.client.cookies).has_key("csrftoken") is False:
        redirect(URL("login", "index"))
    pURL = imp.APP_URL + "sos/"
    headers = dict(session.headers)
    headers["disaster"] = dis_id
    r = session.client.get(pURL,
                           headers=headers,
                           cookies=session.cookies,
                           proxies=imp.PROXY)
    table = TABLE(TR(TH("Created"), TH("Message"), TH("Latitude"), TH("Longitude")),
                  _class="table")
    res = json.loads(r.text)
    for i in res:
        table.append(TR(TD(imp.getdatetime(i["created"])), TD(i["message"]), TD(i["latitude"]), TD(i["longitude"])))

    return dict(table=table)

def email(orglist):
      from gluon.tools import Mail 
      mail = Mail() 
      mail.settings.server = 'smtp.gmail.com:587'
      mail.settings.sender = 'helpatdisres@gmail.com' 
      mail.settings.login = 'helpatdisres@gmail.com:iiit123disres' 
      mail.send(to=orglist, 
               subject='Hello World - Test email from web2py', 
               # If reply_to is omitted, then mail.settings.sender is used 
               message='hi there') 

      return

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)

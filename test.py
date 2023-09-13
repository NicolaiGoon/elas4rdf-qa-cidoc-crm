from array import array
import re
import time
import requests

subg = {
    "@graph": [
        {
            "@id": "http://ldf.fi/ww1lod/162aac3d",
            "prefLabel": "Eastern Front "
        },
        {
            "@id": "http://ldf.fi/ww1lod/5d2e435d",
            "P10_falls_within": "http://ldf.fi/ww1lod/162aac3d",
            "P14_carried_out_by": "http://ldf.fi/ww1lod/a1f3de8e",
            "P4_has_time-span": "http://seco.tkk.fi/saha3/u6a7af972-c4c3-412c-af41-6d9a10ed1f32",
            "P7_took_place_at": "http://ldf.fi/ww1lod/711c50c9",
            "prefLabel": [
                "Fall of Przemsyl ",
                {
                    "@language": "sv",
                    "@value": "Fall of Przemsyl "
                },
                {
                    "@language": "fi",
                    "@value": "Fall of Przemsyl "
                },
                {
                    "@language": "en",
                    "@value": "Fall of Przemsyl "
                }
            ]
        },
        {
            "@id": "http://ldf.fi/ww1lod/711c50c9",
            "prefLabel": "Przemyśl"
        },
        {
            "@id": "http://ldf.fi/ww1lod/a1f3de8e",
            "prefLabel": "Russia"
        },
        {
            "@id": "http://seco.tkk.fi/saha3/u6a7af972-c4c3-412c-af41-6d9a10ed1f32",
            "prefLabel": "3/6/1915"
        }
    ],
    "@context": {
        "prefLabel": {
            "@id": "http://www.w3.org/2004/02/skos/core#prefLabel"
        },
        "P4_has_time-span": {
            "@id": "http://www.cidoc-crm.org/cidoc-crm/P4_has_time-span",
            "@type": "@id"
        },
        "P10_falls_within": {
            "@id": "http://www.cidoc-crm.org/cidoc-crm/P10_falls_within",
            "@type": "@id"
        },
        "P7_took_place_at": {
            "@id": "http://www.cidoc-crm.org/cidoc-crm/P7_took_place_at",
            "@type": "@id"
        },
        "P14_carried_out_by": {
            "@id": "http://www.cidoc-crm.org/cidoc-crm/P14_carried_out_by",
            "@type": "@id"
        },
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "crm": "http://www.cidoc-crm.org/cidoc-crm/"
    }
}

def cidoc_uri_to_str(e):
    '''
    Convert a cidoc-crm uri to a readable string
    '''
    strip_prefix = re.sub(r'^[A-Za-z0-9]*_','',e[e.rindex("/")+1:])
    return strip_prefix.replace('_',' ')

'''
works on virtuoso
'''
def cidocGraphToText(g,labelName="prefLabel"):
    '''
    Converts a cidoc-crm subgraph to text by connecting the triples and replacing ids with labels
    '''

    # label id map
    labelDict = dict()
    text = ""
    for s in g:
        for p in g[s]:
            if("cidoc-crm" in p):
                objects = ""
                for o in g[s][p]: 
                    if(o["type"] == "uri"):
                        objects += o["value"] + ", "
                # replace last comma and replace the previous one with an "and"
                objects =  ' and '.join(objects[:-2].rsplit(",",1))
                # add only cidoc property
                text += " "+s+" "+cidoc_uri_to_str(p)+" "+objects+"."
            elif(labelName in p):
                labelDict[s]  = g[s][p][0]["value"]
    # replace id with label
    for key in labelDict:
        text = text.replace(key,labelDict[key])
    return re.sub(r'\s{2,}',' ',text).replace(" .",".")

'''
does not work on virtuoso
'''
def cidocGraphToText2(g,labelName="prefLabel"):
    '''
    Converts a cidoc-crm subgraph to text by connecting the triples and replacing ids with labels
    json-ld
    '''
    # map uri to label
    labelDict = dict()
    # final text
    text = ""
    for node in g['@graph']:
        uri = node["@id"]
        label = node[labelName]
        if(isinstance(label,list)):
            label = label[0]
        labelDict[uri] = label
        for predicate in node.keys():
            if(predicate != "@id" and predicate != labelName):
                objUri = node[predicate]
                if(isinstance(objUri,list)):
                    objUriText = ""
                    for x in objUri:
                        objUriText += x + ", "
                    # replace last comma and replace the previous one with an "and"
                    objUriText =  ' and '.join(objUriText[:-2].rsplit(",",1))
                    text += " " + uri + " " + cidoc_uri_to_str("http://www.cidoc-crm.org/cidoc-crm/"+predicate) + " " + objUriText + "." 
                else:
                    text += " " + uri + " " + cidoc_uri_to_str("http://www.cidoc-crm.org/cidoc-crm/"+predicate) + " " + objUri + "." 
    # replace id with label
    # for key in labelDict:
    #     text = text.replace(key,labelDict[key])
    return re.sub(r'\s{2,}',' ',text).replace(" .",".")


print(cidocGraphToText2(subg))
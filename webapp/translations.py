import pandas as pd


def get_race_translation():
    return pd.read_json('{"Race":{"0":"01","1":"02","2":"03","3":"04","4":"05","5":"06","6":"07","7":"08","8":"10",'
                        '"9":"11","10":"12","11":"13","12":"14","13":"15","14":"16","15":"17","16":"20","17":"21",'
                        '"18":"22","19":"25","20":"26","21":"27","22":"28","23":"30","24":"31","25":"32","26":"96",'
                        '"27":"97","28":"99","29":"88"},"Translation":{"0":"White","1":"Black or African-American",'
                        '"2":"American Indian\\/Alaska Native","3":"Chinese","4":"Japanese","5":"Filipino",'
                        '"6":"Native Hawaiian","7":"Korean","8":"Vietnamese","9":"Laotian","10":"Hmong",'
                        '"11":"Cambodian","12":"Thai","13":"Asian Indian NOS\\/Pakistani NOS","14":"Asian Indian",'
                        '"15":"Pakistani","16":"Micronesian","17":"Chamorro","18":"Guamanian NOS","19":"Polynesian '
                        'NOS","20":"Tahitian","21":"Samoan","22":"Tongan","23":"Melanesian NOS","24":"Fiji Islander",'
                        '"25":"Papua New Guinean","26":"Other Asian or Asian NOS","27":"Pacific Islander NOS",'
                        '"28":"Unknown by patient","29":"No further race documented"}}')


def get_stage_group_translation():
    return pd.read_json('{"Stage":{"0":0,"1":1,"2":2,"3":3,"4":4},"Translation":{"0":"0","1":"I","2":"II","3":"III",'
                        '"4":"IV"}}')

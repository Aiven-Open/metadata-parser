import configparser
import requests
import json
import sys
from aiven.client import client

config = configparser.ConfigParser()
config.read('conf/conf.env')
config['DEFAULT']['USERNAME']

aiven_client = client.AivenClient(base_url=config['DEFAULT']['BASE_URL'])

result = aiven_client.authenticate_user(email=config['DEFAULT']['USERNAME'], password=config['DEFAULT']['PASSWORD'])
aiven_client.auth_token=result["token"]

project=config['DEFAULT']['PROJECT']
prj = sys.argv[1]

if prj:
    project = prj

service = aiven_client.get_service(project=project, service="demo-grafana")
users = service["users"]

password = "fake"
for user in users:
    if user["username"]== "avnadmin":
        password = user["password"]

base_url = "https://"+service["service_uri_params"]["host"]+":443"
datasources = requests.get(base_url+"/api/datasources", auth=("avnadmin", password))
for datasource in json.loads(datasources.text):
    uid = -1
    if datasource["name"] == "aiven-pg-demo-pg":
        uid = datasource["uid"]
        content='''{
  
  "dashboard": {
    "annotations": {
      "list": [
        {
          "builtIn": 1,
          "datasource": "-- Grafana --",
          "enable": true,
          "hide": true,
          "iconColor": "rgba(0, 211, 255, 1)",
          "name": "Annotations & Alerts",
          "target": {
            "limit": 100,
            "matchAny": false,
            "tags": [],
            "type": "dashboard"
          },
          "type": "dashboard"
        }
      ]
    },
    "editable": true,
    "fiscalYearStartMonth": 0,
    "graphTooltip": 0,
    "id": null,
    "links": [],
    "liveNow": false,
    "panels": [
      {
        "datasource": {
          "type": "postgres",
          "uid": "REPLACE_UID"
        },
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "custom": {
              "align": "auto",
              "displayMode": "auto"
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": null
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 9,
          "w": 12,
          "x": 0,
          "y": 0
        },
        "id": 2,
        "options": {
          "footer": {
            "fields": "",
            "reducer": [
              "sum"
            ],
            "show": false
          },
          "showHeader": true
        },
        "pluginVersion": "8.3.2",
        "targets": [
          {
            "datasource": {
              "type": "postgres",
              "uid": "REPLACE_UID"
            },
            "format": "time_series",
            "group": [],
            "hide": false,
            "metricColumn": "pasta_name",
            "rawQuery": false,
            "rawSql": "SELECT  NOW(),  pasta_name AS metric,  cooking_minutes FROM pasta ORDER BY 1,2",
            "refId": "A",
            "select": [
              [
                {
                  "params": [
                    "cooking_minutes"
                  ],
                  "type": "column"
                }
              ]
            ],
            "table": "pasta",
            "timeColumn": "NOW()",
            "where": []
          }
        ],
        "title": "Panel Title",
        "type": "table"
      }
    ],
    "schemaVersion": 33,
    "style": "dark",
    "tags": [],
    "templating": {
      "list": []
    },
    "time": {
      "from": "now-12h",
      "to": "now"
    },
    "timepicker": {},
    "timezone": "",
    "title": "my_dashboard",
    "uid": "kq-3gR-7k",
    "weekStart": ""
  },
  "id": null,
  "overwrite": true
}'''
        
        headers={"Content-Type": 'application/json'}
        rep = requests.post(base_url+"/api/dashboards/import", auth=("avnadmin", password), data=content.replace('REPLACE_UID',uid),headers=headers)
        print(rep.text)


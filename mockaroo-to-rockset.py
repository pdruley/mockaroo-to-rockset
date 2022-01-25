import requests
#from rockset import Client
import argparse
import os, sys

#using environment variable to get the api key
ROCKSET_APIKEY = os.getenv('ROCKSET_APIKEY')
if ROCKSET_APIKEY:
  auth = 'ApiKey ' + ROCKSET_APIKEY
else:
  sys.exit("Missing environment variable ROCKSET_APIKEY. Please define before running again.")

headers = {"Authorization": auth,"Content-Type": "application/json"}
#print(headers)

#https://rockset.com/docs/rest-api/
ROCKSET_APISERVER = os.getenv('ROCKSET_APISERVER')
if ROCKSET_APISERVER:
  api = ROCKSET_APISERVER
else:
  sys.exit(
'''
Missing environment variable ROCKSET_APISERVER. Please define before running again. 
See https://rockset.com/docs/rest-api/ for more information
'''
  )

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("url", help="url for the data api request")
  parser.add_argument("-w", "--workspace", help="set workspace name, default is commons")
  parser.add_argument("-c", "--collection", help="set collection name, required", required=True)
  parser.add_argument("-i", "--iterations", help="set the number of data api requests, default is 1")
  parser.add_argument("-t", "--test", help="use for testing, will not add data", action="store_true")

  args = parser.parse_args()

  return args

#list collections
def check_collections(collection):
  r = requests.get(api + '/v1/orgs/self/collections', headers=headers)
  exist = False

  response = r.json()

  if(r.raise_for_status()):
    print(r.status_code, r.text)
  else:
    for existing_collection in response['data']:
      if(existing_collection['name'] == collection):
        print("Collection " + collection + " already exist.")
        exist = True
        break
  
  return exist
      

#create collection
def create_collection(workspace, collection, desc):

  data = '{"name": "' + collection + '", ' + '"description": "' + desc + '"}' 

  #print(data)
  url = api + '/v1/orgs/self/ws/' + workspace + '/collections'
  r = requests.post(url, headers=headers, data=data)
  #print(r.text)

  if(r.raise_for_status()):
    print(r.status_code, r.text)
  else:
    return collection

#get mockaroo data records
#make sure mockaroo schema is set to output array
def get_data(url):
  r = requests.get(url)

  #print(r.text)
  if(r.raise_for_status()):
    print(r.status_code, r.text)
  else:
    return '{ "data": ' + str(r.text) + '}'

#data needs to be an arrary of documents
def add_doc(workspace, collection, data):
  url = api + '/v1/orgs/self/ws/' + workspace + '/collections/' + collection + '/docs'
  r = requests.post(url, data=data, headers=headers)
  if(r.raise_for_status()):
    print(r.status_code)
    print(r.text)
  else:
    print("Response: ")
    json = r.json()
    for record in json['data']:
      #we could actually check the error field and only print those records
      #otherwise we can just do a count of those with status ADDED and return that
      print(record)

def main():

  #get command line arguments
  args = parse_args()

  #defaults:
  workspace = "commons"
  collection = None
  desc = "demo"
  iterations = 1

  if args.url:
    url = args.url
  if args.workspace:
    workspace = args.workspace    
  if args.collection:
    collection = args.collection
  if args.iterations:
    iterations = args.iterations
    
  if args.test:
    print("testing only")
  else:
    if check_collections(collection):
      print("Collection " + collection + " already exist, just adding data.")
    else:
      create_collection(workspace, collection, desc)
      
    for i in range(int(iterations)):
      response = get_data(url)
      add_doc(workspace, collection, response)
      
main()

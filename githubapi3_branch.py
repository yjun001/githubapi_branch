#!/usr/bin/env python

import requests
import base64
import json
import os

class gBranch:
    def __init__(self, org=''):
        self.__ss = self.__load_json("./.setting.json")
        self.__org = self.__ss["organization"] if not org else org 

        self.__pbh_file = "./protected_branches.json"
        self.__protected_branches = {}
        if os.path.exists(self.__pbh_file):
            self.__protected_branches = self.__load_json(self.__pbh_file)

    def __load_json(self, file):
        try:
            with open(file, "rb") as f:
                return json.load(f)
        except IOError:
            print ("Json file load error")
            return None
    
    def __save_protected_branches(self, js_data):
        with open(self.__pbh_file, "w+") as f:
            json.dump(js_data,f)
            f.flush

    def __githubapi_request(self, url, data="", method='GET'):
        base64string = base64.encodestring('%s/token:%s' % (self.__ss['org_owner_id'],self.__ss['org_token'])).replace('\n', '')
        headers={ 'Content-Type': 'application/json', 'Authorization': "Basic %s" % base64string } 
        #request.get_method = lambda: method
        try:
            res = requests.get(url,data=json.dumps(data), headers=headers)
            response=res.json()
            while 'next' in res.links.keys():
                res=requests.get(res.links['next']['url'],headers=headers)
                response.extend(res.json())
            # print json.dumps(response,sort_keys=True, indent=4)
            return response

        # except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        # except requests.exceptions.TooManyRedirects:
        # Tell the user their URL was bad and try a different one
        except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
            print (e)
            sys.exit(1)
        '''
        except e:
            if hasattr(e, 'reason'):
                print 'failed to reach a server %s.' % url
                print 'Reason: ', e.reason
    
            elif hasattr(e, 'code'):
                print 'The server could not fulfill the request.'
                print 'Error code: ', e.code
        '''

    # list all repositories in an organization
    def list_repos(self):
        url = "%s/orgs/%s/repos" % ( self.__ss['api_endpoint'], self.__org )
        # print "list repoistories url %s in organization %s "  % ( url, self.__org )
        resp = self.__githubapi_request(url)
        return [ r['name'] for r in resp ] 
        
    # list all branches in a repository
    def list_branch(self, repos):
        url = "%s/repos/%s/%s/branches" % ( self.__ss['api_endpoint'], self.__org, repos)
        # print "list branches url %s in repository %s" % ( url, repos )
        resp = self.__githubapi_request(url)
        # print json.dumps(resp, sort_keys=True, indent=4)
        return [ r['name'] for r in resp ]
 
    # get informatoin in a branch of repository
    def get_branch(self, repos, branch, protected=False):
        if protected == 0:
            url = "%s/repos/%s/%s/branches/%s" % ( self.__ss['api_endpoint'], self.__org, repos, branch)
        else:
            url = "%s/repos/%s/%s/branches/%s/protection" % ( self.__ss['api_endpoint'],self.__org, repos, branch)
        resp = self.__githubapi_request(url)
        print (json.dumps(resp, sort_keys=True, indent=4))

    # get informatoin in a protected branch of repository
    def check_branch_protected(self, repos, branch):
        url = "%s/repos/%s/%s/branches/%s" % ( self.__ss['api_endpoint'], self.__org, repos, branch)
        # print "check branch url %s" % url
        resp = self.__githubapi_request(url)
        if resp['protected'] == True:
            print (repos, resp['name'])
            if repos in self.__protected_branches.iterkeys():
                # if resp['name'] not in self.__protected_branches[repos]:
                self.__protected_branches[repos].append(resp['name'])
            else:
                self.__protected_branches[repos] = [ resp['name'] ]
            return resp['protection_url']
        
    def find_protected_branches(self):
        repos = self.list_repos()
        protected_branch = []
        for r in repos:
            for bh in self.list_branch(r):
                pbh = self.check_branch_protected(r, bh)
                if pbh != None:
                    protected_branch.append(pbh)
        return protected_branch

    def get_protected_branch_restrictions(self, url):
        url = "%s/restrictions/users" % ( url )
        # print "list branches url %s in repository %s" % ( url, repos )
        resp = self.__githubapi_request(url)
        print (json.dumps(resp, sort_keys=True, indent=4))
        #return [ r['name'] for r in resp ]

    def get_protected_branches(self):
        return self.__protected_branches

    def save_protected_branches(self):
        self.__save_protected_branches(self.__protected_branches)



def main():
    gb=gBranch()
    # gb=gBranch('UnixServerOperations')
    # gb=gBranch('NGSE')
    # print gb.list_repos()
    pbh = gb.find_protected_branches()
    # print pbh
    # print gb.get_protected_branches();
    # gb.save_protected_branches()
    #for p in pbh:
    #    gb.get_protected_branch_restrictions(p)
    #repos = gb.list_repos()
    #for r in repos:
    #    for bh in gb.list_branch(r):
    #        gb.get_branch(r, bh)

if __name__ == "__main__": main()


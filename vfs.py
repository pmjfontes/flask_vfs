'''
Created on Apr 28, 2016

Copyright (c) 2016 Paulo Fontes

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software 
without restriction, including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH 
THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

from flask import request
import os
import json

## Get file type from extension
# 
# TODO: Look at mimetypes instead
# 
def getFileType(path):
    
    if os.path.isdir(path):
        return "dir"
    else:
        ext = os.path.splitext(path)[1]
        if ext is "":
            ext = "unk" 
        return ext
    
class VFS(object):
    
    def __init__(self, app, mount_point=None):
        self.app = app
        
        self.app.add_url_rule("/api/vfs/<path:args>",view_func=self.crud, methods = ['GET','POST','PUT','DELETE'])
        self.app.add_url_rule("/api/vfs/",view_func=self.crud, methods = ['GET','POST','PUT','DELETE'])
        
        if mount_point==None: 
            self.mount_point = "./"
        else:
            self.mount_point = mount_point + "/"
    
    def crud(self,args=""):
        
        resp = {}
        path = "%s%s" %(self.mount_point,args)
        
        ## Create a new file or folder
        #
        #  Must send type=dir to create a directory
        #
        if request.method == 'POST':
            f_type = request.form.get("type")
            if f_type == "dir":
                os.mkdir(path) 
            else:
                with open(path,"w") as fh:
                    fh.write("")
                                        
            resp["error"] = "0"
        
        ## Read a files content or get a folder list
        elif request.method == 'GET':
            
            if os.path.isdir(path):
                ls = []
                
                for f in os.listdir(path):
                    f_name = f
                    f_type = getFileType("%s%s"%(path,f))
                    ls.append({"f_name":f_name,"f_type":f_type})
                    
                resp['listdir'] = ls
            
            elif os.path.isfile(path):
                with open(path,"r") as fh:
                    resp['content'] = fh.read()
            else:
                resp['error'] = "File not found"
        
        ## Update a file
        elif request.method == 'PUT':
            if os.path.isdir(path):
                resp['error'] = "Cannot write to a directory"
            
            if request.headers['Content-Type'] == "application/octet-stream":
                with open(path,"w") as fh:
                    fh.write(request.data)
                resp["error"] = "0"
        
        ## Delete a file or folder
        elif request.method == 'DELETE':
            
            if path == self.mount_point:
                resp["error"] = "Nothing to delete" 
            
            elif os.path.isdir(path):
                if len(os.listdir(path))>0:
                    resp['error'] = "Directory is not empty"
                else:
                    os.rmdir(path)
                    resp['error'] = "0"
            else:
                os.remove(path)
                resp['error'] = "0"
                
        return json.dumps(resp)
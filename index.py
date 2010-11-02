import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from xml.dom import minidom
from xmlExport import xmlExport
from xmlImport import xmlImportString
from models import *
    
"""
ASN2
Anonymous Social Network phase 2
"""   

def doRender(handler,tname='index.html',values = {}):
    temp = os.path.join(
      os.path.dirname(__file__),
      'templates/' + tname)
    if not os.path.isfile(temp):
        return False

    newval = dict(values)
    newval['path'] = handler.request.path

    outstr = template.render(temp,newval)
    handler.response.out.write(outstr)
    return True

class MainPage(webapp.RequestHandler):
    """
    Request handler for main page (index.html). 
    """
    def get(self):
        doRender(self,'index.html')

class ImportData(webapp.RequestHandler):
    def get(self):
        """
        Return the import page (import.html).
        """
        template_values = None
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'templates/import.html')
        self.response.out.write(template.render(path, template_values, True))

    def post(self):
        """
        Get xml data from the text box and import then redirect to export
        """
        xml_file = self.request.get('xml-file')
        try:       
          xmlImportString(xml_file)
          self.redirect("/export")
        except Exception, e:
            template_values = { 'error' : e.args }
            directory = os.path.dirname(__file__)
            path = os.path.join(directory, 'templates/import.html')
            self.response.out.write(template.render(path, template_values, True))

         
class ExportData(webapp.RequestHandler):
    def get(self):
        """
        Return the export page (export.html)
        """
        students = Student.all().fetch(1000)
        xml = xmlExport(students)
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.out.write(xml)

class ClearData(webapp.RequestHandler):
    def get(self):
        """
        Clear the datastore
        """
        query = Student.all()
        db.delete(query)
        self.redirect("/")

class ListClass(webapp.RequestHandler):
    def get(self):
        classes = Class.all()
        classes.fetch(100)
        doRender(self,'class/list.html',{'classes':classes})
        
class AddClass(webapp.RequestHandler):
    def get(self):
        template_values = {'form':ClassForm()} 
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'templates/class/add.html')
        self.response.out.write(template.render(path, template_values, True))

    def post(self):
        form = ClassForm(self.request.POST)            
        form.save()
      	self.redirect("/class/list")

class EditClass(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        cl = Class.get(db.Key.from_path('Class', id))
	template_values = {'form':ClassForm(instance=cl),'id':id}
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'templates/class/add.html')
        self.response.out.write(template.render(path, template_values, True))

    def post(self):
	id = int(self.request.get('_id'))
	cl = Class.get(db.Key.from_path('Class', id))
        form = ClassForm(data = self.request.POST, instance = cl)            
	form.save()
      	self.redirect("/class/list")

class DeleteClass(webapp.RequestHandler):
    def get(self):
	id = int(self.request.get('id'))
        cl = Class.get(db.Key.from_path('Class', id))
	template_values = {'cl':cl,'id':id}
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'templates/class/delete.html')
        self.response.out.write(template.render(path, template_values, True))

    def post(self):
	id = int(self.request.get('_id'))
	cl = Class.get(db.Key.from_path('Class', id)).delete()
        self.redirect("/class/list")

_URLS = (
     ('/', MainPage),
     ('/export',ExportData),
     ('/import',ImportData),
     ('/dbclear',ClearData),
     ('/class/add', AddClass),
     ('/class/edit', EditClass),
     ('/class/delete', DeleteClass),
     ('/class/list',ListClass))

def main():
    "Run the webapp"
    application = webapp.WSGIApplication(_URLS)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
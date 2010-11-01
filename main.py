import cgi
import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from google.appengine.ext.db import djangoforms

from xml.dom import minidom
from xmlExport import xmlExport
from xmlImport import xmlImportString
from models import *
    
"""
ASN2
Anonymous Social Network phase 2
"""   

class MainPage(webapp.RequestHandler):
    """
    Request handler for main page (index.html). 
    """
    def get(self):
        """
        Return the main page (index.html)
        """
        template_values = None
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'index.html')
        self.response.out.write(template.render(path, template_values, True))

class ImportData(webapp.RequestHandler):
    def get(self):
        """
        Return the import page (import.html).
        """
        template_values = None
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'import.html')
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
            path = os.path.join(directory, 'import.html')
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



class BookForm(djangoforms.ModelForm):
    class Meta:
        model = Book
        # exclude = ['isbn']

class BookList(webapp.RequestHandler):
    def get(self):
        books = Book.all()        
        template_values = {'books': books}
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'templates/booklist.html')
        self.response.out.write(template.render(path, template_values, True))


class BookAdd(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>'
                                '<form method="post" '
                                'action="/book/add">'
                                '<table>')
        # This generates the book form and writes it in the response
        self.response.out.write(BookForm())
        self.response.out.write('</table>'
                                '<input type="submit">'
                                '</form></body></html>')

    def post(self):
        data = BookForm(data=self.request.POST)
        if data.is_valid():
            self.response.out.write("valid data")
            # Save the data, and redirect to the list page
            book = data.save() #(commit=False)
            #book.added_by = users.get_current_user()
            book.put()
            self.redirect('/book/list')
        else:
            # Reprint the form, showing errors (?)
            self.response.out.write('<html><body>'
                                    '<form method="post" '
                                    'action="/book/add">'
                                    '<table>')
            self.response.out.write(data)
            self.response.out.write('</table>'
                                    '<input type="submit">'
                                    '</form></body></html>')


class BookEdit(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        book = Book.get_by_id(id)
        #key = db.Key.from_path('Book', id)
        #book = Book.get(key)
        self.response.out.write('<html><body>'
                                '<form method="POST" '
                                'action="/book/edit">'
                                '<table>')
        self.response.out.write(BookForm(instance=book))
        self.response.out.write('</table>'
                                '<input type="hidden" name="_id" value="%s">'
                                '<input type="submit">'
                                '</form></body></html>' % id)

    def post(self):
        #. so we don't use the hidden field value?
        id = int(self.request.get('id')) # get id from "?id=" in url
        #book = Book.get(db.Key.from_path('Book', id))
        book = Book.get_by_id(id)
        data = BookForm(data=self.request.POST, instance=book)
        if data.is_valid():
            # Save the data, and redirect to the view page
            entity = data.save(commit=False)
            # entity.added_by = users.get_current_user()
            entity.put()
            self.redirect('/book/list')
        else:
            # Reprint the form
            self.response.out.write('<html><body>'
                                    '<form method="POST" '
                                    'action="/book/edit">'
                                    '<table>')
            self.response.out.write(data)
            self.response.out.write('</table>'
                                    '<input type="hidden" name="_id" value="%s">'
                                    '<input type="submit">'
                                    '</form></body></html>' % id)

class BookDelete(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        #key = db.Key.from_path('Book', id)
        book = Book.get_by_id(id)
        book.delete()
        self.redirect('/book/list')



_URLS = (
     ('/', MainPage),
     ('/export',ExportData),
     ('/import',ImportData),
     ('/book/list', BookList),
     ('/book/add', BookAdd),
     ('/book/edit', BookEdit),
     ('/book/delete', BookDelete),
     ('/dbclear',ClearData)
     )

def main():
    "Run the webapp"
    application = webapp.WSGIApplication(_URLS)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

import os
from google.appengine.ext import webapp
from utils.sessions import Session
from models import *

def doRender(handler, filename='index.html', values = {}):
    """
    Render an html template file with the given dictionary values.
    The template file should be a Django html template file. 
    Handles the Session cookie also. 
    """
    
    filepath = os.path.join(os.path.dirname(__file__), '../templates/' + filename)
    if not os.path.isfile(filepath):
        handler.response.out.write("Invalid template file: " + filename)
        return False

    # copy the dictionary, so we can add things to it
    newdict = dict(values)
    newdict['path'] = handler.request.path
    newdict['recentClasses'] = Class.get_by_date()
    newdict['recentBooks'] = Book.get_by_date()
    newdict['recentPapers'] = Paper.get_by_date()
    newdict['recentInternships'] = Internship.get_by_date()
    newdict['recentPlaces'] = Place.get_by_date()
    newdict['recentGames'] = Game.get_by_date()
    handler.session = Session()
    if 'username' in handler.session:
        newdict['username'] = handler.session['username']

    if 'student_id' in handler.session:
        newdict['student_id'] = handler.session['student_id']
    
    if 'admin' in handler.session:
        newdict['admin'] = handler.session['admin']


    s = template.render(filepath, newdict)
    handler.response.out.write(s)
    return True

# Class

class ListClass(webapp.RequestHandler):
    def get(self):
        classes = Class.all()
        # classes.fetch(100)  # Class.all() can be iterated over. 
        doRender(self,'class/list.html',{'classes':classes})
        
class AddClass(webapp.RequestHandler):
    def get(self):
        doRender(self,'class/add.html',{'form':ClassForm()})

    def post(self):
        form = ClassForm(self.request.POST)
        if form.is_valid() :
            try :
                form.save()
                self.redirect("/class/list")
            except db.BadValueError, e :
                doRender(self,'class/add.html',{'form':form, 'error': "ERROR: " + e.args[0]})
        else :
            doRender(self,'class/add.html',{'form':form, 'error':'ERROR: Please correct the following errors and try again.'})
		


class EditClass(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        cl = Class.get_by_id(id)
        doRender(self,'class/add.html',{'form':ClassForm(instance=cl),'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        cl = Class.get_by_id(id)
        form = ClassForm(data = self.request.POST, instance = cl)
        form.save()
        self.redirect("/class/list")

class DeleteClass(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id'))
        cl = Class.get_by_id(id)
        doRender(self,'class/delete.html',{'cl':cl,'id':id})

    def post(self):
        id = int(self.request.get('_id'))
        cl = Class.get_by_id(id).delete()
        self.redirect("/class/list")

class ViewClass(webapp.RequestHandler):
    def get(self):
        id = int(self.request.get('id')) # get id from "?id=" in url
        class_ = Class.get_by_id(id)
        form = ClassForm(instance=class_)
        assocs = class_.studentclass_set
        doRender(self,'class/view.html',{'form':form,'class':class_,'assocs':assocs,'id':id})

    def post(self):

        #print self.request
        self.session = Session()
        student_id = self.session['student_id']
        student = Student.get_by_id(student_id)

        class_id = int(self.request.get('_id'))
        class_ = Class.get_by_id(class_id)

        rating = self.request.get('rating') # 0-100
        comment = self.request.get('comment')

        #print student, book, rating, comment
        
        # add the assocation object
        assoc = StudentClass()
        assoc.student = student
        assoc.class_ = class_
        assoc.rating = rating
        assoc.comment = comment
        assoc.put() # this will update the average rating, etc

        #self.redirect("/book/view?id=%d" % book_id)
        self.redirect("/class/list")



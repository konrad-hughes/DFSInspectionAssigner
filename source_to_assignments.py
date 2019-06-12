#!/usr/bin/env python
# coding: utf-8

# In[1]:


import arcgis
import arrow
import dateutil
import datetime
from arcgis.apps import workforce
from arcgis.gis import GIS
gis = GIS() #FOUO


# In[2]:


source = gis.content.get('d443d3ad15cf442884aa1d980b0958ef')
projectid = gis.content.get('53a74e9905e64688b40944b339cd6988')
project = workforce.Project(projectid)


# In[3]:


dispatchers = project.dispatchers.search()
dispatchers_dict = {}
for dispatcher in dispatchers:
        dispatchers_dict[dispatcher.user_id] = dispatcher
assignment_types = project.assignment_types.search()
workers = project.workers.search()
workers_dict = {}
for worker in workers:
    workers_dict[worker.user_id] = worker
sourcelayer = source.layers[0]


# In[9]:


choice = input("1 - Single Assignemt\r2 - Load Next Month Assignments\r")
if (choice == "1"):
    rfid = int(input("Enter RF ID# of facility\r"))
    where_clause = "\"RF_ID_\" = " + str(rfid)
    selection = sourcelayer.query(where=where_clause, out_fields='RF_ID_,Address_1,City,State,Zip,Due_Date,Worker,AssignmentType')
    proj_ID = selection.features[0].get_value("RF_ID_")
    proj_Due = selection.features[0].get_value("Due_Date")
    proj_Date = datetime.datetime.fromtimestamp(proj_Due / 1e3)
    proj_Worker = selection.features[0].get_value("Worker")
    proj_Assignment = selection.features[0].get_value("AssignmentType")
    if (proj_Assignment == "new"):
        proj_Type = 1
    elif (proj_Assignment == "update"):
        proj_Type = 2
    else:
        proj_Type = 3
    proj_Location = selection.features[0].get_value("Address_1") + ", " + selection.features[0].get_value("City") + ", " + selection.features[0].get_value("State") + ", " + selection.features[0].get_value("Zip")
    assignments_to_add = []
    assignment_to_add = workforce.Assignment(project)
    geometry = selection.features[0].geometry
    assignment_to_add.geometry = geometry
    assignment_to_add.due_date = proj_Date
    assignment_to_add.assignment_type = proj_Type
    assignment_to_add.location = proj_Location
    assignment_to_add.dispatcher = dispatcher
    assignment_to_add.worker = workers_dict[proj_Worker]
    assignment_to_add.assigned_date = arrow.now().to('utc').datetime
    assignment_to_add.status = "assigned"
    assignments_to_add.append(assignment_to_add)
    assignments = project.assignments.batch_add(assignments_to_add)
    
elif (choice == "2"):
    datebegin = datetime.datetime.now()
    datebeginstr = str(datebegin.year) + "-" + str(datebegin.month) + "-" + str(datebegin.day)
    dateendstr = str(datebegin.year) + "-" + str(datebegin.month + 1) + "-" + str(datebegin.day)
    is_next = "\"Due_Date\" >= date '" + datebeginstr + "' AND \"Due_Date\" <= date '" + dateendstr + "'"
    selection3 = sourcelayer.query(where=is_next)
    length = len(selection3.features)
    i=0
    assignments_to_add = []
    
    while(i<length):
        proj_ID = selection3.features[i].get_value("RF_ID_")
        proj_Due = selection3.features[i].get_value("Due_Date")
        proj_Date = datetime.datetime.fromtimestamp(proj_Due / 1e3)
        proj_Worker = selection3.features[i].get_value("Worker")
        proj_Assignment = selection3.features[i].get_value("AssignmentType")
        if (proj_Assignment == "new"):
            proj_Type = 1
        elif (proj_Assignment == "update"):
            proj_Type = 2
        else:
            proj_Type = 3
        proj_Location = selection3.features[i].get_value("Address_1") + ", " + selection3.features[i].get_value("City") + ", " + selection3.features[i].get_value("State") + ", " + selection3.features[i].get_value("Zip")
        assignment_to_add = workforce.Assignment(project)
        geometry = selection3.features[i].geometry
        assignment_to_add.geometry = geometry
        assignment_to_add.due_date = proj_Date
        assignment_to_add.assignment_type = proj_Type
        assignment_to_add.location = proj_Location
        assignment_to_add.dispatcher = dispatcher
        assignment_to_add.worker = workers_dict[proj_Worker]
        assignment_to_add.assigned_date = arrow.now().to('utc').datetime
        assignment_to_add.status = "assigned"
        assignments_to_add.append(assignment_to_add)
        i+=1
        ####

    assignments = project.assignments.batch_add(assignments_to_add)
    
    i=0
    datenow = datetime.datetime.now()
    while(i<length):
        date1 = selection3.features[i].get_value('Due_Date')
        date2 = datetime.datetime.fromtimestamp(date1 / 1e3)
        selection3.features[i].set_value('Due_Date', date2.replace(year = date2.year + 1))
        i+=1

    selection_features = selection3.features
    update_result = sourcelayer.edit_features(updates=selection_features)
    print("test")


# In[ ]:





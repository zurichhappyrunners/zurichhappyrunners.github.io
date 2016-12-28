import csv

# Parameters
curr_date = '12-28-16'
csv_folder = '/Users/jpont/Workspace/zurichhappyrunners/csv_data/'
sel_fields = ["Name", "Member ID", "Meetups attended"]

## ******** Get the global ranking ********
# Open the current file
with open(csv_folder + 'Zurich-Happy-Runners_Member_List_on_'+curr_date+'.xls', 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter='\t')

    # Get the column IDs we're interested in
    field_ids = []
    firstrow = csvreader.next()
    for field in sel_fields:
        field_ids.append(firstrow.index(field))
        
    # Create LUT
    currmembers = dict()
    for row in csvreader:
        if len(row)>0:
            currmembers[row[field_ids[1]]] = [row[field_ids[0]],  int(float(row[field_ids[2]]))]
    
# Get the current ranking
to_sort = []
for mem in currmembers:
    to_sort.append([currmembers[mem][1], mem])
to_sort.sort(reverse=True)
    
# Print ranking to file
with open(csv_folder + 'Ranking-Global-'+curr_date+'.csv', 'w') as csvfile:
    csvfile.write('"Name","Meetups attended"\n')
    for id in to_sort:
        csvfile.write('"%s",%d\n'%(currmembers[id[1]][0],currmembers[id[1]][1]))

# Display
print 'We are currently %d members.'%len(currmembers)
        
        
## ******** Get the year ranking ********
# # Open the file as of last day of previous year
# with open(csv_folder + 'Zurich-Happy-Runners_Member_List_on_12-31-16.xls', 'rb') as csvfile:
#     csvreader = csv.reader(csvfile, delimiter='\t')
#     
#     # Get the column IDs we're interested in
#     field_ids = []
#     firstrow = csvreader.next()
#     for field in sel_fields:
#         field_ids.append(firstrow.index(field))
#     
#     # Create LUT
#     members_prev_year = dict()
#     for row in csvreader:
#         if len(row)>0:
#             members_prev_year[row[field_ids[1]]] = [row[field_ids[0]], int(float(row[field_ids[2]]))]
# 
# # Get the year ranking
# to_sort = []
# for mem in currmembers:
#     # Was him/her a member last year?
#     if mem in members_prev_year:
#         to_sort.append([currmembers[mem][1]-members_prev_year[mem][1], mem])
#     else:
#         to_sort.append([currmembers[mem][1], mem])
# to_sort.sort(reverse=True)
#     
# # Print ranking to file
# with open(csv_folder + 'Ranking-Year-'+curr_date+'.csv', 'w') as csvfile:
#     csvfile.write('"Name","Meetups attended"\n')
#     for id in to_sort:
#         csvfile.write('"%s","%d"\n'%(currmembers[id[1]][0],id[0]))
#         
# # Display
# print 'There were %d members at the end of 2016.'%len(members_prev_year)

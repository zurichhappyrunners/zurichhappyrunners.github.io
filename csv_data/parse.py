import csv
import glob
import os
import re
import sys
import time


DUPLICATED_MEMBERS = {'384470221': '400085235', '287490683': '359129150'}
COUNT_CORRECTION = {'142487402': 2, '230655343': 3, '10931908': 1, '144593412': 6, '53535452': 1}
HEADERS_CSV = ['Name', 'Member ID', 'Events attended']
HEADERS_XLS = ['Name', 'Member ID', 'Meetups attended']


def lut_members_from_file(filename: str):
  if os.path.exists(filename + '.xls'):
    return lut_members_from_csv(
        filename + '.xls', delimiter='\t', headers=HEADERS_XLS
    )
  if os.path.exists(filename + '.csv'):
    return lut_members_from_csv(
        filename + '.csv', delimiter=',', headers=HEADERS_CSV
    )
  raise FileNotFoundError(filename)


def lut_members_from_csv(csv_file, delimiter, headers):
  with open(csv_file, 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=delimiter)

    # Get the column IDs we're interested in
    field_ids = []
    firstrow = next(csvreader)
    for field in headers:
      field_ids.append(firstrow.index(field))

    # Create LUT
    currmembers = dict()
    for row in csvreader:
      if len(row) > 0:
        name = row[field_ids[0]]
        member_id = row[field_ids[1]]
        times = int(float(row[field_ids[2]]))
        if member_id in DUPLICATED_MEMBERS:
          final_member_id = DUPLICATED_MEMBERS[member_id]
        else:
          final_member_id = member_id
        if final_member_id in currmembers:
          currmembers[final_member_id][1] += times
        else:
          currmembers[final_member_id] = [name, times]

  return currmembers


def print_to_file(filename, members, ids):
  with open(filename, 'w') as csvfile:
    csvfile.write('"Name","Meetups attended"\n')
    for id in ids:
      if id[0] > 0:
        csvfile.write('"%s",%d\n' % (members[id[1]][0], id[0]))


# Parameters
if len(sys.argv) > 1:
  curr_date = sys.argv[1]
else:
  curr_date = time.strftime('%Y-%m-%d')

# Global variables
download_folder = '/Users/jponttuset/Downloads/'
root_folder = '/Users/jponttuset/Workspace/Webs/zurichhappyrunners.github.io/'
csv_folder = root_folder + 'csv_data/'
html_file = root_folder + '/index.html'

# Move the file to csv folder
matches = glob.glob(
    download_folder + 'zurich-happy-runners_*_group_members.csv'
)
if matches:
  downloaded_file = matches[0]
  stored_file = (
      csv_folder + 'Zurich-Happy-Runners_Member_List_on_' + curr_date + '.csv'
  )
  os.rename(downloaded_file, stored_file)

# ******* Update the HTML *******
# Read the HTML
with open(html_file) as infile:
  html_str = infile.read()

# Look for the old date
match = re.search(r'\d{4}-\d{2}-\d{2}', html_str)
old_date = str(match.group())

# Replace the date string
html_str = html_str.replace(
    "loadAllTables('" + old_date, "loadAllTables('" + curr_date
)

# Write back to HTML file
print('Updated ' + old_date + ' to ' + curr_date)
with open(html_file, 'w') as outfile:
  outfile.write(html_str)

# ******* Get the global ranking *******
# Read the current file and create a LUT w.r.t. member ID
currmembers = lut_members_from_file(
    csv_folder + 'Zurich-Happy-Runners_Member_List_on_' + curr_date
)

# Sort ids
to_sort = []
for mem in currmembers:
  count = currmembers[mem][1]
  if mem in COUNT_CORRECTION:
    count += COUNT_CORRECTION[mem]
  to_sort.append([count, mem])
to_sort.sort(reverse=True)

# Print to file
filename = csv_folder + 'Ranking-Global-' + curr_date + '.csv'
print_to_file(filename, currmembers, to_sort)

# Display
print('Total members: %d.' % len(currmembers))

# ******** Get the years ranking ********
years = {
    '2017': {'last-before': '12-31-16', 'last-updated': '12-30-17'},
    '2018': {'last-before': '12-30-17', 'last-updated': '2018-12-29'},
    '2019': {'last-before': '2018-12-29', 'last-updated': '2019-12-31'},
    '2020': {'last-before': '2019-12-31', 'last-updated': '2020-10-23'},
    '2021': {'last-before': '2020-10-23', 'last-updated': '2021-12-27'},
    '2022': {'last-before': '2021-12-27', 'last-updated': '2022-12-31'},
    '2023': {'last-before': '2022-12-31', 'last-updated': '2023-12-28'},
    '2024': {'last-before': '2023-12-28', 'last-updated': '2025-01-02'},
    '2025': {'last-before': '2025-01-02', 'last-updated': curr_date},
}

for year in sorted(years):
  # Open the file as of last day of previous year
  members_prev_year = lut_members_from_file(
      csv_folder
      + 'Zurich-Happy-Runners_Member_List_on_'
      + years[year]['last-before']
  )
  members_this_year = lut_members_from_file(
      csv_folder
      + 'Zurich-Happy-Runners_Member_List_on_'
      + years[year]['last-updated']
  )

  # Get the year ranking
  to_sort = []
  for mem in members_this_year:
    name = members_this_year[mem][0]
    times = members_this_year[mem][1]

    if mem in COUNT_CORRECTION and year == '2024':
      times += COUNT_CORRECTION[mem]

    # Was him/her a member last year?
    if mem in members_prev_year:
      # Did they come during the year?
      if times > members_prev_year[mem][1]:
        to_sort.append([times - members_prev_year[mem][1], mem])
    else:
      # Have they ever come?
      if times > 0:
        to_sort.append([times, mem])
  to_sort.sort(reverse=True)

  # Print ranking to file
  ranking_type = year
  date = years[year]['last-updated']
  filename = csv_folder + 'Ranking-' + ranking_type + '-' + date + '.csv'
  print_to_file(filename, members_this_year, to_sort)

  # Display
  print('%s active members: %d.' % (year, len(to_sort)))

# download gradebook, rename to canvas.csv, delete all assignment columns except for the assignment you are trasnferring grades for
# download grades from gradescope, rename to gradescope.csv

from os.path import abspath, dirname, join
import csv

def calculate_score(score, lateness):
    adjusted_score = float(score)

    '''
    #for scavenger hunt where scores are scaled
    adjusted_score /= 50
    adjusted_score *= 5

    if adjusted_score > 5.0:
        adjusted_score = 5.0
    '''

    hours, minutes, seconds = lateness.split(":")
    hours_late = float(hours)
    hours_late += float(minutes) / 60
    hours_late += float(seconds) / 60 / 60

    if .25 <= hours_late < 24:
        adjusted_score *= 0.8
    elif 24 <= hours_late < 48:
        adjusted_score *= 0.6
    elif 48 <= hours_late < 72:
        adjusted_score *= 0.4
    elif 72 <= hours_late:
        adjusted_score = 0.0

    

    return round(adjusted_score, 2)



# GATHER SCORES FROM GRADESCOPE

gradescope = csv.reader(open(abspath(join(dirname(__file__), 'gradescope.csv'))))


scores = {}

next(gradescope)

for line in gradescope:
    status = line[7]
    email = line[3]
    score = line[5]
    multipass = email.split("@")[0]
    

    if status == 'Graded':
        lateness = line[10]
        scores[multipass] = calculate_score(score, lateness)

    elif status == 'Missing':
        scores[multipass] = 0



canvas = open(abspath(join(dirname(__file__), 'canvas.csv')))
canvas_csv = csv.reader(canvas, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
upload = open(abspath(join(dirname(__file__), 'upload.csv')), 'w', newline='')
upload_csv = csv.writer(upload, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

header = next(canvas_csv)

while 'Points Possible' not in header[0]:
    upload_csv.writerow(header)
    header = next(canvas_csv)
upload_csv.writerow(header)



not_in_gradescope = []

for line in canvas_csv:
    multipass = line[2]

    if multipass in scores:
        line[-1] = scores[multipass]
        upload_csv.writerow(line)
        del scores[multipass]
    else:
        line[-1] = 0
        upload_csv.writerow(line)
        not_in_gradescope.append(multipass)

canvas.close()
upload.close()

print("students in gradescope not in canvas--------------------")
for student in scores:
    print(student)

print()
print("students in canvas not in gradescope--------------------")
for student in not_in_gradescope:
    print(student)

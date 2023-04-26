from django.http import HttpResponse

from django.shortcuts import render
from django.template import loader

import pandas as pd
from plotly.offline import plot
import plotly.graph_objs as go

from render.forms import GPAForm
import os

# Create your views here.

module_dir = os.path.dirname(__file__)

## retrieve FTIAC data

file_path = os.path.join(module_dir, 'ftiac_data.csv')
df = pd.read_csv(file_path)
ftiacs = df.iloc[-1]['FTIACs']
year = df.iloc[-1]['Year']
ftiac_frame = df

## retrieve course data

file_path = os.path.join(module_dir, 'track_courses.csv')
course_frame = pd.read_csv(file_path)

courses = list(course_frame[course_frame.columns[0]])
course_dict = {}
for course in courses:
    dept, number = course.split()
    course_nums = course_dict.get(dept, [])
    course_nums.append(number)
    course_dict[dept] = course_nums

for k, v in course_dict.items():
    v.sort()

depts = list(course_dict.keys())
depts.sort()

def index(request):
    placement = None
    if request.method == 'POST':
        if 'clear' in request.POST:
            gpa_form = GPAForm()
        else:
            gpa_form = GPAForm(request.POST)
            if gpa_form.is_valid():
                gpa = gpa_form.cleaned_data['gpa']
                sat = gpa_form.cleaned_data['sat']
                act = gpa_form.cleaned_data['act']
                if gpa != None: gpa = float(gpa)
                if sat != None: sat = int(sat)
                if act != None: act = int(act)
                placement = get_placement(gpa, sat, act)
    else:
        gpa_form = GPAForm()
        
    context = {
        'gpa_form': gpa_form,
        'placement': placement
    }

    return render(request, 'render/index.html', context)

def enrollment(request):
    
    cscale = [[0.0, "rgb(128,128,255)"],
              [1.0, "rgb(255,128,128)"]]

    plot_div = plot(
        {
            'data': [
                go.Bar(x=ftiac_frame['Year'],
                       y=ftiac_frame['FTIACs'],
                       marker=dict(color=ftiac_frame['color'],
                                   colorscale=cscale)
                       )
            ],
            'layout': go.Layout(
                autosize=False,
                width=800,
                height=600,
                title="We expect " + str(ftiacs) + " FTIACs in Fall " + str(year),
                xaxis_title="Year",
                yaxis_title="FTIACs",
                font_family="Arial",
                font_size  =15,
                title_font_size=25,
                xaxis = dict(
                    tickmode='linear'
                    )
            ),            
        },
        output_type='div',
        include_plotlyjs=False)


    context = {
        'ftiacs': ftiacs,
        'year': year,
        'plot_div': plot_div,
        'depts': depts
    }
    return render(request, 'render/enrollment.html', context)

def get_placement(gpa, sat, act):
    if gpa == None and sat == None and act == None: return "No MTH placement"
    if gpa != None:
        if sat == None and act == None:
            if gpa <= 3.2: return "MTH 108"
            if gpa <= 3.7: return "MTH 108 Fulfilled"
            return "MTH 110 Fulfilled"

        if sat != None:
            if -11.1 + 0.87 * gpa + 0.020 * sat < 0: return "MTH 108"
            if -14.5 + 1.35 * gpa + 0.019 * sat < 0: return "MTH 108 Fulfilled"
            if -18.6 + 1.83 * gpa + 0.018 * sat < 0: return "MTH 110 Fulfilled"
            return "MTH 122 & MTH 123 Fulfilled"

        if -11.1 + 0.87 * gpa + 0.020 * (17.9*act + 153.6) < 0: return "MTH 108"
        if -14.5 + 1.35 * gpa + 0.019 * (17.9*act + 153.6) < 0: return "MTH 108 Fulfilled"
        if -18.6 + 1.83 * gpa + 0.018 * (17.9*act + 153.6) < 0: return "MTH 110 Fulfilled"
        return "MTH 122 & MTH 123 Fulfilled"

    if sat != None:
        if sat <= 450: return "MTH 108"
        if sat <= 520: return "MTH 108 Fulfilled"
        if sat <= 680: return "MTH 110 Fulfilled"
        return "MTH 122 & MTH 123 Fulfilled"

    sat_inferred = 17.9*act + 153.6
    if sat_inferred <= 450: return "MTH 108"
    if sat_inferred <= 520: return "MTH 108 Fulfilled"
    if sat_inferred <= 680: return "MTH 110 Fulfilled"
    return "MTH 122 & MTH 123 Fulfilled"


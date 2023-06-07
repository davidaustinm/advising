from django.http import HttpResponse

from django.shortcuts import render
from django.template import loader

import pandas as pd
from plotly.offline import plot
import plotly.graph_objs as go

from render.forms import GPAForm
import os
import itertools

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
                title={
                    'text':"We expect " + str(ftiacs) + " FTIACs in Fall " + str(year),
                    'xanchor':'left',
                    'yanchor':'top',
                    'y':0.9,
                    'x':0.1
                },
                xaxis_title="Year",
                yaxis_title="FTIACs",
                font_family="Arial",
                font_size  =15,
                title_font_size=30,
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

'''
def dept(request, dept):
    courses = course_dict[dept]
    semester = 'Fall ' + str(year)

    last_year = 'Fall ' + str(year - 1)
    current_year = 'Fall ' + str(year)

    module_dir = os.path.dirname(__file__)  
    file_path = os.path.join(module_dir, 'weekly_enrollment.csv')
    df = pd.read_csv(file_path, skiprows=5)

    col_dict = {df.columns[0]: 'Semester', df.columns[1]: 'Course'}
    df = df.rename(columns = col_dict)

    def good_year(x):
        return x == last_year or x == current_year
    
    df = df[df['Semester'].apply(good_year)]

    file_path = os.path.join(module_dir, 'attendance.csv')
    att = pd.read_csv(file_path, index_col=0).T
    att = att[att['total'].isna() == False]
    att['total'] = att['total'].astype(int)
    total_attended = att['total'].sum()
    fraction_attended = total_attended/ftiacs

    plots = []
    for course in courses:
        course_num = dept + " " + course
        try :
            course_df = df[df['Course'] == course_num].set_index('Semester').T
            seats = course_df[current_year].loc['Seats']
            weeks = ['Week ' + str(w) for w in range(1,26)]
            course_df = course_df.loc[weeks]
            missing = course_df.iloc[-1][current_year]

            current = course_df[course_df[current_year] != missing]
            baseline = int(current.loc['Week 7'][current_year])
            current_enrollment = int(current.iloc[-1][current_year])

            W = int(baseline + (current_enrollment - baseline)/fraction_attended)
            current = current.reset_index()

            course_df['W'] = W       
            course_df['Seats'] = seats
            course_df = course_df.reset_index()

            data = [
                go.Scatter(x=current['index'],
                           y=current[current_year].astype(int),
                           mode='lines+markers',
                           name=current_year)
            ]
                
            if last_year in course_df.columns:
                data.append(
                    go.Scatter(x=course_df['index'],
                               y=course_df[last_year].astype(int),
                               mode='lines+markers',
                               name=last_year))
            data += [
                go.Scatter(x=course_df['index'],
                           y=course_df['Seats'],
                           mode='lines+markers',
                           name='Current Seats'),
                go.Scatter(x=course_df['index'],
                           y=course_df['W'],
                           mode='lines+markers',
                           name='Predicted Seats')
            ]

            plot_div = plot(
                {
                    'data': data,
                    
                    'layout': go.Layout(
                        autosize=False,
                        width=1000,
                        height=600,
                        title={
                            'text':"We expect " + str(W) + " students to be enrolled in " + course_num + " this Fall",
                            'xanchor':'left',
                            'yanchor':'top',
                            'x':0.1,
                            'y':0.9
                        },
                        xaxis_title="Week",
                        yaxis_title="Students enrolled",
                        font_family="Arial",
                        font_size  =15,
                        title_font_size=24
                    ),
                    
                },
                output_type='div',
                include_plotlyjs=False)
            plots.append(plot_div)

        except:
            continue
        

    if len(plots) == 0:
        plots = None
    
    context = {
        'dept':dept,
        'depts': depts,
        'plots': plots
    }
    return render(request, 'render/dept.html', context)
'''

def dept(request, dept):
    courses = course_dict[dept]
    semester = 'Fall ' + str(year)
    fall_semester = semester
    winter_semester = 'Winter ' + str(year + 1)

    last_year = 'Fall ' + str(year - 1)
    current_year = 'Fall ' + str(year)

    module_dir = os.path.dirname(__file__)  
    file_path = os.path.join(module_dir, 'weekly_enrollment.csv')
    df = pd.read_csv(file_path, skiprows=5)

    col_dict = {df.columns[0]: 'Semester', df.columns[1]: 'Course'}
    df = df.rename(columns = col_dict)

    file_path = os.path.join(module_dir, 'attendance.csv')
    att = pd.read_csv(file_path, index_col=0).T
    att = att[att['total'].isna() == False]
    att['total'] = att['total'].astype(int)
    total_attended = att['total'].sum()
    fraction_attended = total_attended/ftiacs

    file_path = os.path.join(module_dir, 'caps.csv')
    managed_caps = pd.read_csv(file_path)
    caps = {sem: managed_caps[managed_caps['Semester'] == sem].set_index('Course')
            for sem in [fall_semester, winter_semester]}

    fall_plots = []
    winter_plots = []
    for course, semester in itertools.product(courses, [fall_semester, winter_semester]):
        course_num = dept + " " + course
        term, yr = semester.split()
        current_year = semester
        last_year = term + ' ' + str(int(yr) - 1)
    
        semester_df = df[df['Semester'].apply(lambda x: x == current_year or x == last_year)]
        
        try :
            course_df = semester_df[semester_df['Course'] == course_num].set_index('Semester').T
            seats = course_df[current_year].loc['Seats']
            current_seats = int(seats)
            try :
                released = float(caps[semester].loc[course_num]['% Released'])
                current_seats = int(round(float(seats) * 100 /released))
            except:
                pass
            
            weeks = ['Week ' + str(w) for w in range(1,26)]
            course_df = course_df.loc[weeks]
            missing = course_df.iloc[-1][current_year]

            current = course_df[course_df[current_year] != missing]
            baseline = int(current.loc['Week 7'][current_year])
            current_enrollment = int(current.iloc[-1][current_year])

            W = int(baseline + (current_enrollment - baseline)/fraction_attended)
            current = current.reset_index()

            course_df['W'] = W       
            course_df['Seats'] = current_seats
            course_df = course_df.reset_index()

            data = [
                go.Scatter(x=current['index'],
                           y=current[current_year].astype(int),
                           mode='lines+markers',
                           name=current_year)
            ]
                
            if last_year in course_df.columns:
                data.append(
                    go.Scatter(x=course_df['index'],
                               y=course_df[last_year].astype(int),
                               mode='lines+markers',
                               name=last_year))
            data += [
                go.Scatter(x=course_df['index'],
                           y=course_df['Seats'],
                           mode='lines+markers',
                           name='Current Seats'),
                go.Scatter(x=course_df['index'],
                           y=course_df['W'],
                           mode='lines+markers',
                           name='Predicted Seats')
            ]

        except:
            continue
        plot_div = plot(
            {
                'data': data,
                    
                'layout': go.Layout(
                    autosize=False,
                    width=1000,
                    height=600,
                    title={
                        'text':"We expect " + str(W) + " students to be enrolled in " + course_num + " this " + semester.split()[0],
                        'xanchor':'left',
                        'yanchor':'top',
                        'x':0.1,
                        'y':0.9
                    },
                    xaxis_title="Week",
                    yaxis_title="Students enrolled",
                    font_family="Arial",
                    font_size  =15,
                    title_font_size=24
                ),
                
            },
            output_type='div',
            include_plotlyjs=False)
        if semester.startswith('Fall'):
            fall_plots.append(plot_div)
        else:
            winter_plots.append(plot_div)

    if len(fall_plots) == 0:
        fall_plots = None
    if len(winter_plots) == 0:
        winter_plots = None
    
    context = {
        'dept':dept,
        'depts': depts,
        'courses': courses,
        'fall': fall_semester,
        'winter': winter_semester,
        'fallplots': fall_plots,
        'winterplots': winter_plots
    }
    return render(request, 'render/dept.html', context)


    
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


from django.http import HttpResponse

from django.shortcuts import render
from django.template import loader

import pandas as pd
from plotly.offline import plot
import plotly.graph_objs as go

from render.forms import GPAForm
import os

# Create your views here.

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
    
    module_dir = os.path.dirname(__file__)  
    file_path = os.path.join(module_dir, 'ftiac_data.csv')
    df = pd.read_csv(file_path)
    ftiacs = df.iloc[-1]['FTIACs']
    year = df.iloc[-1]['Year']

    ftiac_frame = df.set_index('Year')

    plot_div = plot(
        {
            'data': [
                go.Scatter(x=df['SESSION'],
                           y=df['CUMULATIVE_2018'],
                           mode='lines+markers',
                           name='2022'),
                go.Scatter(x=df['SESSION'],
                           y=df['CUMULATIVE_2021'],
                           mode='lines+markers',
                           name='2021'),
                go.Scatter(x=df['SESSION'],
                           y=df['FTIACS'],
                           mode='lines+markers',
                           name='Predicted FTIACs')
            ],
            'layout': go.Layout(
                title="Number of Students attending Orientation",
                xaxis_title="Session",
                yaxis_title="Orientation attendees",
                font_family="Arial",
                font_size  =15,
                title_font_size=30
            ),            
        },
        output_type='div',
        include_plotlyjs=False)

    context = {
        'ftiacs': ftiacs,
        'year': year,
        'plot_div': plot_div
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


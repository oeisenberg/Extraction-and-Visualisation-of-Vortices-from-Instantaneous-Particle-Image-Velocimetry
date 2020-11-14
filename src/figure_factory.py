import math
import test
import pandas as pd
from Utility import *
from DataType import *
import track_vortices
import holoviews as hv
import plotly.io as pio
from holoviews import opts
import tracking_techniques
import extraction_techniques
from pandas import DataFrame
import matplotlib.pyplot as plt
import chart_studio.plotly as py
import plotly.graph_objects as go
import plotly.figure_factory as ff
from mpl_toolkits.mplot3d import Axes3D
from holoviews.streams import Stream, param

# Figure factory for creating complex figures using Plotly
#
# The factory supports annimated traces on the same figure,
# this was inspired by the online plot available here: 
# https://chart-studio.plotly.com/~empet/15557/animate-succesively-two-traces-in-the-sa/#/,
# which demonstrates the functionality on random line graphs

# combination of contextual and parallel annimation
def parallel_contextual_annimation(dataframes, x_axis=[-300, 0], y_axis=[-100, 100], plt_width=900, plt_height=600, frame_duration=400):
    dataframe = dataframes[0]
    main_quivers = dataframes[1]
    quivers = dataframes[2]
    samples = list(set(dataframe.Frame))
    n_frames = samples[-1:][0] + 1
    samples = list(map(str, samples))
    fam_idxs = list(set(dataframe.Fam_idx))

    dataset_by_frame = dataframe[dataframe["Frame"] == 0]
    dataset_by_nextframe = dataframe[dataframe["Frame"] == 1]
    quivers_by_frame = quivers[quivers["Frame"] == 0]
    main_quivers_by_frame = main_quivers[main_quivers["Frame"] == 0]  
        
    cMin = min(dataframe["Fam_idx"])
    cMax = max(dataframe["Fam_idx"])
        
    fig = go.Figure()
    fig.add_scatter(x=list(dataset_by_nextframe["X"]),
                    y=list(dataset_by_nextframe["Y"]), 
                    mode='markers',
                    opacity=0.8,
                    marker=dict(
                        size = 3,
                        color=list(dataset_by_nextframe["Fam_idx"]),
                        cmin=cMin,
                        cmax=cMax
                    ),
                    name='Vortices +1',
                    hovertext = ["Vortex ID: " + str(point[0]) +
                                "<br>Size: " + str(point[1]) +
                                "<br>Magnitude: " + str(round(point[4],2)) 
                                for point in list(zip(
                                                        list(dataset_by_nextframe["Id"]), list(dataset_by_nextframe["Size"]), list(dataset_by_nextframe["U"]), list(dataset_by_nextframe["V"]), list(dataset_by_nextframe["Velmag"])))
                                ],
                    visible=True)
    fig.add_scatter(x=list(dataset_by_frame["X"]),
                    y=list(dataset_by_frame["Y"]), 
                    mode='markers',
                    marker=dict(
                        color=list(dataset_by_frame["Fam_idx"]),
                        cmin=cMin,
                        cmax=cMax
                    ),
                    name='Vortices',
                    hovertext = ["Vortex ID: " + str(point[0]) +
                                "<br>Size: " + str(point[1]) +
                                "<br>Magnitude: " + str(round(point[4],2)) 
                                for point in list(zip(
                                                        list(dataset_by_frame["Id"]), list(dataset_by_frame["Size"]), list(dataset_by_frame["U"]), list(dataset_by_frame["V"]), list(dataset_by_frame["Velmag"])))
                                ],
                    visible=True)
    quiver = ff.create_quiver(quivers_by_frame["X"],
                            quivers_by_frame["Y"],
                            quivers_by_frame["U"],
                            quivers_by_frame["V"],
                            scale=0.5,
                            name='Quivers').data[0]
    main_quiver = ff.create_quiver(main_quivers_by_frame["X"],
                                main_quivers_by_frame["Y"],
                                main_quivers_by_frame["U"],
                                main_quivers_by_frame["V"],
                                scale=0.5,
                                name='Vortex Quivers').data[0]
    fig.add_traces(quiver)
    fig.add_traces(main_quiver)

    frames = [] 
    for frame in range(n_frames):
        dataset_by_frame = dataframe[dataframe["Frame"] == frame]
        dataset_by_nextframe = dataframe[dataframe["Frame"] == frame+1]
        quivers_by_frame = quivers[quivers["Frame"] == frame]
        main_quivers_by_frame = main_quivers[main_quivers["Frame"] == frame]  
        frames.append(go.Frame(data=[
                                go.Scatter(
                                    x=list(dataset_by_nextframe["X"]),
                                    y=list(dataset_by_nextframe["Y"]), 
                                    marker=dict(
                                        color=list(dataset_by_nextframe["Fam_idx"]),
                                        cmin=cMin,
                                        cmax=cMax
                                    ),
                                    hovertext = ["Vortex ID: " + str(point[0]) +
                                                "<br>Size: " + str(point[1]) +
                                                "<br>Magnitude: " + str(round(point[4],2)) 
                                                for point in list(zip(
                                                    list(dataset_by_nextframe["Id"]), list(dataset_by_nextframe["Size"]), list(dataset_by_nextframe["U"]), list(dataset_by_nextframe["V"]), list(dataset_by_nextframe["Velmag"])))
                                                ],
                                ),
                                go.Scatter(
                                    x=list(dataset_by_frame["X"]),
                                    y=list(dataset_by_frame["Y"]), 
                                    marker=dict(
                                        color=list(dataset_by_frame["Fam_idx"]), 
                                        cmin=cMin,
                                        cmax=cMax
                                    ),
                                    hovertext = ["Vortex ID: " + str(point[0]) +
                                                "<br>Size: " + str(point[1]) +
                                                "<br>Magnitude: " + str(round(point[4],2)) 
                                                for point in list(zip(
                                                    list(dataset_by_frame["Id"]), list(dataset_by_frame["Size"]), list(dataset_by_frame["U"]), list(dataset_by_frame["V"]), list(dataset_by_frame["Velmag"])))
                                                ],
                                ),
                                ff.create_quiver(
                                    quivers_by_frame["X"],
                                    quivers_by_frame["Y"],
                                    quivers_by_frame["U"],
                                    quivers_by_frame["V"],
                                    scale=0.5,
                                    hovertext = [
                                        "U: " + str(point[0]) +
                                        "V: " + str(point[1])
                                        for point in list(zip(
                                            list(dataset_by_frame["U"]), list(dataset_by_frame["V"])))
                                    ],
                                    name='Quivers').data[0],
                                ff.create_quiver(
                                    main_quivers_by_frame["X"],
                                    main_quivers_by_frame["Y"],
                                    main_quivers_by_frame["U"],
                                    main_quivers_by_frame["V"],
                                    scale=0.3,
                                    hovertext = [
                                        "U: " + str(point[0]) +
                                        "V: " + str(point[1])
                                        for point in list(zip(
                                            list(main_quivers_by_frame["U"]), list(main_quivers_by_frame["V"])))
                                    ],
                                    name='Vortex Quivers').data[0]
                                ],
                        traces=[0,1,2,3],  #the scatter in instance in Frame.data[j] updates fig.data[j], j=0,1
                        name=f'fr{frame}')) 
                                        
    button_anim = dict(
                label='Play Animation',
                method='animate',
                args=[None, dict(frame=dict(duration=frame_duration, redraw=False), 
                                transition=dict(duration=0),
                                fromcurrent=True,
                                mode='immediate')])

    fig.update_layout(title_text='Parallel Contextual Annimation',
                    title_x=0.5,
                    width=plt_width, height=plt_height,
                    xaxis_range=x_axis,
                    yaxis_range=y_axis,
                    updatemenus= [{'type': 'buttons', 
                                    'buttons': [button_anim],
                                    'x': 1.05,
                                    'y': 0,
                                    'xanchor': 'left',
                                    'yanchor': 'bottom'}]
                    )  

    sliders = [dict(steps = [dict(method= 'animate',
                                args= [[f'fr{k}'],                           
                                dict(mode= 'immediate',
                                    frame= dict(duration=frame_duration, redraw= False),
                                    transition=dict(duration=0))
                                    ],
                                label=f'fr: {k}'
                                ) for k in range(n_frames)], 
                    x=0, # slider starting position  
                    y=0, 
                len=1.0) #slider length
            ]

    fig.update_layout(sliders=sliders,
                      xaxis_title_text='X (mm)', # xaxis label
                      yaxis_title_text='Y (mm)') # yaxis label)# Optional
    fig.frames = frames
    fig

    return fig

def contextual_annimation(dataframes, x_axis=[-300, 0], y_axis=[-100, 100], plt_width=900, plt_height=600, frame_duration=400):
    dataframe = dataframes[0]
    main_quivers = dataframes[1]
    quivers = dataframes[2]
    samples = list(set(dataframe.Frame))
    n_frames = samples[-1:][0]
    samples = list(map(str, samples))
    fam_idxs = list(set(dataframe.Fam_idx))

    fig = go.Figure()

    cMin = min(dataframe["Fam_idx"])
    cMax = max(dataframe["Fam_idx"])

    dataset_by_frame = dataframe[dataframe["Frame"] == 0]
    quivers_by_frame = quivers[quivers["Frame"] == 0]
    main_quivers_by_frame = main_quivers[main_quivers["Frame"] == 0]
    
    fig.add_scatter(x=list(dataset_by_frame["X"]),
                    y=list(dataset_by_frame["Y"]), 
                    mode='markers',
                    marker=dict(
                        color=list(dataset_by_frame["Fam_idx"]),
                        cmin=cMin,
                        cmax=cMax
                    ),
                    name='Vortices',
                    hovertext = ["Vortex ID: " + str(point[0]) +
                                 "<br>Size: " + str(point[1]) +
                                 "<br>Magnitude: " + str(round(point[4],2)) 
                                 for point in list(zip(
                                                        list(dataset_by_frame["Id"]), list(dataset_by_frame["Size"]), list(dataset_by_frame["U"]), list(dataset_by_frame["V"]), list(dataset_by_frame["Velmag"])))
                                ],
                    visible=True)
    quiver = ff.create_quiver(quivers_by_frame["X"],
                            quivers_by_frame["Y"],
                            quivers_by_frame["U"],
                            quivers_by_frame["V"],
                            scale=0.5,
                            name='Quivers').data[0]
    main_quiver = ff.create_quiver(main_quivers_by_frame["X"],
                                main_quivers_by_frame["Y"],
                                main_quivers_by_frame["U"],
                                main_quivers_by_frame["V"],
                                scale=0.5,
                                name='Vortex Quivers').data[0]
    fig.add_traces(quiver)
    fig.add_traces(main_quiver)
    frames = [] 

    for frame in range(n_frames):
        dataset_by_frame = dataframe[dataframe["Frame"] == frame]
        quivers_by_frame = quivers[quivers["Frame"] == frame]
        main_quivers_by_frame = main_quivers[main_quivers["Frame"] == frame]
        frames.append(go.Frame(data=[
                                    go.Scatter(
                                        x=list(dataset_by_frame["X"]),
                                        y=list(dataset_by_frame["Y"]), 
                                        marker=dict(
                                            color=list(dataset_by_frame["Fam_idx"]),
                                            cmin=cMin,
                                            cmax=cMax
                                        ),
                                        hovertext = ["Vortex ID: " + str(point[0]) +
                                                    "<br>Size: " + str(point[1]) +
                                                    "<br>Magnitude: " + str(round(point[4],2)) 
                                                    for point in list(zip(
                                                        list(dataset_by_frame["Id"]), list(dataset_by_frame["Size"]), list(dataset_by_frame["U"]), list(dataset_by_frame["V"]), list(dataset_by_frame["Velmag"])))
                                                    ],
                                    ),
                                    ff.create_quiver(
                                        quivers_by_frame["X"],
                                        quivers_by_frame["Y"],
                                        quivers_by_frame["U"],
                                        quivers_by_frame["V"],
                                        scale=0.5,
                                        hovertext = [
                                            "U: " + str(point[0]) +
                                            "V: " + str(point[1])
                                            for point in list(zip(
                                                list(dataset_by_frame["U"]), list(dataset_by_frame["V"])))
                                        ],
                                        name='Quivers').data[0],
                                    ff.create_quiver(
                                        main_quivers_by_frame["X"],
                                        main_quivers_by_frame["Y"],
                                        main_quivers_by_frame["U"],
                                        main_quivers_by_frame["V"],
                                        scale=0.3,
                                        hovertext = [
                                            "U: " + str(point[0]) +
                                            "V: " + str(point[1])
                                            for point in list(zip(
                                                list(main_quivers_by_frame["U"]), list(main_quivers_by_frame["V"])))
                                        ],
                                        name='Vortex Quivers').data[0]
                                    ],
                            traces=[0,1,2],  #the scatter in instance in Frame.data[j] updates fig.data[j], j=0,1
                            name=f'fr{frame}'))
        
    button_anim = dict(
                label='Play Animation',
                method='animate',
                args=[None, dict(frame=dict(duration=frame_duration, redraw=False), 
                                transition=dict(duration=0),
                                fromcurrent=True,
                                mode='immediate')])
                                            
    fig.update_layout(title_text='Hybrid Plot',
                    title_x=0.5,
                    width=plt_width, height=plt_height,
                    xaxis_range=x_axis,
                    yaxis_range=y_axis,
                    updatemenus= [{'type': 'buttons', 
                                    'buttons': [button_anim],
                                    'x': 1.05,
                                    'y': 0,
                                    'xanchor': 'left',
                                    'yanchor': 'bottom'}])  
                                      
    # sliders = [
    #     dict(
    #         steps = [
    #             dict(
    #                 method= 'animate',
    #                 args = [
    #                     [f'fr{k}'],                           
    #                     dict(mode = 'immediate',
    #                          frame = dict(duration=frame_duration, redraw=True),
    #                          transition = dict(duration= 0))
    #                     ],
    #                 label = f'fr: {k}'
    #                 ) for k in range(n_frames)
    #             ], 
    #         x=0, # slider starting position  
    #         y=0, 
    #         len=1.0
    #     ) #slider length
    # ]
    sliders = [dict(steps = [dict(method= 'animate',
                              args= [[f'fr{k}'],                           
                              dict(mode= 'immediate',
                                   frame= dict(duration=frame_duration, redraw= False),
                                   transition=dict(duration= 0))
                                 ],
                              label=f'fr: {k}'
                             ) for k in range(n_frames)], 
                x=0, # slider starting position  
                y=0, 
               len=1.0) #slider length
           ]
    fig.update_layout(sliders=sliders)
    fig.frames = frames

    return fig

def parallel_annimation(dataframes, x_axis=[-300, 0], y_axis=[-100, 100], plt_width=900, plt_height=600, frame_duration=400):
    dataframe = dataframes[0]
    main_quivers = dataframes[1]
    quivers = dataframes[2]
    samples = list(set(dataframe.Frame))
    n_frames = samples[-1:][0]
    samples = list(map(str, samples))
    fam_idxs = list(set(dataframe.Fam_idx))

    fig = go.Figure()

    cMin = min(dataframe["Fam_idx"])
    cMax = max(dataframe["Fam_idx"])

    dataset_by_frame = dataframe[dataframe["Frame"] == 0]
    dataset_by_nextframe = dataframe[dataframe["Frame"] == 1]
    
    fig.add_scatter(x=list(dataset_by_nextframe["X"]),
                    y=list(dataset_by_nextframe["Y"]), 
                    mode='markers',
                    opacity=0.8,
                    marker=dict(
                        size = 3,
                        color=list(dataset_by_nextframe["Fam_idx"]),
                        cmin=cMin,
                        cmax=cMax
                    ),
                    name='Vortices +1',
                    hovertext = ["Vortex ID: " + str(point[0]) +
                                 "<br>Size: " + str(point[1]) +
                                 "<br>Magnitude: " + str(round(point[4],2)) 
                                 for point in list(zip(
                                                        list(dataset_by_nextframe["Id"]), list(dataset_by_nextframe["Size"]), list(dataset_by_nextframe["U"]), list(dataset_by_nextframe["V"]), list(dataset_by_nextframe["Velmag"])))
                                ],
                    visible=True)
    fig.add_scatter(x=list(dataset_by_frame["X"]),
                    y=list(dataset_by_frame["Y"]), 
                    mode='markers',
                    marker=dict(
                        color=list(dataset_by_frame["Fam_idx"]),
                        cmin=cMin,
                        cmax=cMax
                    ),
                    name='Vortices',
                    hovertext = ["Vortex ID: " + str(point[0]) +
                                 "<br>Size: " + str(point[1]) +
                                 "<br>Magnitude: " + str(round(point[4],2)) 
                                 for point in list(zip(
                                                        list(dataset_by_frame["Id"]), list(dataset_by_frame["Size"]), list(dataset_by_frame["U"]), list(dataset_by_frame["V"]), list(dataset_by_frame["Velmag"])))
                                ],
                    visible=True)

    frames = [] 

    for frame in range(n_frames):
        dataset_by_frame = dataframe[dataframe["Frame"] == frame]
        dataset_by_nextframe = dataframe[dataframe["Frame"] == frame+1]
        frames.append(go.Frame(data=[
                                    go.Scatter(
                                        x=list(dataset_by_nextframe["X"]),
                                        y=list(dataset_by_nextframe["Y"]), 
                                        marker=dict(
                                            color=list(dataset_by_nextframe["Fam_idx"]),
                                            cmin=cMin,
                                            cmax=cMax
                                        ),
                                        hovertext = ["Vortex ID: " + str(point[0]) +
                                                    "<br>Size: " + str(point[1]) +
                                                    "<br>Magnitude: " + str(round(point[4],2)) 
                                                    for point in list(zip(
                                                        list(dataset_by_nextframe["Id"]), list(dataset_by_nextframe["Size"]), list(dataset_by_nextframe["U"]), list(dataset_by_nextframe["V"]), list(dataset_by_nextframe["Velmag"])))
                                                    ],
                                    ),
                                    go.Scatter(
                                        x=list(dataset_by_frame["X"]),
                                        y=list(dataset_by_frame["Y"]), 
                                        marker=dict(
                                            color=list(dataset_by_frame["Fam_idx"]),
                                            cmin=cMin,
                                            cmax=cMax
                                        ),
                                        hovertext = ["Vortex ID: " + str(point[0]) +
                                                    "<br>Size: " + str(point[1]) +
                                                    "<br>Magnitude: " + str(round(point[4],2)) 
                                                    for point in list(zip(
                                                        list(dataset_by_frame["Id"]), list(dataset_by_frame["Size"]), list(dataset_by_frame["U"]), list(dataset_by_frame["V"]), list(dataset_by_frame["Velmag"])))
                                                    ],
                                    )
                                    ],
                            traces=[0,1],  #the scatter in instance in Frame.data[j] updates fig.data[j], j=0,1
                            name=f'fr{frame}'))
        
    button_anim = dict(
                label='Play Animation',
                method='animate',
                args=[None, dict(frame=dict(duration=frame_duration, redraw=False), 
                                transition=dict(duration=0),
                                fromcurrent=True,
                                mode='immediate')])
                                            
    fig.update_layout(title_text='Hybrid Plot',
                    title_x=0.5,
                    width=plt_width, height=plt_height,
                    xaxis_range=x_axis,
                    yaxis_range=y_axis,
                    updatemenus= [{'type': 'buttons', 
                                    'buttons': [button_anim],
                                    'x': 1.05,
                                    'y': 0,
                                    'xanchor': 'left',
                                    'yanchor': 'bottom'}])  
                                      
    sliders = [
        dict(
            steps = [
                dict(
                    method= 'animate',
                    args = [
                        [f'fr{k}'],                           
                        dict(mode = 'immediate',
                             frame = dict(duration=frame_duration, redraw=True),
                             transition = dict(duration= 0))
                        ],
                    label = f'frame: {k}'
                    ) for k in range(n_frames)
                ], 
            x=0, # slider starting position  
            y=0, 
            len=1.0
        ) #slider length
    ]
    fig.update_layout(sliders=sliders)
    fig.frames = frames

    return fig
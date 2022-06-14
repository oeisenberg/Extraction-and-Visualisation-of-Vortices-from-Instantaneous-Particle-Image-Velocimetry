# Extraction & Visualisation of Vortices from Instantaneous Particle Image Velocimetry (PIV)

## Introduction
The purpose is of this publication is to demonstrate my final year project that I completed during my time at the University of Bath as part of my BSc degree. The final dissertation and codebase are provided.

### Dissertation Abstract
Within Formula One, data gathered from Computational Fluid Dynamics (CFD) does not always correspond to the telemetry collected on the racetrack, where a higher correlation between the sources allows for CFD to carry more weight
resulting in successful aerodynamic packages. To improve correlation, Formula One teams use wind tunnels with a scale model of their car to reproduce conditionsin both CFD and the racetrack. This paper focuses on the visualisation of data measured from the tunnel using Particle Image Velocimetry. Flow visualisation has undergone lots of research and this document explores the current state of the art and applies vortex extraction and visualisation techniques to a time-dependent data set, provided by Scuderia Toro Rosso, to allow for a meaningful interpretation of data.

### Jupyter Notebook
To demonstrate the work completed the code is presented within a Jypyer Notebook, the outputs for which have been compiled as html files with embedded, interactive graphs.

## Details
The file `eisenberg-ohe-walkthrough.html` illistrates the procedure when investigating the problem. The file walks the reader through importing and converting the raw data files into a format ready to be analysed and plot while detailing some of the challenges encountered during the process. 

![Raw Quiver Plot](https://github.com/oeisenberg/Extraction-and-Visualisation-of-Vortices-from-Instantaneous-Particle-Image-Velocimetry/raw/RepoInit/img/initial_quiverplot.png "Raw Quiver Plot")

The process led to the revelation of two visualisation techniques using annimation to collapse temporal data into two dimensions. The two visualisation techniques presented are Parallel Annimations and Contextual Plots which can be combined to form a three dimensional Parrallel Contextual Annimation.

![Parrallel Contextual Annimation Plot](https://github.com/oeisenberg/Extraction-and-Visualisation-of-Vortices-from-Instantaneous-Particle-Image-Velocimetry/raw/RepoInit/img/mock_up_hybrid.png "Parrallel Contextual Annimation")


## Final Output
![Hybrid Plot](https://github.com/oeisenberg/Extraction-and-Visualisation-of-Vortices-from-Instantaneous-Particle-Image-Velocimetry/raw/RepoInit/img/Front-End.png "Parrallel Contextual Annimation - Jupyter Notebook")

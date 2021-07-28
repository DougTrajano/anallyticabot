import plotly.io as pio

def setup_plotly_theme():
    # create our dark theme from the plotly_dark template
    pio.templates["dark"] = pio.templates["plotly_dark"]

    # set the paper_bgcolor and the plot_bgcolor to a new color
    pio.templates["dark"]['layout']['paper_bgcolor'] = "#22272e"
    pio.templates["dark"]['layout']['plot_bgcolor'] = "#22272e"

    # you may also want to change gridline colors if you are modifying background
    pio.templates['dark']['layout']['yaxis']['gridcolor'] = "#adbac4"
    pio.templates['dark']['layout']['xaxis']['gridcolor'] = "#adbac4"

    pio.templates["dark"]["layout"]["font"]["color"] = "#adbac4"
    pio.templates.default = "dark"
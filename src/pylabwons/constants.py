RISE = '#D24D3E'
FALL = '#1261C4'

XAXIS = lambda **kwargs: dict({
    "autorange": True,              # [str | bool] one of ( True | False | "reversed" | "min reversed" |
                                    #                       "max reversed" | "min" | "max" )
    "color": "#444",                # [str]
    "showgrid": True,               # [bool]
    "gridcolor": "lightgrey",       # [str]
    "griddash": "solid",            # [str] one of ( "solid" | "dot" | "dash" | "longdash" | "dashdot" )
    "gridwidth": 0.5,               # [float]
    "showline": True,               # [bool]
    "linecolor": "grey",            # [str]
    "linewidth": 1,                 # [float]
    "mirror": False,                # [str | bool] one of ( True | "ticks" | False | "all" | "allticks" )
    "rangeslider": {
        "visible": False            # [bool]
    },
    "rangeselector": {
        "visible": True,            # [bool]
        "bgcolor": "#eee",          # [str]
        "bordercolor": "#444",      # [str]
        "borderwidth": 0,           # [float]
        "buttons": [
            dict(count=1, label="1M", step="month", stepmode="backward"),
            dict(count=3, label="3M", step="month", stepmode="backward"),
            dict(count=6, label="6M", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1Y", step="year", stepmode="backward"),
            dict(step="all")
        ],
        "xanchor" : "left",         # [str] one of ( "auto" | "left" | "center" | "right" )
        "x" : 0.005,                # [float]
        "yanchor" : "bottom",       # [str] one of ( "auto" | "top" | "middle" | "bottom" )
        "y" : 1.0                   # [float]
    },
    "showticklabels": True,         # [bool]
    "tickformat": "%Y/%m/%d",       # [str]
    "zeroline": True,               # [bool]
    "zerolinecolor": "lightgrey",   # [str]
    "zerolinewidth": 1              # [float]
}, **kwargs)

YAXIS = lambda **kwargs: dict({
    "autorange": True,              # [str | bool] one of ( True | False | "reversed" | "min reversed" |
                                    #                       "max reversed" | "min" | "max" )
    "color": "#444",                # [str]
    "showgrid": True,               # [bool]
    "gridcolor": "lightgrey",       # [str]
    "griddash": "solid",            # [str] one of ( "solid" | "dot" | "dash" | "longdash" | "dashdot" )
    "gridwidth": 0.5,               # [float]
    "showline": True,               # [bool]
    "linecolor": "grey",            # [str]
    "linewidth": 1,                 # [float]
    "mirror": False,                # [str | bool] one of ( True | "ticks" | False | "all" | "allticks" )
    "showticklabels": True,         # [bool]
    "zeroline": True,               # [bool]
    "zerolinecolor": "lightgrey",   # [str]
    "zerolinewidth": 1              # [float]
}, **kwargs)

LEGEND = lambda **kwargs: dict({
    "bgcolor": "white",                 # [str]
    "bordercolor": "#444",              # [str]
    "borderwidth": 0,                   # [float]
    "groupclick" : "togglegroup",       # [str] one of ( "toggleitem" | "togglegroup" )
    "itemclick" : "toggle",             # [str] one of ( "toggle" | "toggleothers" | False )
    "itemdoubleclick": "toggleothers",  # [str | bool] one of ( "toggle" | "toggleothers" | False )
    "itemsizing": "trace",              # [str] one of ( "trace" | "constant" )
    "itemwidth": 30,                    # [int] greater than or equal to 30
    "orientation": "h",                 # [str] one of ( "v" | "h" )
    "tracegroupgap": 10,                # [int] greater than or equal to 0
    "traceorder": "normal",             # [str] combination of "normal", "reversed", "grouped" joined with "+"
    "valign": "middle",                 # [str] one of ( "top" | "middle" | "bottom" )
    "xanchor": "right",                 # [str] one of ( "auto" | "left" | "center" | "right" )
    "x": 1.0,                           # [float] 1.02 for "v", 0.96 for "h"
    # "yanchor": "bottom",                # [str] one of ( "auto" | "top" | "middle" | "bottom" )
    # "y": 1.0,                           # [float] 1.0 for both "v" and "h",
    "yanchor": "top",
    "y": 1.0

}, **kwargs)

LAYOUT = lambda **kwargs:dict({
    "plot_bgcolor": "white",            # [str] colors
    "hovermode": "x unified",           # [str] one of ( "x" | "y" | "closest" | False | "x unified" |
                                        #                "y unified" )
    "dragmode": "zoom",                 # [str] one of ( "zoom" | "pan" | "select" | "lasso" |
                                        #                "drawclosedpath" | "drawopenpath" | "drawline" |
                                        #                "drawrect" | "drawcircle" | "orbit" | "turntable" |
                                        #                False )
    "margin" : {
        "b" : 80,                       # [int] bottom margin
        "l" : 80,                       # [int] left margin
        "r" : 80,                       # [int] right margin
        "t" : 80                        # [int] top margin
    },
}, **kwargs)
from plotly.graph_objects import Figure, Layout

def xaxis(**kwargs) -> dict:
    axis = {
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
    }
    axis.update(kwargs)
    return axis

def yaxis(**kwargs) -> dict:
    axis = {
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
    }
    axis.update(kwargs)
    return axis

def legend(**kwargs) -> dict:
    legend = {
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

    }
    legend.update(kwargs)
    return legend

def layout(**kwargs) -> dict:
    layout = {
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
    }
    layout.update(kwargs)
    return layout

def image(**kwargs) -> dict:
    image = {
        "source": "https://raw.githubusercontent.com/"
                  "Jehoshaphat-kr/"
                  "labwons/"
                  "master/"
                  "nohji/archive/image/LOGO-LABWONS-Watermark.png",
        "xref": "paper", "yref": "paper",
        "x": 1.01, "y": 1.0,
        # "x": 1.12, "y": 1.0,
        "sizex": 0.15, "sizey": 0.15,
        "xanchor":"right", "yanchor":"bottom",
        "opacity": 0.7
    }
    image.update(kwargs)
    return image

class r1c1nsy(Figure):
    def __init__(self, **kwargs):
        super().__init__()
        self.update_xaxes(patch=xaxis())
        self.update_yaxes(patch=yaxis())
        self.update_layout(dict1=layout(legend=legend()), **kwargs)
        self.add_layout_image(image())
        return

class r1c1sy1(Figure):
    def __init__(self, **kwargs):
        super().__init__()
        args = dict(
            rows=1, cols=1,
            shared_xaxes=True,
            x_title='Date',
            specs=[[{"secondary_y": True, "r":-0.06}]]
        )
        args.update(kwargs)
        self.set_subplots(**args)
        self.update_xaxes(patch=xaxis(rangeselector=None))
        self.update_yaxes(patch=yaxis(), secondary_y=False)
        self.update_layout(dict1=layout(legend=legend()))
        self.add_layout_image(image())
        return

class r1c2nsy(Figure):
    def __init__(self, **kwargs):
        super().__init__()
        args = dict(
            rows=1, cols=2
        )
        args.update(kwargs)
        self.set_subplots(**args)
        self.update_xaxes(patch=xaxis(rangeselector=None))
        self.update_yaxes(patch=yaxis())
        self.update_layout(dict1=layout(legend=legend()))
        self.add_layout_image(image())
        return

class r2c1nsy(Figure):
    def __init__(self, **kwargs):
        super().__init__()
        arg = dict(
            rows=2, cols=1,
            shared_xaxes=True,
            row_heights=[0.85, 0.15],
            vertical_spacing=0.01,
            x_title='Date',
        )
        arg.update(kwargs)
        self.set_subplots(**arg)
        self.update_xaxes(row=1, col=1, patch=xaxis(showticklabels=False))
        self.update_xaxes(row=2, col=1, patch=xaxis(rangeselector=None))
        self.update_yaxes(patch=yaxis())
        self.update_layout(dict1=layout(legend=legend()))
        self.add_layout_image(image())
        return

class r2c2nsy(Figure):
    def __init__(self, **kwargs):
        super().__init__()
        arg = dict(
            rows=2, cols=2,
            row_heights=[0.5, 0.5],
            vertical_spacing=0.1,
            x_title="기말"
        )
        arg.update(kwargs)
        self.set_subplots(**arg)
        self.update_yaxes(patch=yaxis())
        self.update_xaxes(patch=xaxis(rangeselector=None))
        self.update_layout(dict1=layout(legend=legend()))
        self.add_layout_image(image())
        return

class r2c3nsy(Figure):
    def __init__(self, **kwargs):
        super().__init__()
        arg = dict(
            rows=2, cols=3,
            vertical_spacing=0.08,
            horizontal_spacing=0.04,
            x_title='Date',
            y_title='[x1 Average]',
        )
        arg.update(kwargs)
        self.set_subplots(**arg)
        self.update_xaxes(patch=xaxis(rangeselector=None))
        self.update_yaxes(patch=yaxis())
        self.update_layout(dict1=layout(legend=legend()))
        self.add_layout_image(image())
        return

class r3c1nsy(Figure):
    def __init__(self, **kwargs):
        super().__init__()
        arg = dict(
            rows=3, cols=1,
            shared_xaxes=True,
            row_heights=[0.65, 0.15, 0.2],
            vertical_spacing=0.01,
            x_title='Date',
        )
        arg.update(kwargs)
        self.set_subplots(**arg)
        self.update_xaxes(row=1, col=1, patch=xaxis(showticklabels=False))
        self.update_xaxes(row=2, col=1, patch=xaxis(showticklabels=False, rangeselector=None))
        self.update_xaxes(row=3, col=1, patch=xaxis(rangeselector=None))
        self.update_yaxes(patch=yaxis())
        self.update_layout(dict1=layout(legend=legend()))
        self.add_layout_image(image())
        return

class r3c1sy3(Figure):
    def __init__(self, **kwargs):
        super().__init__()
        arg = dict(
            rows=3, cols=1,
            shared_xaxes=True,
            row_heights=[0.5, 0.15, 0.35],
            vertical_spacing=0.01,
            x_title='Date',
            specs=[
                [{"secondary_y": False, "r": -0.06}],
                [{"secondary_y": False, "r": -0.06}],
                [{"secondary_y": True, "r": -0.06}]
            ]
        )
        arg.update(kwargs)
        self.set_subplots(**arg)
        self.update_xaxes(row=1, col=1, patch=xaxis(showticklabels=False))
        self.update_xaxes(row=2, col=1, patch=xaxis(showticklabels=False, rangeselector=None))
        self.update_xaxes(row=3, col=1, patch=xaxis(rangeselector=None))
        self.update_yaxes(row=1, col=1, patch=yaxis())
        self.update_yaxes(row=2, col=1, patch=yaxis())
        self.update_yaxes(row=3, col=1, patch=yaxis(), secondary_y=False)
        self.update_layout(dict1=layout(legend=legend()))
        self.add_layout_image(image())
        return

class r4c1nsy(Figure):
    def __init__(self, **kwargs):
        super().__init__()
        arg = dict(
            rows=4, cols=1,
            shared_xaxes=True,
            row_heights=[0.66, 0.1, 0.12, 0.12],
            vertical_spacing=0.01,
            x_title='Date',
        )
        arg.update(kwargs)
        self.set_subplots(**arg)
        self.update_xaxes(row=1, col=1, patch=xaxis(showticklabels=False))
        self.update_xaxes(row=2, col=1, patch=xaxis(showticklabels=False, rangeselector=None))
        self.update_xaxes(row=3, col=1, patch=xaxis(showticklabels=False, rangeselector=None))
        self.update_xaxes(row=4, col=1, patch=xaxis(rangeselector=None))
        self.update_yaxes(patch=yaxis())
        self.update_layout(dict1=layout(legend=legend()))
        self.add_layout_image(image())
        return

class r5c1nsy(Figure):
    def __init__(self, **kwargs):
        super().__init__()
        arg = dict(
            rows=5, cols=1,
            shared_xaxes=True,
            row_heights=[0.45, 0.1, 0.15, 0.15, 0.15],
            vertical_spacing=0.01,
            x_title='Date',
        )
        arg.update(kwargs)
        self.set_subplots(**arg)
        self.update_xaxes(row=1, col=1, patch=xaxis(showticklabels=False))
        self.update_xaxes(row=2, col=1, patch=xaxis(showticklabels=False, rangeselector=None))
        self.update_xaxes(row=3, col=1, patch=xaxis(showticklabels=False, rangeselector=None))
        self.update_xaxes(row=4, col=1, patch=xaxis(showticklabels=False, rangeselector=None))
        self.update_xaxes(row=5, col=1, patch=xaxis(rangeselector=None))
        self.update_yaxes(patch=yaxis())
        self.update_layout(dict1=layout(legend=legend()))
        self.add_layout_image(image())
        return

#     def r5c1nsy(self, **kwargs) -> go.Figure:
#         _kwargs_ = dict(
#             rows=5, cols=1,
#             shared_xaxes=True,
#             row_width=[0.15, 0.15, 0.15, 0.1, 0.45],
#             vertical_spacing=0.01
#         )
#         _kwargs_.update(kwargs)
#         fig = make_subplots(**_kwargs_)
#
#         fig.update_layout(**self.layout(legend=self.legend()))
#         fig.update_xaxes(row=1, col=1, patch=self.xaxis(showticklabels=False))
#         fig.update_xaxes(row=2, col=1, patch=self.xaxis(showticklabels=False, rangeselector=None))
#         fig.update_xaxes(row=3, col=1, patch=self.xaxis(showticklabels=False, rangeselector=None))
#         fig.update_xaxes(row=4, col=1, patch=self.xaxis(showticklabels=False, rangeselector=None))
#         fig.update_xaxes(row=5, col=1, patch=self.xaxis(rangeselector=None))
#         fig.update_yaxes(row=1, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=2, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=3, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=4, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=5, col=1, patch=self.yaxis())
#         return fig

# class chart:
#     def r2c1nsy(self, **kwargs) -> go.Figure:
#         _kwargs_ = dict(
#             rows=2, cols=1,
#             shared_xaxes=True,
#             row_heights=[0.85, 0.15],
#             vertical_spacing=0.01,
#             x_title='Date',
#         )
#         _kwargs_.update(kwargs)
#         fig = make_subplots(**_kwargs_)
#
#         fig.update_layout(**self.layout(legend=self.legend()))
#         fig.update_xaxes(row=1, col=1, patch=self.xaxis(showticklabels=False))
#         fig.update_xaxes(row=2, col=1, patch=self.xaxis(rangeselector=None))
#         fig.update_yaxes(row=1, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=2, col=1, patch=self.yaxis())
#         return fig
#
#     def r2c2nsy(self, **kwargs) -> go.Figure:
#         _kwargs_ = dict(
#             rows=2, cols=2,
#             x_title="기말"
#         )
#         _kwargs_.update(kwargs)
#         fig = make_subplots(**_kwargs_)
#
#         fig.update_layout(**self.layout(legend=self.legend()))
#         fig.update_yaxes(patch=self.yaxis())
#         fig.update_xaxes(patch=self.xaxis(rangeselector=None))
#         return fig
#
#     def r2c3nsy(self, **kwargs) -> go.Figure:
#         _kwargs_ = dict(
#             rows=2, cols=3,
#             vertical_spacing=0.08,
#             horizontal_spacing=0.04,
#             x_title='Date',
#             y_title='[x1 Average]',
#         )
#         _kwargs_.update(kwargs)
#         fig = make_subplots(**_kwargs_)
#
#         fig.update_layout(**self.layout())
#         fig.update_yaxes(patch=self.yaxis())
#         fig.update_xaxes(patch=self.xaxis(rangeselector=None))
#         return fig
#
#     def r3c1nsy(self, **kwargs) -> go.Figure:
#         _kwargs_ = dict(
#             rows=3, cols=1,
#             shared_xaxes=True,
#             row_heights=[0.65, 0.15, 0.2],
#             vertical_spacing=0.01,
#             x_title='Date',
#         )
#         _kwargs_.update(kwargs)
#         fig = make_subplots(**_kwargs_)
#
#         fig.update_layout(**self.layout(legend=self.legend()))
#         fig.update_xaxes(row=1, col=1, patch=self.xaxis(showticklabels=False))
#         fig.update_xaxes(row=2, col=1, patch=self.xaxis(showticklabels=False, rangeselector=None))
#         fig.update_xaxes(row=3, col=1, patch=self.xaxis(rangeselector=None))
#         fig.update_yaxes(row=1, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=2, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=3, col=1, patch=self.yaxis())
#         return fig
#
#     def r3c1sy2(self, **kwargs) -> go.Figure:
#         _kwargs_ = dict(
#             rows=3, cols=1,
#             shared_xaxes=True,
#             row_width=[0.35, 0.15, 0.5],
#             vertical_spacing=0.01,
#             x_title='Date',
#             specs=[
#                 [{"secondary_y":False, "r":-0.06}],
#                 [{"secondary_y":False, "r":-0.06}],
#                 [{"secondary_y":True, "r":-0.06}]
#             ]
#         )
#         _kwargs_.update(kwargs)
#         fig = make_subplots(**_kwargs_)
#
#         fig.update_layout(**self.layout(legend=self.legend()))
#         fig.update_xaxes(row=1, col=1, patch=self.xaxis(showticklabels=False))
#         fig.update_xaxes(row=2, col=1, patch=self.xaxis(showticklabels=False, rangeselector=None))
#         fig.update_xaxes(row=3, col=1, patch=self.xaxis(rangeselector=None))
#         fig.update_yaxes(row=1, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=2, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=3, col=1, patch=self.yaxis(), secondary_y=False)
#         return fig
#
#     def r4c1nsy(self, **kwargs) -> go.Figure:
#         _kwargs_ = dict(
#             rows=4, cols=1,
#             shared_xaxes=True,
#             row_width=[0.12, 0.12, 0.1, 0.66],
#             vertical_spacing=0.01
#         )
#         _kwargs_.update(kwargs)
#         fig = make_subplots(**_kwargs_)
#
#         fig.update_layout(**self.layout(legend=self.legend()))
#         fig.update_xaxes(row=1, col=1, patch=self.xaxis(showticklabels=False))
#         fig.update_xaxes(row=2, col=1, patch=self.xaxis(showticklabels=False, rangeselector=None))
#         fig.update_xaxes(row=3, col=1, patch=self.xaxis(showticklabels=False, rangeselector=None))
#         fig.update_xaxes(row=4, col=1, patch=self.xaxis(rangeselector=None))
#         fig.update_yaxes(row=1, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=2, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=3, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=4, col=1, patch=self.yaxis())
#         return fig
#
#     def r5c1nsy(self, **kwargs) -> go.Figure:
#         _kwargs_ = dict(
#             rows=5, cols=1,
#             shared_xaxes=True,
#             row_width=[0.15, 0.15, 0.15, 0.1, 0.45],
#             vertical_spacing=0.01
#         )
#         _kwargs_.update(kwargs)
#         fig = make_subplots(**_kwargs_)
#
#         fig.update_layout(**self.layout(legend=self.legend()))
#         fig.update_xaxes(row=1, col=1, patch=self.xaxis(showticklabels=False))
#         fig.update_xaxes(row=2, col=1, patch=self.xaxis(showticklabels=False, rangeselector=None))
#         fig.update_xaxes(row=3, col=1, patch=self.xaxis(showticklabels=False, rangeselector=None))
#         fig.update_xaxes(row=4, col=1, patch=self.xaxis(showticklabels=False, rangeselector=None))
#         fig.update_xaxes(row=5, col=1, patch=self.xaxis(rangeselector=None))
#         fig.update_yaxes(row=1, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=2, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=3, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=4, col=1, patch=self.yaxis())
#         fig.update_yaxes(row=5, col=1, patch=self.yaxis())
#         return fig
#
#
# # Alias
# Chart = chart()
#
if __name__ == "__main__":
    myChart = r1c1nsy()
    myChart.show()


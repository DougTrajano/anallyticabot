import json
import os
import pkgutil
import pandas as pd
from IPython.display import display, Javascript, HTML

# From conversation_analytics_toolkit
import conversation_analytics_toolkit as cat
from conversation_analytics_toolkit import wa_assistant_skills
from conversation_analytics_toolkit import transformation
from conversation_analytics_toolkit import analysis


def read_file(filename):
    with open(filename, 'r') as file:
        data = file.read().replace('<style>', '').replace('</style>', '')
    return data


def add_style_to_header(css_string):
    display(Javascript("""
        var newStyle = document.createElement("style");
        newStyle.innerHTML = `%s`;
        document.getElementsByTagName("head")[0].appendChild(newStyle);
    """ % (css_string)))


flowchart_css = pkgutil.get_data(
    __package__, 'flowchart.min.css').decode('utf-8')
flowchart_js = pkgutil.get_data(
    __package__, 'flowchart2.min.js').decode('utf-8')

add_style_to_header(flowchart_css)

display(Javascript(
    "require.config({paths: {d3: 'https://cdnjs.cloudflare.com/ajax/libs/d3/4.13.0/d3.min'}});"))
display(Javascript(
    "require.config({paths: {lodash: 'https://cdn.jsdelivr.net/npm/lodash@4.17.15/lodash.min'}});"))
display(Javascript(data=flowchart_js))


class FlowVisualization:
    def __init__(self, title="All Conversations"):
        self.title = title
        self.selection_var = "selection"
        self.data = None
        self.config = {
            'commonRootPathName': self.title,  # label for the first root node
            'height': 800,  # control the visualization height.  Default 600
            # control the number of immediate children to show (and collapse rest into *others* node).  Default 5
            'nodeWidth': 250,
            # control the width between pathflow layers.  Default 360     'sortByAttribute': 'flowRatio'  # control the sorting of the chart. (Options: flowRatio, dropped_offRatio, flows, dropped_off, rerouted)
            'maxChildrenInNode': 6,
            'linkWidth': 400,
            'sortByAttribute': 'flowRatio',
            'title': self.title,
            'mode': "turn-based"
        }

    def prepare_data(self, logs, skill_id, workspace):
        df_logs = pd.DataFrame(logs)

        assistant_skills = wa_assistant_skills.WA_Assistant_Skills()
        assistant_skills.add_skill(skill_id, workspace)

        df_logs_canonical = transformation.to_canonical_WA_v2(df_logs, assistant_skills,
                                                              skill_id_field=None, include_nodes_visited_str_types=True,
                                                              include_context=False)

        df_logs_to_analyze = df_logs_canonical.copy(deep=False)

        turn_based_path_flows = analysis.aggregate_flows(df_logs_to_analyze, mode="turn-based",
                                                         on_column="turn_label", max_depth=400, trim_reroutes=False)

        self.data = json.loads(
            turn_based_path_flows.to_json(orient='records'))

    def draw_flowchart(self):
        # increase the width of the Jupyter output cell
        display(HTML("<style>.container { width:95% !important; }</style>"))

        display(Javascript("""
            (function(element){
                require(['flowchart2'], function(flowchart2) {
                    var config = %s;
                    if (config["debugger"]===true){
                    debugger;
                    };
                    var chart = flowchart2(element.get(0), config, %s);
                    chart.on("export",function(e){
                        var selection = JSON.stringify(e.selection).replace(/"/g , "'");
                        IPython.notebook.kernel.execute("%s = " + selection);
                    });
                });
            })(element);
        """ % (json.dumps(self.config), json.dumps(self.data), self.selection_var)))

    def plot(self):
        from mako.template import Template

        title = "Dialog Flow"

        obj = """
            (function(element){
                require(['flowchart2'], function(flowchart2) {
                    var config = %s;
                    if (config["debugger"]===true){
                    debugger;
                    };
                    var chart = flowchart2(element.get(0), config, %s);
                    chart.on("export",function(e){
                        var selection = JSON.stringify(e.selection).replace(/"/g , "'");
                        IPython.notebook.kernel.execute("%s = " + selection);
                    });
                });
            })(element);
        """ % (json.dumps(self.config), json.dumps(self.data), self.selection_var)

        template_file = open('template.html', 'r', encoding='utf-8').read()
        html_obj = Template(template_file)
        html_obj = html_obj.render(title=title, data=obj)

        html_file = open("report.html", "w")
        html_file.write(html_obj)
        html_file.close()
        return html_obj
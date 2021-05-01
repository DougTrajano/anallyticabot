# This page uses open source components.
# You can find the source code of their open source projects along with license information below.
# We acknowledge and are grateful to these developers for their contributions to open source.
#
# Project: https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/
# License: Apache 2.0 license.

import json
import pandas as pd
from conversation_analytics_toolkit import analysis
from conversation_analytics_toolkit import transformation
from conversation_analytics_toolkit import wa_assistant_skills
from src.helper_functions import setup_logger

logger = setup_logger()

_html_template = """
<html>

<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/4.13.0/d3.min.js"
    integrity="sha512-RJJ1NNC88QhN7dwpCY8rm/6OxI+YdQP48DrLGe/eSAd+n+s1PXwQkkpzzAgoJe4cZFW2GALQoxox61gSY2yQfg=="
    crossorigin="anonymous"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.15/lodash.min.js"
    integrity="sha512-3oappXMVVac3Ge3OndW0WqpGTWx9jjRJA8SXin8RxmPfc8rg87b31FGy14WHG/ZMRISo9pBjezW9y00RYAEONA=="
    crossorigin="anonymous"></script>
  <style>
    div .botvis.flowchart{{overflow:auto}}.botvis.flowchart rect.node{{fill:#fff;stroke-width:3px}}.botvis.flowchart rect.node.handled{{fill:#00b4a0;stroke:#00b4a0}}.botvis.flowchart rect.node.not-handled{{fill:#fb9a99;stroke:#fb9a99}}.botvis.flowchart rect.node.selected{{stroke:black !important;stroke-width:3px;stroke-dasharray:10 10}}.botvis.infodiv{{right:13px;position:absolute;max-width:400px;background:#cfd0d0a3;padding:10px;overflow-wrap:break-word}}.botvis.infodiv .infodiv-title{{font-weight:bold;font-size:larger}}.botvis.buttondiv{{position:absolute;right:30px;top:18px}}.botvis.infodiv .field-name{{font-weight:bold}}.botvis.titlediv{{position:absolute;width:50%;background:#cfd0d0a3;padding:10px;overflow-wrap:break-word}}.botvis.titlediv .dataset-description-field{{font-weight:bold;font-size:larger}}.botvis.flowchart rect.node-left-twisty{{stroke-width:3px;width:15px;height:15px}}.botvis.flowchart text.node-label{{text-anchor:"left";font-size:13px;font-weight:bolder;font-family:Helvetica Neue for IBM,Helvetica Neue,Helvetica,Arial,sans-serif;fill:white;letter-spacing:1px}}.botvis.flowchart text.node-flow-label{{font-family:Helvetica Neue for IBM,Helvetica Neue,Helvetica,Arial,sans-serif;font-size:14px;fill:black}}.botvis.flowchart text.node-label-num-children{{font-family:Helvetica Neue for IBM,Helvetica Neue,Helvetica,Arial,sans-serif;font-size:11px;fill:black}}.botvis.flowchart text.node-label-new-skill{{font-family:Helvetica Neue for IBM,Helvetica Neue,Helvetica,Arial,sans-serif;font-size:13px;fill:black}}.botvis.flowchart .flow-path{{fill:none;stroke:#ccc;opacity:.5;// stroke-width:2px}}.nothandledlink{{fill:none;stroke:"green";stroke-width:2px}}.botvis.flowchart .node-exit-path{{fill:white}}.botvis.flowchart .node-exit-label{{font-size:12px}}.botvis.flowchart .node-exit-label-background{{fill:black;fill:#fb9a99}}.botvis.flowchart .node-image{{width:20px;height:20px;opacity:1;x:-25;y:-10}}.botvis-tooltip{{position:fixed;line-height:1;text-align:left;width:200px;height:83px;padding:2px;font:12px sans-serif;background:lightsteelblue;border:2px;border-radius:8px;z-index:100}}.botvis-tooltip p{{font-size:13px;left:5px;top:2px;margin:0;position:relative}}.botvis.flowchart.selection{{color:black;margin:10px;font-weight:bold;font-size:14px}}.botvis.flowchart.selection-instruction{{color:red;margin:0;line-height:initial}}.botvis-ba-header{{background-color:#1d3649;height:30px;width:100%;padding:0 32px 0 40px}}.botvis-ba-label{{color:white}}.output_subarea.fullscreen{{z-index:9999 !important;width:100% !important;height:100% !important;background-color:white !important;opacity:1 !important;position:fixed !important;top:50px !important;left:0 !important}}
  </style>

  <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js" type="text/javascript"></script>

  <script type="text/javascript">
    function draw(container, config, data) {{
      //debugger;

      var notHandled2base64 = "PHN2ZyB3aWR0aD0iMjIwIiBoZWlnaHQ9IjIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIw%0D%0AMDAvc3ZnIiB4bWxuczpzdmc9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KIDwhLS0gQ3Jl%0D%0AYXRlZCB3aXRoIFNWRy1lZGl0IC0gaHR0cDovL3N2Zy1lZGl0Lmdvb2dsZWNvZGUuY29tLyAtLT4K%0D%0AIDxnPgogIDx0aXRsZT5MYXllciAxPC90aXRsZT4KICA8Y2lyY2xlIHI9Ijk1IiBjeT0iMTAwIiBj%0D%0AeD0iMTAwIiBzdHJva2Utd2lkdGg9IjlweCIgZmlsbD0id2hpdGUiIHN0cm9rZT0icmdiKDI1MSwg%0D%0AMTU0LCAxNTMpIi8+CiAgPHRleHQgeD0iNjUiIHk9IjE1MCIgZmlsbD0icmdiKDI1MSwgMTU0LCAx%0D%0ANTMpIiBmb250LXNpemU9IjEwcmVtIj4/PC90ZXh0PgogPC9nPgo8L3N2Zz4=";
      var handled2base64 = "PHN2ZyB3aWR0aD0iMjIwIiBoZWlnaHQ9IjIyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxuczpzdmc9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KIDwhLS0gQ3JlYXRlZCB3aXRoIFNWRy1lZGl0IC0gaHR0cDovL3N2Zy1lZGl0Lmdvb2dsZWNvZGUuY29tLyAtLT4KIDxnPgogIDx0aXRsZT5MYXllciAxPC90aXRsZT4KICA8Y2lyY2xlIHI9Ijk1IiBjeT0iMTAwIiBjeD0iMTAwIiBzdHJva2Utd2lkdGg9IjlweCIgZmlsbD0id2hpdGUiIHN0cm9rZT0icmdiKDAsIDE4MCwgMTYwKSIvPgogIDx0ZXh0IHg9IjQwIiB5PSIxNTUiIGZpbGw9InJnYigwLCAxODAsIDE2MCkiIGZvbnQtc2l6ZT0iMTByZW0iPuKckzwvdGV4dD4KIDwvZz4KPC9zdmc+";

      if (config["debugger"] === true) {{
        debugger;
      }}

      var width = 0, height = 0;
      var _tooltip = null;
      var _config = {{}}, _chart = {{}}, _data = null;
      var self = this;

      var defaultConfig = {{
        margin: {{ top: 20, right: 20, bottom: 20, left: 120 }},
        width: 1200,
        height: 600,
        nodeRadius: 10,
        nodeWidth: 200,
        linkWidth: 360,
        exitRatioThreshold: 0.0009,
        notHandledRatioThreshold: 0.30,
        sortByAttribute: "flowRatio",
        showVisitRatio: "fromTotal", // "fromTotal" from total visits or "fromPrevious" from previous node.  
        skillIntentMode: false,
        commonRootPathName: "Session Start", // will create a root node by this name (only works for json_array)
        maxChildrenInNode: 5,
        title: "",
        mode: "turn-based",
        compareMode: false,
        dataModel: "json_array" // "json" or "csv"
      }};

      var _container = container;

      _config = $.extend(true, defaultConfig, config); // merge the default with the incoming config.
      if (data[0].flows_prev)
        _config.compareMode = true;
      var target = Array.isArray(data) ? [] : {{}};
      _data = $.extend(true, target, data); // make a copy of the data so we can update it


      _chart.container = _container;
      _chart.config = _config;

      var baHeader = $('<div>').addClass("botvis-ba-header").appendTo(_chart.container);
      $('<a>', {{ text: 'Anallyticabot | Flow Visualization' }}).addClass("botvis-ba-label").appendTo(baHeader);

      _chart.selectedNode = {{}};
      _chart.selectedD3Node = null;
      createInfoDiv(_chart);
      createTitleDiv(_chart);

      // Set the dimensions and margins of the diagram
      var margin = _config.margin,
        width = _config.width - _config.margin.left - _config.margin.right,
        height = _config.height - _config.margin.top - _config.margin.bottom;

      var svg = d3.select(_container).append("svg")
        .attr("class", "botvis flowchart")
        .attr("width", "95%")
        .attr("width", _config.width)
        .attr("height", height + _config.margin.top + _config.margin.bottom);

      _chart.svg = svg;

      var g = svg.append("g")
        .attr("transform", "translate("
          + _config.margin.left + "," + _config.height / 2 + ")");

      _tooltip = d3.select(_container)
        .append("div")
        .attr("class", "botvis-tooltip")
        .attr('pointer-events', 'none')
        .style("opacity", 0)
        .style("visibility", "hidden");

      var i = 0,
        duration = 750,
        root;

      var treemap = d3.tree().nodeSize([70, 700]);

      if (_config.dataModel == "d3_hierarchy") {{
        if ("stratify" in _config)
          root = _config.stratify(_data);
        else
          throw "Stratify function is not defined for d3_hierarchy data model";
      }} else if (_config.dataModel == "json")
        root = d3.hierarchy(_data, function (d) {{
          return d.children;
        }});
      else {{
        if (_config.dataModel == "csv") {{
          _data = d3.csvParse(_data);

        }} else if (!(_config.dataModel == "json_array")) {{
          throw "data model not supported,  use json, csv and json_array";
        }}
        var stratify = d3.stratify()
          .parentId(function (d) {{
            return d.path.substring(0, d.path.lastIndexOf("\\\\"));
          }})
          .id(function (d) {{
            return d.path;
          }});
        root = stratifyJSONArray(_data);
      }}

      root.x0 = height / 2;
      root.y0 = 0;

      // sort all nodes in the tree
      root.each(function (node) {{
        if (node.children) {{
          node.children = node.children.sort(function (a, b) {{
            var result = b.data[_config.sortByAttribute] - a.data[_config.sortByAttribute];
            return result;
          }});
        }}
      }});

      // replace too long children with other nodes
      root.each(function (node) {{
        if ((_config.mode == "milestone-based") && (node.data.name == "Other")) {{
          node.data.type = "milestone-other";
          node.data.dropped_off = undefined;
          node.data.dropped_offRatio = NaN;
        }} else if (node.children) {{
          if (node.children.length > _config.maxChildrenInNode) {{
            var topChildren = node.children.slice(0, _config.maxChildrenInNode);
            var otherChildren = node.children.slice(_config.maxChildrenInNode);

            var otherData = {{
              dropoffs: 0,
              prev_dropoffs: 0,
              rerouted: 0,
              prev_rerouted: 0,
              flowRatio: 0,
              flow_prevRatio: 0,
              flowRatioFromPrev: 0,
              flow_prevRatioFromPrev: 0,
              flows: 0,
              prev_flows: 0,
              id: "other",
              is_new_skill: 0,
              is_session_start: 0,
              name: "a few other",
              notHandledRatio: 0,
              not_handled: 0,
              path: "other",
              type: "other"
            }};
            var otherNode = {{
              children: null,
              _otherChildren: otherChildren,
              data: otherData,
              depth: node.depth + 1,
              height: 0,
              id: "other" + node.id,
              parent: node
            }}
            // compute othernode summary from children
            otherChildren.forEach(function (node) {{ otherNode.data.flows += node.data.flows; }});
            var num_of_otherChildren = 0;
            otherChildren.forEach(function (node) {{ num_of_otherChildren += node.data.flows; }});
            otherNode.data.flowRatio = otherNode.data.flows / root.data.flows;
            otherNode.data.flowRatioFromPrev = otherNode.parent ? otherNode.data.flows / otherNode.parent.data.flows : otherNode.data.flowRatio;
            otherData.name = num_of_otherChildren + " others ...";

            topChildren.push(otherNode);
            node.children = topChildren;
          }}
        }}
      }});

      // Collapse after the second level
      root.children.forEach(collapse);

      update(root);

      // Collapse the node and all it's children
      function collapse(d) {{
        if (d.children) {{
          d._children = d.children
          d._children.forEach(collapse)
          d.children = null
        }}
      }}

      function update(source) {{

        // Assigns the x and y position for the nodes
        var treeData = treemap(root);

        // Compute the new tree layout.
        var nodes = treeData.descendants(),
          links = treeData.descendants().slice(1);

        // Normalize for fixed-depth.
        nodes.forEach(function (d) {{ d.y = d.depth * _config.linkWidth }});

        // ****************** Nodes section ***************************

        // Update the nodes...
        var node = g.selectAll('g.node-group')
          .data(nodes, function (d) {{ return d.id || (d.id = ++i); }});

        // Enter any new modes at the parent's previous position.
        var nodeEnter = node.enter().append('g')
          .attr('class', 'node-group')
          .attr("transform", function (d) {{
            return "translate(" + source.y0 + "," + source.x0 + ")";
          }});

        // add the left twisty mark
        nodeEnter.append('rect')
          .attr('class', 'node-left-twisty')
          .attr('transform', 'translate(-30, 0)')
          .style("fill", function (d) {{
            return d.data.notHandledRatio >= _config["notHandledRatioThreshold"] ? "#fb9a99" : "#00B4A0";
          }})
          .style("stroke", function (d) {{
            return d.data.notHandledRatio >= _config["notHandledRatioThreshold"] ? "#fb9a99" : "#00B4A0";
          }});

        var nodeObjects = nodeEnter.append('rect')
          .attr('class', function (d) {{
            var classList = ["node"]

            if (d.parent == null)
              classList.push("rootnode");
            else if (d.data.type == "other")
              classList.push("other-node");
            else if ((d.data.type == "milestone-other") && (_config.mode == "milestone-based"))
              classList.push("milestone-other-node");

            if (d.data.notHandledRatio > _config["notHandledRatioThreshold"])
              classList.push("not-handled");
            else
              classList.push("handled");

            return classList.join(" ")
          }}).on('click', nodeClick);

        nodeObjects.on("mouseover", function (d) {{
          _tooltip.transition()
            .duration(100)
            .style("opacity", .9)
            .style("visibility", "visible");

          var nodeNameLabel = "Name";
          var skillRow = "";
          if (_config.skillIntentMode) {{
            nodeNameLabel = "Intent";
            skillRow = '<p><strong>Skill: </strong>' + d.data.skill + '<br>'
          }}

          var compareRow = "";
          if (_config.compareMode) {{
            compareRow = (_config.compareMode ?
              ('<strong>Visits (prev): </strong>' + d.data.flows_prev + " (" + (d.data.trendPercentage * 100).toFixed(2) + "%)") :
              ('<strong>Visits (prev): </strong>  (NA)')) + '<br>'

          }}

          _tooltip.html(
            '<div>' +
            '<p><strong>' + nodeNameLabel + ': </strong>' + d.data.name +
            '<br>' +
            skillRow +
            '<strong>Visits: </strong>' + d.data.flows + " (" + (d.data.flowRatio * 100).toFixed(1) + "% | " + (d.data.flowRatioFromPrev * 100).toFixed(1) + "%)" +
            '<br>' +
            compareRow +
            '<strong>Drop offs: </strong>' + d.data.dropped_off + " (" + (d.data.dropped_offRatio * 100).toFixed(1) + '%)' +
            '<br>' +
            '<strong>Reroutes: </strong>' + d.data.rerouted + " (" + (d.data.reroutedRatio * 100).toFixed(1) + '%)' +
            '<br>' +
            '</p></div>')
            .style("left", (d3.event.pageX + 80) + "px")
            .style("top", (d3.event.pageY - 38) + "px");
        }}).on("mouseout", function (d) {{
          _tooltip.style("visibility", "hidden");
          _tooltip.style("opacity", 0);
        }}).on("mousemove", function (d) {{
          _tooltip.transition()
            .duration(0)
            .style("opacity", .9)
            .style("visibility", "visible")
            .style("left", (d3.event.pageX + 80) + "px")
            .style("top", (d3.event.pageY - 38) + "px");
        }});

        var srcPrefix = "data:image/svg+xml;base64,";
        // add icon for the nodes
        nodeEnter.append('image')
          .attr('cursor', 'pointer')
          .style('pointer-events', 'none')
          .attr('x', '-25')
          .attr('y', '-10')
          .attr('width', '25')
          .attr('height', '25')
          .attr('href', function (d) {{
            return d.data.notHandledRatio >= _config["notHandledRatioThreshold"] ? srcPrefix + notHandled2base64 : srcPrefix + handled2base64;
          }});

        // add the plus sign for children
        nodeEnter.append('text')
          .attr('class', 'node-label-num-children')
          .attr('transform', 'translate(' + _config.nodeWidth + ', -5)')
          .text(function (d) {{
            return "+" + d.height;
          }})
          .style("opacity", function (d) {{
            // if has children which are not collapsed
            var hasHiddenChildren = (d.hasOwnProperty("children") && (d.children != null) && (d.children.length > 0));
            return hasHiddenChildren ? 1 : 0;

          }});

        // add the skill name whenever there's a skill transition
        nodeEnter.append('text')
          .attr('class', 'node-label-new-skill')
          .attr('transform', 'translate(-25, -20)')
          .text(function (d) {{
            return d.data.skill;
          }})
          .style("opacity", function (d) {{
            return (d.data.is_new_skill == 1) ? 1 : 0;
          }});

        // add comparison across periods
        nodeEnter.append('text')
          .attr('class', 'node-label-new-old-flow')
          .attr('transform', 'translate(-35, -20)')
          .text(function (d) {{
            let trend = d.data.trendPercentage
            if (!trend)
              return "";

            return trend == 0 ? "" : trend > 0 ? "+" + (trend * 100).toFixed(2) + " %" : (trend * 100).toFixed(2) + " %";
          }})
          .style("opacity", function (d) {{
            return (_config.compareMode) ? 1 : 0;
          }})
          .style("fill", function (d) {{
            return d.data.trendPercentage > 0 ? "#00b49f" : "#da6363";
          }})
          ;

        // add the node exit path mark
        nodeEnter.append('path')
          .attr('class', 'node-exit-path')
          .attr('d', 'm0,0 Q30,0 30,30')
          .attr('transform', 'translate(' + _config.nodeWidth + ', 0)')
          .attr('opacity', function (d) {{
            return d.data.dropped_offRatio + d.data.reroutedRatio > _config["exitRatioThreshold"] ? 0.5 : 0;
          }})
          .style("stroke", function (d) {{
            return d.data.dropped_offRatio + d.data.reroutedRatio > _config["exitRatioThreshold"] ? "#fb9a99" : "#7fc97f";
          }})
          .style("stroke-width", function (d) {{
            return (d.data.dropped_offRatio + d.data.reroutedRatio) * 10;
          }})
          .style("visibility", function (d) {{
            return d.data.type != "milestone-other" ? "visible" : "hidden";
          }})
          .style("fill", "none")
          ;

        // Add labels for the nodes
        nodeEnter.append('text')
          .attr('class', 'node-label')
          .attr("dy", ".35em")
          .attr("x", function (d) {{
            return 0;
          }})
          .attr('cursor', 'pointer')
          .style('pointer-events', 'none')
          .text(function (d) {{ return d.data.name; }});

        // Add labels for the incoming flow
        nodeEnter.append('text')
          .attr('class', 'node-flow-label')
          .attr("dy", ".35em")
          .attr("x", function (d) {{
            return -70;
          }})
          .attr("text-anchor", function (d) {{
            //return d.children || d._children ? "end" : "start";
            return "middle"
          }})
          .text(function (d) {{
            var flows = d.data.flows;
            var flowsRatio = d.data.flowRatio;
            var flowRatioFromPrev = d.data.flowRatioFromPrev;
            var text = (_config.showVisitRatio == "fromTotal") ? (flowsRatio * 100).toFixed(0) + "% (" + flows + ")" : (flowRatioFromPrev * 100).toFixed(0) + "% (" + flows + ")";
            return text;
          }});

        // Add background for the node exit labels
        nodeEnter.append('rect')
          .attr('class', 'node-exit-label-background')
          .attr('opacity', function (d) {{
            return d.data.dropped_offRatio + d.data.reroutedRatio > _config["exitRatioThreshold"] ? 0.4 : 0;
          }})
          .attr("rx", 3)
          .attr("ry", 3)
          .attr("width", 55)
          .attr("height", 20)
          .style("fill", "rgb(251, 154, 153)")
          .style("visibility", function (d) {{
            return d.data.type != "milestone-other" ? "visible" : "hidden";
          }})
          .attr('transform', 'translate(' + _config.nodeWidth + ',30)');

        // Add labels for the node exit labels
        nodeEnter.append('text')
          .attr('class', 'node-exit-label')
          .attr("dy", ".35em")
          .attr('transform', 'translate(' + _config.nodeWidth + ', 40)')
          //.attr('cursor', 'pointer')
          .attr('opacity', function (d) {{
            return d.data.dropped_offRatio + d.data.reroutedRatio > _config["exitRatioThreshold"] ? 1 : 0;
          }})
          .attr("text-anchor", function (d) {{
            //return d.children || d._children ? "end" : "start";
            return "left"
          }})
          .style("visibility", function (d) {{
            return d.data.type != "milestone-other" ? "visible" : "hidden";
          }})
          .text(function (d) {{
            var exits = d.data.dropped_off + d.data.rerouted;
            var exitsRatio = d.data.dropped_offRatio + d.data.reroutedRatio;
            var text = (exitsRatio * 100).toFixed(0) + "% (" + exits + ")";
            return text
          }});

        // special dots for milestone other nodes
        var milestone_other_dots = nodeEnter.append('g')
          .attr('class', 'node-other-milestone')
          .style("visibility", function (d) {{
            return d.data.type == "milestone-other" ? "visible" : "hidden";
          }});

        for (var i = 1; i <= 3; i++) {{
          milestone_other_dots.append('circle')
            .attr('class', 'node-other-milestone-circle')
            .attr('transform', 'translate(' + (_config.nodeWidth - ((3 - i) * 20) - 30) + ', 0)')
            .attr('r', (6 - i))
        }}

        // UPDATE
        var nodeUpdate = nodeEnter.merge(node);

        // Transition to the proper position for the node
        nodeUpdate.transition()
          .duration(duration)
          .attr("transform", function (d) {{
            return "translate(" + d.y + "," + d.x + ")";
          }});

        // Update the node attributes and style
        nodeUpdate.select('rect.node')
          .style("fill", function (d) {{
            return d.data.notHandledRatio >= _config["notHandledRatioThreshold"] ? "#fb9a99" : "#00B4A0";
          }})
          .attr("x", -30)
          .attr("y", -15)
          .attr("rx", 14)
          .attr("ry", 14)
          .attr("width", function (d) {{

            return d.data.type != "milestone-other" ? _config.nodeWidth + 30 : _config.nodeWidth - 60;
            //return _config.nodeWidth + 30;
          }})
          .attr("height", 30)
          .attr('cursor', 'pointer');

        // Update the plus
        nodeUpdate.selectAll('.node-label-num-children')
          .style("opacity", function (d) {{
            // if has children which are not collapsed
            var hasHiddenChildren = (d.hasOwnProperty("children") && (d.children != null) && (d.children.length > 0));
            return hasHiddenChildren ? 0 : 1;
          }}).style("visibility", function (d) {{
            return d.data.type != "milestone-other" ? "visible" : "hidden";
          }});

        // Remove any exiting nodes
        var nodeExit = node.exit().transition()
          .duration(duration)
          .attr("transform", function (d) {{
            return "translate(" + source.y + "," + source.x + ")";
          }})
          .remove();

        // On exit reduce the node circles size to 0
        nodeExit.select('rect')
          .style('fill-opacity', 1e-6);

        // On exit reduce the opacity of text labels
        nodeExit.select('text')
          .style('fill-opacity', 1e-6);

        // ****************** links section ***************************

        // Update the links...
        var link = g.selectAll('path.flow-path')
          .data(links, function (d) {{ return d.id; }});

        // Enter any new links at the parent's previous position.
        var linkEnter = link.enter().insert('path', "g")
          .attr("class", "flow-path")
          .attr('d', function (d) {{
            var o = {{ x: source.x0, y: source.y0 }}
            return diagonal(o, o)
          }})
          .style('fill', 'none')
          .style('stroke', '#ccc')
          .style('opacity', 0.5)
          ;

        // UPDATE
        var linkUpdate = linkEnter.merge(link);

        // Transition back to the parent element position
        linkUpdate.transition()
          .duration(duration)
          .attr('d', function (d) {{ return diagonal(d, d.parent) }})
          .attr('stroke-width', function (d) {{
            var strokeWidth = d.data.flowRatio * 40
            return strokeWidth > 1 ? strokeWidth : 1;
          }});

        // Remove any exiting links
        var linkExit = link.exit().transition()
          .duration(duration)
          .attr('d', function (d) {{
            var o = {{ x: source.x, y: source.y }}
            return diagonal(o, o)
          }})
          .remove();

        // Store the old positions for transition.
        nodes.forEach(function (d) {{
          d.x0 = d.x;
          d.y0 = d.y;
        }});

        // Creates a curved (diagonal) path from parent to the child nodes
        function diagonal(s, d) {{

          var path = "M " + s.y + " " + s.x +
            " C " + (s.y + d.y) / 2 + " " + s.x + "," +
            (s.y + d.y) / 2 + " " + d.x + "," +
            d.y + " " + d.x;
          return path
        }}

        // Toggle children on click.
        function nodeClick(d) {{
          if (d.children) {{
            d._children = d.children;
            d.children = null;
          }} else {{
            d.children = d._children;
            d._children = null;
          }}
          //debugger;
          var x = d3.event.pageX;
          var y = d3.event.pageY;
          update(d);
          nodeSelectedEventHandler(d, d3.select(this))
          // center_on_click(x,y)
        }}

        var zoom = d3.zoom()
          .scaleExtent([1 / 2, 8])
          .on("zoom", zoomed)
        _chart.zoom = zoom;
        svg.call(zoom);

        function zoomed() {{
          // we need to add the margins and generate the offset translate 
          var k = d3.event.transform.k;
          var x = d3.event.transform.x + _config.margin.left;
          var y = d3.event.transform.y + _config.height / 2;

          g.attr("transform", "translate(" + x + "," + y + ") scale (" + k + ")");

        }}

      }}

      function stratifyJSONArray(data) {{
        // transform JSONArray structure into D3 hierarchy, and perform some computation of attributes along the way.  This function will be called by the chart to process the data.

        // create the tree structure
        var rootNode = {{ path: _config.commonRootPathName, id: _config.commonRootPathName, "name": _config.commonRootPathName, type: "start", is_new_skill: 0, is_session_start: 0, dropped_off: 0, rerouted: 0, flows: 0, not_handled: 0, dropped_offRatio: 0, reroutedRatio: 0, flowRatio: 100, flowRatioFromPrev: 100, notHandledRatio: 0 }};

        // update path of all elements to have shared session start element
        data.forEach(function (row) {{ row.path = _config.commonRootPathName + "\\\\" + row.path }});
        // add a parent node
        data.push(rootNode);
        // let d3 stratify the data into a tree
        var toHierarchy = d3.stratify()
          .parentId(function (d) {{
            return d.path.substring(0, d.path.lastIndexOf("\\\\"));
          }})
          .id(function (d) {{
            return d.path;
          }});
        var root = toHierarchy(data);
        // compute aggregates for root node based on children
        for (var childIndex in root.children) {{
          root.data.flows += root.children[childIndex].data.flows;
        }};
        // compute percentages
        root.each(function (node) {{
          node.data.dropped_offRatio = node.data.dropped_off / node.data.flows;
          node.data.reroutedRatio = node.data.rerouted / node.data.flows;
          node.data.flowRatio = node.data.flows / root.data.flows;
          node.data.flowRatioFromPrev = node.parent ? node.data.flows / node.parent.data.flows : node.data.flowRatio;
          node.data.notHandledRatio = node.data.not_handled / node.data.flows;
          if (_config.compareMode) {{ // if including previous period
            node.data.dropped_off_prevRatio = node.data.dropped_off_prev / node.data.flows_prev;
            node.data.rerouted_prevRatio = node.data.rerouted_prev / node.data.flows_prev;
            node.data.flow_prevRatio = node.data.flows_prev / root.data.flows_prev;
            node.data.flow_prevRatioFromPrev = node.parent ? node.data.flows_prev / node.parent.data.flows_prev : node.data.flow_prevRatio;
            node.data.trendPercentage = node.data.flows > node.data.flows_prev ?
              (node.data.flows - node.data.flows_prev) / node.data.flows :
              (node.data.flows - node.data.flows_prev) / node.data.flows_prev;
            // (node.data.flows / node.data.flows_prev * 100 ) - 100;
          }}

        }});
        return root;

      }}

      function updateInfoDiv() {{
        var node = _chart.selectedNode;
        d3.select(_chart.container).select(".infodiv-node-name").html("<span class='field-name'>Node name: </span>" + node.name);
        d3.select(_chart.container).select(".infodiv-node-path").html("<span class='field-name'>Path: </span>" + node.path);
        d3.select(_chart.container).select(".infodiv-node-visits").html("<span class='field-name'>Visits: </span>" + node.flows + " (" + (node.flowRatio * 100).toFixed(1) + "% of total | " + (node.flowRatioFromPrev * 100).toFixed(1) + "% of previous)");
        d3.select(_chart.container).select(".infodiv-node-dropoffs").html("<span class='field-name'>Drop offs: </span>" + node.dropped_off + " (" + (node.dropped_offRatio * 100).toFixed(1) + "%)");
        d3.select(_chart.container).select(".infodiv-node-reroutes").html("<span class='field-name'>Reroutes: </span>" + node.rerouted + " (" + (node.reroutedRatio * 100).toFixed(1) + "%)");
      }}

      function nodeSelectedEventHandler(d, selectedD3Node) {{

        _chart.selectedNode = d.data;
        // remove previous selection
        if (_chart.selectedD3Node)
          _chart.selectedD3Node.node().classList.remove("selected");
        // udpate current selection
        _chart.selectedD3Node = selectedD3Node;
        _chart.selectedD3Node.node().classList.add("selected");

        updateInfoDiv();
        var selection = {{ "dropped_off": [], "rerouted": [], "name": _chart.selectedNode.name, "path": _chart.selectedNode.path }};
        if (_chart.selectedNode.hasOwnProperty("conversation_log_ids_dropped_off"))
          selection.dropped_off = _chart.selectedNode.conversation_log_ids_dropped_off;
        if (_chart.selectedNode.hasOwnProperty("conversation_log_ids_rerouted"))
          selection.rerouted = _chart.selectedNode.conversation_log_ids_rerouted;

        //alert("List of abandoned conversation IDs copied to Python 'selection' variable");
        var handler = _chart.eventHandler["export"];
        if (handler) {{
          handler({{ 'selection': selection }});
        }}
      }};

      function createInfoDiv(_chart) {{
        var infodiv = $('<div>').addClass("botvis infodiv").appendTo(_chart.container);
        $('<div>', {{ text: 'Selection Details' }}).addClass("infodiv-title").appendTo(infodiv);
        $('<div>', {{ text: 'Name: ' }}).addClass("infodiv-node-name").appendTo(infodiv);
        $('<div>', {{ text: 'Path: ' }}).addClass("infodiv-node-path").appendTo(infodiv);
        $('<div>', {{ text: 'Visits: ' }}).addClass("infodiv-node-visits").appendTo(infodiv);
        $('<div>', {{ text: 'Drop offs: ' }}).addClass("infodiv-node-dropoffs").appendTo(infodiv);
        $('<div>', {{ text: 'Reroutes: ' }}).addClass("infodiv-node-reroutes").appendTo(infodiv);

      }}

      function createTitleDiv(_chart) {{
        var titleDiv = $('<div>').addClass("botvis titlediv").appendTo(_chart.container);
        $('<span>', {{ text: 'Description: ' }}).addClass("dataset-description-field").appendTo(titleDiv);
        $('<span>', {{ text: _chart.config.title }}).addClass("dataset-description").appendTo(titleDiv);
      }}

      _chart.eventHandler = [];
      _chart.on = function (event, fct) {{
        _chart.eventHandler[event] = fct;
      }};

      return _chart;
    }};
  </script>
</head>

<body>
  <div id="graph"></div>

  <script>
    var element = document.getElementById("graph");

    var config = {config}
    if (config["debugger"] === true) {{
      debugger;
    }};
    var chart = draw(element, config, {data});
    chart.on("export", function (e) {{
      var selection = JSON.stringify(e.selection).replace(/"/g, "'");
    }});
  </script>
</body>

</html>
"""


def prepare_data(logs, skill_id, workspace):

    logger.info(
        {"message": "Preparing data for dialog flow.", "skill_id": skill_id})

    df_logs = pd.DataFrame(logs)

    assistant_skills = wa_assistant_skills.WA_Assistant_Skills()
    assistant_skills.add_skill(skill_id, workspace)

    df_logs_canonical = transformation.to_canonical_WA_v2(df_logs, assistant_skills,
                                                          skill_id_field=None, include_nodes_visited_str_types=True,
                                                          include_context=False)

    df_logs_to_analyze = df_logs_canonical.copy(deep=False)

    turn_based_path_flows = analysis.aggregate_flows(df_logs_to_analyze, mode="turn-based",
                                                     on_column="turn_label", max_depth=400, trim_reroutes=False)

    return json.loads(turn_based_path_flows.to_json(orient='records'))


def generate_html_report(config, data):

    logger.info({"message": "Generating HTML report for Dialog Flow."})
    
    config = json.dumps(config)
    data = json.dumps(data)

    return _html_template.format(config=config, data=data)

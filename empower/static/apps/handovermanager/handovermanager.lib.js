var BASE_AUTH;

jQuery(document).ready(function($){

/* SVG for D3 dimensions. */
var area_width  = $("#graphRow").width(),
    area_height = $("#graphRow").height(),
    colors = d3.scale.category20();

/* Nodes and links of the graph. */
var nodes = [],
    links = [];

var svg = d3.select('#graphRow')
    .append('svg')
    .attr('class', 'nw_graph')
    .attr('width', area_width)
    .attr('height', area_height);

var gue;

/* Handles to link and node element groups. */
var nw_paths = svg.append('svg:g').selectAll('.link'),
    nw_enbs = svg.append('svg:g').selectAll('.enb'),
    nw_ues = svg.append('svg:g').selectAll('.ue');

/* Introduce force layout in the graph. */
var force = d3.layout.force()
    .size([area_width, area_height])
    .charge(-400)
    .linkDistance(60)
    .on("tick", tick);

/* Introduce drag event. */
var drag = force.drag()
    .on("dragstart", dragstart);

/* Define 'div' for tooltips */
var tp_div = d3.select('body')
    .append('div')
    .attr('class', 'tooltip')
    .style('opacity', 0);

fetchGraphData(tenant_id);

function fetchGraphData(tenant_id) {

    setTimeout(function () {

        $.getJSON("/api/v1/tenants/" + tenant_id + "/components/empower.apps.handovermanager.handovermanager", function(data) {
            /* Process the data here after receiving from app.*/
            if (data == null) {
                return;
            }

            var graph_data = data['graphData']

            var existing_nodes = nodes.slice(0);

            links.splice(0, links.length);
            nodes.splice(0, nodes.length);

            /* Iterate through already existing nodes. */
            for (var k in existing_nodes) {
                /* Existing node. */
                var en = existing_nodes[k];

                for (var i in graph_data.nodes) {
                    /* Node from API JSON result. */
                    var n = graph_data.nodes[i];

                    if (en.node_id === n.node_id && en.entity === n.entity &&
                        en.vbs_id === n.vbs_id) {
                        var node = {
                            id: n.id,
                            node_id: n.node_id,
                            vbs_id: n.vbs_id,
                            entity: n.entity,
                            tooltip: n.tooltip,
                            cells: n.cells,
                            stats: n.stats,
                            x: en.x,
                            y: en.y,
                            fixed: en.fixed
                           };
                        nodes.push(node);
                        graph_data.nodes.splice(i, 1);
                        break;
                    }
                }
            }

            /* Whatever nodes remains in graph_data should be added to nodes. */
            for (var i in graph_data.nodes) {
                var n = graph_data.nodes[i];
                var node = {
                            id: n.id,
                            node_id: n.node_id,
                            vbs_id: n.vbs_id,
                            entity: n.entity,
                            tooltip: n.tooltip,
                            cells: n.cells,
                            stats: n.stats,
                            x: n.x,
                            y: (area_height - n.y),
                            fixed: true
                           };
                nodes.push(node);
            }

            /* Add links from graph_data. */
            for (var i in graph_data.links) {
                var l = graph_data.links[i];

                var source, target;

                for (var m in nodes) {
                    if (nodes[m].id == l.src) {
                        source = nodes[m];
                    }
                    if (nodes[m].id == l.dst) {
                        target = nodes[m];
                    }
                }

                var link = {
                    source: source,
                    target: target,
                    rsrp: l.rsrp,
                    rsrq: l.rsrq,
                    color: l.color,
                    width: l.width
                }
                links.push(link);
            }

            updateNtkGraph();
            fetchGraphData(tenant_id);

            var $radios = $('input:radio[name=load_balance]');
            $("#load_balance_c").text(data['load_balance']);
            if ($radios.is(':checked') === false) {
                if (data['load_balance'] == true) {
                    $radios.filter('[value=true]').prop('checked', true);
                } else {
                    $radios.filter('[value=false]').prop('checked', true);
                }
            }
            $("#s_dl_thr_c").text(data['s_dl_thr']);
            $("#s_ul_thr_c").text(data['s_ul_thr']);
            $("#t_dl_thr_c").text(data['t_dl_thr']);
            $("#t_ul_thr_c").text(data['t_ul_thr']);
            $("#rsrq_thr_c").text(data['rsrq_thr']);
            $("#min_ue_c").text(data['min_ue']);
            $("#max_ho_from_c").text(data['max_ho_from']);
            $("#max_ho_to_c").text(data['max_ho_to']);
            $("#every_c").text(data['every']);

            BASE_AUTH = "Basic " + btoa(data['base_auth_usr'] + ':' + data['base_auth_pwd'])
        });

    }, 1000);

}

/* Update graph. */
function updateNtkGraph() {

    var g_nodes = nodes.slice(0);
    var g_links = links.slice(0);

    /* Setting SVG background color to white.*/
    d3.select('svg')
        .style('background-color', '#FFFFFF');

    force
    .nodes(g_nodes)
    .links(g_links);

    nw_paths = nw_paths.data(g_links)

    nw_paths.enter().append('line')
            .attr('class', 'link')
            .style('stroke', function(d) { return d.color; })
            .style('stroke-width', function(d) { return d.width; })
            .classed('neigh_cell', function(d) { return (d.width == 4); });

    nw_paths.on("mouseover", function(d) {
                tp_div.transition()
                    .duration(500)
                    .style("opacity", 0);
                tp_div.transition()
                    .duration(200)
                    .style("opacity", .9);
                tp_div.html("<p>" + "RSRP: " + d.rsrp + "</br>" +
                          "RSRQ: " + d.rsrq + "</p>")
                    .style("left", (d3.event.pageX + 18) + "px")
                    .style("top", (d3.event.pageY - 28) + "px");
            });

    nw_paths.style('stroke', function(d) { return d.color; })
            .style('stroke-width', function(d) { return d.width; })
            .classed('neigh_cell', function(d) { return (d.width == 4); });

    nw_paths.exit().remove();

    nw_enbs = nw_enbs.data(g_nodes.filter(function(d) {
                                            return d.entity === "enb";
                                        }),
                                        function(d) {
                                            return d.id;
                                        });

    nw_enbs.enter()
            .append('svg:image')
            .attr('class', 'enb')
            .attr('xlink:href', "/static/apps/handovermanager/bs.png")
            .attr('width', 50)
            .attr('height', 50)
            .on("dblclick", dblclick)
            .call(drag);

    nw_enbs.on("mouseover", function(d) {
                tp_div.transition()
                    .duration(500)
                    .style("opacity", 0);
                tp_div.transition()
                    .duration(200)
                    .style("opacity", .9);
                tt_str = "<p>" + "eNB Id" + ": " + d.node_id;
                if (!d.stats || Object.keys(d.stats).length == 0) {
                    tt_str = tt_str + "<br>" + d.tooltip + ": " +
                            d.cells.join();
                } else {
                    for (var c in d.stats) {
                        tt_str = tt_str + "<br>" + d.tooltip + ": " + c;
                        if (d.stats[c] && d.stats[c].hasOwnProperty('DL')) {
                            tt_str = tt_str + "</br>" + "DL: " +
                                    d.stats[c]['DL'] + "%";
                        }
                        if (d.stats[c] && d.stats[c].hasOwnProperty('UL')) {
                            tt_str = tt_str + "</br>" + "UL: " +
                                    d.stats[c]['UL'] + "%";
                        }
                    }
                }
                tt_str = tt_str + "</p>";
                tp_div .html(tt_str)
                    .style("left", (d3.event.pageX + 18) + "px")
                    .style("top", (d3.event.pageY - 28) + "px");
            });

    nw_enbs.attr('xlink:href', "/static/apps/handovermanager/bs.png")
            .attr('width', 50)
            .attr('height', 50);

    nw_enbs.exit().remove();

    nw_ues = nw_ues.data(g_nodes.filter(function(d) {
                                        return d.entity === "ue";
                        }),
                        function(d) {
                                    return d.id;
                        });

    gue = nw_ues.enter()
        .append('svg:g')
        .attr('class', 'ue');

    gue.append('svg:circle')
        .attr('r', 13)
        .style('fill', function(d) { return colors(d.id); })
        .style('stroke', function(d) { return d3.rgb(colors(d.id)).darker().toString(); })
        .style('stroke-width', '2.5px');

    gue.append('svg:text')
        .attr('x', 0)
        .attr('y', 4)
        .attr('class', 'node_id')
        .text(function(d) {
            return "UE";
        });

    gue.on("mouseover", function(d) {
            tp_div.transition()
                .duration(500)
                .style("opacity", 0);
            tp_div.transition()
                .duration(200)
                .style("opacity", .9);
            tp_div .html(d.tooltip + ": " + d.node_id)
                .style("left", (d3.event.pageX + 18) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
        });

    gue.on("dblclick", dblclick)
        .call(drag);

    gue.selectAll('circle')
        .style('fill', function(d) { return colors(d.id); })
        .style('stroke', function(d) { return d3.rgb(colors(d.id)).darker().toString(); })
        .style('stroke-width', '2.5px');

    nw_ues.exit().remove();

    force.start();
}

function tick() {

    nw_paths.attr("x1", function(d) {
                    return d.source.x;
            })
            .attr("y1", function(d) {
                    return d.source.y;
            })
            .attr("x2", function(d) {
                    return d.target.x;
            })
            .attr("y2", function(d) {
                    return d.target.y;
            });

    nw_enbs.attr('transform', function(d) {
        return 'translate(' + (d.x - 25) + ',' + (d.y - 25) + ')';
    });

    nw_ues.attr('transform', function(d) {
        return 'translate(' + d.x + ',' + d.y + ')';
    });
}

function dblclick(d) {
    d3.select(this).classed("fixed", d.fixed = false);
}

function dragstart(d, i) {
    d3.select(this).classed("fixed", d.fixed = true);
}

});

function openNav() {
    document.getElementById("hoSidenav").style.width = "100%";
}

function closeNav() {
    $('input[name="s_dl_thr"]').val('');
    $('input[name="s_ul_thr"]').val('');
    $('input[name="t_dl_thr"]').val('');
    $('input[name="t_ul_thr"]').val('');
    $('input[name="rsrq_thr"]').val('');
    $('input[name="min_ue"]').val('');
    $('input[name="max_ho_from"]').val('');
    $('input[name="max_ho_to"]').val('');
    $('input[name="every"]').val('');
    document.getElementById("hoSidenav").style.width = "0";
}

function modHOParam() {

    var url = "/api/v1/tenants/" + tenant_id + "/components/empower.apps.handovermanager.handovermanager";

    var load_balance = $('input[name="load_balance"]:checked').val();
    var s_dl_thr = $('input[name="s_dl_thr"]').val();
    var s_ul_thr = $('input[name="s_ul_thr"]').val();
    var t_dl_thr = $('input[name="t_dl_thr"]').val();
    var t_ul_thr = $('input[name="t_ul_thr"]').val();
    var rsrq_thr = $('input[name="rsrq_thr"]').val();
    var min_ue = $('input[name="min_ue"]').val();
    var max_ho_from = $('input[name="max_ho_from"]').val();
    var max_ho_to = $('input[name="max_ho_to"]').val();
    var every = $('input[name="every"]').val();

    if (s_dl_thr != "" && s_dl_thr > 100) {
        alert("Source DL threshold must be < 100");
        return false;
    }
    if (s_ul_thr != "" && s_ul_thr > 100) {
        alert("Source UL threshold must be < 100");
        return false;
    }
    if (t_dl_thr != "" && t_dl_thr > 100) {
        alert("Target DL threshold must be < 100");
        return false;
    }
    if (t_ul_thr != "" && t_ul_thr > 100) {
        alert("Target UL threshold must be < 100");
        return false;
    }
    if (rsrq_thr != "" && (rsrq_thr > -3 || rsrq_thr < -20)) {
        alert("UE RSRQ threshold must be within -3 and -20");
        return false;
    }
    if (every != "" && every < 100) {
        alert("Evaluation period (in ms.) must be greater than 100ms.");
        return false;
    }

    var data = new Object();
    data.version = '1.0';

    var params = new Object();
    if (load_balance != "") {
        if (load_balance == "true")
            params.load_balance = true
        else
            params.load_balance = false
    }
    if (s_dl_thr != "") {
        params.s_dl_thr = s_dl_thr;
    }
    if (s_ul_thr != "") {
        params.s_ul_thr = s_ul_thr;
    }
    if (s_dl_thr != "") {
        params.s_dl_thr = s_dl_thr;
    }
    if (t_dl_thr != "") {
        params.t_dl_thr = t_dl_thr;
    }
    if (t_ul_thr != "") {
        params.t_ul_thr = t_ul_thr;
    }
    if (rsrq_thr != "") {
        params.rsrq_thr = rsrq_thr;
    }
    if (min_ue != "") {
        params.min_ue = min_ue;
    }
    if (max_ho_from != "") {
        params.max_ho_from = max_ho_from;
    }
    if (max_ho_to != "") {
        params.max_ho_to = max_ho_to;
    }
    if (every != "") {
        params.every = every;
    }
    data.params  = params;

    $.ajax({
        url: url,
        type: 'PUT',
        dataType: 'json',
        data: JSON.stringify(data),
        cache: false,
        beforeSend: function (request) {
            request.setRequestHeader("Authorization", BASE_AUTH);
        },
        statusCode: {
            400: function (data) {
                alert(data.responseJSON.message);
            },
            404: function (data) {
                alert('Component not found');
            },
            500: function (data) {
                alert('Internal error');
            }
        }
    });

    $('input[name="s_dl_thr"]').val('');
    $('input[name="s_ul_thr"]').val('');
    $('input[name="t_dl_thr"]').val('');
    $('input[name="t_ul_thr"]').val('');
    $('input[name="rsrq_thr"]').val('');
    $('input[name="min_ue"]').val('');
    $('input[name="max_ho_from"]').val('');
    $('input[name="max_ho_to"]').val('');
    $('input[name="every"]').val('');

    document.getElementById("hoSidenav").style.width = "0";
}

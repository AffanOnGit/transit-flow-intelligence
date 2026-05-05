"""
app.py — Premium Dash Application for Transit Flow Intelligence
Tasks 3, 4, and 5 with Modern UI/UX
"""
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd
from pathlib import Path
from utils import (
    load_routes, group_by_case, compute_edges, aggregate_edges,
    compute_throughput, throughput_summary, detect_bottlenecks,
    build_node_positions
)
from task5_agent import TransitAgent

# Load Data
script_dir = Path(__file__).parent
csv_path = script_dir.parent / "data" / "routes.csv"
rows = load_routes(str(csv_path))
cases = group_by_case(rows)
all_edges = aggregate_edges(compute_edges(cases))
throughput_data = compute_throughput(cases)
node_coords = build_node_positions(rows)

# Initialize AI Agent
agent = TransitAgent(str(csv_path))

# Load Inter font from Google
external_stylesheets = [
    dbc.themes.SLATE,
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap",
    "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
]

app = dash.Dash(
    __name__, 
    title="Transit Flow Intelligence",
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True
)

# Normalise Lat/Lon for Cytoscape
def normalise_coords(coords):
    if not coords: return {}
    lats = [c[0] for c in coords.values()]
    lons = [c[1] for c in coords.values()]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    
    norm = {}
    for name, (lat, lon) in coords.items():
        x = 100 + (lon - min_lon) / (max_lon - min_lon + 1e-9) * 1200
        y = 1200 - (lat - min_lat) / (max_lat - min_lat + 1e-9) * 1200
        norm[name] = {"x": x, "y": y}
    return norm

norm_coords = normalise_coords(node_coords)

# Build Cytoscape Elements
def get_cyto_elements(route_id="All", bottleneck_threshold=1.5):
    nodes = []
    edges = []
    
    filtered_rows = [r for r in rows if route_id == "All" or r["route_id"] == route_id]
    stops_in_view = set(r["stop_name"] for r in filtered_rows)
    
    for stop in stops_in_view:
        pos = norm_coords.get(stop, {"x": 500, "y": 500})
        nodes.append({
            'data': {'id': stop, 'label': stop},
            'position': pos
        })
        
    current_edges = [e for e in all_edges if route_id == "All" or e["route_id"] == route_id]
    current_edges = detect_bottlenecks(current_edges, bottleneck_threshold)
    
    for e in current_edges:
        is_bottleneck = e.get("is_bottleneck", False)
        edges.append({
            'data': {
                'source': e['from_stop'], 
                'target': e['to_stop'], 
                'label': e['label'],
                'avg_sec': e['avg_sec'],
                'cases': e['case_count'],
                'route': e['route_id'],
                'bottleneck': 'yes' if is_bottleneck else 'no'
            },
            'classes': 'bottleneck' if is_bottleneck else ''
        })
        
    return nodes + edges

# Custom Styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body { font-family: 'Inter', sans-serif; background-color: #020617; }
            .glass-card {
                background: rgba(30, 41, 59, 0.7);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            }
            .sidebar {
                height: 100vh;
                padding: 24px;
                border-right: 1px solid rgba(255, 255, 255, 0.1);
            }
            .stats-pill {
                background: rgba(59, 130, 246, 0.1);
                border: 1px solid rgba(59, 130, 246, 0.2);
                padding: 12px;
                border-radius: 12px;
                margin-bottom: 12px;
            }
            .chat-bubble-user {
                background: #3b82f6;
                color: white;
                padding: 10px 16px;
                border-radius: 16px 16px 4px 16px;
                margin-bottom: 12px;
                align-self: flex-end;
                max-width: 80%;
            }
            .chat-bubble-agent {
                background: #334155;
                color: #f1f5f9;
                padding: 10px 16px;
                border-radius: 16px 16px 16px 4px;
                margin-bottom: 12px;
                align-self: flex-start;
                max-width: 80%;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
            .bottleneck-item {
                border-left: 4px solid #ef4444;
                background: rgba(239, 68, 68, 0.05);
                padding: 8px 12px;
                margin-bottom: 8px;
                border-radius: 4px;
                font-size: 0.9rem;
            }
            ::-webkit-scrollbar { width: 6px; }
            ::-webkit-scrollbar-track { background: transparent; }
            ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
            ::-webkit-scrollbar-thumb:hover { background: #475569; }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = dbc.Container(fluid=True, style={'padding': '0', 'overflow': 'hidden'}, children=[
    dbc.Row(className="g-0", children=[
        # Left Sidebar
        dbc.Col(md=3, lg=2, className="sidebar glass-card d-flex flex-column", children=[
            html.Div(className="mb-4", children=[
                html.H4("TransitFlow", className="fw-bold text-primary mb-0", style={'letterSpacing': '1px'}),
                html.P("Intelligence Dashboard", className="text-muted small")
            ]),
            
            html.Div(className="flex-grow-1", children=[
                html.Label("Route Network", className="text-muted small fw-bold text-uppercase mb-2"),
                dcc.Dropdown(
                    id='route-filter',
                    options=[{'label': 'All CDA Routes', 'value': 'All'}] + [{'label': f"Route {r}", 'value': r} for r in sorted(list(set(r["route_id"] for r in rows)))],
                    value='All',
                    className="mb-4 custom-dropdown",
                    style={'backgroundColor': 'transparent', 'color': '#000'}
                ),
                
                html.Label("Bottleneck Threshold", className="text-muted small fw-bold text-uppercase mb-2"),
                dcc.Slider(
                    id='bottleneck-slider',
                    min=1.0, max=3.0, step=0.1, value=1.5,
                    marks={1: '1x', 2: '2x', 3: '3x'},
                    className="mb-5"
                ),
                
                html.Hr(style={'opacity': '0.1'}),
                
                html.H6("Network Performance", className="text-white mb-3"),
                html.Div(id='throughput-stats'),
                
                html.H6("Critical Bottlenecks", className="text-white mt-4 mb-3"),
                html.Div(id='bottleneck-list')
            ]),
            
            html.Div(className="mt-auto pt-3", style={'borderTop': '1px solid rgba(255,255,255,0.05)'}, children=[
                html.P("© 2026 PMS Group 4", className="text-muted extra-small mb-0")
            ])
        ]),
        
        # Main Map View
        dbc.Col(md=6, lg=7, style={'height': '100vh', 'position': 'relative'}, children=[
            cyto.Cytoscape(
                id='transit-map',
                layout={'name': 'preset'},
                style={'width': '100%', 'height': '100%'},
                elements=get_cyto_elements(),
                stylesheet=[
                    {
                        'selector': 'node',
                        'style': {
                            'label': 'data(label)',
                            'color': '#cbd5e1',
                            'background-color': '#6366f1',
                            'font-size': '12px',
                            'width': '24px',
                            'height': '24px',
                            'border-width': '3px',
                            'border-color': '#1e1b4b',
                            'text-valign': 'bottom',
                            'text-margin-y': 8,
                            'font-weight': '600'
                        }
                    },
                    {
                        'selector': 'edge',
                        'style': {
                            'label': 'data(label)',
                            'width': 3,
                            'line-color': '#334155',
                            'target-arrow-color': '#334155',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'font-size': '10px',
                            'color': '#94a3b8',
                            'text-rotation': 'autorotate',
                            'text-margin-y': -12,
                            'opacity': 0.8
                        }
                    },
                    {
                        'selector': '.bottleneck',
                        'style': {
                            'line-color': '#ef4444',
                            'line-style': 'dashed',
                            'width': 5,
                            'target-arrow-color': '#ef4444',
                            'opacity': 1
                        }
                    },
                    {
                        'selector': 'node:selected',
                        'style': {
                            'background-color': '#f59e0b',
                            'width': '32px',
                            'height': '32px',
                            'color': '#fbbf24'
                        }
                    }
                ]
            ),
            
            # Floating Tooltip
            html.Div(id='edge-detail', className="glass-card", style={'position': 'absolute', 'bottom': '30px', 'left': '30px', 'padding': '20px', 'display': 'none', 'zIndex': '1000'})
        ]),
        
        # Right Chat Sidebar
        dbc.Col(md=3, lg=3, className="sidebar glass-card d-flex flex-column", children=[
            html.Div(className="mb-4 d-flex align-items-center", children=[
                html.I(className="fas fa-robot text-primary me-2", style={'fontSize': '20px'}),
                html.H5("AI Trip Planner", className="mb-0 text-white")
            ]),
            
            html.Div(id='chat-history', className="flex-grow-1 d-flex flex-column", style={'overflowY': 'auto', 'padding': '5px'}),
            
            html.Div(className="mt-3", children=[
                dbc.InputGroup(children=[
                    dbc.Input(id='chat-input', placeholder="Where would you like to go?", style={'backgroundColor': '#0f172a', 'border': '1px solid #334155', 'color': 'white'}),
                    dbc.Button(html.I(className="fas fa-paper-plane"), id='chat-send', color="primary")
                ])
            ])
        ])
    ])
])

@app.callback(
    [Output('transit-map', 'elements'),
     Output('throughput-stats', 'children'),
     Output('bottleneck-list', 'children')],
    [Input('route-filter', 'value'),
     Input('bottleneck-slider', 'value')]
)
def update_dashboard(route_id, threshold):
    elements = get_cyto_elements(route_id, threshold)
    
    filtered_tp = [t for t in throughput_data if route_id == "All" or t["route_id"] == route_id]
    stats = throughput_summary(filtered_tp)
    
    tp_content = [
        html.Div(className="stats-pill", children=[
            html.Div("Average Trip", className="text-muted small"),
            html.Div(stats['avg'], className="fw-bold text-white fs-5")
        ]),
        html.Div(className="stats-pill", children=[
            html.Div("Fastest Trip", className="text-muted small"),
            html.Div(stats['min'], className="fw-bold text-success fs-5")
        ])
    ]
    
    current_edges = [e for e in all_edges if route_id == "All" or e["route_id"] == route_id]
    bottlenecks = detect_bottlenecks(current_edges, threshold)
    top_3 = [b for b in bottlenecks if b.get("is_bottleneck")][:3]
    
    if not top_3:
        bl_content = html.Div("Optimum flow detected.", className="text-muted small italic")
    else:
        bl_content = [
            html.Div(className="bottleneck-item", children=[
                html.Div(f"{b['from_stop']} → {b['to_stop']}", className="fw-bold text-white"),
                html.Div(f"Duration: {b['label']}", className="text-danger small")
            ]) for b in top_3
        ]
        
    return elements, tp_content, bl_content

@app.callback(
    Output('edge-detail', 'children'),
    Output('edge-detail', 'style'),
    Input('transit-map', 'tapEdgeData')
)
def display_edge_data(data):
    if not data:
        return "", {'display': 'none'}
    
    content = [
        html.H6(f"{data['source']} ➔ {data['target']}", className="text-primary fw-bold mb-3"),
        dbc.Row([
            dbc.Col([
                html.Div("Route", className="text-muted small"),
                html.Div(data['route'], className="fw-bold")
            ]),
            dbc.Col([
                html.Div("Frequency", className="text-muted small"),
                html.Div(f"{data['cases']} trips", className="fw-bold")
            ])
        ]),
        html.Hr(style={'opacity': '0.1', 'margin': '15px 0'}),
        html.Div([
            html.Div("Average Transition Time", className="text-muted small"),
            html.Div(data['label'], className="fw-bold text-white fs-4")
        ])
    ]
    return content, {'position': 'absolute', 'bottom': '30px', 'left': '30px', 'padding': '20px', 'display': 'block', 'zIndex': '1000', 'minWidth': '280px'}

@app.callback(
    Output('chat-history', 'children'),
    Output('chat-input', 'value'),
    Input('chat-send', 'n_clicks'),
    State('chat-input', 'value'),
    State('chat-history', 'children'),
    prevent_initial_call=True
)
def chat(n_clicks, user_input, history):
    if not user_input:
        return history, ""
    
    history = history or []
    
    # User message
    history.append(html.Div(user_input, className="chat-bubble-user"))
    
    # Agent response
    response = agent.query(user_input)
    history.append(html.Div(response, className="chat-bubble-agent"))
    
    return history, ""

if __name__ == "__main__":
    app.run(debug=True)

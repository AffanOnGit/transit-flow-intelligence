"""
app.py — Main Dash Application for Transit Flow Intelligence
Tasks 3, 4, and 5
"""
import dash
from dash import dcc, html, Input, Output, State, callback
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

app = dash.Dash(__name__, title="Transit Flow Intelligence")

# Normalise Lat/Lon for Cytoscape
def normalise_coords(coords):
    if not coords: return {}
    lats = [c[0] for c in coords.values()]
    lons = [c[1] for c in coords.values()]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    
    norm = {}
    for name, (lat, lon) in coords.items():
        # Map to 100-900 range
        x = 100 + (lon - min_lon) / (max_lon - min_lon + 1e-9) * 800
        y = 900 - (lat - min_lat) / (max_lat - min_lat + 1e-9) * 800
        norm[name] = {"x": x, "y": y}
    return norm

norm_coords = normalise_coords(node_coords)

# Build Cytoscape Elements
def get_cyto_elements(route_id="All", bottleneck_threshold=1.5):
    nodes = []
    edges = []
    
    filtered_rows = [r for r in rows if route_id == "All" or r["route_id"] == route_id]
    stops_in_view = set(r["stop_name"] for r in filtered_rows)
    
    # Add Nodes
    for stop in stops_in_view:
        pos = norm_coords.get(stop, {"x": 500, "y": 500})
        nodes.append({
            'data': {'id': stop, 'label': stop},
            'position': pos
        })
        
    # Add Edges
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

app.layout = html.Div(style={'backgroundColor': '#0f172a', 'color': '#f8fafc', 'fontFamily': 'Inter, sans-serif', 'height': '100vh', 'display': 'flex', 'flexDirection': 'column'}, children=[
    # Header
    html.Div(style={'padding': '20px', 'backgroundColor': '#1e293b', 'borderBottom': '1px solid #334155', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[
        html.H1("Bus Route Process Mining Dashboard", style={'margin': '0', 'fontSize': '24px', 'fontWeight': '700'}),
        html.Div("CDA Transit Network Analysis", style={'opacity': '0.7'})
    ]),
    
    # Main Content
    html.Div(style={'display': 'flex', 'flex': '1', 'overflow': 'hidden'}, children=[
        # Left Panel (Controls & Analytics)
        html.Div(style={'width': '350px', 'padding': '20px', 'backgroundColor': '#1e293b', 'borderRight': '1px solid #334155', 'overflowY': 'auto'}, children=[
            html.H3("Filters", style={'marginTop': '0'}),
            html.Label("Route Selection"),
            dcc.Dropdown(
                id='route-filter',
                options=[{'label': 'All Routes', 'value': 'All'}] + [{'label': r, 'value': r} for r in sorted(list(set(r["route_id"] for r in rows)))],
                value='All',
                style={'color': '#000', 'marginBottom': '20px'}
            ),
            
            html.Label("Bottleneck Threshold (Multiplier)"),
            dcc.Slider(
                id='bottleneck-slider',
                min=1.0, max=3.0, step=0.1, value=1.5,
                marks={1: '1x', 1.5: '1.5x', 2: '2x', 3: '3x'},
            ),
            
            html.Hr(style={'margin': '30px 0', 'opacity': '0.2'}),
            
            html.H3("Route Performance"),
            html.Div(id='throughput-stats', style={'backgroundColor': '#334155', 'padding': '15px', 'borderRadius': '8px', 'marginBottom': '20px'}),
            
            html.H3("Top Bottlenecks"),
            html.Div(id='bottleneck-list')
        ]),
        
        # Center Panel (Map)
        html.Div(style={'flex': '1', 'position': 'relative', 'backgroundColor': '#020617'}, children=[
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
                            'color': '#f8fafc',
                            'background-color': '#3b82f6',
                            'font-size': '12px',
                            'width': '20px',
                            'height': '20px'
                        }
                    },
                    {
                        'selector': 'edge',
                        'style': {
                            'label': 'data(label)',
                            'width': 2,
                            'line-color': '#64748b',
                            'target-arrow-color': '#64748b',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'font-size': '10px',
                            'color': '#cbd5e1',
                            'text-margin-y': -10
                        }
                    },
                    {
                        'selector': '.bottleneck',
                        'style': {
                            'line-color': '#ef4444',
                            'line-style': 'dashed',
                            'width': 4,
                            'target-arrow-color': '#ef4444'
                        }
                    }
                ]
            ),
            # Edge Click Detail
            html.Div(id='edge-detail', style={'position': 'absolute', 'bottom': '20px', 'right': '20px', 'backgroundColor': '#1e293b', 'padding': '15px', 'borderRadius': '8px', 'border': '1px solid #334155', 'display': 'none'})
        ]),
        
        # Right Panel (AI Agent)
        html.Div(style={'width': '400px', 'padding': '20px', 'backgroundColor': '#1e293b', 'borderLeft': '1px solid #334155', 'display': 'flex', 'flexDirection': 'column'}, children=[
            html.H3("AI Trip Planner", style={'marginTop': '0'}),
            html.Div(id='chat-history', style={'flex': '1', 'overflowY': 'auto', 'marginBottom': '20px', 'padding': '10px', 'backgroundColor': '#0f172a', 'borderRadius': '8px', 'fontSize': '14px'}),
            html.Div(style={'display': 'flex'}, children=[
                dcc.Input(id='chat-input', type='text', placeholder='Ask about routes...', style={'flex': '1', 'padding': '10px', 'borderRadius': '4px 0 0 4px', 'border': 'none'}),
                html.Button("Send", id='chat-send', style={'padding': '10px 20px', 'backgroundColor': '#3b82f6', 'color': '#fff', 'border': 'none', 'borderRadius': '0 4px 4px 0', 'cursor': 'pointer'})
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
    # Map Elements
    elements = get_cyto_elements(route_id, threshold)
    
    # Throughput Stats
    filtered_tp = [t for t in throughput_data if route_id == "All" or t["route_id"] == route_id]
    stats = throughput_summary(filtered_tp)
    tp_content = [
        html.P(f"Avg: {stats['avg']}"),
        html.P(f"Min: {stats['min']}"),
        html.P(f"Max: {stats['max']}")
    ]
    
    # Bottlenecks
    current_edges = [e for e in all_edges if route_id == "All" or e["route_id"] == route_id]
    bottlenecks = detect_bottlenecks(current_edges, threshold)
    top_3 = [b for b in bottlenecks if b.get("is_bottleneck")][:3]
    
    if not top_3:
        bl_content = html.P("No bottlenecks detected at this threshold.", style={'fontStyle': 'italic', 'opacity': '0.5'})
    else:
        bl_content = html.Ul([
            html.Li(f"{b['from_stop']} → {b['to_stop']} ({b['label']})") for b in top_3
        ])
        
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
        html.B(f"{data['source']} to {data['target']}"),
        html.P(f"Route: {data['route']}"),
        html.P(f"Avg Duration: {data['label']}"),
        html.P(f"Total Trips: {data['cases']}")
    ]
    return content, {'position': 'absolute', 'bottom': '20px', 'right': '20px', 'backgroundColor': '#1e293b', 'padding': '15px', 'borderRadius': '8px', 'border': '1px solid #334155', 'display': 'block', 'zIndex': '100'}

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
    history.append(html.Div([
        html.B("You: "), html.Span(user_input)
    ], style={'marginBottom': '10px', 'color': '#3b82f6'}))
    
    # Agent response
    response = agent.query(user_input)
    history.append(html.Div([
        html.B("Agent: "), html.Span(response)
    ], style={'marginBottom': '20px'}))
    
    return history, ""

if __name__ == "__main__":
    app.run_server(debug=True)

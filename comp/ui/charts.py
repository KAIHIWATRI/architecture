import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_latency_comparison(trad_stats, adv_stats):
    fig = go.Figure(data=[
        go.Bar(name='Traditional', x=['Total Access Time (ns)'], y=[trad_stats['total_time_ns']]),
        go.Bar(name='Advanced', x=['Total Access Time (ns)'], y=[adv_stats['total_time_ns']])
    ])
    fig.update_layout(barmode='group', title='Total Execution Time Comparison')
    return fig

def plot_cache_hits_pie(stats, title):
    caches = stats['caches']
    if not caches:
        return None
    
    hits = sum(c['hits'] for c in caches)
    misses = caches[0]['misses'] # Misses out of the first level cache
    
    fig = go.Figure(data=[go.Pie(labels=['Cache Hits', 'Cache Misses (L1)'], values=[hits, misses])])
    fig.update_layout(title=title)
    return fig

def plot_amats(trad_stats, adv_stats, trad_amat, adv_amat):
    fig = go.Figure(data=[
        go.Bar(name='Traditional', x=['AMAT (ns)'], y=[trad_amat]),
        go.Bar(name='Advanced', x=['AMAT (ns)'], y=[adv_amat])
    ])
    fig.update_layout(barmode='group', title='Average Memory Access Time (AMAT)')
    return fig

def plot_page_faults(trad_stats, adv_stats):
    trad_faults = trad_stats['virtual_memory']['page_table']['faults'] if 'virtual_memory' in trad_stats else 0
    adv_faults = adv_stats['virtual_memory']['page_table']['faults'] if 'virtual_memory' in adv_stats else 0
    
    fig = go.Figure(data=[
        go.Bar(name='Traditional', x=['Page Faults'], y=[trad_faults]),
        go.Bar(name='Advanced', x=['Page Faults'], y=[adv_faults])
    ])
    fig.update_layout(barmode='group', title='Page Faults Comparison')
    return fig

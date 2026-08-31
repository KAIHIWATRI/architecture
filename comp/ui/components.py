import streamlit as st
from sim.storage.storage_models import STORAGE_MODELS

def config_form(prefix, default_preset='traditional'):
    st.subheader(f"{prefix} Architecture")
    
    if default_preset == 'traditional':
        l1_size, l2_size, l3_size = 32*1024, 256*1024, 0
        cache_policy = 'FIFO'
        use_vm = False
        storage_model = 'HDD'
        page_policy = 'FIFO'
    else:
        l1_size, l2_size, l3_size = 32*1024, 512*1024, 8*1024*1024
        cache_policy = 'LRU'
        use_vm = True
        storage_model = 'NVMe SSD'
        page_policy = 'LRU'

    with st.expander("Cache Hierarchy", expanded=True):
        l1_size = st.number_input(f"{prefix} L1 Size (Bytes)", value=l1_size, step=1024)
        l2_size = st.number_input(f"{prefix} L2 Size (Bytes)", value=l2_size, step=1024)
        l3_size = st.number_input(f"{prefix} L3 Size (Bytes)", value=l3_size, step=1024)
        cache_policy = st.selectbox(f"{prefix} Cache Policy", ['LRU', 'FIFO', 'Random'], index=['LRU', 'FIFO', 'Random'].index(cache_policy))
        block_size = st.number_input(f"{prefix} Block Size", value=64, step=16)

    with st.expander("Virtual Memory & Storage", expanded=True):
        use_vm = st.checkbox(f"{prefix} Enable Virtual Memory", value=use_vm)
        tlb_size = st.number_input(f"{prefix} TLB Size (Entries)", value=64 if use_vm else 0)
        page_policy = st.selectbox(f"{prefix} Page Replacement", ['LRU', 'FIFO', 'Optimal'], index=['LRU', 'FIFO', 'Optimal'].index(page_policy))
        storage_model = st.selectbox(f"{prefix} Storage Technology", list(STORAGE_MODELS.keys()), index=list(STORAGE_MODELS.keys()).index(storage_model))
        
        # Info panel for simulated models
        if STORAGE_MODELS[storage_model].is_simulated:
            st.info(f"**Educational Simulation Notice**: {storage_model} is a parameterized simulation model, not physical hardware testing.")

    return {
        'l1_size': l1_size, 'l1_assoc': 4, 'l1_latency': 1.0,
        'l2_size': l2_size, 'l2_assoc': 8, 'l2_latency': 5.0,
        'l3_size': l3_size, 'l3_assoc': 16, 'l3_latency': 20.0,
        'block_size': block_size,
        'cache_policy': cache_policy,
        'ram_size': 1024 * 1024 * 1024, # 1GB
        'ram_latency': 100.0,
        'use_virtual_memory': use_vm,
        'tlb_size': tlb_size,
        'tlb_latency': 0.5,
        'page_size': 4096,
        'page_replacement_policy': page_policy,
        'storage_model': STORAGE_MODELS[storage_model]
    }

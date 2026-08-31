import streamlit as st
import pandas as pd
from ui.components import config_form
from ui.charts import plot_latency_comparison, plot_cache_hits_pie, plot_amats, plot_page_faults
from sim.core.simulator import Simulator
from sim.core.metrics import MetricsAnalyzer
from sim.workload.generator import WorkloadGenerator

st.set_page_config(page_title="Memory Architecture Simulator", layout="wide")

st.title("Optimizing Computer System Performance through Advanced Cache Hierarchies, Virtual Memory, and Emerging Storage Technologies")
st.markdown("""
**Educational Architectural Simulation Model**
This application simulates how different memory architectures affect computer-system performance. It compares a traditional memory architecture with an advanced architecture featuring deeper cache hierarchies, optimized virtual memory, and emerging storage technologies. Note that this is not a cycle-accurate CPU simulator, but an educational model.
""")

# Experiment Presets
preset = st.selectbox("Load Experiment Preset", ["Default Experiment", "Cache Comparison", "Page Replacement Comparison", "Storage Comparison", "Stress Test"])

if 'history' not in st.session_state:
    st.session_state.history = []

col1, col2 = st.columns(2)

with col1:
    trad_config = config_form("Traditional", "traditional")

with col2:
    adv_config = config_form("Advanced", "advanced")
    
st.header("Workload Configuration")
wl_col1, wl_col2, wl_col3 = st.columns(3)
with wl_col1:
    workload_type = st.selectbox("Workload Type", ["Sequential", "Random", "Locality", "Stress (Thrashing)"])
with wl_col2:
    num_accesses = st.number_input("Number of Memory Accesses", value=10000, step=1000)
with wl_col3:
    random_seed = st.number_input("Random Seed (for reproducibility)", value=42)

if st.button("RUN SIMULATION", type="primary"):
    with st.spinner("Generating workload and running simulations..."):
        # Generate Workload
        generator = WorkloadGenerator(seed=random_seed)
        if workload_type == "Sequential":
            workload = generator.generate_sequential(0, num_accesses)
        elif workload_type == "Random":
            workload = generator.generate_random(0, 1024*1024, num_accesses)
        elif workload_type == "Locality":
            workload = generator.generate_locality(0, num_accesses)
        elif workload_type == "Stress (Thrashing)":
            workload = generator.generate_stress(num_accesses, adv_config['l1_size'])
            
        # Run Traditional
        trad_sim = Simulator(trad_config)
        trad_sim.run(workload, generate_trace=True)
        trad_stats = trad_sim.get_stats()
        trad_amat = MetricsAnalyzer.calculate_amat(trad_stats, num_accesses)
        
        # Run Advanced
        adv_sim = Simulator(adv_config)
        adv_sim.run(workload, generate_trace=True)
        adv_stats = adv_sim.get_stats()
        adv_amat = MetricsAnalyzer.calculate_amat(adv_stats, num_accesses)
        
        speedup = MetricsAnalyzer.calculate_speedup(trad_stats, adv_stats)
        improvement = (trad_stats['total_time_ns'] - adv_stats['total_time_ns']) / trad_stats['total_time_ns'] * 100 if trad_stats['total_time_ns'] > 0 else 0
        
        # Save to history
        st.session_state.history.append({
            'preset': preset,
            'workload': workload_type,
            'accesses': num_accesses,
            'trad_amat': trad_amat,
            'adv_amat': adv_amat,
            'speedup': speedup
        })
        
        st.header("Simulation Results")
        
        # Main Dashboard Metrics
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.subheader("TRADITIONAL")
            st.metric("Total Time (ns)", f"{trad_stats['total_time_ns']:.2f}")
            st.metric("AMAT (ns)", f"{trad_amat:.2f}")
            hr = sum(c['hits'] for c in trad_stats['caches']) / (trad_stats['caches'][0]['accesses'] if trad_stats['caches'] else 1) * 100
            st.metric("Overall Cache Hit Rate", f"{hr:.2f}%")
            if trad_config['use_virtual_memory']:
                tlb_hr = trad_stats['virtual_memory']['tlb']['hit_rate']*100 if trad_stats['virtual_memory']['tlb'] else 0
                st.metric("TLB Hit Rate", f"{tlb_hr:.2f}%")
                st.metric("Page Faults", trad_stats['virtual_memory']['page_table']['faults'])
                st.metric("Total Storage Time (ns)", trad_stats['virtual_memory']['storage']['total_time'])
        
        with res_col2:
            st.subheader("ADVANCED")
            st.metric("Total Time (ns)", f"{adv_stats['total_time_ns']:.2f}")
            st.metric("AMAT (ns)", f"{adv_amat:.2f}")
            hr = sum(c['hits'] for c in adv_stats['caches']) / (adv_stats['caches'][0]['accesses'] if adv_stats['caches'] else 1) * 100
            st.metric("Overall Cache Hit Rate", f"{hr:.2f}%")
            if adv_config['use_virtual_memory']:
                tlb_hr = adv_stats['virtual_memory']['tlb']['hit_rate']*100 if adv_stats['virtual_memory']['tlb'] else 0
                st.metric("TLB Hit Rate", f"{tlb_hr:.2f}%")
                st.metric("Page Faults", adv_stats['virtual_memory']['page_table']['faults'])
                st.metric("Total Storage Time (ns)", adv_stats['virtual_memory']['storage']['total_time'])
                
        st.markdown("---")
        st.subheader(f"Performance Improvement: {improvement:.2f}%")
        st.subheader(f"Speedup: {speedup:.2f}x")
        
        st.header("Automatic Explanation")
        explanation = MetricsAnalyzer.generate_explanation(trad_stats, adv_stats, num_accesses, num_accesses)
        st.info(explanation)
        
        st.header("Visualizations")
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.plotly_chart(plot_latency_comparison(trad_stats, adv_stats), use_container_width=True)
            st.plotly_chart(plot_cache_hits_pie(trad_stats, "Traditional Cache Hits/Misses"), use_container_width=True)
        with chart_col2:
            st.plotly_chart(plot_amats(trad_stats, adv_stats, trad_amat, adv_amat), use_container_width=True)
            if adv_config['use_virtual_memory'] or trad_config['use_virtual_memory']:
                st.plotly_chart(plot_page_faults(trad_stats, adv_stats), use_container_width=True)
                
        with st.expander("Detailed Simulation Trace (First 100 Accesses)"):
            st.write("### Advanced Architecture Trace")
            for entry in adv_sim.trace:
                st.text(f"Access #{entry['access_num']} | Address: {entry['address']} | Latency: {entry['latency']:.1f} ns")
                st.text("  -> " + " | ".join(entry['events']))

if st.session_state.history:
    with st.expander("Experiment History"):
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df)

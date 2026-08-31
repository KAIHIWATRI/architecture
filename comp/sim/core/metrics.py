class MetricsAnalyzer:
    @staticmethod
    def calculate_amat(stats, workload_size: int) -> float:
        """
        Calculates effective AMAT from actual simulation time.
        AMAT = Total Time / Number of Accesses
        """
        if workload_size == 0:
            return 0.0
        return stats['total_time_ns'] / workload_size

    @staticmethod
    def generate_explanation(trad_stats, adv_stats, trad_workload_size: int, adv_workload_size: int) -> str:
        trad_time = trad_stats['total_time_ns']
        adv_time = adv_stats['total_time_ns']
        
        explanation = []
        if adv_time < trad_time:
            explanation.append("The Advanced architecture performed better for this workload.")
        elif trad_time < adv_time:
            explanation.append("The Traditional architecture performed better for this workload.")
        else:
            explanation.append("Both architectures performed equally for this workload.")

        # Analyze Cache
        def get_overall_hit_rate(stats):
            hits = sum(c['hits'] for c in stats['caches'])
            accesses = stats['caches'][0]['accesses'] if stats['caches'] else 1
            return hits / accesses if accesses > 0 else 0

        trad_hr = get_overall_hit_rate(trad_stats)
        adv_hr = get_overall_hit_rate(adv_stats)

        if adv_hr > trad_hr:
            explanation.append("• Higher overall cache hit rate in the Advanced architecture reduced slower memory accesses.")
        elif trad_hr > adv_hr:
            explanation.append("• The Traditional architecture had a better cache hit rate for this specific access pattern.")

        # Analyze L3
        if len(adv_stats['caches']) > 2 and len(trad_stats['caches']) <= 2:
            l3_hits = adv_stats['caches'][2]['hits']
            if l3_hits > 0:
                explanation.append(f"• The L3 cache absorbed {l3_hits} accesses that would have otherwise gone to main memory.")

        # Analyze Virtual Memory
        if 'virtual_memory' in adv_stats:
            adv_faults = adv_stats['virtual_memory']['page_table']['faults']
            if 'virtual_memory' in trad_stats:
                trad_faults = trad_stats['virtual_memory']['page_table']['faults']
                if adv_faults < trad_faults:
                    explanation.append("• The advanced page replacement policy reduced the number of page faults.")
                
            adv_storage_avg = adv_stats['virtual_memory']['storage']['read_latency_avg']
            if 'virtual_memory' in trad_stats:
                trad_storage_avg = trad_stats['virtual_memory']['storage']['read_latency_avg']
                if adv_storage_avg < trad_storage_avg:
                    explanation.append("• The modern/emerging storage technology significantly reduced page fault penalty latency.")
            else:
                explanation.append("• Storage latency was mitigated by the advanced storage technology during page faults.")

        if adv_time < trad_time:
             explanation.append("• Overall, the optimized configuration reduced total memory-access time.")

        return "\n".join(explanation)

    @staticmethod
    def calculate_speedup(trad_stats, adv_stats) -> float:
        if adv_stats['total_time_ns'] == 0:
            return 1.0
        return trad_stats['total_time_ns'] / adv_stats['total_time_ns']

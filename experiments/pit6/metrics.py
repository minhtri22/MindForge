def decision_improvement(results):
    return results["pit_accuracy"]-results["memory_accuracy"]

def pattern_precision(tp, fp):
    return tp/(tp+fp) if tp+fp else 0

def false_pattern_rate(fp,total):
    return fp/total if total else 0

def calibration(conf,correct):
    return abs(conf-correct)

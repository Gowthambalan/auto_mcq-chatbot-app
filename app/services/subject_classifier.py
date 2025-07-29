def detect_subject_from_text(text: str):
    lower = text.lower()
    if any(word in lower for word in ['algebra', 'calculus', 'integration', 'geometry', 'set', 'mathematics']):
        return 'maths'
    elif any(word in lower for word in ['reaction', 'molecule', 'compound', 'acid']):
        return 'chemistry'
    elif any(word in lower for word in ['velocity', 'force', 'mass', 'quantum']):
        return 'physics'
    return 'unknown'

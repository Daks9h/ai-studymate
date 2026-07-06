def chunk_transcript(segments, chunk_size=600, overlap=100):
    chunks = []
    
    i = 0
    chunk_index = 0
    
    while i < len(segments):
        current_segments = []
        current_words = 0
        
        while i < len(segments) and current_words < chunk_size:
            segment = segments[i]
            current_segments.append(segment)
            word_count = len(segment.get("text", "").split())
            current_words += word_count
            i += 1
            
        if not current_segments:
            break
            
        chunk_text = " ".join([seg.get("text", "") for seg in current_segments]).strip()
        chunk_start = current_segments[0].get("start", 0.0)
        chunk_end = current_segments[-1].get("end", 0.0)
        
        chunks.append({
            "chunk_index": chunk_index,
            "start": chunk_start,
            "end": chunk_end,
            "text": chunk_text
        })
        chunk_index += 1
        
        if i < len(segments):
            overlap_words = 0
            backtrack_count = 0
            for j in range(len(current_segments) - 1, -1, -1):
                seg_words = len(current_segments[j].get("text", "").split())
                if overlap_words + seg_words > overlap:
                    break
                overlap_words += seg_words
                backtrack_count += 1
            
            if backtrack_count == 0 and len(current_segments) > 1:
                backtrack_count = 1
            elif backtrack_count == len(current_segments):
                backtrack_count = len(current_segments) - 1
                
            i -= backtrack_count
            
    return chunks

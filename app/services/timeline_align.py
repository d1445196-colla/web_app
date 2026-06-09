"""
TimelineAlign — 時間軸對齊邏輯

負責將前端錄音時產生的即時標記（Markers）與
Whisper API 回傳的轉寫段落（Segments）進行時間軸配對。

對齊規則：
    對每個 Marker 的時間點，找到包含該時間點的 Segment
    （即 segment.start_time <= marker_time <= segment.end_time）。
    若 Marker 時間點未落入任何 Segment 區間，則 segment_id 設為 None。
"""


def align(markers, segments):
    """
    將即時標記與轉寫段落進行時間軸對齊。

    對每個 marker，找到其時間點落入的 segment 區間，
    並將對應的 segment_id 寫入 marker 資料中。

    Args:
        markers (list[dict]): 即時標記列表，每筆包含：
            - marker_time (float): 標記時間點 (秒)
            - label (str): 標記備註文字
        segments (list[dict]): 轉寫段落列表，每筆包含：
            - id (int): 段落 ID（資料庫主鍵）
            - segment_index (int): 段落順序索引
            - start_time (float): 起始時間 (秒)
            - end_time (float): 結束時間 (秒)
            - text (str): 轉寫文字

    Returns:
        list[dict]: 對齊後的標記列表，每筆新增 segment_id 欄位
    """
    aligned_markers = []

    for marker in markers:
        marker_time = marker.get('marker_time', 0)
        label = marker.get('label', '')
        matched_segment_id = None

        # 線性搜尋：找到包含 marker_time 的 segment
        for seg in segments:
            seg_start = seg['start_time'] if isinstance(seg, dict) else seg['start_time']
            seg_end = seg['end_time'] if isinstance(seg, dict) else seg['end_time']
            seg_id = seg['id'] if isinstance(seg, dict) else seg['id']

            if seg_start <= marker_time <= seg_end:
                matched_segment_id = seg_id
                break

        # 若未精確命中，找最接近的 segment
        if matched_segment_id is None and segments:
            matched_segment_id = _find_nearest_segment(marker_time, segments)

        aligned_markers.append({
            'marker_time': marker_time,
            'label': label,
            'segment_id': matched_segment_id,
        })

    return aligned_markers


def _find_nearest_segment(marker_time, segments):
    """
    找到離指定時間點最近的 segment。

    當 marker_time 未精確落入任何 segment 區間時，
    選擇距離最近的 segment 作為對齊目標。

    Args:
        marker_time (float): 標記時間點 (秒)
        segments (list): 轉寫段落列表

    Returns:
        int | None: 最近的 segment ID
    """
    min_distance = float('inf')
    nearest_id = None

    for seg in segments:
        seg_start = seg['start_time'] if isinstance(seg, dict) else seg['start_time']
        seg_end = seg['end_time'] if isinstance(seg, dict) else seg['end_time']
        seg_id = seg['id'] if isinstance(seg, dict) else seg['id']

        # 計算 marker_time 到 segment 區間的距離
        if marker_time < seg_start:
            distance = seg_start - marker_time
        elif marker_time > seg_end:
            distance = marker_time - seg_end
        else:
            distance = 0  # 在區間內

        if distance < min_distance:
            min_distance = distance
            nearest_id = seg_id

    return nearest_id

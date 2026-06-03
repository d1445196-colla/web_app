// app/static/js/marker.js
// 標記管理模組 — 負責在錄音過程中新增、儲存與編輯即時時間標記

class MarkerTracker {
    constructor() {
        this.markers = []; // 結構: { type_id: int, timestamp_sec: int, note: string }
        this.markerTypes = {}; // 對照表: id -> { name, icon, color }
    }

    setMarkerTypes(typesList) {
        typesList.forEach(t => {
            this.markerTypes[t.id] = t;
        });
    }

    addMarker(typeId, timestampSec, note = '') {
        const marker = {
            type_id: parseInt(typeId),
            timestamp_sec: parseInt(timestampSec),
            note: note.trim()
        };
        this.markers.push(marker);
        this.renderMarkerLog();
        return marker;
    }

    clear() {
        this.markers = [];
        this.renderMarkerLog();
    }

    getMarkers() {
        return this.markers;
    }

    toJSON() {
        return JSON.stringify(this.markers);
    }

    // 渲染錄音時畫面下方的即時標記歷史紀錄
    renderMarkerLog() {
        const logContainer = document.getElementById('live-markers-log');
        if (!logContainer) return;
        
        logContainer.innerHTML = '';
        
        if (this.markers.length === 0) {
            logContainer.innerHTML = '<div class="empty-log-text">尚未新增任何時間標記</div>';
            return;
        }

        // 由新到舊排序顯示
        const sortedMarkers = [...this.markers].reverse();
        
        sortedMarkers.forEach((m, idx) => {
            const typeInfo = this.markerTypes[m.type_id] || { name: '標記', icon: '🏷', color: '#64748b' };
            const item = document.createElement('div');
            item.className = 'live-marker-item';
            item.style.borderLeft = `4px solid ${typeInfo.color}`;
            
            const timeStr = this.formatTime(m.timestamp_sec);
            
            item.innerHTML = `
                <span class="live-marker-time">${timeStr}</span>
                <span class="live-marker-type">${typeInfo.icon} ${typeInfo.name}</span>
                <span class="live-marker-note">${m.note ? m.note : '<span class="no-note">無備註</span>'}</span>
                <button class="live-marker-edit-btn" data-index="${this.markers.length - 1 - idx}">✏️</button>
            `;
            
            // 綁定編輯備註事件
            const editBtn = item.querySelector('.live-marker-edit-btn');
            editBtn.addEventListener('click', (e) => {
                const markerIdx = parseInt(e.target.getAttribute('data-index'));
                this.promptEditNote(markerIdx);
            });
            
            logContainer.appendChild(item);
        });
    }

    promptEditNote(index) {
        const marker = this.markers[index];
        if (!marker) return;
        
        const newNote = prompt('請輸入標記備註：', marker.note);
        if (newNote !== null) {
            marker.note = newNote.trim();
            this.renderMarkerLog();
        }
    }

    formatTime(totalSeconds) {
        const hrs = Math.floor(totalSeconds / 3600);
        const mins = Math.floor((totalSeconds % 3600) / 60);
        const secs = totalSeconds % 60;
        return [
            hrs.toString().padStart(2, '0'),
            mins.toString().padStart(2, '0'),
            secs.toString().padStart(2, '0')
        ].join(':');
    }
}

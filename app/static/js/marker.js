// app/static/js/marker.js
// 錄音標記管理模組

window.MarkerManager = (function() {
    let markers = [];

    return {
        clear: function() {
            markers = [];
            this.updateFormInput();
        },
        add: function(typeId, timestampSec, note = '') {
            markers.push({
                type_id: parseInt(typeId),
                timestamp_sec: parseInt(timestampSec),
                note: note
            });
            this.updateFormInput();
            console.log(`[Marker Added] Type: ${typeId}, Time: ${timestampSec}s, Note: "${note}"`);
        },
        getAll: function() {
            return markers;
        },
        getJSON: function() {
            return JSON.stringify(markers);
        },
        updateFormInput: function() {
            const input = document.getElementById('markers-json-input');
            if (input) {
                input.value = this.getJSON();
            }
        }
    };
})();

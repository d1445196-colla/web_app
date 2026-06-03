// app/static/js/keyboard.js
// 錄音鍵盤快捷鍵控制

document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('keydown', function(e) {
        // 如果使用者正在輸入文字 (例如在儲存對話框的 input 中)，不觸發快捷鍵
        const activeElem = document.activeElement;
        if (activeElem && (
            activeElem.tagName === 'INPUT' || 
            activeElem.tagName === 'TEXTAREA' || 
            activeElem.isContentEditable
        )) {
            return;
        }

        // 檢查全域錄音控制器是否存在
        if (!window.RecorderControl) return;

        // 1. 空白鍵：暫停 / 繼續
        if (e.key === ' ' || e.code === 'Space') {
            if (window.RecorderControl.isRecording()) {
                e.preventDefault(); // 阻止空白鍵捲動網頁
                if (window.RecorderControl.isPaused()) {
                    window.RecorderControl.resume();
                } else {
                    window.RecorderControl.pause();
                }
            }
        }

        // 2. 數字鍵 1-5：快速標記
        if (e.key >= '1' && e.key <= '5') {
            if (window.RecorderControl.isRecording() && !window.RecorderControl.isPaused()) {
                e.preventDefault();
                const index = parseInt(e.key);
                window.RecorderControl.clickMarker(index);
            }
        }
    });
});

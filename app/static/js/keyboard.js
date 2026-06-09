// app/static/js/keyboard.js
// 鍵盤快捷鍵模組 — 負責監聽全域鍵盤操作，提昇錄音時的操作便利性

class KeyboardShortcutManager {
    constructor(callbacks) {
        this.callbacks = callbacks || {}; // 包含: onSpace, onNumber(numKey)
        this.enabled = true;
        this.init();
    }

    init() {
        document.addEventListener('keydown', (e) => {
            if (!this.enabled) return;

            // 如果使用者正在輸入文字（如在 input 或 textarea 中），不要觸發快捷鍵
            const activeEl = document.activeElement;
            if (activeEl && (
                activeEl.tagName === 'INPUT' || 
                activeEl.tagName === 'TEXTAREA' || 
                activeEl.isContentEditable
            )) {
                return;
            }

            const key = e.key;

            if (key === ' ') {
                // 空白鍵暫停/繼續
                e.preventDefault(); // 防止網頁捲動
                if (this.callbacks.onSpace) {
                    this.callbacks.onSpace();
                }
            } else if (/^[1-9]$/.test(key)) {
                // 數字鍵 1-9 快速標記
                const num = parseInt(key);
                if (this.callbacks.onNumber) {
                    this.callbacks.onNumber(num);
                }
            }
        });
    }

    enable() {
        this.enabled = true;
    }

    disable() {
        this.enabled = false;
    }
}

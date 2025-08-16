/**
 * Game Implementation using RandomBag Class
 * This file contains the game logic and UI interactions
 */

// Game Application Object
const gameApp = {
    // Game objects data
    gameObjects: [
        { id: 1, name: "Object1", color: "#FF6B6B", power: 10, description: "Fire Element" },
        { id: 2, name: "Object2", color: "#4ECDC4", power: 15, description: "Water Element" },
        { id: 3, name: "Object3", color: "#45B7D1", power: 20, description: "Air Element" },
        { id: 4, name: "Object4", color: "#96CEB4", power: 12, description: "Earth Element" },
        { id: 5, name: "Object5", color: "#FFEAA7", power: 18, description: "Light Element" },
        { id: 6, name: "Object6", color: "#DDA0DD", power: 25, description: "Magic Element" },
        { id: 7, name: "Object7", color: "#98D8C8", power: 8, description: "Ice Element" },
        { id: 8, name: "Object8", color: "#FFB6C1", power: 22, description: "Thunder Element" }
    ],
    
    // RandomBag instance
    itemBag: null,
    
    // Initialize the game
    init() {
        // Create RandomBag with game objects
        this.itemBag = new RandomBag(this.gameObjects);
        
        // Set up initial UI
        this.updateAllUI();
        
        // Add keyboard shortcuts
        this.setupKeyboardShortcuts();
        
        // Log to console for debugging
        console.log('Game initialized with RandomBag:', this.itemBag);
        console.log('Available methods:', Object.getOwnPropertyNames(RandomBag.prototype));
    },
    
    // Draw an item from the bag
    drawItem() {
        const item = this.itemBag.draw();
        
        // Animate the draw
        this.animateDrawResult(item);
        
        // Update all UI elements
        this.updateAllUI();
        
        // Play sound effect (if you add audio later)
        // this.playSound('draw');
        
        // Check for special conditions
        this.checkSpecialConditions(item);
        
        return item;
    },
    
    // Reset the bag
    resetBag() {
        this.itemBag.hardReset();
        
        // Show reset message
        this.showMessage('Bag has been reset! All items are available again.', 'reset');
        
        // Update UI
        this.updateAllUI();
    },
    
    // Show bag information
    showInfo() {
        const info = {
            totalItems: this.itemBag.getOriginalItems().length,
            remainingItems: this.itemBag.getRemainingCount(),
            currentCycle: this.itemBag.getCycleCount(),
            totalDraws: this.itemBag.getTotalDraws(),
            isEmpty: this.itemBag.isEmpty()
        };
        
        const infoHTML = `
            <div style="text-align: left; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                <h2 style="color: #2d3748; margin-bottom: 20px;">📊 Bag Information</h2>
                <div style="display: grid; gap: 10px; font-size: 1.125rem;">
                    <div><strong>Total Items:</strong> ${info.totalItems}</div>
                    <div><strong>Remaining Items:</strong> ${info.remainingItems}</div>
                    <div><strong>Current Cycle:</strong> ${info.currentCycle}</div>
                    <div><strong>Total Draws:</strong> ${info.totalDraws}</div>
                    <div><strong>Bag Status:</strong> ${info.isEmpty ? '🔴 Empty (will reset on next draw)' : '🟢 Active'}</div>
                </div>
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #e2e8f0;">
                <div style="color: #718096; font-size: 0.875rem;">
                    <p><strong>How it works:</strong></p>
                    <p>• Each item can only be drawn once per cycle</p>
                    <p>• When all items are drawn, the bag automatically resets</p>
                    <p>• The cycle counter increases each time the bag resets</p>
                </div>
            </div>
        `;
        
        this.displayResult(infoHTML);
    },
    
    // Animate the draw result
    animateDrawResult(item) {
        const display = document.getElementById('resultDisplay');
        const content = document.getElementById('resultContent');
        
        // Add animation class
        display.classList.add('has-result');
        
        // Create object display
        const objectHTML = `
            <div class="object-display" style="background: linear-gradient(135deg, ${item.color} 0%, ${this.darkenColor(item.color, 20)} 100%);">
                <div class="object-name">${item.name}</div>
                <div class="object-power">Power: ${item.power}</div>
                <div style="margin-top: 10px; font-size: 1rem; opacity: 0.9;">${item.description}</div>
            </div>
        `;
        
        content.innerHTML = objectHTML;
        
        // Add animation
        content.style.animation = 'none';
        setTimeout(() => {
            content.style.animation = 'popIn 0.5s ease';
        }, 10);
    },
    
    // Display a result in the result area
    displayResult(html) {
        const content = document.getElementById('resultContent');
        content.innerHTML = html;
    },
    
    // Show a message
    showMessage(message, type = 'info') {
        const colors = {
            info: '#3182ce',
            reset: '#e53e3e',
            success: '#38a169'
        };
        
        const messageHTML = `
            <div style="color: ${colors[type]}; font-size: 1.25rem; text-align: center;">
                ${message}
            </div>
        `;
        
        this.displayResult(messageHTML);
    },
    
    // Update all UI elements
    updateAllUI() {
        this.updateStats();
        this.updateRemainingItems();
        this.updateHistory();
        this.updateButtonStates();
    },
    
    // Update statistics display
    updateStats() {
        document.getElementById('totalItems').textContent = this.itemBag.getOriginalItems().length;
        document.getElementById('remainingCount').textContent = this.itemBag.getRemainingCount();
        document.getElementById('cycleCount').textContent = this.itemBag.getCycleCount();
        document.getElementById('totalDraws').textContent = this.itemBag.getTotalDraws();
    },
    
    // Update remaining items display
    updateRemainingItems() {
        const container = document.getElementById('remainingItems');
        const remaining = this.itemBag.getRemaining();
        
        if (remaining.length === 0) {
            container.innerHTML = '<div class="empty-state">Bag is empty! Will reset on next draw.</div>';
            return;
        }
        
        container.innerHTML = remaining.map(item => 
            `<span class="item-badge" style="background: linear-gradient(135deg, ${item.color} 0%, ${this.darkenColor(item.color, 20)} 100%);">
                ${item.name}
            </span>`
        ).join('');
    },
    
    // Update history display
    updateHistory() {
        const container = document.getElementById('historyList');
        const history = this.itemBag.getHistory();
        
        if (history.length === 0) {
            container.innerHTML = '<div class="empty-state">No items drawn yet</div>';
            return;
        }
        
        // Show last 20 draws, most recent first
        const recentHistory = history.slice(-20).reverse();
        
        container.innerHTML = recentHistory.map(draw => `
            <div class="history-item">
                <span class="history-name" style="color: ${draw.item.color};">
                    ${draw.item.name}
                </span>
                <span class="history-meta">
                    Draw #${draw.drawNumber} • Cycle ${draw.cycle}
                </span>
            </div>
        `).join('');
    },
    
    // Update button states
    updateButtonStates() {
        const drawBtn = document.getElementById('drawBtn');
        const resetBtn = document.getElementById('resetBtn');
        
        // Disable reset button if no draws have been made
        resetBtn.disabled = this.itemBag.getTotalDraws() === 0;
        
        // Update draw button text if bag is about to reset
        if (this.itemBag.isEmpty()) {
            drawBtn.innerHTML = '<span>🔄</span><span>Draw & Reset</span>';
        } else {
            drawBtn.innerHTML = '<span>🎯</span><span>Draw Item</span>';
        }
    },
    
    // Check for special conditions after drawing
    checkSpecialConditions(item) {
        // Check if this was the last item in the cycle
        if (this.itemBag.isEmpty()) {
            setTimeout(() => {
                this.showMessage('All items drawn! Bag will reset on next draw.', 'info');
            }, 1500);
        }
        
        // Check for high power items
        if (item.power >= 20) {
            console.log('High power item drawn!', item);
            // You could add special effects here
        }
        
        // Check for milestones
        const totalDraws = this.itemBag.getTotalDraws();
        if (totalDraws === 10 || totalDraws === 50 || totalDraws === 100) {
            console.log(`Milestone reached: ${totalDraws} draws!`);
        }
    },
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Space or Enter to draw
            if (e.code === 'Space' || e.code === 'Enter') {
                e.preventDefault();
                this.drawItem();
            }
            // R to reset
            else if (e.code === 'KeyR' && e.ctrlKey) {
                e.preventDefault();
                this.resetBag();
            }
            // I for info
            else if (e.code === 'KeyI') {
                e.preventDefault();
                this.showInfo();
            }
        });
    },
    
    // Utility function to darken a color
    darkenColor(color, percent) {
        const num = parseInt(color.replace('#', ''), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) - amt;
        const G = (num >> 8 & 0x00FF) - amt;
        const B = (num & 0x0000FF) - amt;
        return '#' + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255))
            .toString(16).slice(1);
    },
    
    // Save game state to localStorage
    saveState() {
        const state = {
            bagState: this.itemBag.exportState(),
            timestamp: Date.now()
        };
        localStorage.setItem('randomBagGameState', JSON.stringify(state));
        console.log('Game state saved');
    },
    
    // Load game state from localStorage
    loadState() {
        const saved = localStorage.getItem('randomBagGameState');
        if (saved) {
            const state = JSON.parse(saved);
            this.itemBag.importState(state.bagState);
            this.updateAllUI();
            console.log('Game state loaded from', new Date(state.timestamp));
            return true;
        }
        return false;
    },
    
    // Clear saved state
    clearSavedState() {
        localStorage.removeItem('randomBagGameState');
        console.log('Saved state cleared');
    }
};

// Initialize game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    gameApp.init();
    
    // Try to load saved state
    const loaded = gameApp.loadState();
    if (loaded) {
        gameApp.showMessage('Previous game state restored!', 'success');
    }
    
    // Auto-save state on draw
    const originalDraw = gameApp.drawItem.bind(gameApp);
    gameApp.drawItem = function() {
        const result = originalDraw();
        gameApp.saveState();
        return result;
    };
    
    // Log usage examples
    console.log('=== RandomBag Usage Examples ===');
    console.log('Draw an item: gameApp.drawItem()');
    console.log('Reset bag: gameApp.resetBag()');
    console.log('Get remaining: gameApp.itemBag.getRemaining()');
    console.log('Draw multiple: gameApp.itemBag.drawMultiple(3)');
    console.log('Check probability: gameApp.itemBag.getProbability(gameApp.gameObjects[0])');
    console.log('Save state: gameApp.saveState()');
    console.log('Load state: gameApp.loadState()');
});

// Make gameApp globally accessible for debugging
window.gameApp = gameApp;
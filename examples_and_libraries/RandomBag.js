/**
 * RandomBag Class - Non-repeating Random Selection System
 * 
 * This class implements a "bag" system where items are randomly selected
 * without replacement until all items have been drawn, then the bag resets.
 * Perfect for games where you want random but fair distribution.
 * 
 * @author Your Name
 * @version 1.0.0
 */

class RandomBag {
    /**
     * Create a new RandomBag
     * @param {Array} items - Array of items to put in the bag
     */
    constructor(items) {
        // Store the original items array
        this.originalItems = [...items];
        // Create a working copy for the current cycle
        this.remainingItems = [...items];
        // Track statistics
        this.cycleCount = 0;
        this.drawHistory = [];
        this.totalDraws = 0;
    }
    
    /**
     * Draw a random item from the bag
     * @returns {*} The randomly selected item
     */
    draw() {
        // If bag is empty, reset it automatically
        if (this.remainingItems.length === 0) {
            this.reset();
            this.cycleCount++;
        }
        
        // Get random index from remaining items
        const randomIndex = Math.floor(Math.random() * this.remainingItems.length);
        
        // Remove and return the selected item
        const selectedItem = this.remainingItems.splice(randomIndex, 1)[0];
        
        // Track the draw
        this.drawHistory.push({
            item: selectedItem,
            drawNumber: ++this.totalDraws,
            cycle: this.cycleCount
        });
        
        return selectedItem;
    }
    
    /**
     * Draw multiple items at once
     * @param {number} count - Number of items to draw
     * @returns {Array} Array of drawn items
     */
    drawMultiple(count) {
        const drawn = [];
        for (let i = 0; i < count; i++) {
            drawn.push(this.draw());
        }
        return drawn;
    }
    
    /**
     * Reset the bag to include all items again
     */
    reset() {
        this.remainingItems = [...this.originalItems];
    }
    
    /**
     * Force reset and clear all history
     */
    hardReset() {
        this.reset();
        this.cycleCount = 0;
        this.drawHistory = [];
        this.totalDraws = 0;
    }
    
    /**
     * Get remaining items without modifying the bag
     * @returns {Array} Copy of remaining items
     */
    getRemaining() {
        return [...this.remainingItems];
    }
    
    /**
     * Get count of remaining items
     * @returns {number} Number of items left in bag
     */
    getRemainingCount() {
        return this.remainingItems.length;
    }
    
    /**
     * Check if bag is empty
     * @returns {boolean} True if no items remain
     */
    isEmpty() {
        return this.remainingItems.length === 0;
    }
    
    /**
     * Get all original items
     * @returns {Array} Copy of original items
     */
    getOriginalItems() {
        return [...this.originalItems];
    }
    
    /**
     * Get draw history
     * @returns {Array} Copy of draw history
     */
    getHistory() {
        return [...this.drawHistory];
    }
    
    /**
     * Get current cycle count
     * @returns {number} Current cycle number
     */
    getCycleCount() {
        return this.cycleCount;
    }
    
    /**
     * Get total draws count
     * @returns {number} Total number of draws made
     */
    getTotalDraws() {
        return this.totalDraws;
    }
    
    /**
     * Add new items to the bag (both original and remaining)
     * @param {Array} newItems - Items to add
     */
    addItems(newItems) {
        this.originalItems.push(...newItems);
        this.remainingItems.push(...newItems);
    }
    
    /**
     * Remove items from the bag completely
     * @param {Array} itemsToRemove - Items to remove
     */
    removeItems(itemsToRemove) {
        itemsToRemove.forEach(item => {
            // Remove from original items
            const origIndex = this.originalItems.indexOf(item);
            if (origIndex > -1) {
                this.originalItems.splice(origIndex, 1);
            }
            
            // Remove from remaining items
            const remIndex = this.remainingItems.indexOf(item);
            if (remIndex > -1) {
                this.remainingItems.splice(remIndex, 1);
            }
        });
    }
    
    /**
     * Peek at the next item without removing it
     * @returns {*} Random item that would be drawn next (or null if empty)
     */
    peek() {
        if (this.remainingItems.length === 0) {
            return null;
        }
        const randomIndex = Math.floor(Math.random() * this.remainingItems.length);
        return this.remainingItems[randomIndex];
    }
    
    /**
     * Get probability of drawing a specific item
     * @param {*} item - Item to check
     * @returns {number} Probability (0-1) or 0 if not in bag
     */
    getProbability(item) {
        if (this.remainingItems.length === 0) return 0;
        const count = this.remainingItems.filter(i => i === item).length;
        return count / this.remainingItems.length;
    }
    
    /**
     * Shuffle remaining items (changes order but not contents)
     */
    shuffle() {
        for (let i = this.remainingItems.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [this.remainingItems[i], this.remainingItems[j]] = 
            [this.remainingItems[j], this.remainingItems[i]];
        }
    }
    
    /**
     * Export current state for saving
     * @returns {Object} Serializable state object
     */
    exportState() {
        return {
            originalItems: this.originalItems,
            remainingItems: this.remainingItems,
            cycleCount: this.cycleCount,
            drawHistory: this.drawHistory,
            totalDraws: this.totalDraws
        };
    }
    
    /**
     * Import state from saved data
     * @param {Object} state - Previously exported state
     */
    importState(state) {
        this.originalItems = [...state.originalItems];
        this.remainingItems = [...state.remainingItems];
        this.cycleCount = state.cycleCount;
        this.drawHistory = [...state.drawHistory];
        this.totalDraws = state.totalDraws;
    }
}

// Export for use in Node.js environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RandomBag;
}
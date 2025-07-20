// Timezone and time display utilities
class TimeDisplay {
    constructor() {
        this.userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        this.init();
    }

    init() {
        // Convert all server times to user's local time
        this.convertServerTimes();
        
        // Update times every minute
        setInterval(() => {
            this.updateRelativeTimes();
        }, 60000);
    }

    convertServerTimes() {
        const timeElements = document.querySelectorAll('[data-server-time]');
        timeElements.forEach(element => {
            const serverTime = element.getAttribute('data-server-time');
            const localTime = this.convertToLocalTime(serverTime);
            element.textContent = localTime;
        });
    }

    convertToLocalTime(serverTimeStr) {
        // Server time is in Nigeria time (UTC+1)
        const serverTime = new Date(serverTimeStr);
        const now = new Date();
        const diff = now - serverTime;
        
        // Format based on how long ago
        if (diff < 60000) { // Less than 1 minute
            return "Just now";
        } else if (diff < 3600000) { // Less than 1 hour
            const minutes = Math.floor(diff / 60000);
            return `${minutes}m ago`;
        } else if (diff < 86400000) { // Less than 1 day
            const hours = Math.floor(diff / 3600000);
            return `${hours}h ago`;
        } else if (diff < 604800000) { // Less than 1 week
            const days = Math.floor(diff / 86400000);
            return `${days}d ago`;
        } else {
            // Show date and time
            return serverTime.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            });
        }
    }

    updateRelativeTimes() {
        const timeElements = document.querySelectorAll('[data-server-time]');
        timeElements.forEach(element => {
            const serverTime = element.getAttribute('data-server-time');
            const localTime = this.convertToLocalTime(serverTime);
            element.textContent = localTime;
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new TimeDisplay();
}); 
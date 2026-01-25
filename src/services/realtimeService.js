/**
 * RealTimeDataManager
 * 
 * A robust utility class for managing real-time data connections.
 * It attempts to establish a WebSocket connection first. If the connection fails
 * or is unsupported by the client, it automatically falls back to HTTP Long Polling.
 * 
 * Features:
 * - Automatic reconnection with exponential backoff.
 * - WebSocket fallback to HTTP Polling.
 * - Event-based architecture (onMessage, onError, onStatusChange).
 * - Heartbeat/Ping mechanism to detect stale connections.
 */
class RealTimeDataManager {
    /**
     * @param {string} url - The WebSocket URL (e.g., wss://api.example.com/stream).
     * @param {Object} options - Configuration options.
     * @param {number} [options.pollingInterval=3000] - Interval in ms for polling fallback.
     * @param {number} [options.reconnectDelay=1000] - Initial delay in ms for reconnection attempts.
     * @param {number} [options.maxReconnectDelay=30000] - Maximum delay in ms for reconnection.
     * @param {number} [options.heartbeatInterval=30000] - Interval in ms to send ping frames.
     */
    constructor(url, options = {}) {
        this.url = url;
        this.pollingUrl = url.replace(/^wss?:\/\//, 'https://').replace(/^ws:\/\//, 'http://');
        
        // Configuration
        this.pollingInterval = options.pollingInterval || 3000;
        this.reconnectDelay = options.reconnectDelay || 1000;
        this.maxReconnectDelay = options.maxReconnectDelay || 30000;
        this.heartbeatInterval = options.heartbeatInterval || 30000;

        // State
        this.isConnected = false;
        this.isManualClose = false;
        this.currentReconnectDelay = this.reconnectDelay;
        this.mode = 'websocket'; // 'websocket' or 'polling'
        
        // Connection Objects
        this.ws = null;
        this.pollTimer = null;
        this.heartbeatTimer = null;

        // Callbacks
        this.onMessage = () => {};
        this.onError = () => {};
        this.onStatusChange = () => {};
    }

    /**
     * Initiates the connection.
     * Tries WebSocket first, falls back to polling if setup fails.
     */
    connect() {
        this.isManualClose = false;
        this.currentReconnectDelay = this.reconnectDelay;
        this._attemptWebSocket();
    }

    /**
     * Closes the connection and stops reconnection logic.
     */
    disconnect() {
        this.isManualClose = true;
        this._cleanup();
        this._updateStatus('disconnected');
    }

    /**
     * Sends data through the active channel.
     * @param {string|Object} data - Data to send.
     */
    send(data) {
        const payload = typeof data === 'string' ? data : JSON.stringify(data);

        if (this.mode === 'websocket' && this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(payload);
        } else {
            console.warn('Cannot send data: WebSocket is not connected. Sending via polling is not supported.');
        }
    }

    // --- Private Methods ---

    /**
     * Attempts to establish a WebSocket connection.
     */
    _attemptWebSocket() {
        if (this.isManualClose) return;

        this._updateStatus('connecting');

        try {
            this.ws = new WebSocket(this.url);

            this.ws.onopen = () => {
                this.mode = 'websocket';
                this.isConnected = true;
                this.currentReconnectDelay = this.reconnectDelay; // Reset backoff
                this._updateStatus('connected');
                this._startHeartbeat();
            };

            this.ws.onmessage = (event) => {
                this._handleIncomingData(event.data);
                this._startHeartbeat(); // Reset heartbeat on activity
            };

            this.ws.onclose = (event) => {
                this.ws = null;
                this.isConnected = false;
                this._stopHeartbeat();
                
                // If not closed manually, attempt reconnection or fallback
                if (!this.isManualClose) {
                    this._updateStatus('disconnected');
                    this._scheduleReconnect();
                }
            };

            this.ws.onerror = (error) => {
                this.onError(new Error('WebSocket Error occurred'));
                // The onclose event will handle the reconnection logic
            };

        } catch (error) {
            this.onError(error);
            this._startPolling(); // Fallback immediately if WS construction throws
        }
    }

    /**
     * Initiates HTTP Long Polling as a fallback.
     */
    _startPolling() {
        if (this.mode === 'polling' && this.pollTimer) return;
        
        console.log('Falling back to HTTP Polling...');
        this.mode = 'polling';
        this._updateStatus('connecting');

        const poll = async () => {
            if (this.isManualClose || this.mode === 'websocket') return;

            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.pollingInterval + 5000);

                const response = await fetch(this.pollingUrl, {
                    method: 'GET',
                    headers: { 'Accept': 'application/json' },
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);

                if (response.ok) {
                    const data = await response.text();
                    this._handleIncomingData(data);
                    
                    if (!this.isConnected) {
                        this.isConnected = true;
                        this._updateStatus('connected');
                    }
                } else {
                    throw new Error(`Polling failed with status: ${response.status}`);
                }
            } catch (error) {
                this.onError(error);
                // If polling fails, we keep trying via the timeout logic below
            }

            // Schedule next poll
            if (!this.isManualClose && this.mode === 'polling') {
                this.pollTimer = setTimeout(poll, this.pollingInterval);
            }
        };

        poll();
    }

    /**
     * Handles data parsing and dispatching to the client callback.
     * @param {string} rawData 
     */
    _handleIncomingData(rawData) {
        try {
            // Attempt to parse JSON, fallback to raw text
            let data;
            try {
                data = JSON.parse(rawData);
            } catch {
                data = rawData;
            }
            this.onMessage(data);
        } catch (error) {
            console.error('Error parsing incoming data:', error);
        }
    }

    /**
     * Schedules a reconnection attempt using exponential backoff.
     */
    _scheduleReconnect() {
        // If we were in WebSocket mode and failed, try polling immediately once
        // before waiting, or just stick to backoff. 
        // Here we implement a simple backoff strategy.
        
        setTimeout(() => {
            if (this.isManualClose) return;
            
            // If we are currently polling, we just keep polling (handled in _startPolling).
            // If we were WebSocket, we try WS again.
            if (this.mode === 'websocket') {
                this._attemptWebSocket();
            }
        }, this.currentReconnectDelay);

        // Increase delay for next time (Exponential Backoff)
        this.currentReconnectDelay = Math.min(this.currentReconnectDelay * 2, this.maxReconnectDelay);
    }

    /**
     * Starts the heartbeat timer to detect stale connections.
     */
    _startHeartbeat() {
        this._stopHeartbeat();
        if (this.mode !== 'websocket') return;

        this.heartbeatTimer = setTimeout(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                // Send a ping or a lightweight JSON message
                this.ws.send(JSON.stringify({ type: 'ping' }));
            } else {
                // If socket is not open, trigger close/reconnect logic
                if (this.ws) this.ws.close();
            }
        }, this.heartbeatInterval);
    }

    /**
     * Stops the heartbeat timer.
     */
    _stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearTimeout(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    /**
     * Cleans up resources (timers, sockets).
     */
    _cleanup() {
        this._stopHeartbeat();
        
        if (this.ws) {
            this.ws.onclose = null; // Prevent onclose triggering reconnect
            this.ws.close();
            this.ws = null;
        }

        if (this.pollTimer) {
            clearTimeout(this.pollTimer);
            this.pollTimer = null;
        }
        
        this.isConnected = false;
    }

    /**
     * Updates status and notifies listeners.
     * @param {string} status 
     */
    _updateStatus(status) {
        this.onStatusChange(status);
    }
}

// --- Usage Example ---

// 1. Initialize
const dataManager = new RealTimeDataManager('wss://echo.websocket.org', {
    pollingInterval: 2000,
    reconnectDelay: 1000
});

// 2. Attach Listeners
dataManager.onMessage = (data) => {
    console.log('Received:', data);
};

dataManager.onStatusChange = (status) => {
    console.log(`Connection Status: ${status}`);
    const indicator = document.getElementById('status-indicator');
    if(indicator) indicator.innerText = status.toUpperCase();
};

dataManager.onError = (err) => {
    console.error('Connection Error:', err.message);
};

// 3. Start Connection
dataManager.connect();

// 4. Send Data (Example)
// setTimeout(() => {
//     dataManager.send({ text: 'Hello Server' });
// }, 2000);
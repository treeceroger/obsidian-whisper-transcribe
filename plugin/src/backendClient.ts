/**
 * Backend API client for communicating with the Python transcription service
 */

export interface BackendStatus {
    service: string;
    ollama_connected: boolean;
    model_available: boolean;
    is_recording: boolean;
    timestamp: string;
}

export interface TranscriptionResult {
    status: string;
    transcription: string;
    timestamp: string;
}

export class BackendClient {
    private baseUrl: string;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
    }

    /**
     * Check backend and Ollama status
     */
    async getStatus(): Promise<BackendStatus> {
        const response = await fetch(`${this.baseUrl}/status`);
        if (!response.ok) {
            throw new Error(`Backend request failed: ${response.statusText}`);
        }
        return await response.json();
    }

    /**
     * Start audio recording
     */
    async startRecording(): Promise<void> {
        const response = await fetch(`${this.baseUrl}/start-recording`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to start recording');
        }
    }

    /**
     * Stop recording and get transcription
     */
    async stopRecording(): Promise<TranscriptionResult> {
        const response = await fetch(`${this.baseUrl}/stop-recording`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to stop recording');
        }

        return await response.json();
    }

    /**
     * Get the last transcription result
     */
    async getLastTranscription(): Promise<TranscriptionResult> {
        const response = await fetch(`${this.baseUrl}/transcription`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'No transcription available');
        }

        return await response.json();
    }

    /**
     * Update backend configuration
     */
    async updateConfig(ollamaUrl: string, modelName: string): Promise<void> {
        const response = await fetch(`${this.baseUrl}/config`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ollama_url: ollamaUrl,
                model: modelName
            })
        });

        if (!response.ok) {
            throw new Error('Failed to update backend config');
        }
    }

    /**
     * Check if backend is reachable
     */
    async isReachable(): Promise<boolean> {
        try {
            await this.getStatus();
            return true;
        } catch {
            return false;
        }
    }
}

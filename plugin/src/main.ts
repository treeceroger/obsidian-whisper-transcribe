import { Notice, Plugin, TFile } from 'obsidian';
import { VoiceNotesSettings, DEFAULT_SETTINGS, VoiceNotesSettingTab } from './settings';
import { BackendClient } from './backendClient';

export default class VoiceNotesPlugin extends Plugin {
    settings: VoiceNotesSettings;
    backendClient: BackendClient;
    statusBarItem: HTMLElement;
    isRecording: boolean = false;
    ribbonIcon: HTMLElement;

    async onload() {
        await this.loadSettings();

        // Initialize backend client
        this.backendClient = new BackendClient(this.settings.backendUrl);

        // Add ribbon icon for recording
        this.ribbonIcon = this.addRibbonIcon(
            'microphone',
            'Voice Note',
            async (evt: MouseEvent) => {
                await this.toggleRecording();
            }
        );

        // Add status bar item
        this.statusBarItem = this.addStatusBarItem();
        this.statusBarItem.setText('🎤 Ready');

        // Add commands
        this.addCommand({
            id: 'start-voice-recording',
            name: 'Start Voice Recording',
            callback: async () => {
                await this.startRecording();
            }
        });

        this.addCommand({
            id: 'stop-voice-recording',
            name: 'Stop Voice Recording',
            callback: async () => {
                await this.stopRecording();
            }
        });

        this.addCommand({
            id: 'toggle-voice-recording',
            name: 'Toggle Voice Recording',
            callback: async () => {
                await this.toggleRecording();
            }
        });

        // Add settings tab
        this.addSettingTab(new VoiceNotesSettingTab(this.app, this));

        // Check backend connection on load
        this.checkBackendConnection();

        console.log('Voice Notes Transcription plugin loaded');
    }

    async checkBackendConnection() {
        try {
            const isReachable = await this.backendClient.isReachable();
            if (!isReachable) {
                new Notice('⚠️ Voice Notes: Backend service not running. Please start backend service.');
            }
        } catch (error) {
            console.error('Backend connection check failed:', error);
        }
    }

    async toggleRecording() {
        if (this.isRecording) {
            await this.stopRecording();
        } else {
            await this.startRecording();
        }
    }

    async startRecording() {
        if (this.isRecording) {
            new Notice('Already recording');
            return;
        }

        try {
            await this.backendClient.startRecording();
            this.isRecording = true;
            this.statusBarItem.setText('🔴 Recording...');
            this.ribbonIcon.addClass('voice-notes-recording');
            new Notice('🎤 Recording started - speak now');
        } catch (error) {
            new Notice(`Failed to start recording: ${error.message}`);
            console.error('Start recording error:', error);
        }
    }

    async stopRecording() {
        if (!this.isRecording) {
            new Notice('Not currently recording');
            return;
        }

        try {
            this.statusBarItem.setText('⏳ Processing...');
            this.ribbonIcon.removeClass('voice-notes-recording');

            const result = await this.backendClient.stopRecording();
            this.isRecording = false;

            if (result.transcription) {
                await this.appendTranscriptionToNote(result.transcription);
                this.statusBarItem.setText('✓ Transcribed');
                new Notice('✓ Voice note saved');

                // Reset status after 3 seconds
                setTimeout(() => {
                    this.statusBarItem.setText('🎤 Ready');
                }, 3000);
            } else {
                this.statusBarItem.setText('✗ Failed');
                new Notice('Transcription failed');
            }
        } catch (error) {
            this.isRecording = false;
            this.statusBarItem.setText('✗ Error');
            this.ribbonIcon.removeClass('voice-notes-recording');
            new Notice(`Failed to transcribe: ${error.message}`);
            console.error('Stop recording error:', error);

            // Reset status after 3 seconds
            setTimeout(() => {
                this.statusBarItem.setText('🎤 Ready');
            }, 3000);
        }
    }

    async appendTranscriptionToNote(transcription: string) {
        const noteName = this.settings.targetNoteName;
        const timestamp = new Date().toLocaleString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });

        // Format the note entry
        const entry = `## [${timestamp}]\n${transcription}\n\n`;

        try {
            // Get or create the note file
            let file = this.app.vault.getAbstractFileByPath(noteName);

            if (!file) {
                // Create new file if it doesn't exist
                await this.app.vault.create(noteName, entry);
                new Notice(`Created new voice notes file: ${noteName}`);
            } else if (file instanceof TFile) {
                // Append to existing file
                const currentContent = await this.app.vault.read(file);
                const newContent = currentContent + entry;
                await this.app.vault.modify(file, newContent);
            } else {
                throw new Error(`${noteName} exists but is not a file`);
            }
        } catch (error) {
            new Notice(`Failed to save transcription: ${error.message}`);
            console.error('Save transcription error:', error);
            throw error;
        }
    }

    onunload() {
        console.log('Voice Notes Transcription plugin unloaded');
    }

    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() {
        await this.saveData(this.settings);

        // Update backend client URL if changed
        this.backendClient = new BackendClient(this.settings.backendUrl);

        // Update backend config
        try {
            await this.backendClient.updateConfig(
                this.settings.ollamaUrl,
                this.settings.modelName
            );
        } catch (error) {
            console.error('Failed to update backend config:', error);
        }
    }
}

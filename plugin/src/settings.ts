import { App, PluginSettingTab, Setting } from 'obsidian';
import VoiceNotesPlugin from './main';

export interface VoiceNotesSettings {
    backendUrl: string;
    ollamaUrl: string;
    modelName: string;
    targetNoteName: string;
    wakePhrase: string;
    stopPhrase: string;
    autoStartListening: boolean;
}

export const DEFAULT_SETTINGS: VoiceNotesSettings = {
    backendUrl: 'http://localhost:8765',
    ollamaUrl: 'http://localhost:11434',
    modelName: 'dimavz/whisper-tiny',
    targetNoteName: 'Voice Notes.md',
    wakePhrase: 'computer start note',
    stopPhrase: 'computer end note',
    autoStartListening: false
};

export class VoiceNotesSettingTab extends PluginSettingTab {
    plugin: VoiceNotesPlugin;

    constructor(app: App, plugin: VoiceNotesPlugin) {
        super(app, plugin);
        this.plugin = plugin;
    }

    display(): void {
        const { containerEl } = this;

        containerEl.empty();

        containerEl.createEl('h2', { text: 'Voice Notes Transcription Settings' });

        // Backend URL
        new Setting(containerEl)
            .setName('Backend Service URL')
            .setDesc('URL of the Python backend service')
            .addText(text => text
                .setPlaceholder('http://localhost:8765')
                .setValue(this.plugin.settings.backendUrl)
                .onChange(async (value) => {
                    this.plugin.settings.backendUrl = value;
                    await this.plugin.saveSettings();
                }));

        // Ollama URL
        new Setting(containerEl)
            .setName('Ollama URL')
            .setDesc('URL of your local Ollama instance')
            .addText(text => text
                .setPlaceholder('http://localhost:11434')
                .setValue(this.plugin.settings.ollamaUrl)
                .onChange(async (value) => {
                    this.plugin.settings.ollamaUrl = value;
                    await this.plugin.saveSettings();
                }));

        // Model Name
        new Setting(containerEl)
            .setName('Ollama Model')
            .setDesc('Name of the Whisper model in Ollama')
            .addText(text => text
                .setPlaceholder('dimavz/whisper-tiny')
                .setValue(this.plugin.settings.modelName)
                .onChange(async (value) => {
                    this.plugin.settings.modelName = value;
                    await this.plugin.saveSettings();
                }));

        // Target Note Name
        new Setting(containerEl)
            .setName('Voice Notes File')
            .setDesc('Name of the file where voice notes will be appended')
            .addText(text => text
                .setPlaceholder('Voice Notes.md')
                .setValue(this.plugin.settings.targetNoteName)
                .onChange(async (value) => {
                    this.plugin.settings.targetNoteName = value;
                    await this.plugin.saveSettings();
                }));

        // Wake Phrase (for future use)
        new Setting(containerEl)
            .setName('Wake Phrase')
            .setDesc('Phrase to start recording (future feature)')
            .addText(text => text
                .setPlaceholder('computer start note')
                .setValue(this.plugin.settings.wakePhrase)
                .setDisabled(true)
                .onChange(async (value) => {
                    this.plugin.settings.wakePhrase = value;
                    await this.plugin.saveSettings();
                }));

        // Stop Phrase (for future use)
        new Setting(containerEl)
            .setName('Stop Phrase')
            .setDesc('Phrase to stop recording (future feature)')
            .addText(text => text
                .setPlaceholder('computer end note')
                .setValue(this.plugin.settings.stopPhrase)
                .setDisabled(true)
                .onChange(async (value) => {
                    this.plugin.settings.stopPhrase = value;
                    await this.plugin.saveSettings();
                }));

        // Connection Status
        containerEl.createEl('h3', { text: 'Status' });

        const statusEl = containerEl.createDiv('voice-notes-status');
        this.checkBackendStatus(statusEl);

        new Setting(containerEl)
            .setName('Test Connection')
            .setDesc('Check if backend service is running')
            .addButton(button => button
                .setButtonText('Test')
                .onClick(async () => {
                    await this.checkBackendStatus(statusEl);
                }));
    }

    async checkBackendStatus(statusEl: HTMLElement): Promise<void> {
        statusEl.empty();
        statusEl.createEl('p', { text: 'Checking backend status...' });

        try {
            const response = await fetch(`${this.plugin.settings.backendUrl}/status`);
            if (response.ok) {
                const data = await response.json();
                statusEl.empty();
                statusEl.createEl('p', {
                    text: '✓ Backend service is running',
                    cls: 'voice-notes-status-success'
                });
                statusEl.createEl('p', {
                    text: data.ollama_connected ? '✓ Ollama is connected' : '✗ Ollama is not connected',
                    cls: data.ollama_connected ? 'voice-notes-status-success' : 'voice-notes-status-error'
                });
                statusEl.createEl('p', {
                    text: data.model_available ? '✓ Model is available' : '✗ Model not found',
                    cls: data.model_available ? 'voice-notes-status-success' : 'voice-notes-status-error'
                });
            } else {
                statusEl.empty();
                statusEl.createEl('p', {
                    text: '✗ Backend service is not responding',
                    cls: 'voice-notes-status-error'
                });
            }
        } catch (error) {
            statusEl.empty();
            statusEl.createEl('p', {
                text: '✗ Cannot connect to backend service',
                cls: 'voice-notes-status-error'
            });
            statusEl.createEl('p', {
                text: 'Make sure the backend is running (start.bat)',
                cls: 'voice-notes-status-hint'
            });
        }
    }
}

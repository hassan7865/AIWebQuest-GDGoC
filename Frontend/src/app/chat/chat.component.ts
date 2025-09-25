import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService, UploadResponse, AskResponse } from '../../services/chat.service';
import { marked } from 'marked';

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isMarkdown?: boolean;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.component.html'
})
export class ChatComponent {
  messages: ChatMessage[] = [];
  currentQuestion: string = '';
  selectedFile: File | null = null;
  currentDocId: string | null = null;
  uploadedFileName: string = '';
  isUploading: boolean = false;
  isAsking: boolean = false;

  constructor(private chatService: ChatService) {}

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      this.selectedFile = file;
      // Automatically upload after file selection
      this.uploadDocument();
    } else {
      alert('Please select a PDF file');
    }
  }

  uploadDocument(): void {
    if (!this.selectedFile) {
      alert('Please select a file first');
      return;
    }

    this.isUploading = true;
    this.chatService.uploadDocument(this.selectedFile).subscribe({
      next: (response: UploadResponse) => {
        this.currentDocId = response.doc_id;
        this.uploadedFileName = this.selectedFile!.name;
        this.messages = [];
        
        // Add welcome message after successful upload
        this.messages.push({
          id: this.generateId(),
          type: 'assistant',
          content: `Document "${this.selectedFile!.name}" uploaded successfully! You can now ask questions about its content.`,
          timestamp: new Date()
        });
        
        this.isUploading = false;
        this.selectedFile = null;
      },
      error: (error) => {
        this.messages.push({
          id: this.generateId(),
          type: 'assistant',
          content: 'Error uploading document. Please check your connection and try again.',
          timestamp: new Date()
        });
        this.isUploading = false;
        this.selectedFile = null;
      }
    });
  }

  clearDocument(): void {
    this.currentDocId = null;
    this.uploadedFileName = '';
    this.selectedFile = null;
    this.messages = [];
    this.currentQuestion = '';
  }

  askQuestion(): void {
    if (!this.currentQuestion.trim()) {
      alert('Please enter a question');
      return;
    }

    if (!this.currentDocId) {
      alert('Please upload a document first');
      return;
    }

    // Add user message
    this.messages.push({
      id: this.generateId(),
      type: 'user',
      content: this.currentQuestion,
      timestamp: new Date()
    });

    this.isAsking = true;
    this.chatService.askQuestion(this.currentQuestion, this.currentDocId).subscribe({
      next: async (response: AskResponse) => {
        // Convert markdown to HTML
        const htmlContent = await marked(response.answer);
        this.messages.push({
          id: this.generateId(),
          type: 'assistant',
          content: htmlContent,
          timestamp: new Date(),
          isMarkdown: true
        });
        this.currentQuestion = '';
        this.isAsking = false;
      },
      error: (error) => {
        this.messages.push({
          id: this.generateId(),
          type: 'assistant',
          content: 'Error getting answer. Please try again.',
          timestamp: new Date()
        });
        this.isAsking = false;
        console.error('Ask error:', error);
      }
    });
  }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  formatTime(timestamp: Date): string {
    return timestamp.toLocaleTimeString();
  }
}

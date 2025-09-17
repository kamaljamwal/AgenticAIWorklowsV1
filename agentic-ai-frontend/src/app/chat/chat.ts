import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../services/api';
import { ChatMessage, SearchRequest, SearchResponse, FilePreview } from '../models/api.models';
import { MarkdownPipe } from '../pipes/markdown-pipe';

@Component({
  selector: 'app-chat',
  imports: [CommonModule, FormsModule, MarkdownPipe],
  templateUrl: './chat.html',
  styleUrls: ['./chat.scss']
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  @ViewChild('messageInput') private messageInput!: ElementRef;

  messages: ChatMessage[] = [];
  currentMessage = '';
  isLoading = false;
  selectedFilePreview: FilePreview | null = null;
  showFileModal = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.addWelcomeMessage();
    setTimeout(() => {
      this.messageInput?.nativeElement?.focus();
    }, 100);
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  private addWelcomeMessage() {
    const welcomeMessage: ChatMessage = {
      id: this.generateId(),
      type: 'assistant',
      content: 'Welcome to Agentic AI Workflows! I can help you search across multiple data sources including files, APIs, GitHub, JIRA, and more. What would you like to find?',
      timestamp: new Date()
    };
    this.messages.push(welcomeMessage);
  }

  sendMessage() {
    const message = this.currentMessage?.trim();
    if (!message || this.isLoading) {
      console.log('Cannot send message:', { message, isLoading: this.isLoading });
      return;
    }
    
    console.log('Sending message:', message);

    // Add user message
    const userMessage: ChatMessage = {
      id: this.generateId(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };
    this.messages.push(userMessage);

    // Add loading message
    const loadingMessage: ChatMessage = {
      id: this.generateId(),
      type: 'assistant',
      content: 'Searching...',
      timestamp: new Date(),
      isLoading: true
    };
    this.messages.push(loadingMessage);

    const searchRequest: SearchRequest = {
      prompt: message,
      max_results: 10
    };

    this.isLoading = true;
    this.currentMessage = '';

    this.apiService.search(searchRequest).subscribe({
      next: (response: SearchResponse) => {
        console.log('Response received:', response);
        this.isLoading = false;
        
        // Remove all loading messages
        this.messages = this.messages.filter(m => !m.isLoading);
        
        // Add response message
        const formattedContent = this.formatSearchResponse(response);
        console.log('Formatted content:', formattedContent);
        
        const responseMessage: ChatMessage = {
          id: this.generateId(),
          type: 'assistant',
          content: formattedContent,
          timestamp: new Date(),
          searchResponse: response,
          isLoading: false // Explicitly set to false
        };
        
        this.messages.push(responseMessage);
        console.log('Messages after push:', this.messages.length);
      },
      error: (error) => {
        this.isLoading = false;
        // Remove loading message
        this.messages = this.messages.filter(m => !m.isLoading);
        
        // Add error message
        const errorMessage: ChatMessage = {
          id: this.generateId(),
          type: 'assistant',
          content: `Sorry, I encountered an error: ${error.message}`,
          timestamp: new Date()
        };
        this.messages.push(errorMessage);
      }
    });
  }

  private formatSearchResponse(response: SearchResponse): string {
    if (!response.results || response.results.length === 0) {
      return 'I couldn\'t find any results for your query. Please try rephrasing or being more specific.';
    }

    let formattedResponse = response.summary || 'Here are the results I found:';
    
    if (response.total_results > 0) {
      formattedResponse += `\n\n**Found ${response.total_results} result${response.total_results > 1 ? 's' : ''} across ${response.agents_used.length} agent${response.agents_used.length > 1 ? 's' : ''}**`;
    }

    return formattedResponse;
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  onInputChange() {
    // Trigger change detection for button state
    // This ensures the button state updates as user types
  }

  canSend(): boolean {
    return !!(this.currentMessage && this.currentMessage.trim() && !this.isLoading);
  }

  previewFile(filePath: string) {
    this.apiService.previewFile(filePath).subscribe({
      next: (preview: FilePreview) => {
        this.selectedFilePreview = preview;
        this.showFileModal = true;
      },
      error: (error) => {
        console.error('Error previewing file:', error);
        alert('Error loading file preview: ' + error.message);
      }
    });
  }

  closeFileModal() {
    this.showFileModal = false;
    this.selectedFilePreview = null;
  }

  copyToClipboard(text: string) {
    navigator.clipboard.writeText(text).then(() => {
      // Could add a toast notification here
    }).catch(err => {
      console.error('Failed to copy text: ', err);
    });
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  formatDate(timestamp: number): string {
    return new Date(timestamp * 1000).toLocaleString();
  }

  getAgentIcon(agentType: string): string {
    const icons: { [key: string]: string } = {
      'FILESYSTEM': '📁',
      'API': '🔗',
      'URL': '🌐',
      'GITHUB': '🐙',
      'JIRA': '🎫',
      'VIDEO': '🎥',
      'S3': '☁️'
    };
    return icons[agentType.toUpperCase()] || '🤖';
  }

  private scrollToBottom(): void {
    try {
      if (this.messagesContainer) {
        this.messagesContainer.nativeElement.scrollTop = this.messagesContainer.nativeElement.scrollHeight;
      }
    } catch (err) {
      console.error('Error scrolling to bottom:', err);
    }
  }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }
}

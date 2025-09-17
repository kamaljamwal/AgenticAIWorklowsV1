import { Component } from '@angular/core';
import { ChatComponent } from './chat/chat';

@Component({
  selector: 'app-root',
  imports: [ChatComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  title = 'Agentic AI Workflows';
}

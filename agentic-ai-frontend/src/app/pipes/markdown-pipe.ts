import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'markdown',
  standalone: true
})
export class MarkdownPipe implements PipeTransform {

  transform(value: string): string {
    if (!value) return '';
    
    // Simple markdown-like transformations
    let result = value
      // Bold text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Italic text
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      // Line breaks
      .replace(/\n/g, '<br>')
      // Code blocks
      .replace(/`(.*?)`/g, '<code>$1</code>');
    
    return result;
  }
}

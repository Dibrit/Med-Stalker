import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ToastService } from './toast.service';

@Component({
  selector: 'app-toast-stack',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './toast-stack.component.html',
  styleUrl: './toast-stack.component.scss'
})
export class ToastStackComponent {
  readonly toastSvc = inject(ToastService);

  dismiss(id: string) {
    this.toastSvc.dismiss(id);
  }
}


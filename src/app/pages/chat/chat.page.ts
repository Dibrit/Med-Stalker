import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { Message } from '../../core/models';
import { MessageService } from '../../core/messages/message.service';
import { PatientService } from '../../core/patients/patient.service';
import { SessionService } from '../../core/session/session.service';
import { ToastService } from '../../shared/toast/toast.service';
import { AppointmentService } from '../../core/appointments/appointment.service';

@Component({
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './chat.page.html',
  styleUrl: './chat.page.scss'
})
export class ChatPage {
  private readonly messageSvc = inject(MessageService);
  private readonly patientSvc = inject(PatientService);
  private readonly appointmentSvc = inject(AppointmentService);
  readonly session = inject(SessionService);
  private readonly toasts = inject(ToastService);
  private readonly cdr = inject(ChangeDetectorRef);

  loading = true;
  sending = false;
  error: string | null = null;

  messages: Message[] = [];
  conversationPartners: any[] = [];
  selectedPartner: any | null = null;
  messageContent: string = '';

  ngOnInit() {
    this.loadMessages();
  }

  private loadMessages() {
    this.loading = true;
    this.error = null;

    const snapshot = this.session.snapshot();
    const session$ = snapshot.mode === 'unknown' ? this.session.hydrate() : of(snapshot);

    let doctorsOrPatients$;
    const isDoctor = snapshot.mode === 'doctor';
    if (isDoctor) {
      doctorsOrPatients$ = this.patientSvc.list();
    } else {
      doctorsOrPatients$ = this.appointmentSvc.listDoctors();
    }

    forkJoin({
      session: session$,
      messages: this.messageSvc.list(),
      partners: doctorsOrPatients$
    }).subscribe({
      next: ({ session, messages, partners }) => {
        this.messages = messages.sort((a, b) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        this.conversationPartners = partners;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.error = 'Could not load messages.';
        this.loading = false;
        this.toasts.error(this.error);
        this.cdr.detectChanges();
      }
    });
  }

  getPartnerDisplay(partner: any): string {
    if (partner.full_name) {
      // Doctor
      return `${partner.full_name} (${partner.specialization})`;
    } else {
      // Patient
      return `${partner.first_name} ${partner.last_name}`;
    }
  }

  getMessagesWithPartner(): Message[] {
    if (!this.selectedPartner) return [];

    const isDoctor = this.session.snapshot().mode === 'doctor';
    return this.messages.filter((msg) => {
      if (isDoctor) {
        // Show messages where I'm the doctor and this is the patient
        return (
          (msg.sender_doctor && msg.recipient_patient === this.selectedPartner.id) ||
          (msg.sender_patient === this.selectedPartner.id && msg.recipient_doctor)
        );
      } else {
        // Show messages where I'm the patient and this is the doctor
        return (
          (msg.sender_patient && msg.recipient_doctor === this.selectedPartner.id) ||
          (msg.sender_doctor === this.selectedPartner.id && msg.recipient_patient)
        );
      }
    });
  }

  sendMessage() {
    if (!this.selectedPartner) {
      this.toasts.error('Please select a conversation partner.');
      return;
    }

    if (!this.messageContent.trim()) {
      this.toasts.error('Please enter a message.');
      return;
    }

    this.sending = true;
    const isDoctor = this.session.snapshot().mode === 'doctor';
    const payload = isDoctor 
      ? { recipient_patient: this.selectedPartner.id, content: this.messageContent }
      : { recipient_doctor: this.selectedPartner.id, content: this.messageContent };

    this.messageSvc.create(payload).subscribe({
      next: (message) => {
        this.messages.push(message);
        this.messages.sort((a, b) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        this.messageContent = '';
        this.sending = false;
        this.cdr.detectChanges();
        this.scrollToBottom();
      },
      error: (err) => {
        this.sending = false;
        const errorMsg = err?.error?.detail || 'Could not send message.';
        this.toasts.error(errorMsg);
        this.cdr.detectChanges();
      }
    });
  }

  private scrollToBottom() {
    setTimeout(() => {
      const messagesContainer = document.querySelector('.chat__messages');
      if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    }, 0);
  }

  isMyMessage(message: Message): boolean {
    const isDoctor = this.session.snapshot().mode === 'doctor';
    return isDoctor ? message.sender_type === 'doctor' : message.sender_type === 'patient';
  }
}

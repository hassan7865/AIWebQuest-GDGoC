import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./chat/chat.component').then(m => m.ChatComponent)
  },
  
];

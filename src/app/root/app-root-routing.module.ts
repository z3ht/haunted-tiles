import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

const routes: Routes = [
  {path: '', redirectTo: 'about', pathMatch: 'full'},
  {path: 'about', loadChildren: () => import('../about/about.module').then(m => m.AboutModule)},
  {path: 'game', loadChildren: () => import('../game-host/game-host.module').then(m => m.GameHostModule)},
  {path: 'register', loadChildren: () => import('../registration/registration.module').then(m => m.RegistrationModule)},
  {path: 'rules', loadChildren: () => import('../rules/rules.module').then(m => m.RulesModule)},
  {path: 'tournament', loadChildren: () => import('../tournament/tournament.module').then(m => m.TournamentModule)},
  {path: 'submission', loadChildren: () => import('../submission/submission.module').then(m => m.SubmissionModule)},
  {path: '**', redirectTo: 'about'},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRootRoutingModule { }

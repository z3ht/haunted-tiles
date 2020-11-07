import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { GameHostContainerComponent } from './game-host-container/game-host-container.component';

const routes: Routes = [
  {path: '', component: GameHostContainerComponent}
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class GameHostRoutingModule { }

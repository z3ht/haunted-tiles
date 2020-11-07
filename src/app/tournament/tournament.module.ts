import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';

import { TournamentRoutingModule } from './tournament-routing.module';
import { TournamentComponent } from './tournament/tournament.component';
import { BracketComponent } from './bracket/bracket/bracket.component';



@NgModule({
  declarations: [TournamentComponent, BracketComponent],
  imports: [
    MatTabsModule,
    TournamentRoutingModule,
    CommonModule
  ],
  entryComponents: [TournamentComponent]
})
export class TournamentModule { }

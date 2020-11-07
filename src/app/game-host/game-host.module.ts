import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTabsModule } from '@angular/material/tabs';
import { MatToolbarModule } from '@angular/material/toolbar';
import { GameHostContainerComponent } from './game-host-container/game-host-container.component';
import { GameHostRoutingModule } from './game-host-routing.module';
import { SimpleRunComponent } from './simple-run/simple-run.component';
import { TeamConfigAdderComponent } from './team-config-adder/team-config-adder.component';
import { CodemirrorModule } from '@ctrl/ngx-codemirror';


@NgModule({
  declarations: [GameHostContainerComponent, TeamConfigAdderComponent, SimpleRunComponent],
  imports: [
    CommonModule,
    GameHostRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatSelectModule,
    MatCardModule,
    MatListModule,
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule,
    MatSnackBarModule,
    MatToolbarModule,
    MatIconModule,
    MatTabsModule,
    MatDialogModule,
    CodemirrorModule,
  ]
})
export class GameHostModule { }

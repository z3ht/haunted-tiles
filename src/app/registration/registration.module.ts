import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { RegistrationRoutingModule } from './registration-routing.module';
import { RegisterComponent } from './register/register.component';
import { FlexLayoutModule } from '@angular/flex-layout';


@NgModule({
  declarations: [RegisterComponent],
  imports: [
    CommonModule,
    RegistrationRoutingModule,
    FlexLayoutModule
  ]
})
export class RegistrationModule { }

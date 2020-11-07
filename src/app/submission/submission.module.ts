import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SubmissionComponent } from './submission/submission.component';
import { SubmissionRoutingModule } from './submission-routing.module';
import { FlexLayoutModule } from '@angular/flex-layout';



@NgModule({
  declarations: [SubmissionComponent],
  imports: [
    CommonModule,
    SubmissionRoutingModule,
    FlexLayoutModule
  ]
})
export class SubmissionModule { }

import { Injectable } from '@angular/core';
import { ToastrService } from 'ngx-toastr';

@Injectable({
  providedIn: 'root'
})
export class ToastService {

  constructor(private toastr: ToastrService) { }

  showError(message, title){
    console.log("Toast error");
    this.toastr.error(message, title);
  }
}

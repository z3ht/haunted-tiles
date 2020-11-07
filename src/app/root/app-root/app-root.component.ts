import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app-root.component.html',
  styleUrls: ['./app-root.component.scss']
})
export class AppRootComponent {

  opened: boolean = true;

  constructor(router: Router) {
  }

  openSidenav () {
    this.opened = !this.opened;
  }
}

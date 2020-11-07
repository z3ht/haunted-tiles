import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'tyl-tournament',
  templateUrl: './tournament.component.html',
  styleUrls: ['./tournament.component.scss']
})
export class TournamentComponent implements OnInit {

  links = ['FINALS', 'CSM', 'TTU', 'UMaine'];
  activeLink = this.links[0];

  constructor() { }

  ngOnInit(): void {
  }

}

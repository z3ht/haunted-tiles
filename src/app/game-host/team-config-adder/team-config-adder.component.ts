import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { ITeamConfig, MonsterType, Side } from 'src/app/game/objects/interfaces';

@Component({
  selector: 'tyl-team-config-adder',
  templateUrl: './team-config-adder.component.html',
  styleUrls: ['./team-config-adder.component.scss']
})
export class TeamConfigAdderComponent implements OnInit {

  monsters: string[] = Object.keys(MonsterType);

  teamForm = new FormGroup({
    teamName: new FormControl('', Validators.required),
    schoolName: new FormControl('', Validators.required),
    script: new FormControl('', Validators.required),
    monsterChoice1: new FormControl('', Validators.required),
    monsterChoice2: new FormControl('', Validators.required)
  });

  @Output() addTeam = new EventEmitter<ITeamConfig>();

  constructor() { }

  ngOnInit(): void {
  }

  onSubmit() {
    let teamConfig: ITeamConfig = {
      name: this.teamForm.value.teamName,
      org: this.teamForm.value.schoolName,
      preferredMonsters: {
        [Side.Home]: MonsterType[this.teamForm.value.monsterChoice1],
        [Side.Away]: MonsterType[this.teamForm.value.monsterChoice2],
      },
      aiSrc: this.teamForm.value.script
    }
    this.addTeam.emit(teamConfig);
    this.teamForm.reset();
  }
}
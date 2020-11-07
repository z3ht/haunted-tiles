import { Injectable } from '@angular/core';
import { ITeamConfig, MonsterType, Side, } from 'src/app/game/objects/interfaces';
import { wanderScript, tileStatusScript } from 'src/app/game/ai';
import { parse } from 'papaparse';
import { Observable, of } from 'rxjs';
import { developmentScript } from '../game/ai/development.ai';
import { Observer } from 'rxjs/internal/types';

@Injectable({
  providedIn: 'root'
})

export class TeamConfigsService {

  teamConfigs: ITeamConfig[] = [];

  // const path = 'https://www.dropbox.com/s/u88xk27egffpvr8/CodeSubmission.csv?dl=0';
  url = '/assets/matchSetup/CodeSubmission.csv';

  developmentConfig: ITeamConfig = {
    name: 'Development Team',
    org: 'Development',
    preferredMonsters: {
      [Side.Home]: MonsterType.Bobo,
      [Side.Away]: MonsterType.Triclops,
    },
    aiSrc: developmentScript,
  };

  constructor() { }

  parseTeamConfigs(): Observable<ITeamConfig[]> {
    this.teamConfigs.push(this.developmentConfig);
    const self = this;
    return new Observable((observer: Observer<ITeamConfig[]>) => {
      parse(this.url, {
        header: true,
        download: true,
        error(error, file) {
          console.log('Error parsing file: ' + file);
          console.log(error);
        },
        complete(results) {
          console.log('Completed Parse:' + results);
          results.data.forEach(element => {
            let team: ITeamConfig = {
              name: element['Team Name'],
              preferredMonsters: {
                [Side.Home]: element['Home Monster Choice'].toLowerCase() as MonsterType,
                [Side.Away]: element['Away Monster Choice'].toLowerCase() as MonsterType,
              },
              aiSrc: element['URL/Code'],
              org: element['School']
            };
            self.teamConfigs.push(team);
          });
          console.log(self.teamConfigs);
          observer.next(self.teamConfigs);
          observer.complete();
        }
      })
    });
  }
}
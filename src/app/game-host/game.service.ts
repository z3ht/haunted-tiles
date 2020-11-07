import { Injectable } from '@angular/core';
import { from, fromEvent, merge, ReplaySubject } from 'rxjs';
import { first, map, mapTo, mergeMap, shareReplay, startWith, switchMap } from 'rxjs/operators';
import { createGame, Game, MainKey, SceneEvent } from '../game/game';
import { TeamInfo, Teams } from '../game/objects/game-manager';
import { MatchEventArgs, ITeamConfig, Side, StateChangeEvent, MatchEvent, GameWinningSide, MonsterType } from '../game/objects/interfaces';
import { Team } from '../game/objects/team';
import { MainScene } from '../game/scenes/main.scene';
import { MapConfigsService } from './map-config.service';
import { ToastService } from './toast.service';

@Injectable({
  providedIn: 'root'
})
export class GameService {
  private game$ = new ReplaySubject<Game>(1);
  private mainScene$ = this.game$.pipe(
    map(game => game.scene.getScene(MainKey) as MainScene),
    shareReplay(1),
  );

  teamsInfo$ = this.mainScene$.pipe(
    switchMap(mainScene => fromEvent<Record<Side, TeamInfo>>(mainScene.match, StateChangeEvent.ScoreBoardUpdate)),
    shareReplay(1),
  );

  homeTeamInfo$ = this.teamsInfo$.pipe(
    map(teamsInfo => teamsInfo[Side.Home]),
    shareReplay(1),
  );

  awayTeamInfo$ = this.teamsInfo$.pipe(
    map(teamsInfo => teamsInfo[Side.Away]),
    shareReplay(1),
  );

  gameOver$ = this.mainScene$.pipe(
    switchMap(mainScene => fromEvent<MatchEventArgs>(mainScene.match, MatchEvent.GameEnd)),
    shareReplay(1),
  );

  isPaused$ = this.mainScene$.pipe(
    mergeMap(scene => merge(
      fromEvent(scene.events, SceneEvent.PAUSE).pipe(mapTo(true)),
      fromEvent(scene.events, SceneEvent.RESUME).pipe(mapTo(false))
    ).pipe(startWith(scene.scene.isPaused(MainKey)))),
  );

  readonly containerElement: HTMLDivElement;

  constructor(
    private toastService: ToastService,
    private mapConfigService: MapConfigsService
    ) {
    const parent = document.createElement('div');
    parent.style.flex = "1 1 auto";
    this.containerElement = parent;

    from(createGame({ parent })).subscribe(game => this.game$.next(game));
  }

  pause() {
    this.mainScene$.pipe(first()).subscribe(scene => scene.scene.pause(MainKey));
  }

  resume() {
    this.mainScene$.pipe(first()).subscribe(scene => scene.scene.resume(MainKey));
  }

  setTeamConfigs(homeTeamConfig: ITeamConfig, awayTeamConfig: ITeamConfig) {
    this.mainScene$.pipe(first()).subscribe(scene => {
      const homeTeam = new Team(scene, homeTeamConfig, this.toastService);
      const awayTeam = new Team(scene, awayTeamConfig, this.toastService);
      const teams: Teams = {
          [Side.Home]: homeTeam,
          [Side.Away]: awayTeam
      }
      scene.gameEnd.reset();
      scene.match.clearBoard();
      scene.match.applyMap(this.mapConfigService.currentMap);
      scene.match.initTeams(teams);
      scene.match.initialize();
    });
  }

  resetGame(){
    this.mainScene$.pipe(first()).subscribe(scene => {
      scene.gameEnd.reset();
      scene.match.clearBoard();
      scene.match.initialize();
    });
  }

  gameEnd(winningSide: GameWinningSide, victoryMonsterType: MonsterType, defeatMonsterType: MonsterType) {
    this.mainScene$.pipe(first()).subscribe(scene => {
      scene.match.hide();
      scene.gameEnd.init(scene, winningSide, victoryMonsterType, defeatMonsterType);
    });
  }
}

import { Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { on } from 'process';
import { Subscription } from 'rxjs';
import { first, map } from 'rxjs/operators';
import { GameState, GameWinningSide, ITeamConfig, GridMap, TeamState } from 'src/app/game/objects/interfaces';
import { TeamInfo } from '../../game/game';
import { GameService } from '../game.service';
import { MapConfigsService } from '../map-config.service';
import { RoundManagerService } from '../round-manager-service';
import { SimpleRunComponent } from '../simple-run/simple-run.component';
import { TeamConfigAdderComponent } from '../team-config-adder/team-config-adder.component';
import { TeamConfigsService } from '../team-configs.service';


const getTeamName = () => map<TeamInfo, string>(({ teamName }) => teamName + ":");
const getTeamScore = () => map<TeamInfo, number>(({ totalTilesDecremented }) => totalTilesDecremented);
const getTeamIcon = () => map<TeamInfo, string>(({ teamIcon }) => `assets/scoreBoardIcons/${teamIcon}.png`);

@Component({
  selector: 'tyl-game-host-container',
  templateUrl: './game-host-container.component.html',
  styleUrls: ['./game-host-container.component.scss']
})
export class GameHostContainerComponent implements OnInit, OnDestroy {
  @ViewChild('gameHost', { static: true }) hostElement: ElementRef<HTMLElement>;

  homeTeamName$ = this.gameService.homeTeamInfo$.pipe(getTeamName());
  awayTeamName$ = this.gameService.awayTeamInfo$.pipe(getTeamName());
  homeTeamScore$ = this.gameService.homeTeamInfo$.pipe(getTeamScore());
  awayTeamScore$ = this.gameService.awayTeamInfo$.pipe(getTeamScore());
  homeTeamIcon$ = this.gameService.homeTeamInfo$.pipe(getTeamIcon());
  awayTeamIcon$ = this.gameService.awayTeamInfo$.pipe(getTeamIcon());
  pause$ = this.gameService.isPaused$;
  homeTeamConfig: ITeamConfig;
  awayTeamConfig: ITeamConfig;

  //TODO: Figure out the flow of data w/events to properly hide / show UI elements
  showScoreBoard: boolean = true;
  showTeamConfigs: boolean = true;
  showTeamScores: boolean = false;

  gameOverSubscription: Subscription = this.gameService.gameOver$.subscribe(args => {
    let homeState = args.team.home.state;
    let awayState = args.team.away.state;
    if(homeState == TeamState.Win){
      this.roundManagerService.homeRoundWins++;
    }else if(awayState == TeamState.Win){
      this.roundManagerService.awayRoundWins++;
    }else if(args.state == GameState.Draw){
      if(args.team.home.tilesDecremented > args.team.away.tilesDecremented){
        this.roundManagerService.homeRoundWins++;
      }else if(args.team.home.tilesDecremented < args.team.away.tilesDecremented){
        this.roundManagerService.awayRoundWins++;
      }else{
        this.roundManagerService.roundDraws++;
      }
    }
    this.delay(3000).then(any => {
      this.roundManagerService.completedRounds++;
      if (this.roundManagerService.completedRounds < this.roundManagerService.numRounds) {
        this.gameService.setTeamConfigs(this.homeTeamConfig, this.awayTeamConfig);
      } else {
        if (this.roundManagerService.homeRoundWins === this.roundManagerService.awayRoundWins) {
          this.gameService.gameEnd(GameWinningSide.Draw, args.team.home.monsterType, args.team.away.monsterType);
        } else if (this.roundManagerService.homeRoundWins > this.roundManagerService.awayRoundWins) {
          this.gameService.gameEnd(GameWinningSide.Home, args.team.home.monsterType, args.team.away.monsterType);
        } else if (this.roundManagerService.homeRoundWins < this.roundManagerService.awayRoundWins) {
          this.gameService.gameEnd(GameWinningSide.Away, args.team.away.monsterType, args.team.home.monsterType);
        }
      }
    })
  });

  constructor(private roundManagerService: RoundManagerService, 
    private gameService: GameService, 
    private snackBar: MatSnackBar, 
    private configService: TeamConfigsService, 
    private mapConfigService: MapConfigsService,
    public dialog: MatDialog) { }

  async delay(ms: number) {
    await new Promise(resolve => setTimeout(() => resolve(), ms));
  }

  ngOnInit(): void {
    this.populateTeamConfigs();
    this.mapConfigService.parseMaps();
    this.hostElement.nativeElement.appendChild(this.gameService.containerElement);
    this.gameService.resume();
  }

  ngOnDestroy(): void {
    this.gameService.pause();
    this.hostElement.nativeElement.removeChild(this.gameService.containerElement);
    this.gameOverSubscription.unsubscribe();
  }

  startGame() {
    this.roundManagerService.completedRounds = 0;
    this.roundManagerService.homeRoundWins = 0;
    this.roundManagerService.awayRoundWins = 0;
    this.roundManagerService.roundDraws = 0;
    this.gameService.setTeamConfigs(this.homeTeamConfig, this.awayTeamConfig);
    // this.showScoreBoard = true;
    this.showTeamScores = true;
  }

  resetGame() {
    this.gameService.resetGame();
  }

  resume() {
    this.gameService.resume();
  }

  pause() {
    this.gameService.isPaused$.pipe(first()).subscribe(paused => !paused ?
      this.gameService.pause() : this.gameService.resume())
  }
  addTeam() {
    const dialogRef = this.dialog.open(TeamConfigAdderComponent);
    dialogRef.componentInstance.addTeam.subscribe((teamConfig) => {
      this.onAddTeam(teamConfig);
    })
    dialogRef.afterClosed().subscribe(result => {
      console.log(`Dialog result: ${result}`);
    });
  }

  openCodeDialog() {
    const dialogConfig = new MatDialogConfig();
    dialogConfig.width = '80%';
    dialogConfig.height = '80%';

    const dialogRef = this.dialog.open(SimpleRunComponent, dialogConfig);
    dialogRef.afterClosed().subscribe(result => {
      console.log(`Dialog result: ${result}`);
    });
  }


  onAddTeam(teamConfig: ITeamConfig) {
    this.configService.teamConfigs.push(teamConfig);
    this.snackBar.open("Configuration added: " + teamConfig.name, "Dismiss", { duration: 5000 });
  }

  setStartingTeamConfigs(): void{
    this.homeTeamConfig = this.configService.developmentConfig;
      if (this.configService.teamConfigs.length > 1) {
        this.awayTeamConfig = this.configService.teamConfigs[1];
      }
  }

  populateTeamConfigs(): void {
    if(this.configService.teamConfigs.length > 0){
      this.setStartingTeamConfigs();
    }else{
      this.configService.parseTeamConfigs().subscribe(teamConfigs => {
        console.log("teamConfigs: " + teamConfigs.toString());
        this.setStartingTeamConfigs();
      });
    }
  }

  // Needed for html binding to actually store object in component on selection of config
  compareConfigs(o1: any, o2: any): boolean {
    return o1.name === o2.name;
  }

  getTeamConfigs() {
    return this.configService.teamConfigs;
  }

}

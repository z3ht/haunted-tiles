import { Events } from 'phaser';
import { TileGrid } from './grid';
import {
  ErrorReason,
  IGameState,
  ILocation,
  MoveDirection,
  MoveSet,
  Side,
  StateChangeEvent,
  StateUpdatedEventArgs,
  TeamStates,
  GameState,
  TeamState,
  MatchEventArgs,
  MatchEvent, GridMap 
} from './interfaces';
import { Monster } from './monster';
import { Team } from './team';


export type Teams = Record<Side, Team>;
export type StartLocations = Record<Side, ILocation[]>;

export interface IMatchConfig {
  grid: TileGrid;
  teams: Teams;
  startLocations: StartLocations;
}

export interface TeamInfo {
  teamName:string;
  totalTilesDecremented:number;
  teamIcon:string;
}

export class GameManager {
  private eventEmitter = new Events.EventEmitter();

  private _state: GameState;
  get state() { return this._state; }

  private matchConfig: IMatchConfig;

  private teams: Teams;
  private grid: TileGrid;

  private readonly sides = Object.values(Side);

  constructor(private readonly thinkingTime = 2000, private readonly minThinkingTime = 1000) {
  }

  initGrid(grid: TileGrid) {
    let gridLength = grid.getGridLength()-1;
    let halfGridLength = Math.floor(gridLength/2);
    this.matchConfig = {
      grid: grid,
      teams: null,
      startLocations:{
        [Side.Home]: [grid.getTileAtIndex(0, 0), grid.getTileAtIndex(0, halfGridLength), grid.getTileAtIndex(0, gridLength)],
        [Side.Away]: [grid.getTileAtIndex(gridLength, 0), grid.getTileAtIndex(gridLength, halfGridLength), grid.getTileAtIndex(gridLength, gridLength)],
      }
    }
  }

  initTeams(teams: Teams){
    this.matchConfig.teams = teams;
  }

  clearBoard(){
    this.sides.forEach(side => {
      if(this.teams && this.teams[side]){
        this.teams[side].reset();
      }
    });
    this.grid?.reset();
  }

  update(dt: number) {

  }

  on(event: string | symbol, fn: Function, context?: any): this {
    this.eventEmitter.on(event, fn, context);
    return this;
  }

  addListener(event: string | symbol, fn: Function, context?: any): this {
    this.eventEmitter.addListener(event, fn, context);
    return this;
  }

  once(event: string | symbol, fn: Function, context?: any): this {
    this.eventEmitter.once(event, fn, context);
    return this;
  }

  removeListener(event: string | symbol, fn?: Function, context?: any, once?: boolean): this {
    this.eventEmitter.removeListener(event, fn, context, once);
    return this;
  }

  off(event: string | symbol, fn?: Function, context?: any, once?: boolean): this {
    this.eventEmitter.off(event, fn, context, once);
    return this;
  }

  removeAllListeners(event?: string | symbol): this {
    this.eventEmitter.removeAllListeners(event);
    return this;
  }

  hide() {
    this.sides.forEach(side => this.teams[side].setVisible(false));
    this.grid.setVisible(false);
  }

  show() {
    this.sides.forEach(side => this.teams[side].setVisible(true));
    this.grid.setVisible(true);
  }

  private stateChangeHandler = function (this: GameManager, { payload }: StateUpdatedEventArgs<TeamState, ErrorReason>) {
    const teamStates = Object.values(this.teams).map(team => team.state);

    if (this.state !== GameState.Resolving && !teamStates.some(state => state === TeamState.Updating) && !teamStates.some(state => state === TeamState.Initializing)) {
      if (teamStates.every(state => state === TeamState.Error)) {
        this.setState(GameState.Error);
        return;
      }

      // if (teamStates.every(state => state === TeamState.Dead || state === TeamState.Error)) {
      //   this.setState(GameState.Draw);
      //   return;
      // }

      if (teamStates.every(state => state === TeamState.Thinking)) {
        this.setState(GameState.Resolving);
        return;
      }

      // check for a winning team
      // const isLost = (state: TeamState) => state === TeamState.Dead || state === TeamState.Error;
      // const isLostHome = isLost(this.teams[Side.Home].state);
      // const isLostAway = isLost(this.teams[Side.Away].state);
      // if (isLostHome && !isLostAway) {
      //   this.setState(GameState.AwayTeamWins);
      // } else if (!isLostHome && isLostAway) {
      //   this.setState(GameState.HomeTeamWins);
      // }
      this.checkWinLossTie();
    }
  }

  private checkWinLossTie() {
    // check for a winning team
    const isLost = (state: TeamState) => state === TeamState.Dead || state === TeamState.Error;
    const isLostHome = isLost(this.teams[Side.Home].state);
    const isLostAway = isLost(this.teams[Side.Away].state);
    if (isLostHome && isLostAway) {
      this.setState(GameState.Draw);
    } else if (isLostHome && !isLostAway) {
      this.setState(GameState.AwayTeamWins);
    } else if (!isLostHome && isLostAway) {
      this.setState(GameState.HomeTeamWins);
    } else {
      return false;
    }
    return true;
  }

  public async initialize() {
    const { teams, grid, startLocations } = this.matchConfig;

    //TODO: initialize should probably never be called without teams being set, only happens when pressing R
    if(teams == null){
      return;
    }

    if (this.teams) {
      // clear any handlers on existing teams
      Object.values(this.teams).forEach(team => team.removeAllListeners(StateChangeEvent.Updated));
    }

    this.setState(GameState.Initializing);
    this.teams = teams;
    // register for team events
    Object.values(teams).forEach(team => team.on(StateChangeEvent.Updated, this.stateChangeHandler, this));
    this.grid = grid;

    // figure out if the away team needs to switch monsters.
    const { home: homeMonsterType } = this.teams[Side.Home].getPreferredTypes();
    const { home: awayMonsterType } = this.teams[Side.Away].getPreferredTypes();
    const useAlternateMonster = homeMonsterType === awayMonsterType;

    // wait for all scripts to load
    const promises = [
      this.teams[Side.Home].setupTeam(startLocations[Side.Home], Side.Home),
      this.teams[Side.Away].setupTeam(startLocations[Side.Away], Side.Away, useAlternateMonster),
    ];

    await Promise.allSettled(promises);

    this.sides.forEach(side => {
      this.teams[side].setVisible(true);
    });
    this.grid.setVisible(true);

    const homeTeamReady = this.teams[Side.Home].state !== TeamState.Error;
    const awayTeamReady = this.teams[Side.Away].state !== TeamState.Error;

    if (homeTeamReady && awayTeamReady) {
      // nothing to do here, the teams will report in when all is well, and the
      // state change handler for the teams will update the state!
    } else if (!homeTeamReady && !awayTeamReady) {
      this.setState(GameState.Draw);
    } else if (homeTeamReady && !awayTeamReady) {
      this.setState(GameState.HomeTeamWins);
    } else {
      this.setState(GameState.AwayTeamWins);
    }
  }

  private requestMoveSets() {
    const serializedGameState: IGameState = {
      boardSize: [this.grid.size, this.grid.size],
      tileStates: this.grid.serialize(),
      teamStates: this.sides.reduce((states: TeamStates, side) => {
        states[side] = this.teams[side].serialize();
        return states;
      }, {} as TeamStates)
    };

    const home = this.teams[Side.Home];
    const away = this.teams[Side.Away];

    const promises = [home.getNextMovesAsync(serializedGameState, this.thinkingTime), away.getNextMovesAsync(serializedGameState, this.thinkingTime)];
    return Promise.allSettled(promises);
  }


  private async updateMoves() {
    const minTimerPromise = new Promise(resolve => setTimeout(() => resolve(), this.minThinkingTime));
    const allSettled = await this.requestMoveSets();

    const [homeError, awayError] = allSettled.map(({status, reason}: PromiseRejectedResult) => status === 'rejected' ? reason : null);

    const home = this.teams[Side.Home];
    const away = this.teams[Side.Away];

    // make sure the team state didnt slip into error.
    // this occurs when there is a critical failure in the ai
    const homeOkay = home.state !== TeamState.Error;
    const awayOkay = away.state !== TeamState.Error;

    if (homeOkay && awayOkay) {
      this.setState(GameState.Thinking);
      const [homeResponse, awayResponse] = allSettled.map(result => (<any>result).value);

      // validate teh moves
      const [homeMoves, awayMoves] = [this.validateMoves(homeResponse, Side.Home), this.validateMoves(awayResponse, Side.Away)];

      // make sure the move set returned is actually a valid move
      if (homeMoves === null && awayMoves === null) {
        // neither team had valid moves
        this.setState(GameState.Draw);
        return;
      } else if(homeMoves === null && awayMoves !== null) {
        // home team did not return valid moves
        this.setState(GameState.AwayTeamWins);
        return;
      } else if(homeMoves !== null && awayMoves === null) {
        // away team did not return valid moves
        this.setState(GameState.HomeTeamWins);
        return;
      }

      // make sure the minimum amount of thinking time has occurred
      await minTimerPromise;

      // all moves are dispatched, time to wait for the teams
      // to say they are done animating!
      this.setState(GameState.Updating);

      // instruct teams to move
      home.moveTeam(homeMoves);
      away.moveTeam(awayMoves);

    } else if (!homeOkay && awayOkay) {
      console.warn(`${home.name} script error.`, homeError);
      // home team script critically failed
      this.setState(GameState.AwayTeamWins);
      return;
    } else if (homeOkay && !awayOkay) {
      console.warn(`${away.name} script error.`, awayError);
      // away team script critically failed
      this.setState(GameState.HomeTeamWins);
      return;
    } else {
      console.warn(`${home.name} script error.`, homeError);
      console.warn(`${away.name} script error.`, awayError);
      // both team scripts critically failed
      this.setState(GameState.Draw);
      return;
    }
  }

  private validateMoves(moves: any, side: Side): MoveSet | null {
    const team = this.teams[side];
    const isValidMove = (move: any) => {
      return move === MoveDirection.None ||
        move === MoveDirection.North ||
        move === MoveDirection.South ||
        move === MoveDirection.East ||
        move === MoveDirection.West;
    }

    // console.log('validate-moves', moves, side, team);

    if (Array.isArray(moves)) {
      const resolvedMoves: MoveSet = [];
      if (moves.length != team.count) {
        console.warn(`Not enough moves returned, attempting to match moves with alive members`);
        // try and match up the moves to non-dead team members
        team.getChildren().forEach((member: Monster) => {
          console.log('validate-moves.member', member);
          if (member.isAlive()) {
            const nextMove = moves.shift();
            resolvedMoves.push(isValidMove(nextMove) ? nextMove : MoveDirection.None);
          } else {
            resolvedMoves.push(MoveDirection.None);
          }
        });
      } else {
        // return the right number of moves, let's just check to make sure they are valid moves
        // if not force the move to be "none"
        const validMoves = moves.map(move => isValidMove(move) ? move : MoveDirection.None);
        resolvedMoves.push(...validMoves);
      }

      return resolvedMoves;
    } else {
      // player script failed to return an array.  Must not have read the rules
      console.warn(`${team.name} did not return an array.`);
    }
    return null;
  }

  private exitState(state: GameState) {
    switch (state) {
      case GameState.Initializing:
      case GameState.Updating:
        if (state === GameState.Initializing) {
          this.printGameStateMsg('match started');
        }

        const home = this.teams[Side.Home];
        const away = this.teams[Side.Away];
        const teamInfo: Record<Side, TeamInfo> = {
          [Side.Home]: {teamName: home.name, totalTilesDecremented: home.getTotalTilesDecremented(), teamIcon: home.teamIcon},
          [Side.Away]: {teamName: away.name, totalTilesDecremented: away.getTotalTilesDecremented(), teamIcon: away.teamIcon},
        };
        this.eventEmitter.emit(StateChangeEvent.ScoreBoardUpdate, teamInfo);
        break;
    }
  }

  private enterState(state: GameState) {
    switch (state) {
      case GameState.Resolving:
        // this.printGameStateMsg();
        this.grid.killVisitors();
        const isOver = this.checkWinLossTie();

        if(!isOver) {
          this.updateMoves();
        }
        break;
      case GameState.Thinking:
      case GameState.Updating:
        // this.printGameStateMsg();
        break;
      case GameState.HomeTeamWins:
        this.teams[Side.Home].win();
        this.printGameStateMsg();
        this.teams[Side.Away].teamKill();

        break;
      case GameState.AwayTeamWins:
        this.teams[Side.Away].win();
        this.printGameStateMsg();
        this.teams[Side.Home].teamKill();
        break;
      case GameState.Draw:
      case GameState.Error:
        this.printGameStateMsg();
        this.teams[Side.Home].teamKill();
        this.teams[Side.Away].teamKill();
        break
      case GameState.Initializing:
        this.printGameStateMsg();
        break;
    }

    if (this.isGameOver(state)) {
      const {home, away} = this.teams;
      const { home: homeMonsterType } = this.teams[Side.Home].getPreferredTypes();
      const { home: awayMonsterType, away: awayAlternateMonsterType } = this.teams[Side.Away].getPreferredTypes();
      const useAlternateMonster = homeMonsterType === awayMonsterType;

      const eventArgs: MatchEventArgs = {
        state,
        team: {
          [Side.Home]: {
            name: home.name,
            org: home.org,
            state: home.state,
            monsterType: homeMonsterType,
            reason: home.errorReason,
            tilesDecremented: home.getTotalTilesDecremented()
          },
          [Side.Away]: {
            name: away.name,
            org: away.org,
            state: away.state,
            monsterType: useAlternateMonster ? awayAlternateMonsterType : awayMonsterType,
            reason: away.errorReason,
            tilesDecremented: away.getTotalTilesDecremented()
          }
        }
      };
      this.eventEmitter.emit(MatchEvent.GameEnd, eventArgs);
    }
  }

  private isGameOver(state: GameState) {
    return state === GameState.Draw ||
      state === GameState.Error ||
      state === GameState.HomeTeamWins ||
      state === GameState.AwayTeamWins;
  }

  private transitionState(nextState: GameState) {
    if (nextState !== GameState.Initializing) {
      if (this.isGameOver(this.state)) {
        return false;
      }
    }

    this._state = nextState;
    return true;
  }

  private printGameStateMsg(msg: string = '') {
    console.log('[Game State] ::::', msg ? msg : this.state);
  }

  private setState(nextState: GameState) {
    const lastState = this.state;
    if (this.transitionState(nextState)) {
      this.exitState(lastState);
      this.enterState(this.state);

      const stateUpdatedEventArgs: StateUpdatedEventArgs<GameState> = {
        last: lastState,
        current: this.state as GameState,
        target: this,
      }

      this.eventEmitter.emit(StateChangeEvent.Updated, stateUpdatedEventArgs);
    }
  }

  applyMap(map: GridMap){
    map.tiles.forEach(tile=>{
        console.log(tile);
        this.matchConfig.grid.setTileAtIndex(tile.x,tile.y,tile.status);
      })
  }

 
}

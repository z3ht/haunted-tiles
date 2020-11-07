import { Team } from './team';

export enum MonsterType {
  Bobo = 'bobo',
  Triclops = 'triclops',
  Goldy = 'goldy',
  Pinky = 'pinky',
  Spike = 'spike',
  Grouchy = 'grouchy',
}

export type WorldPosition = [number, number];

export type Coord = [number, number];

export interface INeighbor {
  [MoveDirection.North]: ILocation | null;
  [MoveDirection.South]: ILocation | null;
  [MoveDirection.East]: ILocation | null;
  [MoveDirection.West]: ILocation | null;
}

export interface IVisitor {
  id: number;
  side: Side;
  die();
  addDecrementedTiles();
}

export interface ILocation {
  neighbor: INeighbor;
  index: number, // single dimension index of the tile within the grid
  coord: Coord, // [x, y] index of the tile within the grid
  state: TileState;
  acceptVisitor(visitor: IVisitor): boolean;
  exitVisitor(visitor: IVisitor);
  getPosition(): WorldPosition;
  setState(tile: TileState)
}

export enum Side {
  Home = 'home',
  Away = 'away',
}


export enum MoveDirection {
  North = 'north',
  South = 'south',
  East = 'east',
  West = 'west',
  None = 'none',
}

export enum TileState {
  Good = 3,
  Warning = 2,
  Danger = 1,
  Broken = 0,
}

export interface ITeamMemberState {
  coord: Coord;
  isDead: boolean;
}

export type TeamStates = Record<Side, ITeamMemberState[]>;

export interface IGameState {
  boardSize: [number, number];
  tileStates: TileState[][];
  teamStates: TeamStates;
}

export type MoveSet = MoveDirection[];

export type GetMoveSetFn = (gameState: IGameState, side: Side) => MoveSet;

export interface ITeamConfig {
  name: string;
  org: string;
  preferredMonsters: {
    [Side.Home]: MonsterType;
    [Side.Away]: MonsterType;
  };
  aiSrc: string;
}

export interface StateUpdatedEventArgs<State, Payload = any> {
  current: State;
  last: State;
  target: any;
  payload?: Payload;
}

export enum StateChangeEvent {
  ScoreBoardUpdate = 'scoreboard_update',
  Updated = 'state_updated',
  GameOver = 'game_over',
}

export enum MatchEvent {
  GameEnd = 'game_end',
  GameStart = 'game_start'
}

export enum GameState {
  Initializing = 'initializing',
  Resolving = 'resolving',
  Thinking = 'thinking',
  Updating = 'updating',
  HomeTeamWins = 'homeTeamWins',
  AwayTeamWins = 'awayTeamWins',
  Error = 'error',
  Draw = 'draw',
}

export enum GameWinningSide {
  Home = 'home',
  Away = 'away',
  Draw = 'draw',
}

export enum TeamState {
  Error = 'error',
  Initializing = 'initializing',
  Thinking = 'thinking',
  Updating = 'updating',
  Win = 'win',
  Dead = 'dead',
}

export type MatchTeamInfo = Record<Side, {
  name: string,
  org: string,
  state: TeamState
  monsterType: MonsterType,
  reason?: ErrorReason,
  tilesDecremented?: number
}>

export interface MatchEventArgs {
  state: GameState;
  team: MatchTeamInfo;
}

export enum ErrorReason {
  Compile = 'compile',
  RunTime = 'run-time',
  Bug = 'bug',
  Unknown = 'unknown',
}

export interface GridMap{
  name: string,
  tiles: {
    x:number,
    y:number,
    status:number
  }[]
}

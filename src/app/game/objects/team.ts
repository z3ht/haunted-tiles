import { format } from 'path';
import { GameObjects, Scene, Events } from 'phaser';
import { ToastService } from 'src/app/game-host/toast.service';
import { createSandboxAsync, ISandbox } from 'src/app/helpers';
import { ErrorReason, IGameState, ILocation, ITeamConfig, ITeamMemberState, MonsterType, MoveSet, Side, StateChangeEvent, StateUpdatedEventArgs, TeamState } from './interfaces';
import { Monster, MonsterState } from './monster';

export class Team extends GameObjects.Group {
  private _currentSide: Side;
  get currentSide() { return this._currentSide; }

  private _state: TeamState;
  get state() { return this._state };

  private _errorReason: ErrorReason | null = null;
  get errorReason() { return this._errorReason; }

  private _teamIcon: MonsterType ;
  get teamIcon() { return this._teamIcon; }

  private eventEmitter = new Events.EventEmitter();

  get count(): number {
    return this.countActive(true);
  }

  get locations(): ILocation[] {
    return this.getChildren()
      .map((monster: Monster) => monster.location);
  }

  private sandbox: ISandbox<MoveSet> = null;

  private showLog = true;

  get org() { return this.config.org };

  constructor(scene: Scene, private config: ITeamConfig, private toastService: ToastService) {
    super(scene);
    scene.add.existing(this);
    this.runChildUpdate = true;
    this.maxSize = 3;

    this.name = this.config.name;

    this.reset();
  }

  log(...args: any) {
    if (this.showLog) {
      console.log(`[T-${this.name}]`, ...args);
    }
  }

  getPreferredTypes() {
    return {...this.config.preferredMonsters};
  }

  getTotalTilesDecremented(){
    let tilesDec = 0;
    this.getChildren().forEach((monster: Monster, index: number) => {
      tilesDec += monster.tilesDecremented;
    });
    return tilesDec;
  }

  async setupTeam(locations: ILocation[], side: Side, useAlternateMonster = false) {
    if(!this.sandbox) {
      try {
        this.sandbox = await createSandboxAsync<MoveSet>(this.name, this.config.aiSrc);
      } catch (err) {
        const formattedSide = side.charAt(0).toUpperCase() + side.substring(1);
        this.toastService.showError(`${formattedSide} team loses round`, `${formattedSide} Team: script failed to load`);
        this.setState(TeamState.Error, ErrorReason.Compile);
      }
    }

    this._errorReason = null;
    this.maxSize = locations.length;
    this._currentSide = side;
    const monsterTypeSide = useAlternateMonster ? Side.Away : Side.Home;

    const monsterType = this.config.preferredMonsters[monsterTypeSide];
    this._teamIcon = monsterType;
    for(let i = 0; i < this.maxSize; i++) {
      const monster = new Monster(this.scene, 0, 0, monsterType, side);
      monster.setLocation(locations[i]);
      monster.on(StateChangeEvent.Updated, this.stateChangeHandler, this);
      this.add(monster, true);
      if (this.state === TeamState.Error) {
        // randomly stagger the dying in the event the ai fails to compile
        this.delayMonsterKill(monster);
      }
    }

    this.setState(TeamState.Thinking);
  }

  private delayMonsterKill(monster: Monster, ms = -1) {
    setTimeout(() => monster.errorOut(), ms < 0 ? Math.floor(Math.random() * 700) : ms)
  }

  teamKill() {
    this.getChildren().forEach((monster: Monster) => this.delayMonsterKill(monster));
  }

  getNextMovesAsync(gameState: IGameState, timeout?: number) {
    return this.sandbox.evalAsync([gameState, this.currentSide], timeout).catch(err => {
      this.setState(TeamState.Error, ErrorReason.RunTime);
      throw err;
    });
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

  reset() {
    this._errorReason = null;
    this.clearTeam();
    this.setState(TeamState.Initializing);
  }

  clearTeam() {
    // remove event handlers to prevent memory leak
    this.getChildren().forEach(monster => monster.removeAllListeners(StateChangeEvent.Updated));
    this.clear(true, true);
  }

  win() {
    this.getChildren().forEach((monster: Monster) => monster.win());
    this.setState(TeamState.Win);
  }

  moveTeam(moves: MoveSet) {
    this.getChildren().forEach((monster: Monster, index: number) => {
      monster.move(moves[index])
    });
    this.setState(TeamState.Updating);
  }

  errorTeamOut() {
    this.getChildren().forEach((monster: Monster) => monster.errorOut());
  }

  serialize(): ITeamMemberState[] {
    return this.getChildren().reduce((states, monster: Monster) => {
      const coord = monster.location.coord;
      const isDead = monster.state === MonsterState.Dead;
      states.push({coord, isDead});
      return states;
    }, [] as ITeamMemberState[])
  }

  private stateChangeHandler = function(this: Team, {current}: StateUpdatedEventArgs<MonsterState>) {
    const monsterStates = this.getChildren()
      .map((monster: Monster) => monster.state as MonsterState);

    if (monsterStates.every(state => state === MonsterState.Error)) {
      this.setState(TeamState.Error, ErrorReason.Bug);
      return;
    }

    if (monsterStates.every(state => state === MonsterState.Dead)) {
      this.setState(TeamState.Dead);
      return;
    }

    if (monsterStates.every(state => state === MonsterState.Thinking || state === MonsterState.Dead)) {
      this.setState(TeamState.Thinking);
      return;
    }
  };

  private transitionState(nextState: TeamState) {
    if (nextState !== TeamState.Initializing) {
      if (this.state === TeamState.Dead ||
          this.state === TeamState.Error ||
          this.state === TeamState.Win) {
            return false;
      }
    }

    this._state = nextState;
    return true;
  }

  private setState(nextState: TeamState, info?: ErrorReason) {
    const lastState = this.state;
    if (this.state !== nextState && this.transitionState(nextState)) {
      if (this.state === TeamState.Error) {
        this._errorReason = info || ErrorReason.Unknown;
      } else {
        this._errorReason = null;
      }

      const stateUpdatedEventArgs: StateUpdatedEventArgs<TeamState, ErrorReason> = {
        last: lastState,
        current: this.state as TeamState,
        target: this,
        payload: info
      }

      this.eventEmitter.emit(StateChangeEvent.Updated, stateUpdatedEventArgs);
    }
  }
}

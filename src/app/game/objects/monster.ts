import { GameObjects, Scene, Types, Animations, Math } from 'phaser';
import { MakeIdGen } from 'src/app/helpers/id-gen';
import {
  ILocation,
  IVisitor,
  MonsterType,
  MoveDirection,
  Side,
  StateChangeEvent,
  StateUpdatedEventArgs,
} from './interfaces';

export enum MonsterColor {
  Bobo = 0xf46969,
  Triclops = 0xb383ff,
  Spike = 0x85de00,
  Goldy = 0xffcc06,
  Grouchy = 0x54d2ff,
  Pinky = 0xff95bd,
}

export const MonstersAtlas = 'monsters';
const assetsPath = 'assets/sprites';

export function loadMonsterAssets(scene: Scene) {
  scene.load.multiatlas(MonstersAtlas, `${assetsPath}/monsters.json`, assetsPath);
}

export enum MonsterAnim {
  Attack = 'attack',
  Die = 'die',
  Idle = 'idle',
  Jump = 'jump',
  Run = 'run',
  Walk = 'walk',
}

export enum MonsterState {
  MovingNorth = 'moving_north',
  MovingSouth = 'moving_south',
  MovingEast = 'moving_east',
  MovingWest = 'moving_west',
  Idle = 'idle',
  Thinking = 'thinking',
  Dead = 'dead',
  Win = 'win',
  Error = 'error',
}

export function createMonsterAnimFrames(anims: Animations.AnimationManager, monster: MonsterType) {
  const start = 0;
  const zeroPad = 3;
  const suffix = '.png';
  const animFrameMap: Record<string, Types.Animations.AnimationFrame[]> = {
    [MonsterAnim.Attack]: anims.generateFrameNames(MonstersAtlas, { prefix: `${monster}/attack/Attack_`, end: 7, start, zeroPad, suffix }),
    [MonsterAnim.Die]: anims.generateFrameNames(MonstersAtlas, { prefix: `${monster}/die/Die_`, end: 9, start, zeroPad, suffix }),
    [MonsterAnim.Idle]: anims.generateFrameNames(MonstersAtlas, { prefix: `${monster}/idle/Idle_`, end: 11, start, zeroPad, suffix }),
    [MonsterAnim.Jump]: anims.generateFrameNames(MonstersAtlas, { prefix: `${monster}/jump/Jump_`, end: 4, start, zeroPad, suffix }),
    [MonsterAnim.Run]: anims.generateFrameNames(MonstersAtlas, { prefix: `${monster}/run/Run_`, end: 7, start, zeroPad, suffix }),
    [MonsterAnim.Walk]: anims.generateFrameNames(MonstersAtlas, { prefix: `${monster}/walk/Walk_`, end: 11, start, zeroPad, suffix }),
  };

  anims.create({ key: `${monster}_${MonsterAnim.Attack}`, frames: animFrameMap[MonsterAnim.Attack], frameRate: 5, repeat: -1 });
  anims.create({ key: `${monster}_${MonsterAnim.Die}`, frames: animFrameMap[MonsterAnim.Die], frameRate: 15, hideOnComplete: true });
  anims.create({ key: `${monster}_${MonsterAnim.Idle}`, frames: animFrameMap[MonsterAnim.Idle], frameRate: 12, repeat: -1 });
  anims.create({ key: `${monster}_${MonsterAnim.Jump}`, frames: animFrameMap[MonsterAnim.Jump], frameRate: 15, repeat: -1 });
  anims.create({ key: `${monster}_${MonsterAnim.Run}`, frames: animFrameMap[MonsterAnim.Run], frameRate: 15, repeat: -1 });
  anims.create({ key: `${monster}_${MonsterAnim.Walk}`, frames: animFrameMap[MonsterAnim.Walk], frameRate: 15, repeat: -1 });
}

export function createAllMonsterAnimFrames(anims: Animations.AnimationManager) {
  Object.values(MonsterType).forEach(monster => createMonsterAnimFrames(anims, monster));
}

const idGen = MakeIdGen();

const MONSTER_SCALE = 0.25;
const JUMP_SCALE_MULTIPLIER = 1.5;

export class Monster extends GameObjects.Sprite implements IVisitor {
  tilesDecremented =0;
  private lastLocation: ILocation;
  private nextLocation: ILocation | null = null;
  private actionTime = 0;
  private maxActionTime = 2000;

  readonly id = idGen.next().value as number;

  get location(): ILocation { return this.lastLocation; }

  showLog = false;
  showId = false;

  private displayText: GameObjects.Text;

  constructor(scene: Scene, x: number, y: number, public readonly type: MonsterType, public readonly side: Side) {
    super(scene, x, y, MonstersAtlas, `${type}/idle/Idle_000.png`);

    this.scale = MONSTER_SCALE;
    this.state = MonsterState.Thinking;

    if (this.showId) {
      this.displayText = scene.add.text(x, y, `${this.id}`);
    }
  }

  destroy(fromScene?: boolean): void {
    this.displayText?.destroy(fromScene);
    super.destroy(fromScene);
  }

  private updateTextPos() {
    this.displayText?.setPosition(this.x, this.y, 100);
  }

  log(...args) {
    if (this.showLog) {
      console.log(`[M-${this.id}]`, ...args);
    }
  }

  play(key: MonsterAnim, ignoreIfPlaying?: boolean, startFrame?: integer): this {
    return super.play(`${this.type}_${key}`, ignoreIfPlaying, startFrame);
  };

  update(time: number, dt: number): void {
    this.updateState(dt);
  }

  setLocation(location: ILocation) {
    this.lastLocation = location;

    const [x, y] = location.getPosition();
    this.setPosition(x, y);
    this.updateTextPos();

    this.setState(MonsterState.Thinking);
  }

  die() {
    this.setState(MonsterState.Dead);
  }

  addDecrementedTiles() {
    this.tilesDecremented +=1;
  }

  errorOut() {
    this.setState(MonsterState.Error)
  }

  move(direction: MoveDirection) {
    switch (direction) {
      case MoveDirection.North: this.setState(MonsterState.MovingNorth); break;
      case MoveDirection.South: this.setState(MonsterState.MovingSouth); break;
      case MoveDirection.East: this.setState(MonsterState.MovingEast); break;
      case MoveDirection.West: this.setState(MonsterState.MovingWest); break;
      case MoveDirection.None:
      default:
        this.setState(MonsterState.Idle);
        break;
    }
  }

  win() {
    this.setState(MonsterState.Win);
  }

  isAlive() {
    return this.state !== MonsterState.Dead &&
      this.state !== MonsterState.Error;
  }

  private exitState(state: MonsterState) {
    switch (state) {
      case MonsterState.Dead:
      case MonsterState.Error:
        return;
      case MonsterState.Idle:
        this.actionTime = 0;
        break;
      case MonsterState.Win:
      case MonsterState.Thinking:
        return;
      case MonsterState.MovingNorth:
      case MonsterState.MovingSouth:
      case MonsterState.MovingEast:
      case MonsterState.MovingWest:
        this.actionTime = 0;
        break;
      default:
        console.error('unhandled exit state', this.state);
        return;
    }
  }

  private startState(state: MonsterState) {
    if (state === MonsterState.Dead || this.state === MonsterState.Error) {
      this.play(MonsterAnim.Die);
      this.lastLocation.exitVisitor(this);
      return;
    }

    if (state === MonsterState.Win) {
      this.play(MonsterAnim.Jump);
      return;
    }

    if (state === MonsterState.Thinking) {
      this.play(MonsterAnim.Idle, false, Math.Between(0, 11));
      return;
    }

    if (state === MonsterState.Idle) {
      this.play(MonsterAnim.Jump);
      return;
    }

    let moveDirection: MoveDirection;
    switch (state) {
      case MonsterState.MovingNorth:
        moveDirection = MoveDirection.North;
        break;

      case MonsterState.MovingSouth:
        moveDirection = MoveDirection.South;
        break;

      case MonsterState.MovingEast:
        this.flipX = true;
        moveDirection = MoveDirection.East;
        break;

      case MonsterState.MovingWest:
        this.flipX = false;
        moveDirection = MoveDirection.West;
        break;

      // catch any new states that are not explicitly handled
      default:
        console.error('unhandled start state', this.state);
        return;
    }

    this.lastLocation.exitVisitor(this);
    this.nextLocation = this.lastLocation.neighbor[moveDirection];
    this.play(MonsterAnim.Run);
  }

  private isAnimationPlaying(animation: MonsterAnim) {
    return this.anims.getCurrentKey() === `${this.type}_${animation}`
  }

  private updateState(dt: number) {
    switch (this.state) {
      case MonsterState.Error:
      case MonsterState.Win:
      case MonsterState.Dead:
        // nothing to update!
        return;

      case MonsterState.Idle:
        this.actionTime += dt;

        const halfMaxActionTime = this.maxActionTime / 2.0;
        const quarterMaxActionTime = this.maxActionTime / 4.0;
        const normalizedJumpUpTime = Math.Clamp(this.actionTime / quarterMaxActionTime, 0, 1);
        const normalizedJumpDownTime = Math.Clamp((this.actionTime - quarterMaxActionTime) / quarterMaxActionTime, 0, 1);

        if (this.actionTime < quarterMaxActionTime) {
          this.scale = Math.Interpolation.Linear([MONSTER_SCALE, MONSTER_SCALE * JUMP_SCALE_MULTIPLIER], normalizedJumpUpTime);
        } else if (this.actionTime >= quarterMaxActionTime && this.actionTime < halfMaxActionTime) {
          this.scale = Math.Interpolation.Linear([MONSTER_SCALE * JUMP_SCALE_MULTIPLIER, MONSTER_SCALE], normalizedJumpDownTime);
        } else if (this.actionTime >= halfMaxActionTime && this.actionTime < this.maxActionTime) {
          if (this.isAnimationPlaying(MonsterAnim.Jump)) {
            this.scale = MONSTER_SCALE;
            this.play(MonsterAnim.Idle, false, Math.Between(0, 11));
            this.lastLocation.acceptVisitor(this);
          }
        }

        if (this.actionTime >= this.maxActionTime) {
          this.setState(MonsterState.Thinking);
        }
        return;

      case MonsterState.Thinking:
        // waiting for instruction
        return;

      case MonsterState.MovingEast:
      case MonsterState.MovingWest:
      case MonsterState.MovingNorth:
      case MonsterState.MovingSouth:
        this.actionTime += dt;
        const normalizedActionTime = Math.Clamp(this.actionTime / this.maxActionTime, 0, 1);

        const [lx, ly] = this.lastLocation.getPosition();
        const [nx, ny] = this.nextLocation.getPosition();
        const x = Math.Interpolation.Linear([lx, nx], normalizedActionTime);
        const y = Math.Interpolation.Linear([ly, ny], normalizedActionTime);
        this.setPosition(x, y)
        this.updateTextPos();

        if (normalizedActionTime === 1.0) {
          this.lastLocation = this.nextLocation;
          this.nextLocation = null;
          this.lastLocation.acceptVisitor(this);
          this.setState(MonsterState.Thinking);
        }
        return;
    }
  }

  // transitionState validates the proposed state transition
  // and if it validates, updates the current state
  // returns true if a state update occurs
  private transitionState(nextState: MonsterState): boolean {
    if (this.state !== MonsterState.Dead &&
      this.state !== MonsterState.Error &&
      this.state !== MonsterState.Win) {
      this.state = nextState;
      return true;
    }
    return false;
  }

  setState(state: MonsterState): this {
    // make sure our state actually changed!
    const lastState = this.state as MonsterState;
    if (this.transitionState(state)) {
      this.exitState(lastState);
      this.startState(this.state as MonsterState);

      const stateUpdatedEventArgs: StateUpdatedEventArgs<MonsterState> = {
        last: lastState,
        current: this.state as MonsterState,
        target: this,
      }

      this.emit(StateChangeEvent.Updated, stateUpdatedEventArgs);
    }
    return this;
  }
}

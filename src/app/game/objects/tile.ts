import { GameObjects, Scene, Geom, Math as PMath, Display } from 'phaser';
import { ILocation, INeighbor, IVisitor, TileState, Coord, WorldPosition } from './interfaces';

export const TileAtlas = 'tiles';
const assetsPath = 'assets/sprites';

export function loadTileAssets(scene: Scene) {
  scene.load.multiatlas(TileAtlas, `${assetsPath}/tiles.json`, assetsPath);
}

export class Tile extends GameObjects.Container implements ILocation {
  state: TileState = TileState.Good;
  displayTile: GameObjects.TileSprite;
  transitionTile: GameObjects.TileSprite;
  visitors = new Set<IVisitor>();

  neighbor: INeighbor;

  constructor(
    scene: Scene,
    x: number,
    y: number,
    width: number,
    height: number,
    public readonly index: number,
    public readonly coord: Coord
  ){
    super(scene, x, y);

    this.displayTile = new GameObjects.TileSprite(
      scene,
      0,
      0,
      width,
      height,
      'tiles',
      '3hp-tile.png'
    );
    this.displayTile.tileScaleX = width / 256;
    this.displayTile.tileScaleY = height / 256;
    this.transitionTile = new GameObjects.TileSprite(
      scene,
      0,
      0,
      width,
      height,
      'tiles',
      '2hp-tile.png'
    );
    this.transitionTile.tileScaleX = width / 256;
    this.transitionTile.tileScaleY = height / 256;
    this.transitionTile.setVisible(false);

    this.add(this.displayTile);
    this.add(this.transitionTile);
  }


  private transition(frameKey: string) {
    this.displayTile.setAlpha(1);
    this.transitionTile.setFrame(frameKey);
    this.transitionTile.setVisible(true);
    this.transitionTile.setAlpha(0);
    this.scene.tweens.addCounter({
      from: 0, to: 100, duration: 300,
      ease: PMath.Easing.Sine.InOut,
      onUpdate: tween => {
        const value = tween.getValue();

        if (value === 100) {
          this.displayTile.setFrame(frameKey);
          this.displayTile.setAlpha(this.state !== TileState.Broken ? 1 : 0.5);
          this.transitionTile.setVisible(false);
        } else if (value > 0 && value <= 50) {
          const fadeIn = value / 50;
          this.transitionTile.setAlpha(fadeIn);
        } else if (value > 50) {
          this.transitionTile.setAlpha(1);
          const fadeOut = (100 - value) / 50;
          this.displayTile.setAlpha(fadeOut);
        }
      }
    })
  }

  getPosition(): WorldPosition {
    return [
      this.x + this.parentContainer.x,
      this.y + this.parentContainer.y
    ];
  }

  exitVisitor(visitor: IVisitor){
    this.visitors.delete(visitor);
  }

  acceptVisitor(visitor: IVisitor): boolean {
    let nextState = TileState.Broken;
    switch(this.state) {
      case TileState.Good:
        nextState = TileState.Warning;
        visitor.addDecrementedTiles();
        break;
      case TileState.Warning:
        nextState = TileState.Danger;
        visitor.addDecrementedTiles();
        break;
      case TileState.Danger:
      default:
        nextState = TileState.Broken;
        visitor.addDecrementedTiles();
        break;
    }

    this.setState(nextState);

    if (this.state === TileState.Broken) {
      visitor.die();
    } else {
      this.visitors.add(visitor);
    }

    return nextState != TileState.Broken;
  }

  setState(state: TileState): this {
    if (this.state === state) {
      return;
    }
    super.setState(state);


    switch (state) {
      case TileState.Good:
        this.transition('3hp-tile.png');
        break;
      case TileState.Warning:
        this.transition('2hp-tile.png');
        break;
      case TileState.Danger:
        this.transition('1hp-tile.png');
        break;
      case TileState.Broken:
        this.transition('0hp-tile.png');
        break;
    }

    return this;
  }

  killVisitors() {
    if (this.state === TileState.Broken && this.visitors.size > 0) {
      // because the act of dying removes a visitor from a tile
      // we need to create a different array to iterate against
      // to kill existing visitors
      [...this.visitors].forEach(v => v.die());
    }
  }

  reset(state = TileState.Good) {
    this.visitors.clear();
    this.setState(state);
  }
}

import { GameObjects, Scene, Scale } from 'phaser';
import { ILocation, INeighbor, TileState } from './interfaces';
import { KillTile } from './kill-tile';
import { Tile } from './tile';

export function squareGrid(scene: Scene, scale: Scale.ScaleManager, size: number): TileGrid {
  const cellSize = scale.height / (size + 2);
  const gridHeight = cellSize * size;
  const gridWidth = cellSize * size;
  const gridY = cellSize;
  const gridX = (scale.width - gridWidth) / 2;
  const grid = new TileGrid(scene, gridX, gridY, gridWidth, gridHeight, size);
  return grid;
}

export class TileGrid extends GameObjects.Container {

  tiles: Tile[] = [];
  private readonly squareSize: number;
  private readonly gridLength:number;

  private states: TileState[];

  constructor(scene: Scene, x: number, y: number, public readonly width: number, public readonly height: number, public readonly size: number) {
    super(scene, x, y);
    scene.add.existing(this);

    this.squareSize = width / size;
    if(width > height){
      this.squareSize = height / size;
    }

    const halfSquareSize = this.squareSize * 0.5;

    this.states = Array.from({length: size*size}, () => TileState.Good);

    // create the tiles
    for(let i = 0; i < size * size; i++) {
      const tile = new Tile(
        scene,
        (((i % size) * this.squareSize) + halfSquareSize),
        ((Math.floor(i / size) * this.squareSize) + halfSquareSize),
        this.squareSize,
        this.squareSize,
        i,
        [Math.floor(i / size), i % size]
      );

      this.tiles.push(tile);
    }

    const killNeighbors: INeighbor = { north: null, south: null, west: null, east: null };
    const offsetX = this.x;
    const offsetY = this.y;

    // resolve neighbors
    for(let i = 0; i < size * size; i ++) {
      const curr_x = i % size;
      const curr_y = Math.floor(i / size);
      const tile = this.tiles[i];

      let north: ILocation = this.getTileAtIndex(curr_y-1, curr_x);
      if (!north) { north  = new KillTile([curr_y-1, curr_x], {...killNeighbors, south: tile}, [tile.x + offsetX, tile.y - this.squareSize + offsetY]); }

      let south: ILocation = this.getTileAtIndex(curr_y+1, curr_x);
      if (!south) { south  = new KillTile([curr_y+1, curr_x], {...killNeighbors, north: tile}, [tile.x + offsetX, tile.y + this.squareSize + offsetY]); }

      let west:  ILocation = this.getTileAtIndex(curr_y, curr_x-1);
      if (!west)  { west   = new KillTile([curr_y, curr_x-1], {...killNeighbors, east: tile}, [tile.x - this.squareSize + offsetX, tile.y + offsetY]); }

      let east:  ILocation = this.getTileAtIndex(curr_y, curr_x+1);
      if (!east)  { east   = new KillTile([curr_y, curr_x+1], {...killNeighbors, west: tile}, [tile.x + this.squareSize + offsetX, tile.y + offsetY]); }


      this.tiles[i].neighbor = { north, south, west, east, };
    }

    this.add(this.tiles);

    this.gridLength = size;
  }

  setTileStates(tileStates: TileState[]) {
    this.states = tileStates;
    this.tiles.forEach((tile, i) => {
      const tileState = tileStates[i] || TileState.Good;
      tile.setState(tileState);
    })
  }

  getGridLength() {
    return this.gridLength;
  }

  getTileAtIndex(row: number, column: number): ILocation | null {
    const size1 = this.size - 1;
    if (row < 0 || row > size1 || column < 0 || column > size1) {
      return null;
    }

    return this.tiles[row * this.size + column] as Tile;
  }

  setTileAtIndex(row:number, column:number, tileState: TileState){
    let tile = this.getTileAtIndex(row,column);
    tile.setState(tileState);
    
  }

  getTileAtPos(x: number, y: number): ILocation | null {
    const relative_x = x - this.x;
    const relative_y = y - this.y;
    const width1 = this.width - 1;
    const height1 = this.height - 1;

    if (x < 0 || x > width1 || y < 0 || y > height1) {
      return null;
    }

    const column = Math.floor(relative_x / this.squareSize);
    const row = Math.floor(relative_y / this.squareSize);

    return this.tiles[row * this.size + column] as Tile;
  }

  reset() {
    this.tiles.forEach((t, i) => t.reset(this.states[i]));
  }

  serialize(): TileState[][] {
    const arrayLike = {length: this.size};
    const tileStates: TileState[][] =
      Array.from(arrayLike, (_, row) =>
        Array.from(arrayLike, (_, col) =>
          this.tiles[row * this.size + col].state
        )
      );

    return tileStates;
  }

  killVisitors() {
    this.tiles.forEach(tile => tile.killVisitors());
  }

}
